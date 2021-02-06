from notification.models import UserSetting
from notification.out.free_carrier_messaging import FreeCarrierMessaging
from notification.out.telegram_messaging import TelegramMessaging


class Messaging:
    def __init__(self, telegram: TelegramMessaging, free_carrier: FreeCarrierMessaging):
        self.telegram_messaging = telegram
        self.free_carrier_messaging = free_carrier

    def _s(self, method_name: str, *args, **kwargs):
        """
        mapping between field: function to call.
        Fields are the fields defined in UserSetting model.
        """
        configurations = {
            'free_carrier': self.free_carrier_messaging,
            'telegram_chat': self.telegram_messaging
        }

        user_settings = UserSetting.objects.all()
        for user_setting in user_settings:
            for field, class_ref in configurations.items():
                user_setting_conf = getattr(user_setting, field)

                if not user_setting_conf:
                    continue

                func = getattr(class_ref, method_name, None)
                if callable(func):
                    func(*[user_setting_conf], *args, **kwargs)

    def send_message(self, message: str):
        self._s('send_message', message)

    def send_picture(self, picture_path: str):
        self._s('send_picture', picture_path)

    def send_video(self, video_path: str):
        self._s('send_video', video_path)

def messaging_factory() -> Messaging:
    return Messaging(TelegramMessaging(), FreeCarrierMessaging())
