import os
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from registered_bots import BOTS

# chat_id = 749348319
# got from: print(update.message.chat_id)
# curl -X POST "https://api.telegram.org/bot<token>/sendMessage" -d "chat_id=749348319&text=Hello world"
# https://api.telegram.org/bot<token>/getUpdates doesn't work for me.

def help(update, context):
    update.message.reply_text("Use /start to test this bot.")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(os.getenv("BOT_TOKEN"), use_context=True)

    updater.bot.send_message(chat_id="749348319", text="Hello world!")

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
