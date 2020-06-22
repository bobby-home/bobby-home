from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from urllib.parse import urljoin
import requests
import os


class AlarmStatusRepository:
    def __init__(self, api_url: str, get_status_endpoint: str):
        self.url = urljoin(api_url, get_status_endpoint)

    def set_status(self, status: bool):
        r = requests.post(self.url, data={'running': status})
        r.raise_for_status()

    @property
    def is_on(self):
        r = requests.get(self.url)
        r.raise_for_status()
        data = r.json()

        return data[0]['running']


class AlarmStatusBot:
    def __init__(self, repository: AlarmStatusRepository, telegram_updater: Updater):
        self.repository = repository
        self._register_commands(telegram_updater)
    
    def _alarm_status(self, update, context):
        status = self.repository.is_on

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
    repository = AlarmStatusRepository(os.environ['API_URL'], os.environ['API_GET_STATUS_ENDPOINT'])
    return AlarmStatusBot(repository, telegram_updater)
