import os, sys
from typing import List

import django
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
from django.utils.translation import gettext as _
from telegram import Update


class BotData(Enum):
    OFF = 'off'
    ON = 'on'

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
        # chat_id = update.message.chat.id
        statuses = self.repository.statuses

        texts = []
        for status in statuses:
            running = status.running

            if running is True:
                text = _('Your alarm %(alarm)s is on.') % {'alarm': status.device.location}
                texts.append(text)
            elif running is False:
                text = _('Your alarm %(alarm)s is off.') % {'alarm': status.device.location}
                texts.append(text)

        keyboard = [
            InlineKeyboardButton(_('Deactivate all'), callback_data=BotData.OFF.value),
            InlineKeyboardButton(_('Activate all'), callback_data=BotData.ON.value)]

        if len(texts) > 0:
            update.message.reply_text('\n'.join(texts), reply_markup=InlineKeyboardMarkup([keyboard]))
        else:
            update.message.reply_text('No alarm configured.')

    def _set_alarm_status(self, update: Update, context):
        query = update.callback_query
        status = query.data

        if status == BotData.ON.value:
            self.repository.set_status(True)
            text = _('All of your alarms are on.')
            return query.edit_message_text(text)

        if status == BotData.OFF.value:
            self.repository.set_status(False)
            text = _('All of your alarms are off.')
            return query.edit_message_text(text)

        query.edit_message_text(_('Something went wrong.'))


    def _register_commands(self, update: Updater):
        update.dispatcher.add_handler(CommandHandler('alarm', self._alarm_status))
        update.dispatcher.add_handler(CallbackQueryHandler(self._set_alarm_status))


def alarm_status_bot_factory(telegram_updater: Updater) -> AlarmStatusBot:
    repository = AlarmStatusRepository()
    return AlarmStatusBot(repository, telegram_updater)
