from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

class AlarmStatusRepository:
    def __init__(self):
        pass

    @property
    def is_on(self):
        # @TODO make HTTP request to the rest api
        return True


class AlarmStatusBot:
    def __init__(self, repository: AlarmStatusRepository, telegram_updater: Updater):
        self.repository = repository
        self._register_commands(telegram_updater)
    
    def _alarm_status(self, update, context):
        status = self.repository.is_on
        print('_alarm_status called, alarm status is ', status)

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
            text = "Votre alarme est désormais active."
        elif status == "off":
            text = "Votre alarme est désormais désactivée"
        

        query.edit_message_text(text)

    
    def _register_commands(self, update):
        print('register commands')
        update.dispatcher.add_handler(CommandHandler('status_alarm', self._alarm_status))
        update.dispatcher.add_handler(CallbackQueryHandler(self._set_alarm_status))

def alarm_status_bot_factory(telegram_updater: Updater) -> AlarmStatusBot:
    repository = AlarmStatusRepository()
    return AlarmStatusBot(repository, telegram_updater)
