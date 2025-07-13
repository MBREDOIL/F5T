# Add your details here and then deploy by clicking on HEROKU Deploy button
import os
from os import environ

API_ID = int(environ.get("API_ID", "22581733"))
API_HASH = environ.get("API_HASH", "1db7bdcf908100cc641c6a5276765c3d")
BOT_TOKEN = environ.get("BOT_TOKEN", "")
OWNER = int(environ.get("OWNER", "6935604936"))
CREDIT = "💖 M S 💖"
AUTH_USER = os.environ.get('AUTH_USERS', '6935604936,6233692970,5329562709,6106998329').split(',')
AUTH_USERS = [int(user_id) for user_id in AUTH_USER]
if int(OWNER) not in AUTH_USERS:
    AUTH_USERS.append(int(OWNER))
  
#WEBHOOK = True  # Don't change this
#PORT = int(os.environ.get("PORT", 8080))  # Default to 8000 if not set
