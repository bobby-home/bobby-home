from telegram.ext import Updater

from house.models import TelegramBot
from notification.models import UserTelegramBotChatId


class TelegramMessaging:

    def __init__(self):
        self.token = TelegramBot.objects.house_token()
        updater = Updater(self.token, use_context=True)
        self.bot = updater.bot


    def send_message(self, chat_id: UserTelegramBotChatId, *args, **kwargs):
        message = args[0]
        print(f'send_message: {chat_id} message={message}')

        self.bot.send_message(chat_id=chat_id.chat_id, text=message)


    def send_picture(self, chat_id: UserTelegramBotChatId, *args, **kwargs):
        picture_path = args[0]

        print(f'send_picture: {chat_id} picture_path={picture_path}')

        self.bot.send_photo(chat_id=chat_id.chat_id, photo=open(picture_path, 'rb'))

    def send_video(self, chat_id: UserTelegramBotChatId, *args, **kwargs):
        video_path = args[0]

        print(f'send_video: {chat_id} picture_path={video_path}')

        self.bot.send_video(chat_id=chat_id.chat_id, video=open(video_path, 'rb'))
