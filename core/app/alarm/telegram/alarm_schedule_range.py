from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    Filters,
    CallbackContext
)
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup


CONFIRMATION = range(1)


class AlarmScheduleRangeBot():
    def __init__(self, telegram_updater: Updater):
        self._register_commands(telegram_updater)

    def _schedule_range_handler(self, update: Update, _c: CallbackContext):
        reply_keyboard = [['Confirm', 'Cancel']]
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

        update.message.reply_text(
            "As you are leaving your home, do you want to turn on all of your alarms and freeze your schedules?",
            reply_markup=reply_markup
        )

        return CONFIRMATION

    def _confirm(self, update: Update, c: CallbackContext):
        text = update.message.text.lower()

        if 'confirm' in text:
            update.message.reply_text("Ok, your alarm is running and won't be interrupted by schedules")
        elif 'cancel' in text:
            update.message.reply_text("Ok, I don't do anything.")
        
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
                CONFIRMATION: [MessageHandler(Filters.text, self._confirm)]
            },
            fallbacks=[CommandHandler('cancel', self._cancel)]
        )

        update.dispatcher.add_handler(conv_handler)

def alarm_schedule_range_bot_factory(telegram_updater: Updater) -> AlarmScheduleRangeBot:
    return AlarmScheduleRangeBot(telegram_updater)
