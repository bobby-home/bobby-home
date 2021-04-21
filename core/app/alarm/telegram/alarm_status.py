import os, sys
from typing import List

import django
sys.path.append('/usr/src/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hello_django.settings')
django.setup()

from enum import Enum
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import telegram.constants as telegram_constants
from telegram.ext.callbackcontext import CallbackContext
from alarm.use_cases.alarm_status import AlarmChangeStatus, alarm_statuses_changed, change_status
from utils.telegram.restrict import restricted
from alarm.models import AlarmStatus
from notification.models import UserTelegramBotChatId
from django.db import transaction
from django.utils.translation import gettext as _
from telegram import Update
from alarm.telegram import texts


class BotData(Enum):
    OFF = 'off'
    ON = 'on'
    CHOOSE = 'choose' # the user choose which alarm to manage.


class AlarmStatusBot:
    def __init__(self, telegram_updater: Updater):
        self._register_commands(telegram_updater)

    @restricted
    def _alarm_status(self, update: Update, _context: CallbackContext):
        statuses = AlarmStatus.objects.all()

        if len(statuses) == 0:
            return update.message.reply_text(texts.NO_ALARM)

        texts_alarm_status = [texts.alarm_status(status) for status in statuses]

        keyboard = [
            InlineKeyboardButton(texts.OFF_ALL, callback_data=BotData.OFF.value),
            InlineKeyboardButton(texts.ON_ALL, callback_data=BotData.ON.value)
        ]
        
        if len(statuses) > 1:
            keyboard.append(
                InlineKeyboardButton(texts.CHOOSE, callback_data=BotData.CHOOSE.value)
            )

        markup = InlineKeyboardMarkup.from_column(keyboard)
        update.message.reply_text('\n'.join(texts_alarm_status), reply_markup=markup, parse_mode=telegram_constants.PARSEMODE_HTML)

    def _set_alarm_status(self, update: Update, _c: CallbackContext):
        query = update.callback_query
        status = query.data
        
        if status == BotData.ON.value:
            AlarmChangeStatus().all_change_status(True, force=True)
            text = texts.ALL_ON 
            return query.edit_message_text(text)

        if status == BotData.OFF.value:
            AlarmChangeStatus().all_change_status(False, force=True)
            text = texts.ALL_OFF
            return query.edit_message_text(text)

        if status == BotData.CHOOSE.value:
            statuses = AlarmStatus.objects.all()
            
            keyboard = [InlineKeyboardButton(texts.change_alarm_status(status), callback_data=status.pk) for status in statuses]
            query.answer()

            # one button per row, only one column.
            markup = InlineKeyboardMarkup.from_column(keyboard)
            return query.edit_message_text(texts.CHOOSE_EXPLAIN, reply_markup=markup) 

        if status.isdigit():
            status_pk = int(status)
            
            """
            Why not use an update query like "NOT running"?
            Because I need to get the running information to display it to the user.
            1) telegram bot sends buttons to deactivate/activate a given alarm.
            2) the user click. But during the time lapsed the status could have been updated by other process.
            Thanks to this, the user knows the real updated value, which is important.
            """
            db_status = AlarmChangeStatus().reverse_status(status_pk, force=True)
            text = texts.alarm_status_changed(db_status)
            query.edit_message_text(text)

            return
        
        query.edit_message_text(texts.WRONG)


    def _register_commands(self, update: Updater) -> None:
        update.dispatcher.add_handler(CommandHandler('alarm', self._alarm_status))
        update.dispatcher.add_handler(CallbackQueryHandler(self._set_alarm_status))


def alarm_status_bot_factory(telegram_updater: Updater) -> AlarmStatusBot:
    return AlarmStatusBot(telegram_updater)
