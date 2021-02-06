from functools import wraps
from telegram import Update
from notification.models import UserTelegramBotChatId


def is_allowed(user_id) -> bool:
    return UserTelegramBotChatId.objects.filter(chat_id=user_id).exists()


def restricted(func):
    """Restrict usage of func to allowed users only and replies if necessary

    Based on https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets#restrict-access-to-a-handler-decorator
    """
    @wraps(func)
    def wrapped(self, update: Update, context, *args, **kwargs):
        user_id = update.message.chat.id

        if not is_allowed(user_id):
            print("WARNING: Unauthorized access denied for {}.".format(user_id))
            update.message.reply_text('User disallowed.')
            return  # quit function

        return func(self, update, context, *args, **kwargs)

    return wrapped
