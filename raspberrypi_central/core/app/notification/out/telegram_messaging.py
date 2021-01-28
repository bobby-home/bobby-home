from telegram.ext import Updater

from house.models import TelegramBot
from notification.models import UserTelegramBotChatId


class TelegramMessaging:

    def __init__(self):
        self.token = TelegramBot.objects.house_token()
        updater = Updater(self.token, use_context=True)
        self.bot = updater.bot

    def send_message(self, chat_id: UserTelegramBotChatId, message: str):
        self.bot.send_message(chat_id=chat_id.chat_id, text=message)

    def send_picture(self, chat_id: UserTelegramBotChatId, picture_path: str):
        self.bot.send_photo(chat_id=chat_id.chat_id, photo=open(picture_path, 'rb'))

    def send_video(self, chat_id: UserTelegramBotChatId, video_path: str):
        self.bot.send_video(chat_id=chat_id.chat_id, video=open(video_path, 'rb'))
