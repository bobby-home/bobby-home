from notification.models import UserSetting
from notification.out.free_carrier_messaging import FreeCarrierMessaging
from notification.out.telegram_messaging import TelegramMessaging


class Messaging:
    def __init__(self, telegram: TelegramMessaging, free_carrier: FreeCarrierMessaging):
        self.telegram_messaging = telegram
        self.free_carrier_messaging = free_carrier


    def send_message(self, message = None, picture_path = None):
        if message is None and picture_path is None:
            raise ValueError(f'message and picture_path not set. At least one of them is required to send a message.')

        """
        mapping between field: function to call.
        Fields are the fields defined in UserSetting model.
        """
        configurations = {
            'free_carrier': self.free_carrier_messaging.send_message,
            'telegram_chat': self.telegram_messaging.send_message
        }

        user_settings = UserSetting.objects.all()
        for user_setting in user_settings:
            for field, function in configurations.items():
                user_setting_conf = getattr(user_setting, field)

                if user_setting_conf:
                    function(*[user_setting_conf, message, picture_path])


def messaging_factory() -> Messaging:
    return Messaging(TelegramMessaging(), FreeCarrierMessaging())
