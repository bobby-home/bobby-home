# TODO: move this logic in a function.
import os, sys
import django

sys.path.append('/usr/src/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hello_django.settings')
django.setup()

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from alarm.models import AlarmStatus
from notification.models import UserTelegramBotChatId


class AlarmStatusRepository:
    def __init__(self):
        pass

    def set_status(self, status: bool):
        # TODO: update because right now this is device by device, you have to choose what device you want to turn on/off
        # and change the query of course...
        s = AlarmStatus(running=status)
        s.save()

    @property
    def status(self):
        status = AlarmStatus.objects.get_status()

        return status


class AlarmStatusBot:
    def __init__(self, repository: AlarmStatusRepository, telegram_updater: Updater):
        self.repository = repository
        self._register_commands(telegram_updater)
    
    def _alarm_status(self, update, context):
        chat_id = update.message.chat.id
        try:
            UserTelegramBotChatId.objects.get(chat_id=chat_id)
        except UserTelegramBotChatId.DoesNotExist:
            update.message.reply_text('Forbidden')
        else:
            status = self.repository.status

            if status is True:
                text = "Votre alarme est activée, voulez-vous la désactiver ?"
                keyboard = [InlineKeyboardButton("Désactiver", callback_data="off")]
            elif status is False:
                text = "Votre alarme est désactivée, voulez-vous l'activer ?"
                keyboard = [InlineKeyboardButton("Activer", callback_data="on")]
            else:
                text = "Nous avons des difficultés technique pour joindre votre alarme. Contactez Maxime !"
            
            update.message.reply_text(text, reply_markup=InlineKeyboardMarkup([keyboard]))

    def _set_alarm_status(self, update, context):
        query = update.callback_query
        status = query.data

        if status == "on":
            self.repository.set_status(True)
            text = "Votre alarme est désormais active."
        elif status == "off":
            self.repository.set_status(False)
            text = "Votre alarme est désormais désactivée."

        query.edit_message_text(text)


    def _register_commands(self, update):
        update.dispatcher.add_handler(CommandHandler('status_alarm', self._alarm_status))
        update.dispatcher.add_handler(CallbackQueryHandler(self._set_alarm_status))


def alarm_status_bot_factory(telegram_updater: Updater) -> AlarmStatusBot:
    repository = AlarmStatusRepository()
    return AlarmStatusBot(repository, telegram_updater)
