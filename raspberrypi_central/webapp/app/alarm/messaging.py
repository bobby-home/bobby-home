from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from house.models import TelegramBot
from notification.models import UserFreeCarrier, UserTelegramBotChatId
from urllib import request, parse
import requests


class TelegramMessaging:
    def __init__(self):
        pass

    def send_message(self, message = None, picture_path = None):
        TOKEN = TelegramBot.objects.house_token()
        updater = Updater(TOKEN, use_context=True)
        bot = updater.bot

        chat_ids = UserTelegramBotChatId.objects.all()

        """
        Telegram API doesn't have methods for sending bulk messages yet.
        see: https://core.telegram.org/bots/faq#how-can-i-message-all-of-my-bots-subscribers-at-once
        So we're basically making n requests.
        """
        for chat_id in chat_ids:
            if message:
                bot.send_message(chat_id=chat_id.chat_id, text=message)

            if picture_path:
                bot.send_photo(chat_id=chat_id.chat_id, photo=open(picture_path, 'rb'))

class FreeOperatorMessaging:
    def __init__(self):
        pass

    def send_message(self, message):

        credentials = UserFreeCarrier.objects.all()

        responses = []

        for credential in credentials:
            credential.free_user
            data = {
                'user': credential.free_user,
                'pass': credential.free_password,
                'msg': message
            }
            query = parse.urlencode(data)
            url = f'https://smsapi.free-mobile.fr/sendmsg?{query}'

            res = requests.get(url)
            responses.append(res)
        
        # I would like to send the request for others users... It might work for them.
        # Here I'll know if one request crashed, but not if multiple crashed...
        # i.e, the first and second ones crashed, the first will raise error here but not the seconde one
        # because the program will be "killed".
        # @TODO: find a solution?
        for res in responses:
            res.raise_for_status()
        # free api
        # errorcodes = {400: 'Missing Parameter',
        #             402: 'Spammer!',
        #             403: 'Access Denied',
        #             500: 'Server Down'}


class Messaging:
    def __init__(self):
        self.telegram_messaging = TelegramMessaging()
        self.free_operator_messaging = FreeOperatorMessaging()

    def send_message(self, message = None, picture_path = None):
        if message is None and picture_path is None:
            raise ValueError(f'message and picture_path not set. At least one of them is required to send a message.')
        
        self.telegram_messaging.send_message(message, picture_path)
        self.free_operator_messaging.send_message(message)
