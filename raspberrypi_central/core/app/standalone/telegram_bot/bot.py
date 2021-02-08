import os
import logging
import sys
import django
from telegram import Update

sys.path.append('/usr/src/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hello_django.settings')
django.setup()

from telegram.ext import Updater, CommandHandler, CallbackContext
from registered_bots import BOTS
from house.models import TelegramBot, TelegramBotStart
from notification.models import UserTelegramBotChatId


def start(update: Update, _context: CallbackContext) -> None:
    if update.message.chat.type != 'private':
        update.message.reply_text("This bot is only available in private chat.")
        return

    if UserTelegramBotChatId.objects.filter(chat_id=update.message.chat.id).exists():
        return update.message.reply_text('You are already onboard.')

    _obj, _created = TelegramBotStart.objects.get_or_create(
        user_id=update.message.chat.id,
        username=update.message.chat.username,
        first_name=update.message.chat.first_name,
        last_name=update.message.chat.last_name
    )

    return update.message.reply_text(f"Hello {update.message.chat.first_name}. Please ask the administrator to register your telegram so you can chat with me.")


def help(update, context):
    update.message.reply_text("Use /start to test this bot.")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def error_handler(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    telegram_bot = TelegramBot.objects.house_token()
    updater = Updater(telegram_bot.token, use_context=True)

    for bot in BOTS:
        bot(updater)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))
    dp.add_error_handler(error_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
