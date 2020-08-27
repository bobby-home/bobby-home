import os
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from registered_bots import BOTS
from house.models import TelegramBot


def help(update, context):
    update.message.reply_text("Use /start to test this bot.")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    token = TelegramBot.objects.house_token()
    updater = Updater(token, use_context=True)

    for bot in BOTS:
        bot(updater)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('help', help))
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
