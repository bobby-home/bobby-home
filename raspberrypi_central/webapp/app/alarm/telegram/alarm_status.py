import os, sys
import django

sys.path.append('/usr/src/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hello_django.settings')
django.setup()

from enum import Enum
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from alarm.models import AlarmStatus
from notification.models import UserTelegramBotChatId

class BotData(Enum):
    OFF = 'off'
    ON = 'on'


class AlarmStatusRepository:
    def __init__(self):
        pass

    @staticmethod
    def set_status(new_status: bool):
        for status in AlarmStatus.objects.all():
            status: AlarmStatus
            status.running = new_status
            status.save()

    @property
    def statuses(self):
        statuses = AlarmStatus.objects.all()

        return statuses


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
            statuses = self.repository.statuses

            texts = []
            for status in statuses:
                running = status.running

                if running is True:
                    text = f"Votre alarme {status.device.location} est activée."
                    texts.append(text)
                elif running is False:
                    text = f"Votre alarme {status.device.location} est désactivée."
                    texts.append(text)

            keyboard = [
                InlineKeyboardButton("Tout désactiver", callback_data=BotData.OFF.value),
                InlineKeyboardButton("Tout activer", callback_data=BotData.ON.value)]

            update.message.reply_text('\n'.join(texts), reply_markup=InlineKeyboardMarkup([keyboard]))

    def _set_alarm_status(self, update, context):
        query = update.callback_query
        status = query.data

        if status == BotData.ON.value:
            self.repository.set_status(True)
            text = "Toutes vos alarmes sont désormais actives."
            return query.edit_message_text(text)

        if status == BotData.OFF.value:
            self.repository.set_status(False)
            text = "Toutes vos alarmes sont désormais désactivées."
            return query.edit_message_text(text)

        query.edit_message_text("Un problème technique est arrivé.")


    def _register_commands(self, update):
        update.dispatcher.add_handler(CommandHandler('alarm', self._alarm_status))
        update.dispatcher.add_handler(CallbackQueryHandler(self._set_alarm_status))


def alarm_status_bot_factory(telegram_updater: Updater) -> AlarmStatusBot:
    repository = AlarmStatusRepository()
    return AlarmStatusBot(repository, telegram_updater)
