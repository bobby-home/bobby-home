from urllib import parse

import requests
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from house.models import TelegramBot
from notification.models import UserFreeCarrier, UserTelegramBotChatId, UserSetting



class TelegramMessaging:

    def send_message(self, chat_id, message = None, picture_path = None, *args):
        TOKEN = TelegramBot.objects.house_token()
        updater = Updater(TOKEN, use_context=True)
        bot = updater.bot

        if message:
            bot.send_message(chat_id=chat_id.chat_id, text=message)

        if picture_path:
            bot.send_photo(chat_id=chat_id.chat_id, photo=open(picture_path, 'rb'))

class FreeCarrierMessaging:

    def send_message(self, credential, message, *args):
        data = {
            'user': credential.free_user,
            'pass': credential.free_password,
            'msg': message
        }
        query = parse.urlencode(data)
        url = f'https://smsapi.free-mobile.fr/sendmsg?{query}'

        res = requests.get(url)
    
        res.raise_for_status()
        # free api
        # errorcodes = {400: 'Missing Parameter',
        #             402: 'Spammer!',
        #             403: 'Access Denied',
        #             500: 'Server Down'}


class Messaging:
    def __init__(self):
        self.telegram_messaging = TelegramMessaging()
        self.free_carrier_messaging = FreeCarrierMessaging()

    def send_message(self, message = None, picture_path = None):
        if message is None and picture_path is None:
            raise ValueError(f'message and picture_path not set. At least one of them is required to send a message.')

        configurations = {
            'free_carrier': self.free_carrier_messaging.send_message,
            'telegram_chat': self.telegram_messaging.send_message
        }

        user_settings = UserSetting.objects.all()
        for user_setting in user_settings:
            for field, function in configurations.items():
                user_setting_conf = getattr(user_setting, field)

                if user_setting_conf:
                    function(*[user_setting_conf, message, picture_path])

        # self.telegram_messaging.send_message(message, picture_path)
        # self.free_carrier_messaging.send_message(message)
