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
            text = "If you are back home, you can deactivate absent mode. It will turn off all your alarms and get your schedules back."
            buttons.append(
                [InlineKeyboardButton(texts.REMOVE_ABSENT_MODE, callback_data=BotData.REMOVE_ABSENT_MODE.value)]
            )
        else:
            text = "If you are leaving home, you can activate absent mode. It will turn on all your alarms and disable your schedules."
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
            query.edit_message_text("Ok, your alarm is running and won't be interrupted by schedules")
        elif BotData.REMOVE_ABSENT_MODE.value in query.data:
            schedule = stop_current_alarm_range_schedule()
            if schedule:
                query.edit_message_text("Ok, your alarm is off and your schedules are back. Welcome home!")
            else:
                query.edit_message_text("Bobby is not in absent mode so I cannot remmove this mode.")
        elif BotData.CANCEL.value in query.data:
            query.edit_message_text("Ok, I don't do anything.")
        
        return ConversationHandler.END

    def _cancel(self, update: Update, _c: CallbackContext) -> int:
        update.message.reply_text(
            'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
        )
    
        return ConversationHandler.END

    def _register_commands(self, update: Updater) -> None:
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('mx', self._schedule_range_handler)],
            states={
                CONFIRMATION: [CallbackQueryHandler(self._confirm)]
            },
            fallbacks=[CommandHandler('cancel', self._cancel)]
        )

        update.dispatcher.add_handler(conv_handler)

def alarm_schedule_range_bot_factory(telegram_updater: Updater) -> AlarmScheduleRangeBot:
    return AlarmScheduleRangeBot(telegram_updater)
