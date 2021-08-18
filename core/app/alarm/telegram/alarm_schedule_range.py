from enum import Enum
from alarm.business.alarm_range_schedule import get_current_range_schedule
from alarm.use_cases.alarm_range_schedule import create_alarm_range_schedule, stop_current_alarm_range_schedule
from django.utils import timezone
from alarm.models import AlarmScheduleDateRange
from alarm.telegram import texts
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    Filters,
    CallbackContext,
    CallbackQueryHandler
)
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup


CONFIRMATION = range(1)

class BotData(Enum):
    ABSENT_MODE = 'on_absence'
    REMOVE_ABSENT_MODE = 'off_absence'
    CANCEL = 'cancel_absence' 


class AlarmScheduleRangeBot():
    def __init__(self, telegram_updater: Updater):
        self._register_commands(telegram_updater)

    def _schedule_range_handler(self, update: Update, _c: CallbackContext):
        schedule = get_current_range_schedule()
        
        buttons = []

        if schedule is not None:
            text = texts.EXPLAIN_REMOVE_ABSENT_MODE
            buttons.append(
                [InlineKeyboardButton(texts.REMOVE_ABSENT_MODE, callback_data=BotData.REMOVE_ABSENT_MODE.value)]
            )
        else:
            text = texts.EXPLAIN_ABSENT_MODE
            buttons.append(
                [InlineKeyboardButton(texts.ABSENT_MODE, callback_data=BotData.ABSENT_MODE.value)],
            )

        buttons.append(
            [InlineKeyboardButton(texts.CANCEL, callback_data=BotData.CANCEL.value)],
        )
        reply_markup = InlineKeyboardMarkup(buttons)

        update.message.reply_text(
            text,
            reply_markup=reply_markup
        )

        return CONFIRMATION

    def _confirm(self, update: Update, c: CallbackContext):
        query = update.callback_query

        if BotData.ABSENT_MODE.value in query.data:
            schedule = AlarmScheduleDateRange(datetime_start=timezone.now())
            create_alarm_range_schedule(schedule)
            query.edit_message_text(texts.OK_ABSENT_MODE)
        elif BotData.REMOVE_ABSENT_MODE.value in query.data:
            schedule = stop_current_alarm_range_schedule()
            if schedule:
                query.edit_message_text(texts.OK_REMOVE_ABSENT_MODE)
            else:
                query.edit_message_text(texts.KO_REMOVE_ABSENT_MODE)
        elif BotData.CANCEL.value in query.data:
            query.edit_message_text(texts.OK_CANCEL)
        
        return ConversationHandler.END

    def _cancel(self, update: Update, _c: CallbackContext) -> int:
        update.message.reply_text(
            texts.OK_CANCEL, reply_markup=ReplyKeyboardRemove()
        )
    
        return ConversationHandler.END

    def _register_commands(self, update: Updater) -> None:
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('absence', self._schedule_range_handler)],
            states={
                CONFIRMATION: [CallbackQueryHandler(self._confirm)]
            },
            fallbacks=[CommandHandler('cancel', self._cancel)]
        )

        update.dispatcher.add_handler(conv_handler)

def alarm_schedule_range_bot_factory(telegram_updater: Updater) -> AlarmScheduleRangeBot:
    return AlarmScheduleRangeBot(telegram_updater)
