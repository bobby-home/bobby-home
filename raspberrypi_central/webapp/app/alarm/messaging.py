from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from house.models import TelegramBot, TelegramBotChatId


class Messaging:
    def __init__(self):
        pass

    def send_message(self, message = None, picture_path = None):
        if message is None and picture_path is None:
            raise ValueError(f'message and picture_path not set. At least one of them is required to send a message.')

        TOKEN = TelegramBot.objects.house_token()
        updater = Updater(TOKEN, use_context=True)
        bot = updater.bot

        chat_ids = TelegramBotChatId.objects.all()

        """
        Telegram API doesn't have methods for sending bulk messages yet.
        see: https://core.telegram.org/bots/faq#how-can-i-message-all-of-my-bots-subscribers-at-once
        So we're basically making n requests.
        """
        for chat_id in chat_ids:
            if message:
                bot.send_message(chat_id=chat_id, text=msg)

            if picture_path:
                bot.send_photo(chat_id=chat_id, photo=open(picture_path, 'rb'))

