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

async def download_with_retry(url, file_path, max_retries=2):
    """Download file with automatic retries"""
    for attempt in range(max_retries + 1):
        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        async with aiofiles.open(file_path, 'wb') as f:
                            await f.write(await response.read())
                        return True
                    else:
                        logger.warning(f"Download failed (attempt {attempt+1}): {url} - Status {response.status}")
        except Exception as e:
            logger.error(f"Download error (attempt {attempt+1}): {url} - {str(e)}")
        
        if attempt < max_retries:
            wait_time = 2 ** attempt  # Exponential backoff
            logger.info(f"Retrying in {wait_time} seconds...")
            await asyncio.sleep(wait_time)
    return False

def duration(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return float(result.stdout)

def get_mps_and_keys(api_url):
    response = requests.get(api_url)
    response_json = response.json()
    mpd = response_json.get('MPD')
    keys = response_json.get('KEYS')
    return mpd, keys
   
def exec(cmd):
    process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = process.stdout.decode()
    return output

def pull_run(work, cmds):
    with concurrent.futures.ThreadPoolExecutor(max_workers=work) as executor:
        fut = executor.map(exec, cmds)

async def download(url, name):
    ka = f'{name}.pdf'
    success = await download_with_retry(url, ka)
    return ka if success else None

async def pdf_download(url, file_name):
    """Download PDF with retry mechanism"""
    try:
        if os.path.exists(file_name):
            os.remove(file_name)
        return await download_with_retry(url, file_name)
    except Exception as e:
        logger.error(f"PDF Download Error: {str(e)}")
        return False
   
async def download_video(url, cmd, name, max_retries=2):
    """Download video with retry mechanism"""
    for attempt in range(max_retries + 1):
        try:
            download_cmd = f'{cmd} -R 25 --fragment-retries 25 --external-downloader aria2c --downloader-args "aria2c: -x 16 -j 32"'
            logger.info(download_cmd)
            
            process = await asyncio.create_subprocess_shell(
                download_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            
            if process.returncode == 0:
                if os.path.isfile(name):
                    return name
                for ext in [".webm", ".mkv", ".mp4", ".mp4.webm"]:
                    if os.path.isfile(f"{name}{ext}"):
                        return f"{name}{ext}"
                return name.split(".")[0] + ".mp4"
        except Exception as e:
            logger.error(f"Video download error (attempt {attempt+1}): {str(e)}")
            if attempt < max_retries:
                await asyncio.sleep(3)
    
    logger.error(f"All download attempts failed for: {name}")
    return None

def decrypt_file(file_path, key):  
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
        logger.error(f"Decryption failed: {str(e)}")
        return False

async def download_and_decrypt_video(url, cmd, name, key):  
    video_path = await download_video(url, cmd, name)
    if not video_path:
        logger.error(f"Video download failed: {name}")
        return None
    
    if decrypt_file(video_path, key):
        logger.info(f"File decrypted successfully: {video_path}")
        return video_path
    else:
        logger.error(f"Decryption failed: {video_path}")
        return None

async def decrypt_and_merge_video(mpd_url, keys_string, output_path, output_name, quality="720"):
    try:
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)
        temp_files = []

        # Download video
        cmd1 = f'yt-dlp -f "bv[height<={quality}]+ba/b" -o "{output_path}/file.%(ext)s" --allow-unplayable-format --no-check-certificate --external-downloader aria2c "{mpd_url}"'
        logger.info(f"Running command: {cmd1}")
        os.system(cmd1)
        
        # Find downloaded files
        avDir = list(output_path.iterdir())
        logger.info(f"Downloaded files: {avDir}")
        
        video_decrypted = False
        audio_decrypted = False

        for data in avDir:
            if data.suffix == ".mp4" and not video_decrypted:
                decrypted_video = output_path / "video.mp4"
                cmd2 = f'mp4decrypt {keys_string} --show-progress "{data}" "{decrypted_video}"'
                logger.info(f"Running command: {cmd2}")
                os.system(cmd2)
                if decrypted_video.exists():
                    video_decrypted = True
                    temp_files.append(data)
                data.unlink()
            elif data.suffix == ".m4a" and not audio_decrypted:
                decrypted_audio = output_path / "audio.m4a"
                cmd3 = f'mp4decrypt {keys_string} --show-progress "{data}" "{decrypted_audio}"'
                logger.info(f"Running command: {cmd3}")
                os.system(cmd3)
                if decrypted_audio.exists():
                    audio_decrypted = True
                    temp_files.append(data)
                data.unlink()

        if not video_decrypted or not audio_decrypted:
            raise FileNotFoundError("Decryption failed: video or audio file not found.")

        # Merge files
        output_file = output_path / f"{output_name}.mp4"
        cmd4 = f'ffmpeg -i "{output_path}/video.mp4" -i "{output_path}/audio.m4a" -c copy "{output_file}"'
        logger.info(f"Running command: {cmd4}")
        os.system(cmd4)
        
        # Get duration
        cmd5 = f'ffmpeg -i "{output_file}" 2>&1 | grep "Duration"'
        duration_info = os.popen(cmd5).read()
        logger.info(f"Duration info: {duration_info}")

        return str(output_file)

    except Exception as e:
        logger.error(f"Error during decryption and merging: {str(e)}")
        raise
    finally:
        # Clean up temporary files
        for file in temp_files:
            if file.exists():
                file.unlink()
        for temp in ["video.mp4", "audio.m4a"]:
            temp_path = output_path / temp
            if temp_path.exists():
                temp_path.unlink()

async def run(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    logger.info(f'[{cmd!r} exited with {proc.returncode}]')
    
    if proc.returncode != 0:
        return False
    if stdout:
        return f'[stdout]\n{stdout.decode()}'
    if stderr:
        return f'[stderr]\n{stderr.decode()}'

def human_readable_size(size, decimal_places=2):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if size < 1024.0 or unit == 'PB':
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"

def time_name():
    date = datetime.date.today()
    now = datetime.datetime.now()
    current_time = now.strftime("%H%M%S")
    return f"{date} {current_time}.mp4"

async def send_doc(bot: Client, m: Message, cc, ka, cc1, prog, count, name, channel_id):
    reply = await bot.send_message(channel_id, f"Downloading pdf:\n<pre><code>{name}</code></pre>")
    await asyncio.sleep(1)
    await bot.send_document(ka, caption=cc1)
    count += 1
    await reply.delete()
    os.remove(ka)

async def send_vvid(bot: Client, m: Message, cc, filename, thumb, name, prog, channel_id):
    # Generate thumbnail
    #thumb_path = f"{filename}.jpg"
    #subprocess.run(f'ffprobe -v error -select_streams v:0 -show_entries stream=duration -of default=noprint_wrappers=1:nokey=1 "{filename}"', shell=True)
    #subprocess.run(f'ffmpeg -i "{filename}" -ss 00:00:10 -vframes 1 "{thumb_path}"', shell=True)
    
    #await prog.delete()
    #reply = await bot.send_message(channel_id, f"**Generate Thumbnail:**\n{name}")
    
    try:
        # Generate thumbnail if needed
        if not thumb:
            thumb_path = f"{filename}.jpg"
            subprocess.run(
                f'ffmpeg -i "{filename}" -ss 00:00:10 -vframes 1 "{thumb_path}" -y',
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            thumbnail = thumb_path
        else:
            thumbnail = thumb
        
    except Exception as e:
        logger.error(f"Thumbnail error: {str(e)}")
        thumbnail = thumb_path
      
    dur = int(duration(filename))
    start_time = time.time()

    try:
        reply = await bot.send_message(channel_id, f"**Generate Thumbnail:**\n{name}")
        await bot.send_video(
            channel_id, filename, 
            caption=cc, 
            supports_streaming=True, 
            thumb=thumbnail, 
            duration=dur,
            progress=progress_bar, 
            progress_args=(reply, start_time)
        )
    except Exception as e:
        logger.warning(f"Video upload failed, sending as document: {str(e)}")
        await bot.send_document(
            channel_id, filename, 
            caption=cc,
            progress=progress_bar, 
            progress_args=(reply, start_time)
        )
    
    # Cleanup
    await reply.delete()
    if os.path.exists(filename):
        os.remove(filename)
    if os.path.exists(thumb_path):
        os.remove(thumb_path)


async def send_vird(bot: Client, m: Message, cc, filename, thumb, name, prog, channel_id):
    try:
        # Generate thumbnail if needed
        if not thumb:
            thumb_path = f"{filename}.jpg"
            subprocess.run(
                f'ffmpeg -i "{filename}" -ss 00:00:10 -vframes 1 "{thumb_path}" -y',
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            thumbnail = thumb_path
        else:
            thumbnail = thumb

        # Check file size
        file_size = os.path.getsize(filename)
        max_size = 1.8 * 1024 * 1024 * 1024  # 1.8 GB in bytes

        if file_size <= max_size:
            # If under 1.8GB, send normally
            dur = int(duration(filename))
            start_time = time.time()
            try:
                reply = await bot.send_message(channel_id, f"**Uploading Video:**\n{name}")
                await bot.send_video(
                    channel_id, 
                    filename, 
                    caption=cc, 
                    supports_streaming=True, 
                    height=720, 
                    width=1280,
                    thumb=thumbnail, 
                    duration=dur,
                    progress=progress_bar, 
                    progress_args=(reply, start_time)
                )
            except Exception as e:
                logger.warning(f"Video upload failed, sending as document: {str(e)}")
                await bot.send_document(
                    channel_id, 
                    filename, 
                    caption=cc,
                    progress=progress_bar, 
                    progress_args=(reply, start_time)
                )
            finally:
                await reply.delete()
                if os.path.exists(filename):
                    os.remove(filename)
                if os.path.exists(thumbnail):
                    os.remove(thumbnail)
        else:
            # Split video into 1.8GB parts
            reply = await bot.send_message(channel_id, "Video is too large. Splitting into 1.8GB parts...")

            # Estimate duration per part using average bitrate
            total_dur = duration(filename)
            avg_bitrate = file_size / total_dur  # bytes per second
            target_duration = max_size / avg_bitrate  # seconds per part
            target_duration = int(target_duration)

            part_number = 1
            start = 0

            while start < total_dur:
                part_file = f"{filename}_part{part_number}.mp4"
                cmd = f'ffmpeg -y -i "{filename}" -ss {start} -t {target_duration} -c copy "{part_file}"'
                subprocess.run(cmd, shell=True)
                part_dur = int(duration(part_file))
                start_time = time.time()
                try:
                    await bot.send_video(
                        channel_id,
                        part_file, 
                        caption=f"{cc}\n\nPart {part_number}", 
                        supports_streaming=True,
                        height=720, 
                        width=1280, 
                        thumb=thumbnail, 
                        duration=part_dur,
                        progress=progress_bar, 
                        progress_args=(reply, start_time)
                    )
                except Exception as e:
                    logger.warning(f"Video upload failed, sending as document: {str(e)}")
                    await bot.send_document(
                        channel_id,
                        part_file, 
                        caption=f"{cc}\n\nPart {part_number}",
                        progress=progress_bar, 
                        progress_args=(reply, start_time)
                    )
                os.remove(part_file)
                part_number += 1
                start += target_duration

            await reply.delete()
            if os.path.exists(filename):
                os.remove(filename)
            if os.path.exists(thumbnail):
                os.remove(thumbnail)
    except Exception as e:
        logger.error(f"send_vid failed: {str(e)}")

async def send_vid(bot: Client, m: Message, cc, filename, thumb, name, prog, channel_id):
    try:
        # Generate frame thumb if no custom thumb is provided
        if not thumb:
            frame_thumb = f"{filename}.jpg"
            subprocess.run(
                f'ffmpeg -i "{filename}" -ss 00:00:10 -vframes 1 "{frame_thumb}" -y',
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            thumbnail = frame_thumb if os.path.exists(frame_thumb) else None
        else:
            thumbnail = thumb

        # File size check
        file_size = os.path.getsize(filename)
        max_size = 1.8 * 1024 * 1024 * 1024  # 1.8 GB

        async def _try_send_video(video_path, thumb_path):
            dur = int(duration(video_path))
            start_time = time.time()
            reply = await bot.send_message(channel_id, f"**Uploading Video:**\n{name}")
            try:
                await bot.send_video(
                    channel_id,
                    video_path,
                    caption=cc,
                    supports_streaming=True,
                    thumb=thumb_path if thumb_path and os.path.exists(thumb_path) else None,
                    duration=dur,
                    progress=progress_bar,
                    progress_args=(reply, start_time)
                )
                return True
            except Exception as e:
                logger.warning(f"send_video failed: {e}")
                # Retry without thumbnail
                try:
                    await bot.send_video(
                        channel_id,
                        video_path,
                        caption=cc,
                        supports_streaming=True,
                        duration=dur,
                        progress=progress_bar,
                        progress_args=(reply, start_time)
                    )
                    return True
                except Exception as e2:
                    logger.error(f"send_video retry (no thumb) failed: {e2}")
                    return False
            finally:
                try:
                    await reply.delete()
                except Exception:
                    pass

        if file_size <= max_size:
            ok = await _try_send_video(filename, thumbnail)
            if not ok:
                await bot.send_message(channel_id, f"⚠️ Video upload failed: {name}")
        else:
            # Split into 1.8GB parts
            notify = await bot.send_message(channel_id, "Video is too large. Splitting into 1.8GB parts...")
            total_dur = duration(filename)
            avg_bitrate = file_size / total_dur
            target_duration = int(max_size / avg_bitrate)

            part_number = 1
            start = 0
            while start < total_dur:
                part_file = f"{filename}_part{part_number}.mp4"
                cmd = f'ffmpeg -y -i "{filename}" -ss {start} -t {target_duration} -c copy "{part_file}"'
                subprocess.run(cmd, shell=True)
                part_thumb = thumbnail if part_number == 1 else None
                ok = await _try_send_video(part_file, part_thumb)
                if not ok:
                    await bot.send_message(channel_id, f"⚠️ Part {part_number} upload failed: {name}")
                os.remove(part_file)
                part_number += 1
                start += target_duration
            try:
                await notify.delete()
            except Exception:
                pass

        # Cleanup main file
        try:
            if os.path.exists(filename):
                os.remove(filename)
        except Exception:
            pass

        # 🔹 Cleanup thumb
        if thumbnail and os.path.exists(thumbnail):
            # agar user-provided hai to mat delete karo
            if not (thumb and thumbnail == thumb):
                os.remove(thumbnail)

    except Exception as e:
        logger.error(f"send_vid failed: {str(e)}")

