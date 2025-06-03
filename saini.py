import os
import re
import time
import mmap
import datetime
import aiohttp
import aiofiles
import asyncio
import logging
import requests
import tgcrypto
import subprocess
import concurrent.futures
from math import ceil
from utils import progress_bar
from pyrogram import Client, filters
from pyrogram.types import Message
from io import BytesIO
from pathlib import Path  
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global counter for failed attempts
failed_counter = 0

async def download_with_retry(url, file_path, max_retries=2):
    """Download file with automatic retries"""
    for attempt in range(max_retries + 1):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        async with aiofiles.open(file_path, 'wb') as f:
                            await f.write(await response.read())
                        return True
                    logger.warning(f"Download failed (attempt {attempt+1}): HTTP {response.status}")
        except Exception as e:
            logger.error(f"Download error (attempt {attempt+1}): {str(e)}")
        
        if attempt < max_retries:
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
    return False

def duration(filename):
    """Get video duration using ffprobe"""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", 
             "-of", "default=noprint_wrappers=1:nokey=1", filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return float(result.stdout)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error getting duration: {e.stderr.decode()}")
        return 0

def get_mps_and_keys(api_url):
    """Fetch MPD and keys from API"""
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        response_json = response.json()
        return response_json.get('MPD'), response_json.get('KEYS')
    except Exception as e:
        logger.error(f"Error fetching MPD/keys: {str(e)}")
        return None, None

async def exec(cmd):
    """Execute shell command with error handling"""
    try:
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"Command failed: {cmd}\nError: {stderr.decode()}")
            return False
        
        output = stdout.decode().strip()
        if output:
            logger.info(f"Command output: {output}")
        return output
    except Exception as e:
        logger.error(f"Error executing command: {str(e)}")
        return False

async def pdf_download(url, file_name, max_retries=2):
    """Download PDF with retry mechanism"""
    try:
        if os.path.exists(file_name):
            os.remove(file_name)
            
        if "drive.google.com" in url:
            url = url.replace("file/d/", "uc?export=download&id=")
            
        success = await download_with_retry(url, file_name, max_retries)
        return file_name if success else None
    except Exception as e:
        logger.error(f"PDF download error: {str(e)}")
        return None

async def download_video(url, cmd, name, max_retries=2):
    """Download video with retry mechanism"""
    global failed_counter
    
    for attempt in range(max_retries + 1):
        try:
            download_cmd = f'{cmd} -R 25 --fragment-retries 25 --external-downloader aria2c --downloader-args "aria2c: -x 16 -j 32"'
            logger.info(f"Download command: {download_cmd}")
            
            proc = await asyncio.create_subprocess_shell(
                download_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                if "visionias" in cmd and failed_counter <= 10:
                    failed_counter += 1
                    await asyncio.sleep(5)
                    continue
                logger.error(f"Download failed (attempt {attempt+1}): {stderr.decode()}")
                continue
            
            # Check for downloaded file
            for ext in ['', '.webm', '.mkv', '.mp4', '.mp4.webm']:
                file_path = f"{name}{ext}"
                if os.path.isfile(file_path):
                    return file_path
            
            return name.split(".")[0] + ".mp4"  # Default fallback
            
        except Exception as e:
            logger.error(f"Video download error (attempt {attempt+1}): {str(e)}")
            if attempt < max_retries:
                await asyncio.sleep(3)
    
    return None

async def decrypt_and_merge_video(mpd_url, keys_string, output_path, output_name, quality="720"):
    """Decrypt and merge video streams with cleanup"""
    try:
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)

        # Download video
        cmd1 = f'yt-dlp -f "bv[height<={quality}]+ba/b" -o "{output_path}/file.%(ext)s" --allow-unplayable-format --no-check-certificate --external-downloader aria2c "{mpd_url}"'
        if not await exec(cmd1):
            raise Exception("Failed to download video")

        # Process downloaded files
        video_decrypted = False
        audio_decrypted = False

        for data in output_path.iterdir():
            if data.suffix == ".mp4" and not video_decrypted:
                cmd2 = f'mp4decrypt {keys_string} --show-progress "{data}" "{output_path}/video.mp4"'
                if await exec(cmd2) and (output_path / "video.mp4").exists():
                    video_decrypted = True
                data.unlink()
                
            elif data.suffix == ".m4a" and not audio_decrypted:
                cmd3 = f'mp4decrypt {keys_string} --show-progress "{data}" "{output_path}/audio.m4a"'
                if await exec(cmd3) and (output_path / "audio.m4a").exists():
                    audio_decrypted = True
                data.unlink()

        if not video_decrypted or not audio_decrypted:
            raise Exception("Decryption failed")

        # Merge streams
        output_file = output_path / f"{output_name}.mp4"
        cmd4 = f'ffmpeg -i "{output_path}/video.mp4" -i "{output_path}/audio.m4a" -c copy "{output_file}"'
        if not await exec(cmd4):
            raise Exception("Failed to merge streams")

        # Cleanup
        for temp_file in ['video.mp4', 'audio.m4a']:
            temp_path = output_path / temp_file
            if temp_path.exists():
                temp_path.unlink()

        return str(output_file)

    except Exception as e:
        logger.error(f"Decrypt/merge error: {str(e)}")
        # Cleanup on failure
        for temp_file in ['video.mp4', 'audio.m4a', f"{output_name}.mp4"]:
            temp_path = output_path / temp_file
            if temp_path.exists():
                temp_path.unlink()
        raise

async def send_vid(bot: Client, m: Message, cc, filename, thumb, name, prog, channel_id):
    """Send video with thumbnail generation"""
    try:
        # Generate thumbnail
        thumb_path = f"{filename}.jpg"
        if not os.path.exists(thumb_path):
            await exec(f'ffmpeg -i "{filename}" -ss 00:00:10 -vframes 1 "{thumb_path}"')
        
        await prog.delete(True)
        
        # Use provided thumb or generated one
        thumbnail = thumb if thumb != "/d" and os.path.exists(thumb) else thumb_path
        
        dur = int(duration(filename))
        
        try:
            await bot.send_video(
                channel_id,
                filename,
                caption=cc,
                supports_streaming=True,
                thumb=thumbnail,
                duration=dur,
                progress=progress_bar,
                progress_args=(prog, time.time())
            )
        except Exception:
            await bot.send_document(
                channel_id,
                filename,
                caption=cc,
                progress=progress_bar,
                progress_args=(prog, time.time())
            )
    except Exception as e:
        logger.error(f"Error sending video: {str(e)}")
        raise
    finally:
        # Cleanup
        if os.path.exists(filename):
            os.remove(filename)
        if os.path.exists(thumb_path):
            os.remove(thumb_path)

def decrypt_file(file_path, key):  
    """Simple XOR file decryption"""
    if not os.path.exists(file_path): 
        return False  

    try:
        with open(file_path, "r+b") as f:  
            num_bytes = min(28, os.path.getsize(file_path))  
            with mmap.mmap(f.fileno(), length=num_bytes, access=mmap.ACCESS_WRITE) as mmapped_file:  
                for i in range(num_bytes):  
                    mmapped_file[i] ^= ord(key[i]) if i < len(key) else i 
        return True
    except Exception as e:
        logger.error(f"Decryption error: {str(e)}")
        return False

async def download_and_decrypt_video(url, cmd, name, key):  
    """Download and decrypt video"""
    try:
        video_path = await download_video(url, cmd, name)
        if not video_path:
            return None
            
        if not decrypt_file(video_path, key):  
            logger.error(f"Failed to decrypt {video_path}")
            return None
            
        return video_path
    except Exception as e:
        logger.error(f"Download/decrypt error: {str(e)}")
        return None

# Utility functions
def human_readable_size(size, decimal_places=2):
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if size < 1024.0 or unit == 'PB':
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"

def time_name():
    """Generate timestamp-based filename"""
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H%M%S.mp4")
