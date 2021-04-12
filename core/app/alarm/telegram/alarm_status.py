import os, sys
from typing import List

import django
from telegram.ext.callbackcontext import CallbackContext
from alarm.business.alarm_status import alarm_statuses_changed
from utils.telegram.restrict import restricted

sys.path.append('/usr/src/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hello_django.settings')
django.setup()

from enum import Enum
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from alarm.models import AlarmStatus
from notification.models import UserTelegramBotChatId
from django.db import transaction
from django.utils.translation import gettext as _
from telegram import Update
from alarm.telegram import textes


class BotData(Enum):
    OFF = 'off'
    ON = 'on'
    CHOOSE = 'choose' # the user choose which alarm to manage.


class AlarmStatusRepository:
    def __init__(self):
        pass

    @staticmethod
    def set_status(new_status: bool):
        """
        When the user decide to change the status of the alarm,
        the system do it for every device (alarm status).
        """
        alarm_statuses: List[AlarmStatus] = AlarmStatus.objects.all()

        for status in alarm_statuses:
            status: AlarmStatus
            status.running = new_status

        AlarmStatus.objects.bulk_update(alarm_statuses, ['running'])
        alarm_statuses_changed(alarm_statuses, force=True)

    @property
    def statuses(self):
        statuses = AlarmStatus.objects.all()

        return statuses


class AlarmStatusBot:
    def __init__(self, repository: AlarmStatusRepository, telegram_updater: Updater):
        self.repository = repository
        self._register_commands(telegram_updater)

    @restricted
    def _alarm_status(self, update: Update, context):
        statuses = self.repository.statuses

        texts = [textes.alarm_status(status) for status in statuses]

        keyboard = [
            InlineKeyboardButton(textes.OFF_ALL, callback_data=BotData.OFF.value),
            InlineKeyboardButton(textes.ON_ALL, callback_data=BotData.ON.value)
        ]
        
        if len(statuses) > 1:
            keyboard.append(
                InlineKeyboardButton(textes.CHOOSE, callback_data=BotData.CHOOSE.value)
            )

        if len(texts) > 0:
            markup = InlineKeyboardMarkup.from_column(keyboard)
            update.message.reply_text('\n'.join(texts), reply_markup=markup)
        else:
            update.message.reply_text(textes.NO_ALARM)

    def _set_alarm_status(self, update: Update, _c: CallbackContext):
        query = update.callback_query
        status = query.data
        
        if status == BotData.ON.value:
            self.repository.set_status(True)
            text = textes.ALL_ON 
            return query.edit_message_text(text)

        if status == BotData.OFF.value:
            self.repository.set_status(False)
            text = textes.ALL_OFF
            return query.edit_message_text(text)

        if status == BotData.CHOOSE.value:
            statuses = self.repository.statuses
            
            keyboard = [InlineKeyboardButton(textes.change_alarm_status(status), callback_data=status.pk) for status in statuses]
            query.answer()

            # one button per row, only one column.
            markup = InlineKeyboardMarkup.from_column(keyboard)
            return query.edit_message_text(textes.CHOOSE_EXPLAIN, reply_markup=markup)

        if status.isdigit():
            status_pk = int(status)
            with transaction.atomic():
                db_status = AlarmStatus.objects.select_for_update().get(pk=status_pk)
                db_status.running =not db_status.running
                db_status.save()
                
                text = textes.alarm_status_changed(db_status)
                transaction.on_commit(lambda: query.edit_message_text(text))
            
            return
        
        query.edit_message_text(textes.WRONG)


    def _register_commands(self, update: Updater):
        update.dispatcher.add_handler(CommandHandler('alarm', self._alarm_status))
        update.dispatcher.add_handler(CallbackQueryHandler(self._set_alarm_status))


def alarm_status_bot_factory(telegram_updater: Updater) -> AlarmStatusBot:
    repository = AlarmStatusRepository()
    return AlarmStatusBot(repository, telegram_updater)
