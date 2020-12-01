from telegram.ext import Updater

from house.models import TelegramBot


class TelegramMessaging:

    def __init__(self):
        self.token = None


    def send_message(self, chat_id, message = None, picture_path = None, *args):
        if self.token is None:
            self.token = TelegramBot.objects.house_token()

        updater = Updater(self.token, use_context=True)
        bot = updater.bot

        if message:
            bot.send_message(chat_id=chat_id.chat_id, text=message)

        if picture_path:
            bot.send_photo(chat_id=chat_id.chat_id, photo=open(picture_path, 'rb'))
