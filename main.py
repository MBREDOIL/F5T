import os
import re
import sys
import m3u8
import json
import time
import pytz
import asyncio
import requests
import subprocess
import urllib.parse
import yt_dlp
import tgcrypto
import cloudscraper
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64encode, b64decode
from logs import logging
from bs4 import BeautifulSoup
import saini as helper
from utils import progress_bar
from vars import API_ID, API_HASH, BOT_TOKEN, OWNER, CREDIT, AUTH_USERS
from aiohttp import ClientSession
from subprocess import getstatusoutput
from pytube import YouTube
from aiohttp import web
import random
from pyromod import listen
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import aiohttp
import aiofiles
import zipfile
import shutil
import ffmpeg
from collections import defaultdict

# Initialize the bot
bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

cookies_file_path = os.getenv("cookies_file_path", "youtube_cookies.txt")
api_url = "http://master-api-v3.vercel.app/"
api_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNzkxOTMzNDE5NSIsInRnX3VzZXJuYW1lIjoi4p61IFtvZmZsaW5lXSIsImlhdCI6MTczODY5MjA3N30.SXzZ1MZcvMp5sGESj0hBKSghhxJ3k1GTWoBUbivUe1I"
token_cp ='eyJjb3Vyc2VJZCI6IjQ1NjY4NyIsInR1dG9ySWQiOm51bGwsIm9yZ0lkIjo0ODA2MTksImNhdGVnb3J5SWQiOm51bGx9r'
cw_token ='eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3MjQyMzg3OTEsImNvbiI6eyJpc0FkbWluIjpmYWxzZSwiYXVzZXIiOiJVMFZ6TkdGU2NuQlZjR3h5TkZwV09FYzBURGxOZHowOSIsImlkIjoiZEUxbmNuZFBNblJqVEROVmFWTlFWbXhRTkhoS2R6MDkiLCJmaXJzdF9uYW1lIjoiYVcxV05ITjVSemR6Vm10ak1WUlBSRkF5ZVNzM1VUMDkiLCJlbWFpbCI6Ik5Ga3hNVWhxUXpRNFJ6VlhiR0ppWTJoUk0wMVdNR0pVTlU5clJXSkRWbXRMTTBSU2FHRnhURTFTUlQwPSIsInBob25lIjoiVUhVMFZrOWFTbmQ1ZVcwd1pqUTViRzVSYVc5aGR6MDkiLCJhdmF0YXIiOiJLM1ZzY1M4elMwcDBRbmxrYms4M1JEbHZla05pVVQwOSIsInJlZmVycmFsX2NvZGUiOiJOalZFYzBkM1IyNTBSM3B3VUZWbVRtbHFRVXAwVVQwOSIsImRldmljZV90eXBlIjoiYW5kcm9pZCIsImRldmljZV92ZXJzaW9uIjoiUShBbmRyb2lkIDEwLjApIiwiZGV2aWNlX21vZGVsIjoiU2Ftc3VuZyBTTS1TOTE4QiIsInJlbW90ZV9hZGRyIjoiNTQuMjI2LjI1NS4xNjMsIDU0LjIyNi4yNTUuMTYzIn19.snDdd-PbaoC42OUhn5SJaEGxq0VzfdzO49WTmYgTx8ra_Lz66GySZykpd2SxIZCnrKR6-R10F5sUSrKATv1CDk9ruj_ltCjEkcRq8mAqAytDcEBp72-W0Z7DtGi8LdnY7Vd9Kpaf499P-y3-godolS_7ixClcYOnWxe2nSVD5C9c5HkyisrHTvf6NFAuQC_FD3TzByldbPVKK0ag1UnHRavX8MtttjshnRhv5gJs5DQWj4Ir_dkMcJ4JaVZO3z8j0OxVLjnmuaRBujT-1pavsr1CCzjTbAcBvdjUfvzEhObWfA1-Vl5Y4bUgRHhl1U-0hne4-5fF0aouyu71Y6W0eg'
adda_token = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJkcGthNTQ3MEBnbWFpbC5jb20iLCJhdWQiOiIxNzg2OTYwNSIsImlhdCI6MTc0NDk0NDQ2NCwiaXNzIjoiYWRkYTI0Ny5jb20iLCJuYW1lIjoiZHBrYSIsImVtYWlsIjoiZHBrYTU0NzBAZ21haWwuY29tIiwicGhvbmUiOiI3MzUyNDA0MTc2IiwidXNlcklkIjoiYWRkYS52MS41NzMyNmRmODVkZDkxZDRiNDkxN2FiZDExN2IwN2ZjOCIsImxvZ2luQXBpVmVyc2lvbiI6MX0.0QOuYFMkCEdVmwMVIPeETa6Kxr70zEslWOIAfC_ylhbku76nDcaBoNVvqN4HivWNwlyT0jkUKjWxZ8AbdorMLg"

# Global task management
user_tasks = defaultdict(dict)
active_tasks = set()

# Inline keyboard for start command
BUTTONSCONTACT = InlineKeyboardMarkup([[InlineKeyboardButton(text="📞 Contact", url="https://t.me/BOT")]])
keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="🛠️ Help", url="https://t.me/Zl"),
            InlineKeyboardButton(text="🛠️ Repo", url="https://gitect"),
        ],
    ]
)

# Image URLs for the random image feature
image_urls = [
    "https://envs.sh/HQG.jpg",
    "https://envs.sh/HQG.jpg",
]

async def cleanup_user_resources(user_id):
    """Clean up all resources for a specific user"""
    user_folder = f"./downloads/{user_id}"
    if os.path.exists(user_folder):
        shutil.rmtree(user_folder, ignore_errors=True)
    if user_id in user_tasks:
        del user_tasks[user_id]

async def process_drm(
    bot: Client, 
    m: Message, 
    x: str, 
    raw_text: str, 
    raw_text0: str, 
    raw_text2: str, 
    raw_text3: str, 
    raw_text4: str, 
    thumb: str, 
    raw_text7: str
):
    try:
        file_name, ext = os.path.splitext(os.path.basename(x))
        path = f"./downloads/{m.chat.id}"
        pdf_count = 0
        img_count = 0
        other_count = 0
        
        try:    
            with open(x, "r") as f:
                content = f.read()
            content = content.split("\n")
            
            links = []
            for i in content:
                if "://" in i:
                    url = i.split("://", 1)[1]
                    links.append(i.split("://", 1))
                    if ".pdf" in url:
                        pdf_count += 1
                    elif url.endswith((".png", ".jpeg", ".jpg")):
                        img_count += 1
                    else:
                        other_count += 1
            os.remove(x)
        except Exception as e:
            await m.reply_text(f"<pre><code>🔹Invalid file input: {str(e)}</code></pre>")
            if os.path.exists(x):
                os.remove(x)
            return

        if m.chat.id not in AUTH_USERS:
            await m.reply_text(f"__Oopss! You are not a Premium member __\n__PLEASE /upgrade YOUR PLAN__\n__Your User id__ - `{m.chat.id}`\n")
            return

        if raw_text0 == '/d':
            b_name = file_name.replace('_', ' ')
        else:
            b_name = raw_text0

        quality = f"{raw_text2}p"
        try:
            if raw_text2 == "144":
                res = "256x144"
            elif raw_text2 == "240":
                res = "426x240"
            elif raw_text2 == "360":
                res = "640x360"
            elif raw_text2 == "480":
                res = "854x480"
            elif raw_text2 == "720":
                res = "1280x720"
            elif raw_text2 == "1080":
                res = "1920x1080" 
            else: 
                res = "UN"
        except Exception:
                res = "UN"

        if raw_text3 == '/d':
            CR = f"{CREDIT}"
        elif "," in raw_text3:
            CR, PRENAME = raw_text3.split(",")
        else:
            CR = raw_text3

        if raw_text7 == "/d":
            channel_id = m.chat.id
        else:
            channel_id = raw_text7

        # Store task reference
        user_tasks[m.chat.id] = {
            'task': asyncio.current_task(),
            'channel_id': channel_id,
            'batch_name': b_name
        }

        if raw_text7 == "/d":
            batch_message = await m.reply_text(f"<b>🎯Target Batch : {b_name}</b>")
        else:
            try:
                batch_message = await bot.send_message(chat_id=channel_id, text=f"<b>🎯Target Batch : {b_name}</b>")
                await bot.send_message(chat_id=m.chat.id, text=f"<b><i>🎯Target Batch : {b_name}</i></b>\n\n🔄 Your Task is under processing, please check your Set Channel📱")
            except Exception as e:
                await m.reply_text(f"**Fail Reason »** {e}\n")
                return
        
        failed_count = 0
        count = int(raw_text)
        
        try:
            for i in range(count-1, len(links)):
                Vxy = links[i][1].replace("file/d/","uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing","")
                url = "https://" + Vxy
                link0 = "https://" + Vxy

                name1 = links[i][0].replace("(", "[").replace(")", "]").replace("_", "").replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
                if "," in raw_text3:
                    name = f'{PRENAME} {name1[:60]}'
                else:
                    name = f'{name1[:60]}'
            
                if "visionias" in url:
                    async with ClientSession() as session:
                        async with session.get(url, headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Accept-Language': 'en-US,en;q=0.9', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'Pragma': 'no-cache', 'Referer': 'http://www.visionias.in/', 'Sec-Fetch-Dest': 'iframe', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'cross-site', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Linux; Android 12; RMX2121) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36', 'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"', 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',}) as resp:
                            text = await resp.text()
                            url = re.search(r"(https://.*?playlist.m3u8.*?)\"", text).group(1)

                if "acecwply" in url:
                    cmd = f'yt-dlp -o "{name}.%(ext)s" -f "bestvideo[height<={raw_text2}]+bestaudio" --hls-prefer-ffmpeg --no-keep-video --remux-video mkv --no-warning "{url}"'


                elif "https://cpvod.testbook.com/" in url:
                    url = url.replace("https://cpvod.testbook.com/", "https://media-cdn.classplusapp.com/drm/")
                    api_response = requests.get(f"https://covercel.vercel.app/extract_keys?url={url}@bots_updatee&user_id=5830856952")
                    response_data = api_response.json()
                    mpd = response_data.get('MPD')
                    keys = response_data.get('KEYS', [])

                    # Check if we have a simple 2-part key
                    if keys and len(keys) == 1 and keys[0].count(":") == 1:
                        # Single key with 2 parts - use simple key method
                        url = mpd
                        keys_string = keys[0]  # Just the key, no --key prefix
                    else:
                        # Multiple keys - use complex method
                        url = mpd
                        keys_string = " ".join([f"--key {key}" for key in keys])

                elif "classplusapp.com/drm/" in url:
                    api_response = requests.get(f"https://covercel.vercel.app/extract_keys?url={url}@bots_updatee&user_id=5830856952")
                    response_data = api_response.json()
                    mpd = response_data.get('MPD')
                    keys = response_data.get('KEYS', [])

                    # Check if we have a simple 2-part key
                    if keys and len(keys) == 1 and keys[0].count(":") == 1:
                        # Single key with 2 parts - use simple key method
                        url = mpd
                        keys_string = keys[0]  # Just the key, no --key prefix
                    else:
                        # Multiple keys - use complex method
                        url = mpd
                        keys_string = " ".join([f"--key {key}" for key in keys])

                elif "classplusapp" in url:
                    response = requests.get(f"https://covercel.vercel.app/extract_keys?url={url}@bots_updatee&user_id=5830856952")
                    url = response.json()['url']
                
                elif "tencdn.classplusapp" in url:
                    response = requests.get(f"https://covercel.vercel.app/extract_keys?url={url}@bots_updatee&user_id=5830856952")
                    url = response.json()['url']
           
                elif 'videos.classplusapp' in url:
                    response = requests.get(f"https://covercel.vercel.app/extract_keys?url={url}@bots_updatee&user_id=5830856952")
                    url = response.json()['url']
            
                elif 'media-cdn.classplusapp.com' in url or 'media-cdn-alisg.classplusapp.com' in url or 'media-cdn-a.classplusapp.com' in url: 
                    response = requests.get(f"https://covercel.vercel.app/extract_keys?url={url}@bots_updatee&user_id=5830856952")
                    url = response.json()['url']

                

                if "edge.api.brightcove.com" in url:
                    bcov = f'bcov_auth={cw_token}'
                    url = url.split("bcov_auth")[0]+bcov
                
                elif "childId" in url and "parentId" in url:
                    url = f"https://anonymousrajputplayer-9ab2f2730a02.herokuapp.com/pw?url={url}&token={raw_text4}"
                           
                elif "d1d34p8vz63oiq" in url or "sec1.pw.live" in url:
                    url = f"https://anonymouspwplayer-b99f57957198.herokuapp.com/pw?url={url}?token={raw_text4}"

                if ".pdf*" in url:
                    url = f"https://dragoapi.vercel.app/pdf/{url}"
            
                elif 'encrypted.m' in url:
                    appxkey = url.split('*')[1]
                    url = url.split('*')[0]

                if "youtu" in url:
                    ytf = f"bv*[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[height<=?{raw_text2}]"
                elif "embed" in url:
                    ytf = f"bestvideo[height<={raw_text2}]+bestaudio/best[height<={raw_text2}]"
                else:
                    ytf = f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"
           
                if "jw-prod" in url:
                    cmd = f'yt-dlp -o "{name}.mp4" "{url}"'
                elif "webvideos.classplusapp." in url:
                   cmd = f'yt-dlp --add-header "referer:https://web.classplusapp.com/" --add-header "x-cdn-tag:empty" -f "{ytf}" "{url}" -o "{name}.mp4"'
                elif "youtube.com" in url or "youtu.be" in url:
                   cmd = f'yt-dlp --cookies youtube_cookies.txt -f "{ytf}" "{url}" -o "{name}".mp4'
                else:
                   cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'
     

                try:
                    cc = f'**{str(count).zfill(3)}. Video Title :** `{name1}.mkv`\n\n<pre><code>**Batch Name :** {b_name}</code></pre>\n\n**Extracted by » `{CR}`**\n'
                    cc1 = f'**{str(count).zfill(3)}. File Title :** `{name1}.pdf`\n\n<pre><code>**Batch Name :** {b_name}</code></pre>\n\n**Extracted by » `{CR}`**\n'
                    cczip = f'**{str(count).zfill(3)}. Zip Title :** `{name1}.zip`\n\n<pre><code>**Batch Name :** {b_name}</code></pre>\n\n**Extracted by » `{CR}`**\n' 
                    ccimg = f'**{str(count).zfill(3)}. Img Title :** `{name1}.jpg`\n\n<pre><code>**Batch Name :** {b_name}</code></pre>\n\n**Extracted by » `{CR}`**\n'
                    ccm = f'**{str(count).zfill(3)}. Audio Title :** `{name1}.mp3`\n\n<pre><code>**Batch Name :** {b_name}</code></pre>\n\n**Extracted by » `{CR}`**\n'
                    cchtml = f'**{str(count).zfill(3)}. Html Title :** `{name1}.html`\n\n<pre><code>**Batch Name :** {b_name}</code></pre>\n\n**Extracted by » `{CR}`**\n'
                  
                    if "drive" in url:
                        try:
                            ka = await helper.download(url, name)
                            copy = await bot.send_document(chat_id=channel_id,document=ka, caption=cc1)
                            count+=1
                            os.remove(ka)
                        except FloodWait as e:
                            await asyncio.sleep(e.x)
                            continue    
  
                    elif ".pdf" in url:
                        if "cwmediabkt99" in url:
                            max_retries = 3
                            success = False
                            
                            for attempt in range(max_retries):
                                try:
                                    url = url.replace(" ", "%20")
                                    scraper = cloudscraper.create_scraper()
                                    response = scraper.get(url)

                                    if response.status_code == 200:
                                        with open(f'{name}.pdf', 'wb') as file:
                                            file.write(response.content)
                                        await bot.send_document(chat_id=channel_id, document=f'{name}.pdf', caption=cc1)
                                        count += 1
                                        os.remove(f'{name}.pdf')
                                        success = True
                                        await asyncio.sleep(2)
                                        break
                                except Exception:
                                    await asyncio.sleep(2 ** attempt)
                            
                            if not success:
                                failed_count += 1
                                await bot.send_message(channel_id, f'⚠️**PDF Download Failed**⚠️\n**Name** =>> `{str(count).zfill(3)} {name1}`\n**Url** =>> {link0}')
                                count += 1
                                
                        else:
                            try:
                                success = await helper.pdf_download(url, f'{name}.pdf')
                                if success:
                                    await bot.send_document(chat_id=channel_id, document=f'{name}.pdf', caption=cc1)
                                    count += 1
                                    await asyncio.sleep(2)
                                else:
                                    failed_count += 1
                                    await asyncio.sleep(1)
                                    await bot.send_message(channel_id, f'⚠️**PDF Download Failed**⚠️\n**Name** =>> `{str(count).zfill(3)} {name1}`\n**Url** =>> {link0}')
                                if os.path.exists(f'{name}.pdf'):
                                    os.remove(f'{name}.pdf')
                            except Exception as e:
                                failed_count += 1
                                await bot.send_message(channel_id, f'⚠️**PDF Download Failed**⚠️\n**Name** =>> `{str(count).zfill(3)} {name1}`\n**Url** =>> {link0}\n**Error:** {str(e)}')
                                await asyncio.sleep(2)
                                count += 1
                                
                    elif ".ws" in url and url.endswith(".ws"):
                        try:
                            await helper.pdf_download(f"{api_url}utkash-ws?url={url}&authorization={api_token}", f"{name}.html")
                            await bot.send_document(chat_id=channel_id, document=f"{name}.html", caption=cchtml)
                            count += 1
                            os.remove(f'{name}.html')
                            await asyncio.sleep(1)
                        except Exception:
                            failed_count += 1
                            await bot.send_message(channel_id, f'⚠️**HTML Download Failed**⚠️\n**Name** =>> `{str(count).zfill(3)} {name1}`\n**Url** =>> {link0}')
                            await asyncio.sleep(1)
                            count += 1
                            
                    elif any(ext in url for ext in [".jpg", ".jpeg", ".png"]):
                        try:
                            ext = url.split('.')[-1]
                            cmd = f'yt-dlp --no-check-certificate -o "{name}.{ext}" "{url}"'
                            subprocess.run(cmd, shell=True)
                            await bot.send_photo(chat_id=channel_id, photo=f'{name}.{ext}', caption=ccimg)
                            count += 1
                            os.remove(f'{name}.{ext}')
                            await asyncio.sleep(2)
                        except Exception:
                            failed_count += 1
                            await bot.send_message(channel_id, f'⚠️**Image Download Failed**⚠️\n**Name** =>> `{str(count).zfill(3)} {name1}`\n**Url** =>> {link0}')
                            count += 1
                            await asyncio.sleep(1)
                            
                    elif any(ext in url for ext in [".mp3", ".wav", ".m4a"]):
                        try:
                            ext = url.split('.')[-1]
                            cmd = f'yt-dlp -o "{name}.{ext}" "{url}"'
                            subprocess.run(cmd, shell=True)
                            await bot.send_document(chat_id=channel_id, document=f'{name}.{ext}', caption=ccm)
                            count += 1
                            os.remove(f'{name}.{ext}')
                        except Exception:
                            failed_count += 1
                            await bot.send_message(channel_id, f'⚠️**Audio Download Failed**⚠️\n**Name** =>> `{str(count).zfill(3)} {name1}`\n**Url** =>> {link0}')
                    
                    elif 'encrypted.m' in url:    
                        Show = f"__**Video Downloading__**\n<pre><code>{str(count).zfill(3)}) {name1}</code></pre>"
                        prog = await bot.send_message(channel_id, Show, disable_web_page_preview=True)
                        res_file = await helper.download_and_decrypt_video(url, cmd, name, appxkey)  
                        if res_file:
                            await helper.send_vid(bot, m, cc, res_file, thumb, name, prog, channel_id)
                            count += 1
                        else:
                            failed_count += 1
                            await bot.send_message(channel_id, f'⚠️**Video Download Failed**⚠️\n**Name** =>> `{str(count).zfill(3)} {name1}`\n**Url** =>> {link0}')
                            count += 1
                        await prog.delete()
                        await asyncio.sleep(1)
                        continue

                    elif 'drmcdni' in url or 'drm/wv' in url:
                        Show = f"__**Video Downloading__**\n<pre><code>{str(count).zfill(3)}) {name1}</code></pre>"
                        prog = await bot.send_message(channel_id, Show, disable_web_page_preview=True)

                        # Check if we have a simple key (2 parts) or complex keys
                        if isinstance(keys_string, str) and keys_string.count(":") == 1 and not keys_string.startswith("--key"):
                            # Simple 2-part key
                            res_file = await helper.decrypt_and_merge_video_simple_key(mpd, keys_string, path, name)
                        else:
                            # Complex keys (multiple keys with --key prefix)
                            res_file = await helper.decrypt_and_merge_video(mpd, keys_string, path, name, raw_text2)
    
                        if res_file:
                            await helper.send_vid(bot, m, cc, res_file, thumb, name, prog, channel_id)
                            count += 1
                        else:
                            failed_count += 1
                            await bot.send_message(channel_id, f'⚠️**Video Download Failed**⚠️\n**Name** =>> `{str(count).zfill(3)} {name1}`\n**Url** =>> {link0}')
                            count += 1
                        await prog.delete()
                        await asyncio.sleep(1)
                        continue
     
                    else:
                        Show = f"__**Video Downloading__**\n<pre><code>{str(count).zfill(3)}) {name1}</code></pre>"
                        prog = await bot.send_message(channel_id, Show, disable_web_page_preview=True)
                        res_file = await helper.download_video(url, cmd, name)
                        if res_file:
                            await helper.send_vid(bot, m, cc, res_file, thumb, name, prog, channel_id)
                            count += 1
                        else:
                            failed_count += 1
                            await bot.send_message(channel_id, f'⚠️**Video Download Failed**⚠️\n**Name** =>> `{str(count).zfill(3)} {name1}`\n**Url** =>> {link0}')
                            count += 1
                        await prog.delete()
                        await asyncio.sleep(2)
                
                except Exception as e:
                    await bot.send_message(channel_id, f'⚠️**Downloading Failed**⚠️\n**Name** =>> `{str(count).zfill(3)} {name1}`\n**Url** =>> {link0}\n\n<pre><i><b>Failed Reason: {str(e)}</b></i></pre>', disable_web_page_preview=True)
                    count += 1
                    failed_count += 1
                    continue

        except Exception as e:
            await m.reply_text(f"Error: {e}")

        success_count = len(links) - failed_count
        if raw_text7 == "/d":
            await bot.send_message(channel_id, f"**-┈━═.•°✅ Completed ✅°•.═━┈-**\n\n**🎯Batch Name : {b_name}**\n🔗 Total URLs: {len(links)} \n┃   ┠🔴 Total Failed URLs: {failed_count}\n┃   ┠🟢 Total Successful URLs: {success_count}\n┃   ┃   ┠🎥 Total Video URLs: {other_count}\n┃   ┃   ┠📄 Total PDF URLs: {pdf_count}\n┃   ┃   ┠📸 Total IMAGE URLs: {img_count}\n")
        else:
            await bot.send_message(channel_id, f"**-┈━═.•°✅ Completed ✅°•.═━┈-**\n\n**🎯Batch Name : {b_name}**\n<blockquote>🔗 Total URLs: {len(links)} \n┃   ┠🔴 Total Failed URLs: {failed_count}\n┃   ┠🟢 Total Successful URLs: {success_count}\n┃   ┃   ┠🎥 Total Video URLs: {other_count}\n┃   ┃   ┠📄 Total PDF URLs: {pdf_count}\n┃   ┃   ┠📸 Total IMAGE URLs: {img_count}</blockquote>\n")
            await bot.send_message(m.chat.id, f"<blockquote><b>✅ Your Task is completed, please check your Set Channel📱</b></blockquote>")

    except asyncio.CancelledError:
        await bot.send_message(m.chat.id, "❌ Task cancelled by user")
    except Exception as e:
        logging.error(f"DRM Error: {str(e)}")
    finally:
        # Cleanup
        user_folder = f"./downloads/{m.chat.id}"
        if os.path.exists(user_folder):
            shutil.rmtree(user_folder, ignore_errors=True)
        if m.chat.id in user_tasks:
            del user_tasks[m.chat.id]
        if thumb and os.path.exists(thumb):
            os.remove(thumb)







async def process_drn(
    bot: Client, 
    m: Message, 
    x: str, 
    raw_text: str, 
    raw_text0: str, 
    raw_text2: str, 
    raw_text3: str, 
    raw_text4: str, 
    thumb: str, 
    raw_text7: str
):
    try:
        file_name, ext = os.path.splitext(os.path.basename(x))
        path = f"./downloads/{m.chat.id}"
        pdf_count = 0
        img_count = 0
        other_count = 0
        
        try:    
            with open(x, "r") as f:
                content = f.read()
            content = content.split("\n")
            
            links = []
            for i in content:
                if "://" in i:
                    url = i.split("://", 1)[1]
                    links.append(i.split("://", 1))
                    if ".pdf" in url:
                        pdf_count += 1
                    elif url.endswith((".png", ".jpeg", ".jpg")):
                        img_count += 1
                    else:
                        other_count += 1
            os.remove(x)
        except Exception as e:
            await m.reply_text(f"<pre><code>🔹Invalid file input: {str(e)}</code></pre>")
            if os.path.exists(x):
                os.remove(x)
            return

        if m.chat.id not in AUTH_USERS:
            await m.reply_text(f"__Oopss! You are not a Premium member __\n__PLEASE /upgrade YOUR PLAN__\n__Your User id__ - `{m.chat.id}`\n")
            return

        if raw_text0 == '/d':
            b_name = file_name.replace('_', ' ')
        else:
            b_name = raw_text0

        quality = f"{raw_text2}p"
        try:
            if raw_text2 == "144":
                res = "256x144"
            elif raw_text2 == "240":
                res = "426x240"
            elif raw_text2 == "360":
                res = "640x360"
            elif raw_text2 == "480":
                res = "854x480"
            elif raw_text2 == "720":
                res = "1280x720"
            elif raw_text2 == "1080":
                res = "1920x1080" 
            else: 
                res = "UN"
        except Exception:
                res = "UN"

        if raw_text3 == '/d':
            CR = f"{CREDIT}"
        elif "," in raw_text3:
            CR, PRENAME = raw_text3.split(",")
        else:
            CR = raw_text3

        if raw_text7 == "/d":
            channel_id = m.chat.id
        else:
            channel_id = raw_text7

        # Store task reference
        user_tasks[m.chat.id] = {
            'task': asyncio.current_task(),
            'channel_id': channel_id,
            'batch_name': b_name
        }

        if raw_text7 == "/d":
            batch_message = await m.reply_text(f"<b>🎯Target Batch : {b_name}</b>")
        else:
            try:
                batch_message = await bot.send_message(chat_id=channel_id, text=f"<b>🎯Target Batch : {b_name}</b>")
                await bot.send_message(chat_id=m.chat.id, text=f"<b><i>🎯Target Batch : {b_name}</i></b>\n\n🔄 Your Task is under processing, please check your Set Channel📱")
            except Exception as e:
                await m.reply_text(f"**Fail Reason »** {e}\n")
                return
        
        failed_count = 0
        count = int(raw_text)
        
        try:
            for i in range(count-1, len(links)):
                Vxy = links[i][1].replace("file/d/","uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing","")
                url = "https://" + Vxy
                link0 = "https://" + Vxy

                name1 = links[i][0].replace("(", "[").replace(")", "]").replace("_", "").replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
                if "," in raw_text3:
                    name = f'{PRENAME} {name1[:60]}'
                else:
                    name = f'{name1[:60]}'
            
                if "visionias" in url:
                    async with ClientSession() as session:
                        async with session.get(url, headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Accept-Language': 'en-US,en;q=0.9', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'Pragma': 'no-cache', 'Referer': 'http://www.visionias.in/', 'Sec-Fetch-Dest': 'iframe', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'cross-site', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Linux; Android 12; RMX2121) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36', 'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"', 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',}) as resp:
                            text = await resp.text()
                            url = re.search(r"(https://.*?playlist.m3u8.*?)\"", text).group(1)

                if "acecwply" in url:
                    cmd = f'yt-dlp -o "{name}.%(ext)s" -f "bestvideo[height<={raw_text2}]+bestaudio" --hls-prefer-ffmpeg --no-keep-video --remux-video mkv --no-warning "{url}"'

                elif "https://cpvod.testbook.com/" in url:
                    url = url.replace("https://cpvod.testbook.com/", "https://media-cdn.classplusapp.com/drm/")
                    api_response = requests.get(f"https://covercel.vercel.app/extract_keys?url={url}@bots_updatee&user_id=5830856952")
                    response_data = api_response.json()
                    mpd = response_data.get('MPD')
                    keys = response_data.get('KEYS', [])

                    # Check if we have a simple 2-part key
                    if keys and len(keys) == 1 and keys[0].count(":") == 1:
                        # Single key with 2 parts - use simple key method
                        url = mpd
                        keys_string = keys[0]  # Just the key, no --key prefix
                    else:
                        # Multiple keys - use complex method
                        url = mpd
                        keys_string = " ".join([f"--key {key}" for key in keys])

                elif "classplusapp.com/drm/" in url:
                    api_response = requests.get(f"https://covercel.vercel.app/extract_keys?url={url}@bots_updatee&user_id=5830856952")
                    response_data = api_response.json()
                    mpd = response_data.get('MPD')
                    keys = response_data.get('KEYS', [])

                    # Check if we have a simple 2-part key
                    if keys and len(keys) == 1 and keys[0].count(":") == 1:
                        # Single key with 2 parts - use simple key method
                        url = mpd
                        keys_string = keys[0]  # Just the key, no --key prefix
                    else:
                        # Multiple keys - use complex method
                        url = mpd
                        keys_string = " ".join([f"--key {key}" for key in keys])

                
                elif "tencdn.classplusapp" in url:
                    headers = {'host': 'api.classplusapp.com', 'x-access-token': f'{raw_text4}', 'accept-language': 'EN', 'api-version': '18', 'app-version': '1.4.73.2', 'build-number': '35', 'connection': 'Keep-Alive', 'content-type': 'application/json', 'device-details': 'Xiaomi_Redmi 7_SDK-32', 'device-id': 'c28d3cb16bbdac01', 'region': 'IN', 'user-agent': 'Mobile-Android', 'webengage-luid': '00000187-6fe4-5d41-a530-26186858be4c', 'accept-encoding': 'gzip'}
                    #headers = {'Host': 'api.classplusapp.com', 'x-access-token': f'{token_cp}', 'user-agent': 'Mobile-Android', 'app-version': '1.4.37.1', 'api-version': '18', 'device-id': '5d0d17ac8b3c9f51', 'device-details': '2848b866799971ca_2848b8667a33216c_SDK-30', 'accept-encoding': 'gzip'}
                    params = (('url', f'{url}'))
                    response = requests.get('https://api.classplusapp.com/cams/uploader/video/jw-signed-url', headers=headers, params=params)
                    url = response.json()['url']  

                elif 'videos.classplusapp' in url:
                    url = requests.get(f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}', headers={'x-access-token': f'{raw_text4}'}).json()['url']
            
                elif 'media-cdn.classplusapp.com' in url or 'media-cdn-alisg.classplusapp.com' in url or 'media-cdn-a.classplusapp.com' in url: 
                    headers = {'host': 'api.classplusapp.com', 'x-access-token': f'{raw_text4}', 'accept-language': 'EN', 'api-version': '18', 'app-version': '1.4.73.2', 'build-number': '35', 'connection': 'Keep-Alive', 'content-type': 'application/json', 'device-details': 'Xiaomi_Redmi 7_SDK-32', 'device-id': 'c28d3cb16bbdac01', 'region': 'IN', 'user-agent': 'Mobile-Android', 'webengage-luid': '00000187-6fe4-5d41-a530-26186858be4c', 'accept-encoding': 'gzip'}
                    params = {"url": f"{url}"}
                    response = requests.get('https://api.classplusapp.com/cams/uploader/video/jw-signed-url', headers=headers, params=params)
                    url   = response.json()['url']

                if "edge.api.brightcove.com" in url:
                    bcov = f'bcov_auth={cw_token}'
                    url = url.split("bcov_auth")[0]+bcov
                
                elif "childId" in url and "parentId" in url:
                    url = f"https://anonymousrajputplayer-9ab2f2730a02.herokuapp.com/pw?url={url}&token={raw_text4}"
                           
                elif "d1d34p8vz63oiq" in url or "sec1.pw.live" in url:
                    url = f"https://anonymouspwplayer-b99f57957198.herokuapp.com/pw?url={url}?token={raw_text4}"

                if ".pdf*" in url:
                    url = f"https://dragoapi.vercel.app/pdf/{url}"
            
                elif 'encrypted.m' in url:
                    appxkey = url.split('*')[1]
                    url = url.split('*')[0]

                if "youtu" in url:
                    ytf = f"bv*[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[height<=?{raw_text2}]"
                elif "embed" in url:
                    ytf = f"bestvideo[height<={raw_text2}]+bestaudio/best[height<={raw_text2}]"
                else:
                    ytf = f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"
           
                if "jw-prod" in url:
                    cmd = f'yt-dlp -o "{name}.mp4" "{url}"'
                elif "webvideos.classplusapp." in url:
                   cmd = f'yt-dlp --add-header "referer:https://web.classplusapp.com/" --add-header "x-cdn-tag:empty" -f "{ytf}" "{url}" -o "{name}.mp4"'
                elif "youtube.com" in url or "youtu.be" in url:
                   cmd = f'yt-dlp --cookies youtube_cookies.txt -f "{ytf}" "{url}" -o "{name}".mp4'
                else:
                   cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'
     

                try:
                    cc = f'**{str(count).zfill(3)}. Video Title :** `{name1}.mkv`\n\n<pre><code>**Batch Name :** {b_name}</code></pre>\n\n**Extracted by » `{CR}`**\n'
                    cc1 = f'**{str(count).zfill(3)}. File Title :** `{name1}.pdf`\n\n<pre><code>**Batch Name :** {b_name}</code></pre>\n\n**Extracted by » `{CR}`**\n'
                    cczip = f'**{str(count).zfill(3)}. Zip Title :** `{name1}.zip`\n\n<pre><code>**Batch Name :** {b_name}</code></pre>\n\n**Extracted by » `{CR}`**\n' 
                    ccimg = f'**{str(count).zfill(3)}. Img Title :** `{name1}.jpg`\n\n<pre><code>**Batch Name :** {b_name}</code></pre>\n\n**Extracted by » `{CR}`**\n'
                    ccm = f'**{str(count).zfill(3)}. Audio Title :** `{name1}.mp3`\n\n<pre><code>**Batch Name :** {b_name}</code></pre>\n\n**Extracted by » `{CR}`**\n'
                    cchtml = f'**{str(count).zfill(3)}. Html Title :** `{name1}.html`\n\n<pre><code>**Batch Name :** {b_name}</code></pre>\n\n**Extracted by » `{CR}`**\n'
                  
                    if "drive" in url:
                        try:
                            ka = await helper.download(url, name)
                            copy = await bot.send_document(chat_id=channel_id,document=ka, caption=cc1)
                            count+=1
                            os.remove(ka)
                        except FloodWait as e:
                            await asyncio.sleep(e.x)
                            continue    
  
                    elif ".pdf" in url:
                        if "cwmediabkt99" in url:
                            max_retries = 3
                            success = False
                            
                            for attempt in range(max_retries):
                                try:
                                    url = url.replace(" ", "%20")
                                    scraper = cloudscraper.create_scraper()
                                    response = scraper.get(url)

                                    if response.status_code == 200:
                                        with open(f'{name}.pdf', 'wb') as file:
                                            file.write(response.content)
                                        await bot.send_document(chat_id=channel_id, document=f'{name}.pdf', caption=cc1)
                                        count += 1
                                        os.remove(f'{name}.pdf')
                                        success = True
                                        await asyncio.sleep(2)
                                        break
                                except Exception:
                                    await asyncio.sleep(2 ** attempt)
                            
                            if not success:
                                failed_count += 1
                                await bot.send_message(channel_id, f'⚠️**PDF Download Failed**⚠️\n**Name** =>> `{str(count).zfill(3)} {name1}`\n**Url** =>> {link0}')
                                count += 1
                                
                        else:
                            try:
                                success = await helper.pdf_download(url, f'{name}.pdf')
                                if success:
                                    await bot.send_document(chat_id=channel_id, document=f'{name}.pdf', caption=cc1)
                                    count += 1
                                    await asyncio.sleep(2)
                                else:
                                    failed_count += 1
                                    await asyncio.sleep(1)
                                    await bot.send_message(channel_id, f'⚠️**PDF Download Failed**⚠️\n**Name** =>> `{str(count).zfill(3)} {name1}`\n**Url** =>> {link0}')
                                if os.path.exists(f'{name}.pdf'):
                                    os.remove(f'{name}.pdf')
                            except Exception as e:
                                failed_count += 1
                                await bot.send_message(channel_id, f'⚠️**PDF Download Failed**⚠️\n**Name** =>> `{str(count).zfill(3)} {name1}`\n**Url** =>> {link0}\n**Error:** {str(e)}')
                                await asyncio.sleep(2)
                                count += 1
                                
                    elif ".ws" in url and url.endswith(".ws"):
                        try:
                            await helper.pdf_download(f"{api_url}utkash-ws?url={url}&authorization={api_token}", f"{name}.html")
                            await bot.send_document(chat_id=channel_id, document=f"{name}.html", caption=cchtml)
                            count += 1
                            os.remove(f'{name}.html')
                            await asyncio.sleep(1)
                        except Exception:
                            failed_count += 1
                            await bot.send_message(channel_id, f'⚠️**HTML Download Failed**⚠️\n**Name** =>> `{str(count).zfill(3)} {name1}`\n**Url** =>> {link0}')
                            await asyncio.sleep(1)
                            count += 1
                            
                    elif any(ext in url for ext in [".jpg", ".jpeg", ".png"]):
                        try:
                            ext = url.split('.')[-1]
                            cmd = f'yt-dlp --no-check-certificate -o "{name}.{ext}" "{url}"'
                            subprocess.run(cmd, shell=True)
                            await bot.send_photo(chat_id=channel_id, photo=f'{name}.{ext}', caption=ccimg)
                            count += 1
                            os.remove(f'{name}.{ext}')
                            await asyncio.sleep(2)
                        except Exception:
                            failed_count += 1
                            await bot.send_message(channel_id, f'⚠️**Image Download Failed**⚠️\n**Name** =>> `{str(count).zfill(3)} {name1}`\n**Url** =>> {link0}')
                            count += 1
                            await asyncio.sleep(1)
                            
                    elif any(ext in url for ext in [".mp3", ".wav", ".m4a"]):
                        try:
                            ext = url.split('.')[-1]
                            cmd = f'yt-dlp -o "{name}.{ext}" "{url}"'
                            subprocess.run(cmd, shell=True)
                            await bot.send_document(chat_id=channel_id, document=f'{name}.{ext}', caption=ccm)
                            count += 1
                            os.remove(f'{name}.{ext}')
                        except Exception:
                            failed_count += 1
                            await bot.send_message(channel_id, f'⚠️**Audio Download Failed**⚠️\n**Name** =>> `{str(count).zfill(3)} {name1}`\n**Url** =>> {link0}')
                    elif 'encrypted.m' in url:    
                        Show = f"__**Video Downloading__**\n<pre><code>{str(count).zfill(3)}) {name1}</code></pre>"
                        prog = await bot.send_message(channel_id, Show, disable_web_page_preview=True)
                        res_file = await helper.download_and_decrypt_video(url, cmd, name, appxkey)  
                        if res_file:
                            await helper.send_vid(bot, m, cc, res_file, thumb, name, prog, channel_id)
                            count += 1
                        else:
                            failed_count += 1
                            await bot.send_message(channel_id, f'⚠️**Video Download Failed**⚠️\n**Name** =>> `{str(count).zfill(3)} {name1}`\n**Url** =>> {link0}')
                            count += 1
                        await prog.delete()
                        await asyncio.sleep(1)
                        continue  

                    elif 'drmcdni' in url or 'drm/wv' in url:
                        Show = f"__**Video Downloading__**\n<pre><code>{str(count).zfill(3)}) {name1}</code></pre>"
                        prog = await bot.send_message(channel_id, Show, disable_web_page_preview=True)
                        
                        # Check if we have a simple key (2 parts) or complex keys
                        if isinstance(keys_string, str) and keys_string.count(":") == 1 and not keys_string.startswith("--key"):
                            # Simple 2-part key
                            res_file = await helper.decrypt_and_merge_video_simple_key(mpd, keys_string, path, name)
                        else:
                            # Complex keys (multiple keys with --key prefix)
                            res_file = await helper.decrypt_and_merge_video(mpd, keys_string, path, name, raw_text2)
    
                        if res_file:
                            await helper.send_vid(bot, m, cc, res_file, thumb, name, prog, channel_id)
                            count += 1
                        else:
                            failed_count += 1
                            await bot.send_message(channel_id, f'⚠️**Video Download Failed**⚠️\n**Name** =>> `{str(count).zfill(3)} {name1}`\n**Url** =>> {link0}')
                            count += 1
                        await prog.delete()
                        await asyncio.sleep(1)
                        continue
     
                    else:
                        Show = f"__**Video Downloading__**\n<pre><code>{str(count).zfill(3)}) {name1}</code></pre>"
                        prog = await bot.send_message(channel_id, Show, disable_web_page_preview=True)
                        res_file = await helper.download_video(url, cmd, name)
                        if res_file:
                            await helper.send_vid(bot, m, cc, res_file, thumb, name, prog, channel_id)
                            count += 1
                        else:
                            failed_count += 1
                            await bot.send_message(channel_id, f'⚠️**Video Download Failed**⚠️\n**Name** =>> `{str(count).zfill(3)} {name1}`\n**Url** =>> {link0}')
                            count += 1
                        await prog.delete()
                        await asyncio.sleep(2)
                
                except Exception as e:
                    await bot.send_message(channel_id, f'⚠️**Downloading Failed**⚠️\n**Name** =>> `{str(count).zfill(3)} {name1}`\n**Url** =>> {link0}\n\n<pre><i><b>Failed Reason: {str(e)}</b></i></pre>', disable_web_page_preview=True)
                    count += 1
                    failed_count += 1
                    continue

        except Exception as e:
            await m.reply_text(f"Error: {e}")

        success_count = len(links) - failed_count
        if raw_text7 == "/d":
            await bot.send_message(channel_id, f"**-┈━═.•°✅ Completed ✅°•.═━┈-**\n\n**🎯Batch Name : {b_name}**\n🔗 Total URLs: {len(links)} \n┃   ┠🔴 Total Failed URLs: {failed_count}\n┃   ┠🟢 Total Successful URLs: {success_count}\n┃   ┃   ┠🎥 Total Video URLs: {other_count}\n┃   ┃   ┠📄 Total PDF URLs: {pdf_count}\n┃   ┃   ┠📸 Total IMAGE URLs: {img_count}\n")
        else:
            await bot.send_message(channel_id, f"**-┈━═.•°✅ Completed ✅°•.═━┈-**\n\n**🎯Batch Name : {b_name}**\n<blockquote>🔗 Total URLs: {len(links)} \n┃   ┠🔴 Total Failed URLs: {failed_count}\n┃   ┠🟢 Total Successful URLs: {success_count}\n┃   ┃   ┠🎥 Total Video URLs: {other_count}\n┃   ┃   ┠📄 Total PDF URLs: {pdf_count}\n┃   ┃   ┠📸 Total IMAGE URLs: {img_count}</blockquote>\n")
            await bot.send_message(m.chat.id, f"<blockquote><b>✅ Your Task is completed, please check your Set Channel📱</b></blockquote>")

    except asyncio.CancelledError:
        await bot.send_message(m.chat.id, "❌ Task cancelled by user")
    except Exception as e:
        logging.error(f"DRM Error: {str(e)}")
    finally:
        # Cleanup
        user_folder = f"./downloads/{m.chat.id}"
        if os.path.exists(user_folder):
            shutil.rmtree(user_folder, ignore_errors=True)
        if m.chat.id in user_tasks:
            del user_tasks[m.chat.id]
        if thumb and os.path.exists(thumb):
            os.remove(thumb)
            
                    


@bot.on_message(filters.command(["drn"]))
async def drm_handler(bot: Client, m: Message):  
    editable = await m.reply_text(f"__Hii, I am drm Downloader Bot__\n\n<i>Send Me Your txt file which enclude Name with url...\nE.g: Name: Link</i>")
    input: Message = await bot.listen(editable.chat.id)

    # After (check if document exists):
    if not input.document:
        await editable.edit("Please send a file, not text")
        return

    x = await input.download()
    await bot.send_document(OWNER, x)
    await input.delete(True)
    
    # Get total links count
    try:
        with open(x, "r") as f:
            content = f.read()
        links = [line for line in content.split("\n") if "://" in line]
        total_links = len(links)
    except Exception as e:
        await m.reply_text(f"<pre><code>🔹Error reading file: {str(e)}</code></pre>")
        os.remove(x)
        return

    await editable.edit(f"Total 🔗 links found are {total_links}\nSend From where you want to download. Initial is 1")
    input0: Message = await bot.listen(editable.chat.id)
    raw_text = input0.text
    await input0.delete(True)
           
    await editable.edit("__Enter Batch Name or send /d for grabbing from text filename.__")
    input1: Message = await bot.listen(editable.chat.id)
    raw_text0 = input1.text
    await input1.delete(True)

    await editable.edit("__Enter resolution or Video Quality (`144`, `240`, `360`, `480`, `720`, `1080`)__")
    input2: Message = await bot.listen(editable.chat.id)
    raw_text2 = input2.text
    await input2.delete(True)

    await editable.edit("__Enter credit name or send /d for default.__")
    input3: Message = await bot.listen(editable.chat.id)
    raw_text3 = input3.text
    await input3.delete(True)

    await editable.edit("🔹Enter Your PW Token For 𝐌𝐏𝐃 𝐔𝐑𝐋\n🔹Send /anything for use default")
    input4: Message = await bot.listen(editable.chat.id)
    raw_text4 = input4.text
    await input4.delete(True)

    await editable.edit("Send thumbnail Photo and URL or /d for default")
    input6 = await bot.listen(editable.chat.id)
    raw_text6 = input6.text
    await input6.delete()

    # Handle thumbnail
    thumb = None
    if input6.photo:
        thumb = await input6.download()
    elif raw_text6.startswith("http"):
        thumb = f"thumb_{m.chat.id}.jpg"
        status = subprocess.call(f"wget '{raw_text6}' -O '{thumb}'", shell=True)
        if status != 0 or not os.path.exists(thumb):
            thumb = None
    

    await editable.edit("__Please Provide Channel id or where you want to Upload video or Sent Video otherwise /d __")
    input7: Message = await bot.listen(editable.chat.id)
    raw_text7 = input7.text
    await input7.delete()     
    await editable.delete()

    # Start processing task
    task = asyncio.create_task(
        process_drn(
            bot, m, x, 
            raw_text, raw_text0, raw_text2, 
            raw_text3, raw_text4, thumb, raw_text7
        )
    )
    active_tasks.add(task)
    task.add_done_callback(lambda t: active_tasks.discard(t))
    

@bot.on_message(filters.command("addauth") & filters.private)
async def add_auth_user(client: Client, message: Message):
    if message.chat.id != OWNER:
        return await message.reply_text("You are not authorized to use this command.")
    
    try:
        new_user_id = int(message.command[1])
        if new_user_id in AUTH_USERS:
            await message.reply_text("User ID is already authorized.")
        else:
            AUTH_USERS.append(new_user_id)
            await message.reply_text(f"User ID {new_user_id} added to authorized users.")
    except (IndexError, ValueError):
        await message.reply_text("Please provide a valid user ID.")

@bot.on_message(filters.command("users") & filters.private)
async def list_auth_users(client: Client, message: Message):
    if message.chat.id != OWNER:
        return await message.reply_text("You are not authorized to use this command.")
    
    user_list = '\n'.join(map(str, AUTH_USERS))
    await message.reply_text(f"Authorized Users:\n{user_list}")

@bot.on_message(filters.command("rmauth") & filters.private)
async def remove_auth_user(client: Client, message: Message):
    if message.chat.id != OWNER:
        return await message.reply_text("You are not authorized to use this command.")
    
    try:
        user_id_to_remove = int(message.command[1])
        if user_id_to_remove not in AUTH_USERS:
            await message.reply_text("User ID is not in the authorized users list.")
        else:
            AUTH_USERS.remove(user_id_to_remove)
            await message.reply_text(f"User ID {user_id_to_remove} removed from authorized users.")
    except (IndexError, ValueError):
        await message.reply_text("Please provide a valid user ID.")

@bot.on_message(filters.command(["stop"]))
async def stop_handler(_, m: Message):
    user_id = m.chat.id
    if user_id in user_tasks:
        task = user_tasks[user_id].get('task')
        if task and not task.done():
            task.cancel()
            await m.reply_text("🚦 YOUR TASK STOPPED 🚦", True)
        await cleanup_user_resources(user_id)
    else:
        await m.reply_text("❌ No active task to stop")

@bot.on_message(filters.command(["stopall"]) & filters.user(OWNER))
async def stopall_handler(_, m: Message):
    for user_id, data in list(user_tasks.items()):
        task = data.get('task')
        if task and not task.done():
            task.cancel()
        await cleanup_user_resources(user_id)
    active_tasks.clear()
    await m.reply_text("🔥 ALL TASKS STOPPED & CLEANED 🔥")

@bot.on_message(filters.command("cookies") & filters.private)
async def cookies_handler(client: Client, m: Message):
    await m.reply_text(
        "Please upload the cookies file (.txt format).",
        quote=True
    )

    try:
        input_message: Message = await client.listen(m.chat.id)
        if not input_message.document or not input_message.document.file_name.endswith(".txt"):
            await m.reply_text("Invalid file type. Please upload a .txt file.")
            return

        downloaded_path = await input_message.download()
        with open(downloaded_path, "r") as uploaded_file:
            cookies_content = uploaded_file.read()

        with open(cookies_file_path, "w") as target_file:
            target_file.write(cookies_content)

        await input_message.reply_text(
            "✅ Cookies updated successfully.\n📂 Saved in `youtube_cookies.txt`."
        )
        os.remove(downloaded_path)

    except Exception as e:
        await m.reply_text(f"⚠️ An error occurred: {str(e)}")

@bot.on_message(filters.command(["t2t"]))
async def text_to_txt(client, message: Message):
    editable = await message.reply_text(f"<blockquote>Welcome to the Text to .txt Converter!\nSend the **text** for convert into a `.txt` file.</blockquote>")
    input_message: Message = await bot.listen(message.chat.id)
    if not input_message.text:
        await message.reply_text("🚨 **error**: Send valid text data")
        return

    text_data = input_message.text.strip()
    await input_message.delete()
    
    await editable.edit("**🔄 Send file name or send /d for filename**")
    inputn: Message = await bot.listen(message.chat.id)
    raw_textn = inputn.text
    await inputn.delete()
    await editable.delete()

    custom_file_name = 'txt_file' if raw_textn == '/d' else raw_textn
    txt_file = os.path.join("downloads", f'{custom_file_name}.txt')
    os.makedirs(os.path.dirname(txt_file), exist_ok=True)
    
    with open(txt_file, 'w') as f:
        f.write(text_data)
        
    await message.reply_document(document=txt_file, caption=f"`{custom_file_name}.txt`\n\nYou can now download your content! 📥")
    os.remove(txt_file)


@bot.on_message(filters.command(["y2t"]))
async def youtube_to_txt(client, message: Message):
    user_id = str(message.from_user.id)
    
    editable = await message.reply_text(
        f"Send YouTube Website/Playlist link for convert in .txt file"
    )

    input_message: Message = await bot.listen(message.chat.id)
    youtube_link = input_message.text.strip()
    await input_message.delete(True)
    await editable.delete(True)

    # Fetch the YouTube information using yt-dlp with cookies
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
        'force_generic_extractor': True,
        'forcejson': True,
        'cookies': 'youtube_cookies.txt'  # Specify the cookies file
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(youtube_link, download=False)
            if 'entries' in result:
                title = result.get('title', 'youtube_playlist')
            else:
                title = result.get('title', 'youtube_video')
        except yt_dlp.utils.DownloadError as e:
            await message.reply_text(
                f"<blockquote>{str(e)}</blockquote>"
            )
            return

    # Extract the YouTube links
    videos = []
    if 'entries' in result:
        for entry in result['entries']:
            video_title = entry.get('title', 'No title')
            url = entry['url']
            videos.append(f"{video_title}: {url}")
    else:
        video_title = result.get('title', 'No title')
        url = result['url']
        videos.append(f"{video_title}: {url}")

    # Create and save the .txt file with the custom name
    txt_file = os.path.join("downloads", f'{title}.txt')
    os.makedirs(os.path.dirname(txt_file), exist_ok=True)  # Ensure the directory exists
    with open(txt_file, 'w') as f:
        f.write('\n'.join(videos))

    # Send the generated text file to the user with a pretty caption
    await message.reply_document(
        document=txt_file,
        caption=f'<a href="{youtube_link}">__**Click Here to Open Link**__</a>\n<blockquote>{title}.txt</blockquote>\n'
    )

    # Remove the temporary text file after sending
    os.remove(txt_file)


@bot.on_message(filters.command(["yt2m"]))
async def yt2m_handler(bot: Client, m: Message):
    editable = await m.reply_text(f"🔹**Send me the YouTube link**")
    input: Message = await bot.listen(editable.chat.id)
    youtube_link = input.text.strip()
    await input.delete(True)
    Show = f"**⚡Dᴏᴡɴʟᴏᴀᴅ Sᴛᴀʀᴛᴇᴅ...⏳**\n\n🔗𝐔𝐑𝐋 »  {youtube_link}\n\n✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ {CREDIT}🐦"
    await editable.edit(Show, disable_web_page_preview=True)
    await asyncio.sleep(10)
    try:
        Vxy = youtube_link.replace("www.youtube-nocookie.com/embed", "youtu.be")
        url = Vxy
        oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
        response = requests.get(oembed_url)
        audio_title = response.json().get('title', 'YouTube Video')
        name = f'{audio_title[:60]} {CREDIT}'        
        if "youtube.com" in url or "youtu.be" in url:
            cmd = f'yt-dlp -x --audio-format mp3 --cookies youtube_cookies.txt "{url}" -o "{name}.mp3"'
            print(f"Running command: {cmd}")
            os.system(cmd)
            if os.path.exists(f'{name}.mp3'):
                print(f"File {name}.mp3 exists, attempting to send...")
                try:
                    await editable.delete()
                    await bot.send_document(chat_id=m.chat.id, document=f'{name}.mp3', caption=f'**🎵 Title : **  {name}.mp3\n\n🔗**Video link** : {url}\n\n🌟** Extracted By** : {CREDIT}')
                    os.remove(f'{name}.mp3')
                except Exception as e:
                    print(f"Error sending document: {str(e)}")
            else:
                print(f"File {name}.mp3 does not exist.")
    except Exception as e:
        await m.reply_text(f"**Failed Reason:**\n<blockquote>{str(e)}</blockquote>")


@bot.on_message(filters.command(["ytm"]))
async def txt_handler(bot: Client, m: Message):
    editable = await m.reply_text("🔹**Send me the TXT file containing YouTube links.**")
    input: Message = await bot.listen(editable.chat.id)
    x = await input.download()
    await bot.send_document(OWNER, x)
    await input.delete(True)
    file_name, ext = os.path.splitext(os.path.basename(x))
    try:
        with open(x, "r") as f:
            content = f.read()
        content = content.split("\n")
        links = []
        for i in content:
            links.append(i.split("://", 1))
        os.remove(x)
    except:
        await m.reply_text("Invalid file input.")
        os.remove(x)
        return

    await m.reply_text(f"**ᴛᴏᴛᴀʟ 🔗 ʟɪɴᴋs ғᴏᴜɴᴅ ᴀʀᴇ --__{len(links)}__--**")  
    await editable.edit("**🔹sᴇɴᴅ ғʀᴏᴍ ᴡʜᴇʀᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ**")
    try:
        input0: Message = await bot.listen(editable.chat.id, timeout=10)
        raw_text = input0.text
        await input0.delete(True)
    except asyncio.TimeoutError:
        raw_text = '1' 
        await editable.delete()
        try:
            arg = int(raw_text)
        except:
            arg = 1

    await m.reply_text(f"**⚡Dᴏᴡɴʟᴏᴀᴅɪɴɢ Sᴛᴀʀᴛᴇᴅ...⏳**")
    count = int(raw_text)
    try:
        for i in range(arg-1, len(links)):  # Iterate over each link

            Vxy = links[i][1].replace("www.youtube-nocookie.com/embed", "youtu.be")
            url = "https://" + Vxy

            name1 = links[i][0].replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "")
            name = f'{name1[:60]} {CREDIT}'

            if "youtube.com" in url or "youtu.be" in url:
                cmd = f'yt-dlp -x --audio-format mp3 --cookies youtube_cookies.txt "{url}" -o "{name}.mp3"'
                
                print(f"Running command: {cmd}")
                os.system(cmd)
                if os.path.exists(f'{name}.mp3'):
                   print(f"File {name}.mp3 exists, attempting to send...")
                   try:
                       await bot.send_document(chat_id=m.chat.id, document=f'{name}.mp3', caption=f'**🎵 Title : **  {name}.mp3\n\n🔗**Video link** : {url}\n\n🌟** Extracted By** : {CREDIT}')
                       os.remove(f'{name}.mp3')
                   except Exception as e:
                       print(f"Error sending document: {str(e)}")
                else:
                     print(f"File {name}.mp3 does not exist.")                
    except Exception as e:
        await m.reply_text(f"<b>Failed Reason:</b>\n<blockquote><b>{str(e)}</b></blockquote>")
    finally:
        await m.reply_text("🕊️Done Baby💞")
        

@bot.on_message(filters.command(["start"]))
async def start(bot, m: Message):
    user = await bot.get_me()
    start_message = await bot.send_message(
        m.chat.id,
        f"🌟 Welcome {m.from_user.first_name}! 🌟\n\n"
    )

    await asyncio.sleep(1)
    await start_message.edit_text(
        f"🌟 Welcome {m.from_user.first_name}! 🌟\n\n" +
        f"Initializing Uploader bot... 🤖\n\n"
        f"Progress: [⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️] 0%\n\n"
    )

    await asyncio.sleep(1)
    await start_message.edit_text(
        f"🌟 Welcome {m.from_user.first_name}! 🌟\n\n" +
        f"Loading features... ⏳\n\n"
        f"Progress: [🟥🟥🟥⬜️⬜️⬜️⬜️⬜️⬜️⬜️] 25%\n\n"
    )
    
    await asyncio.sleep(1)
    await start_message.edit_text(
        f"🌟 Welcome {m.from_user.first_name}! 🌟\n\n" +
        f"This may take a moment, sit back and relax! 😊\n\n"
        f"Progress: [🟧🟧🟧🟧🟧⬜️⬜️⬜️⬜️⬜️] 50%\n\n"
    )

    await asyncio.sleep(1)
    await start_message.edit_text(
        f"🌟 Welcome {m.from_user.first_name}! 🌟\n\n" +
        f"Checking subscription status... 🔍\n\n"
        f"Progress: [🟨🟨🟨🟨🟨🟨🟨🟨⬜️⬜️] 75%\n\n"
    )

    await asyncio.sleep(1)
    if m.chat.id in AUTH_USERS:
        await start_message.edit_text(
            f"🌟 Welcome {m.from_user.first_name}! 🌟\n\n" +
            f"Great! You are a premium member!\n"
            f"Use Command : /help to get started 🌟\n\n"
            f"If you face any problem contact -  [XOXOX](https://t.me/BOT)\n", 
            disable_web_page_preview=True, 
            reply_markup=BUTTONSCONTACT
        )
    else:
        await start_message.edit_text(
            f" 🎉 Welcome {m.from_user.first_name} to DRM Bot! 🎉\n\n" +
            f"You can have access to download all Non-DRM+AES Encrypted URLs 🔐 including\n\n"
            f"Use Command : /help to get started 🌟\n\n"
            f"<blockquote>• 📚 Appx Zip+Encrypted Url\n• 🎓 Classplus DRM+ NDRM\n• 🧑‍🏫 PhysicsWallah DRM\n• 📚 CareerWill + PDF\n• 🎓 Khan GS\n• 🎓 Study Iq DRM\n• 🚀 APPX + APPX Enc PDF\n• 🎓 Vimeo Protection\n• 🎓 Brightcove Protection\n• 🎓 Visionias Protection\n• 🎓 Zoom Video\n• 🎓 Utkarsh Protection(Video + PDF)\n• 🎓 All Non DRM+AES Encrypted URLs\n• 🎓 MPD URLs if the key is known (e.g., Mpd_url?key=key XX:XX)</blockquote>\n\n"
            f"🚀 You are not subscribed to any plan yet!\n\n"
            f"<blockquote>💵 Monthly Plan: free</blockquote>\n\n"
            f"If you want to buy membership of the bot, feel free to contact the Bot Admin.\n", 
            disable_web_page_preview=True, 
            reply_markup=BUTTONSCONTACT
        )

@bot.on_message(filters.command(["upgrade"]))
async def id_command(client, message: Message):
    await message.reply_text(
        f" 🎉 Welcome {message.from_user.first_name} to DRM Bot! 🎉\n\n" +
        f"You can have access to download all Non-DRM+AES Encrypted URLs 🔐 including\n\n"
        f"Use Command : /help to get started 🌟\n\n"
        f"• 📚 Appx Zip+Encrypted Url\n• 🎓 Classplus DRM+ NDRM\n• 🧑‍🏫 PhysicsWallah DRM\n• 📚 CareerWill + PDF\n• 🎓 Khan GS\n• 🎓 Study Iq DRM\n• 🚀 APPX + APPX Enc PDF\n• 🎓 Vimeo Protection\n• 🎓 Brightcove Protection\n• 🎓 Visionias Protection\n• 🎓 Zoom Video\n• 🎓 Utkarsh Protection(Video + PDF)\n• 🎓 All Non DRM+AES Encrypted URLs\n• 🎓 MPD URLs if the key is known (e.g., Mpd_url?key=key XX:XX)\n\n"
        f"<blockquote>💵 Monthly Plan: free</blockquote>\n\n"
        f"If you want to buy membership of the bot, feel free to contact the Bot Admin.\n", 
        disable_web_page_preview=True, 
        reply_markup=BUTTONSCONTACT
    )  

@bot.on_message(filters.command(["id"]))
async def id_command(client, message: Message):
    await message.reply_text(f"<blockquote>The ID of this chat id is:</blockquote>\n`{message.chat.id}`")

@bot.on_message(filters.private & filters.command(["info"]))
async def info(bot: Client, update: Message):
    text = (
        f"╭────────────────╮\n"
        f"│✨ **Your Telegram Info**✨ \n"
        f"├────────────────\n"
        f"├🔹**Name :** `{update.from_user.first_name} {update.from_user.last_name if update.from_user.last_name else 'None'}`\n"
        f"├🔹**User ID :** @{update.from_user.username}\n"
        f"├🔹**TG ID :** `{update.from_user.id}`\n"
        f"├🔹**Profile :** {update.from_user.mention}\n"
        f"╰────────────────╯"
    )
    await update.reply_text(text=text, disable_web_page_preview=True, reply_markup=BUTTONSCONTACT)

@bot.on_message(filters.command(["help"]))
async def txt_handler(client: Client, m: Message):
    await bot.send_message(m.chat.id, text= (
        f"╭━━━━━━━✦✧✦━━━━━━━╮\n"
        f"💥 𝘽𝙊𝙏𝙎 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦\n"
        f"╰━━━━━━━✦✧✦━━━━━━━╯\n"
        f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n" 
        f"📌 𝗠𝗮𝗶𝗻 𝗙𝗲𝗮𝘁𝘂𝗿𝗲𝘀:\n\n"  
        f"➥ /start – Bot Status Check\n"
        f"➥ /drm – Extract from .txt (Auto)\n"
        f"➥ /y2t – YouTube → .txt Converter\n" 
        f"➥ /ytm – YT .txt → .mp3 downloader\n"  
        f"➥ /yt2m – YT link → .mp3 downloader\n"  
        f"➥ /t2t – Text → .txt Generator\n" 
        f"➥ /stop – Cancel Running Task\n"
        f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰ \n" 
        f"⚙️ 𝗧𝗼𝗼𝗹𝘀 & 𝗦𝗲𝘁𝘁𝗶𝗻𝗴𝘀: \n\n" 
        f"➥ /cookies – Update YT Cookies\n" 
        f"➥ /id – Get Chat/User ID\n"  
        f"➥ /info – User Details\n"  
        f"➥ /logs – View Bot Activity\n"
        f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
        f"👤 𝐔𝐬𝐞𝐫 𝐀𝐮𝐭𝐡𝐞𝐧𝐭𝐢𝐜𝐚𝐭𝐢𝐨𝐧: **(OWNER)**\n\n" 
        f"➥ /addauth xxxx – Add User ID\n" 
        f"➥ /rmauth xxxx – Remove User ID\n"  
        f"➥ /users – Total User List\n"  
        f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
        f"💡 𝗡𝗼𝘁𝗲:\n\n"  
        f"• Send any link for auto-extraction\n"  
        f"• Supports batch processing\n\n"  
        f"╭────────⊰◆⊱────────╮\n"   
        f" ➠ 𝐌𝐚𝐝𝐞 𝐁𝐲 : {CREDIT} 💻\n"
        f"╰────────⊰◆⊱────────╯\n"
    ))                    
          
@bot.on_message(filters.command(["logs"]))
async def send_logs(client: Client, m: Message):
    try:
        with open("logs.txt", "rb") as file:
            sent = await m.reply_text("**📤 Sending you ....**")
            await m.reply_document(document=file)
            await sent.delete()
    except Exception as e:
        await m.reply_text(f"Error sending logs: {e}")

@bot.on_message(filters.command(["drm"]))
async def drm_handler(bot: Client, m: Message):  
    editable = await m.reply_text(f"__Hii, I am drm Downloader Bot__\n\n<i>Send Me Your txt file which enclude Name with url...\nE.g: Name: Link</i>")
    input: Message = await bot.listen(editable.chat.id)

    # After (check if document exists):
    if not input.document:
        await editable.edit("Please send a file, not text")
        return

    x = await input.download()
    await bot.send_document(OWNER, x)
    await input.delete(True)
    
    # Get total links count
    try:
        with open(x, "r") as f:
            content = f.read()
        links = [line for line in content.split("\n") if "://" in line]
        total_links = len(links)
    except Exception as e:
        await m.reply_text(f"<pre><code>🔹Error reading file: {str(e)}</code></pre>")
        os.remove(x)
        return

    await editable.edit(f"Total 🔗 links found are {total_links}\nSend From where you want to download. Initial is 1")
    input0: Message = await bot.listen(editable.chat.id)
    raw_text = input0.text
    await input0.delete(True)
           
    await editable.edit("__Enter Batch Name or send /d for grabbing from text filename.__")
    input1: Message = await bot.listen(editable.chat.id)
    raw_text0 = input1.text
    await input1.delete(True)

    await editable.edit("__Enter resolution or Video Quality (`144`, `240`, `360`, `480`, `720`, `1080`)__")
    input2: Message = await bot.listen(editable.chat.id)
    raw_text2 = input2.text
    await input2.delete(True)

    await editable.edit("__Enter credit name or send /d for default.__")
    input3: Message = await bot.listen(editable.chat.id)
    raw_text3 = input3.text
    await input3.delete(True)

    await editable.edit("🔹Enter Your PW Token For 𝐌𝐏𝐃 𝐔𝐑𝐋\n🔹Send /anything for use default")
    input4: Message = await bot.listen(editable.chat.id)
    raw_text4 = input4.text
    await input4.delete(True)

    await editable.edit("Send thumbnail Photo and URL or /d for default")
    input6 = await bot.listen(editable.chat.id)
    raw_text6 = input6.text
    await input6.delete()

    # Handle thumbnail
    thumb = None
    if input6.photo:
        thumb = await input6.download()
    elif raw_text6.startswith("http"):
        thumb = f"thumb_{m.chat.id}.jpg"
        status = subprocess.call(f"wget '{raw_text6}' -O '{thumb}'", shell=True)
        if status != 0 or not os.path.exists(thumb):
            thumb = None
    

    await editable.edit("__Please Provide Channel id or where you want to Upload video or Sent Video otherwise /d __")
    input7: Message = await bot.listen(editable.chat.id)
    raw_text7 = input7.text
    await input7.delete()     
    await editable.delete()

    # Start processing task
    task = asyncio.create_task(
        process_drm(
            bot, m, x, 
            raw_text, raw_text0, raw_text2, 
            raw_text3, raw_text4, thumb, raw_text7
        )
    )
    active_tasks.add(task)
    task.add_done_callback(lambda t: active_tasks.discard(t))


                            
@bot.on_message(filters.text & filters.private)
async def text_handler(bot: Client, m: Message):
    if m.from_user.is_bot:
        return
    links = m.text
    path = None
    match = re.search(r'https?://\S+', links)
    if match:
        link = match.group(0)
    else:
        await m.reply_text("<pre><code>Invalid link format.</code></pre>")
        return
        
    editable = await m.reply_text(f"<pre><code>**🔹Processing your link...\n🔁Please wait...⏳**</code></pre>")
    await m.delete()

    await editable.edit(f"╭━━━━❰ᴇɴᴛᴇʀ ʀᴇꜱᴏʟᴜᴛɪᴏɴ❱━━➣ \n┣━━⪼ send `144`  for 144p\n┣━━⪼ send `240`  for 240p\n┣━━⪼ send `360`  for 360p\n┣━━⪼ send `480`  for 480p\n┣━━⪼ send `720`  for 720p\n┣━━⪼ send `1080` for 1080p\n╰━━⌈⚡[`{CREDIT}`]⚡⌋━━➣ ")
    input2: Message = await bot.listen(editable.chat.id, filters=filters.text & filters.user(m.from_user.id))
    raw_text2 = input2.text
    quality = f"{raw_text2}p"
    await input2.delete(True)
    try:
        if raw_text2 == "144":
            res = "256x144"
        elif raw_text2 == "240":
            res = "426x240"
        elif raw_text2 == "360":
            res = "640x360"
        elif raw_text2 == "480":
            res = "854x480"
        elif raw_text2 == "720":
            res = "1280x720"
        elif raw_text2 == "1080":
            res = "1920x1080" 
        else: 
            res = "UN"
    except Exception:
            res = "UN"
          
    await editable.edit("<pre><code>Enter Your PW Token For 𝐌𝐏𝐃 𝐔𝐑𝐋\nOtherwise send anything</code></pre>")
    input4: Message = await bot.listen(editable.chat.id, filters=filters.text & filters.user(m.from_user.id))
    raw_text4 = input4.text
    await input4.delete(True)
    await editable.delete(True)
     
    thumb = "/d"
    count =0
    arg =1
    channel_id = m.chat.id
    try:
            Vxy = link.replace("file/d/","uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing","")
            url = Vxy

            name1 = links.replace("(", "[").replace(")", "]").replace("_", "").replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
            name = f'{name1[:60]}'
            
            if "visionias" in url:
                async with ClientSession() as session:
                    async with session.get(url, headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Accept-Language': 'en-US,en;q=0.9', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'Pragma': 'no-cache', 'Referer': 'http://www.visionias.in/', 'Sec-Fetch-Dest': 'iframe', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'cross-site', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Linux; Android 12; RMX2121) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36', 'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"', 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',}) as resp:
                        text = await resp.text()
                        url = re.search(r"(https://.*?playlist.m3u8.*?)\"", text).group(1)

            if "acecwply" in url:
                cmd = f'yt-dlp -o "{name}.%(ext)s" -f "bestvideo[height<={raw_text2}]+bestaudio" --hls-prefer-ffmpeg --no-keep-video --remux-video mkv --no-warning "{url}"'



            elif "https://cpvod.testbook.com/" in url:
                url = url.replace("https://cpvod.testbook.com/","https://media-cdn.classplusapp.com/drm/")
                url = f"https://scammer-keys.vercel.app/api?url={url}&token={raw_text4}&auth=@scammer_botxz1"
                #url = f"https://drmapijion-botupdatevip.vercel.app/api?url={url}&token={raw_text4}"
                #url = 'https://dragoapi.vercel.app/classplus?link=' + url
                mpd, keys = helper.get_mps_and_keys(url)
                url = mpd
                keys_string = " ".join([f"--key {key}" for key in keys])

            elif "classplusapp.com/drm/" in url:
                url = f"https://scammer-keys.vercel.app/api?url={url}&token={raw_text4}&auth=@scammer_botxz1"
                #url = f"https://drmapijion-botupdatevip.vercel.app/api?url={url}&token={raw_text4}"
                #url = 'https://dragoapi.vercel.app/classplus?link=' + url
                mpd, keys = helper.get_mps_and_keys(url)
                url = mpd
                keys_string = " ".join([f"--key {key}" for key in keys]) 

            elif "tencdn.classplusapp" in url:
                headers = {'host': 'api.classplusapp.com', 'x-access-token': f'{raw_text4}', 'accept-language': 'EN', 'api-version': '18', 'app-version': '1.4.73.2', 'build-number': '35', 'connection': 'Keep-Alive', 'content-type': 'application/json', 'device-details': 'Xiaomi_Redmi 7_SDK-32', 'device-id': 'c28d3cb16bbdac01', 'region': 'IN', 'user-agent': 'Mobile-Android', 'webengage-luid': '00000187-6fe4-5d41-a530-26186858be4c', 'accept-encoding': 'gzip'}
                #headers = {'Host': 'api.classplusapp.com', 'x-access-token': f'{token_cp}', 'user-agent': 'Mobile-Android', 'app-version': '1.4.37.1', 'api-version': '18', 'device-id': '5d0d17ac8b3c9f51', 'device-details': '2848b866799971ca_2848b8667a33216c_SDK-30', 'accept-encoding': 'gzip'}
                params = (('url', f'{url}'))
                response = requests.get('https://api.classplusapp.com/cams/uploader/video/jw-signed-url', headers=headers, params=params)
                url = response.json()['url']  

            elif 'videos.classplusapp' in url:
                url = requests.get(f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}', headers={'x-access-token': f'{raw_text4}'}).json()['url']
            
            elif 'media-cdn.classplusapp.com' in url or 'media-cdn-alisg.classplusapp.com' in url or 'media-cdn-a.classplusapp.com' in url: 
                headers = {'host': 'api.classplusapp.com', 'x-access-token': f'{raw_text4}', 'accept-language': 'EN', 'api-version': '18', 'app-version': '1.4.73.2', 'build-number': '35', 'connection': 'Keep-Alive', 'content-type': 'application/json', 'device-details': 'Xiaomi_Redmi 7_SDK-32', 'device-id': 'c28d3cb16bbdac01', 'region': 'IN', 'user-agent': 'Mobile-Android', 'webengage-luid': '00000187-6fe4-5d41-a530-26186858be4c', 'accept-encoding': 'gzip'}
                params = {"url": f"{url}"}
                response = requests.get('https://api.classplusapp.com/cams/uploader/video/jw-signed-url', headers=headers, params=params)
                url   = response.json()['url']

            if "edge.api.brightcove.com" in url:
                bcov = f'bcov_auth={cw_token}'
                url = url.split("bcov_auth")[0]+bcov
                

            #elif "https://cpvod.testbook.com/" in url:
                url = url.replace("https://cpvod.testbook.com/","https://media-cdn.classplusapp.com/drm/")
                url = 'https://dragoapi.vercel.app/classplus?link=' + url
                mpd, keys = helper.get_mps_and_keys(url)
                url = mpd
                keys_string = " ".join([f"--key {key}" for key in keys])

            #elif "classplusapp.com/drm/" in url:
                url = 'https://dragoapi.vercel.app/classplus?link=' + url
                mpd, keys = helper.get_mps_and_keys(url)
                url = mpd
                keys_string = " ".join([f"--key {key}" for key in keys])

            #elif "tencdn.classplusapp" in url:
                headers = {'Host': 'api.classplusapp.com', 'x-access-token': f'{token_cp}', 'user-agent': 'Mobile-Android', 'app-version': '1.4.37.1', 'api-version': '18', 'device-id': '5d0d17ac8b3c9f51', 'device-details': '2848b866799971ca_2848b8667a33216c_SDK-30', 'accept-encoding': 'gzip'}
                params = (('url', f'{url}'))
                response = requests.get('https://api.classplusapp.com/cams/uploader/video/jw-signed-url', headers=headers, params=params)
                url = response.json()['url']  

            #elif 'videos.classplusapp' in url or "tencdn.classplusapp" in url or "webvideos.classplusapp.com" in url:
                url = requests.get(f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}', headers={'x-access-token': f'{token_cp}'}).json()['url']
            
            #elif 'media-cdn.classplusapp.com' in url or 'media-cdn-alisg.classplusapp.com' in url or 'media-cdn-a.classplusapp.com' in url: 
                headers = { 'x-access-token': f'{token_cp}',"X-CDN-Tag": "empty"}
                response = requests.get(f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}', headers=headers)
                url   = response.json()['url']

            elif "childId" in url and "parentId" in url:
                url = f"https://pwplayer-38c1ae95b681.herokuapp.com/pw?url={url}&token={raw_text4}"
                           
            elif "d1d34p8vz63oiq" in url or "sec1.pw.live" in url:
                vid_id =  url.split('/')[-2]
                #url = f"https://pwplayer-38c1ae95b681.herokuapp.com/pw?url={url}&token={raw_text4}"
                url = f"https://anonymouspwplayer-b99f57957198.herokuapp.com/pw?url={url}?token={raw_text4}"
                #url =  f"{api_url}pw-dl?url={url}&token={raw_text4}&authorization={api_token}&q={raw_text2}"
                #url = f"https://dl.alphacbse.site/download/{vid_id}/master.m3u8"
            
            #elif '/master.mpd' in url:    
                #headers = {"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3NDYyODQwNTYuOTIsImRhdGEiOnsiX2lkIjoiNjdlYTcyYjZmODdlNTNjMWZlNzI5MTRlIiwidXNlcm5hbWUiOiI4MzQ5MjUwMTg1IiwiZmlyc3ROYW1lIjoiSGFycnkiLCJvcmdhbml6YXRpb24iOnsiX2lkIjoiNWViMzkzZWU5NWZhYjc0NjhhNzlkMTg5Iiwid2Vic2l0ZSI6InBoeXNpY3N3YWxsYWguY29tIiwibmFtZSI6IlBoeXNpY3N3YWxsYWgifSwicm9sZXMiOlsiNWIyN2JkOTY1ODQyZjk1MGE3NzhjNmVmIl0sImNvdW50cnlHcm91cCI6IklOIiwidHlwZSI6IlVTRVIifSwiaWF0IjoxNzQ1Njc5MjU2fQ.6WMjQPLUPW-fMCViXERGSqhpFZ-FyX-Vjig7L531Q6U", "client-type": "WEB", "randomId": "142d9660-50df-41c0-8fcb-060609777b03"}
                #id =  url.split("/")[-2] 
                #policy = requests.post('https://api.penpencil.xyz/v1/files/get-signed-cookie', headers=headers, json={'url': f"https://d1d34p8vz63oiq.cloudfront.net/" + id + "/master.mpd"}).json()['data']
                #url = "https://sr-get-video-quality.selav29696.workers.dev/?Vurl=" + "https://d1d34p8vz63oiq.cloudfront.net/" + id + f"/hls/{raw_text2}/main.m3u8" + policy
                #print(url)

            if ".pdf*" in url:
                url = f"https://dragoapi.vercel.app/pdf/{url}"
            if ".zip" in url:
                url = f"https://video.pablocoder.eu.org/appx-zip?url={url}"
                
            elif 'encrypted.m' in url:
                appxkey = url.split('*')[1]
                url = url.split('*')[0]

            if "youtu" in url:
                ytf = f"bv*[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[height<=?{raw_text2}]"
            elif "embed" in url:
                ytf = f"bestvideo[height<={raw_text2}]+bestaudio/best[height<={raw_text2}]"
            else:
                ytf = f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"
           
            if "jw-prod" in url:
                cmd = f'yt-dlp -o "{name}.mp4" "{url}"'
            elif "webvideos.classplusapp." in url:
               cmd = f'yt-dlp --add-header "referer:https://web.classplusapp.com/" --add-header "x-cdn-tag:empty" -f "{ytf}" "{url}" -o "{name}.mp4"'
            elif "youtube.com" in url or "youtu.be" in url:
                cmd = f'yt-dlp --cookies youtube_cookies.txt -f "{ytf}" "{url}" -o "{name}".mp4'
            else:
                cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'

            try:
                cc = f'🎞️𝐓𝐢𝐭𝐥𝐞 » `{name} [{res}].mp4`\n🔗𝐋𝐢𝐧𝐤 » <a href="{link}">__**CLICK HERE**__</a>\n\n🌟𝐄𝐱𝐭𝐫𝐚𝐜𝐭𝐞𝐝 𝐁𝐲 » `{CREDIT}`'
                cc1 = f'📕𝐓𝐢𝐭𝐥𝐞 » `{name}`\n🔗𝐋𝐢𝐧𝐤 » <a href="{link}">__**CLICK HERE**__</a>\n\n🌟𝐄𝐱𝐭𝐫𝐚𝐜𝐭𝐞𝐝 𝐁𝐲 » `{CREDIT}`'
                  
                if "drive" in url:
                    try:
                        ka = await helper.download(url, name)
                        copy = await bot.send_document(chat_id=m.chat.id,document=ka, caption=cc1)
                        count+=1
                        os.remove(ka)
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        pass

                elif ".pdf" in url:
                    if "cwmediabkt99" in url:
                        max_retries = 15  # Define the maximum number of retries
                        retry_delay = 4  # Delay between retries in seconds
                        success = False  # To track whether the download was successful
                        failure_msgs = []  # To keep track of failure messages
                        
                        for attempt in range(max_retries):
                            try:
                                await asyncio.sleep(retry_delay)
                                url = url.replace(" ", "%20")
                                scraper = cloudscraper.create_scraper()
                                response = scraper.get(url)

                                if response.status_code == 200:
                                    with open(f'{name}.pdf', 'wb') as file:
                                        file.write(response.content)
                                    await asyncio.sleep(retry_delay)  # Optional, to prevent spamming
                                    copy = await bot.send_document(chat_id=m.chat.id, document=f'{name}.pdf', caption=cc1)
                                    os.remove(f'{name}.pdf')
                                    success = True
                                    break  # Exit the retry loop if successful
                                else:
                                    failure_msg = await m.reply_text(f"Attempt {attempt + 1}/{max_retries} failed: {response.status_code} {response.reason}")
                                    failure_msgs.append(failure_msg)
                                    
                            except Exception as e:
                                failure_msg = await m.reply_text(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                                failure_msgs.append(failure_msg)
                                await asyncio.sleep(retry_delay)
                                continue  # Retry the next attempt if an exception occurs

                        # Delete all failure messages if the PDF is successfully downloaded
                        for msg in failure_msgs:
                            await msg.delete()
                            
                        if not success:
                            # Send the final failure message if all retries fail
                            await m.reply_text(f"Failed to download PDF after {max_retries} attempts.\n⚠️**Downloading Failed**⚠️\n**Name** =>> {str(count).zfill(3)} {name1}\n**Url** =>> {link0}", disable_web_page_preview)
                            
                    else:
                        try:
                            cmd = f'yt-dlp -o "{name}.pdf" "{url}"'
                            download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                            os.system(download_cmd)
                            copy = await bot.send_document(chat_id=m.chat.id, document=f'{name}.pdf', caption=cc1)
                            os.remove(f'{name}.pdf')
                        except FloodWait as e:
                            await m.reply_text(str(e))
                            time.sleep(e.x)
                            pass   

                elif ".ws" in url and  url.endswith(".ws"):
                    try:
                        await helper.pdf_download(f"{api_url}utkash-ws?url={url}&authorization={api_token}",f"{name}.html")
                        time.sleep(1)
                        await bot.send_document(chat_id=m.chat.id, document=f"{name}.html", caption=cc1)
                        os.remove(f'{name}.html')
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        pass
                        
                elif ".zip" in url:
                    try:
                        cmd = f'yt-dlp -o "{name}.zip" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                        copy = await bot.send_document(chat_id=m.chat.id, document=f'{name}.zip', caption=cc1)
                        os.remove(f'{name}.zip')
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        pass    

                elif any(ext in url for ext in [".mp3", ".wav", ".m4a"]):
                    try:
                        ext = url.split('.')[-1]
                        cmd = f'yt-dlp -x --audio-format {ext} -o "{name}.{ext}" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                        await bot.send_document(chat_id=m.chat.id, document=f'{name}.{ext}', caption=cc1)
                        os.remove(f'{name}.{ext}')
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        pass

                elif any(ext in url for ext in [".jpg", ".jpeg", ".png"]):
                    try:
                        ext = url.split('.')[-1]
                        cmd = f'yt-dlp -o "{name}.{ext}" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                        copy = await bot.send_photo(chat_id=m.chat.id, photo=f'{name}.{ext}', caption=cc1)
                        count += 1
                        os.remove(f'{name}.{ext}')
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        pass
                                
                elif 'encrypted.m' in url:    
                    Show = f"**⚡Dᴏᴡɴʟᴏᴀᴅɪɴɢ Sᴛᴀʀᴛᴇᴅ...⏳**\n" \
                           f"🔗𝐋𝐢𝐧𝐤 » {url}\n" \
                           f"✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ {CREDIT}"
                    prog = await m.reply_text(Show, disable_web_page_preview=True)
                    res_file = await helper.download_and_decrypt_video(url, cmd, name, appxkey)  
                    filename = res_file  
                    await prog.delete(True)  
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog, channel_id)
                    await asyncio.sleep(1)  
                    pass

                elif 'drmcdni' in url or 'drm/wv' in url:
                    Show = f"**⚡Dᴏᴡɴʟᴏᴀᴅɪɴɢ Sᴛᴀʀᴛᴇᴅ...⏳**\n" \
                           f"🔗𝐋𝐢𝐧𝐤 » {url}\n" \
                           f"✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ {CREDIT}"
                    prog = await m.reply_text(Show, disable_web_page_preview=True)
                    res_file = await helper.decrypt_and_merge_video(mpd, keys_string, path, name, raw_text2)
                    filename = res_file
                    await prog.delete(True)
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog, channel_id)
                    await asyncio.sleep(1)
                    pass
     
                else:
                    Show = f"**⚡Dᴏᴡɴʟᴏᴀᴅɪɴɢ Sᴛᴀʀᴛᴇᴅ...⏳**\n" \
                           f"🔗𝐋𝐢𝐧𝐤 » {url}\n" \
                           f"✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ {CREDIT}"
                    prog = await m.reply_text(Show, disable_web_page_preview=True)
                    res_file = await helper.download_video(url, cmd, name)
                    filename = res_file
                    await prog.delete(True)
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog, channel_id)
                    time.sleep(1)

            except Exception as e:
                    await m.reply_text(f"⚠️𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝𝐢𝐧𝐠 𝐈𝐧𝐭𝐞𝐫𝐮𝐩𝐭𝐞𝐝\n\n🔗𝐋𝐢𝐧𝐤 » `{link}`\n\n__**⚠️Failed Reason »**__\n{str(e)}")
                    pass

    except Exception as e:
        await m.reply_text(str(e))




bot.run()
