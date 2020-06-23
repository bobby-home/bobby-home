from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import os
from dotenv import load_dotenv
from pathlib import Path  # python3 only

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

def send_message(msg: str, picture_path: str) -> None:
    updater = Updater(os.getenv("TELEGRAM_BOT_TOKEN"), use_context=True)
    bot = updater.bot

    bot.send_message(chat_id="749348319", text=msg)
    bot.send_photo(chat_id="749348319", photo=open(picture_path, 'rb'))
