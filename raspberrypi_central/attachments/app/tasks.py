from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import os
from pathlib import Path
from celery import Celery

app = Celery('tasks', broker='amqp://admin:mypass@rabbit:5672')


TOKEN=os.environ['TELEGRAM_BOT_TOKEN']

@app.task
def send_message(msg: str, picture_path = None):
    print('SEND MESSAGE!')
    updater = Updater(TOKEN, use_context=True)
    bot = updater.bot

    bot.send_message(chat_id="749348319", text=msg)

    if picture_path:
        bot.send_photo(chat_id="749348319", photo=open(picture_path, 'rb'))
