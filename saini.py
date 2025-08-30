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
import tempfile
import shutil
import xml.etree.ElementTree as ET
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

def download_file_sync(url, out_path, headers):
    """Synchronous file download"""
    r = requests.get(url, headers=headers, stream=True)
    r.raise_for_status()
    with open(out_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024 * 512):
            f.write(chunk)

def run_cmd_sync(cmd):
    """Run shell command synchronously"""
    subprocess.check_call(cmd)

def decrypt_and_merge_sync(mpd_url, key, out_path, resolution=None):
    """Synchronous version of the decryption function"""
    workdir = tempfile.mkdtemp(prefix="saini_")
    try:
        audio_enc = os.path.join(workdir, "audio.mp4")
        video_enc = os.path.join(workdir, "video.mp4")
        audio_dec = os.path.join(workdir, "audio_dec.mp4")
        video_dec = os.path.join(workdir, "video_dec.mp4")

        # fetch MPD
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 12; Mobile; rv:109.0) Gecko/117.0 Firefox/117.0"
        }
        
        mpd_content = requests.get(mpd_url, headers=headers).text

        # detect type
        if "<SegmentTemplate" in mpd_content:
            # OLD STYLE (SegmentTemplate)
            audio_init = re.search(r'initialization="([^"]+audio[^"]+)"', mpd_content).group(1)
            audio_media = re.search(r'media="([^"]+audio[^"]+)"', mpd_content).group(1).replace("$Number$", "1")
            audio_url = mpd_url.rsplit("/", 1)[0] + "/" + audio_init.split("/")[0] + "/"
            
            # Download audio
            download_file_sync(audio_url + audio_init, audio_enc, headers)
            download_file_sync(audio_url + audio_media, audio_enc, headers)

            # Video
            video_init = re.search(r'initialization="([^"]+video[^"]+)"', mpd_content).group(1)
            video_media = re.search(r'media="([^"]+video[^"]+)"', mpd_content).group(1).replace("$Number$", "1")
            video_url = mpd_url.rsplit("/", 1)[0] + "/" + video_init.split("/")[0] + "/"
            
            # Download video
            download_file_sync(video_url + video_init, video_enc, headers)
            download_file_sync(video_url + video_media, video_enc, headers)

        else:
            # NEW STYLE (BaseURL + SegmentBase)
            root = ET.fromstring(mpd_content)
            ns = {"mpd": "urn:mpeg:dash:schema:mpd:2011"}
            period = root.find("mpd:Period", ns)

            # audio
            audio_repr = period.find(".//mpd:AdaptationSet[@contentType='audio']/mpd:Representation", ns)
            audio_url = mpd_url.rsplit("/", 1)[0] + "/" + audio_repr.find("mpd:BaseURL", ns).text
            download_file_sync(audio_url, audio_enc, headers)

            # video (choose resolution if given)
            video_reprs = period.findall(".//mpd:AdaptationSet[@contentType='video']/mpd:Representation", ns)
            if resolution:
                chosen = None
                for v in video_reprs:
                    if v.attrib.get("height") == str(resolution):
                        chosen = v
                        break
                video_repr = chosen or video_reprs[-1]
            else:
                video_repr = video_reprs[-1]

            video_url = mpd_url.rsplit("/", 1)[0] + "/" + video_repr.find("mpd:BaseURL", ns).text
            download_file_sync(video_url, video_enc, headers)

        # Decrypt
        run_cmd_sync(["mp4decrypt", "--key", key, video_enc, video_dec])
        run_cmd_sync(["mp4decrypt", "--key", key, audio_enc, audio_dec])

        # Merge
        run_cmd_sync([
            "ffmpeg", "-y", "-i", video_dec, "-i", audio_dec,
            "-c", "copy", out_path
        ])

    finally:
        # Cleanup
        shutil.rmtree(workdir, ignore_errors=True)

async def decrypt_and_merge_video(mpd_url, keys_string, output_path, output_name, quality="720"):
    try:
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)

        # Parse keys from keys_string
        keys = []
        key_parts = keys_string.split()
        for i in range(0, len(key_parts)):
            if key_parts[i] == "--key" and i+1 < len(key_parts):
                keys.append(key_parts[i+1])

        if not keys:
            raise ValueError("No decryption keys provided")

        # Use the first key for both audio and video
        key = keys[0]

        # Download and process using the new method
        final_output = output_path / f"{output_name}.mp4"
        
        # Run the synchronous decryption in a thread pool
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None, 
            decrypt_and_merge_sync,
            mpd_url,
            key,
            str(final_output),
            int(quality) if quality.isdigit() else 720
        )

        return str(final_output)

    except Exception as e:
        logger.error(f"Error during decryption and merging: {str(e)}")
        raise

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
