from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import os
from pathlib import Path  # python3 only

TOKEN=os.environ['TELEGRAM_BOT_TOKEN']


def send_message(msg: str, picture_path: str) -> None:
    updater = Updater(TOKEN, use_context=True)
    bot = updater.bot

    bot.send_message(chat_id="749348319", text=msg)
    bot.send_photo(chat_id="749348319", photo=open(picture_path, 'rb'))
