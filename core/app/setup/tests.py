from http import HTTPStatus
from notification.models import UserSetting, UserTelegramBotChatId
from account.factories import AccountFactory, DEFAULT_PASSWORD
from django.test import TestCase, Client


class TelegramBotStartViewTestCase(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user = AccountFactory()
        return super().setUp()

    def test_create_user_notification_setting(self):
        self.client.force_login(self.user)

        data = {
            'chat_id': 'coucou',
            'user': self.user.id
        }

        response = self.client.post('/setup/telegram_bot_start', data=data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        chat_ids = UserTelegramBotChatId.objects.all()
        self.assertEqual(len(chat_ids), 1)
        chat_id = chat_ids[0]

        user_settings = UserSetting.objects.all()
        self.assertEqual(len(user_settings), 1)
        
        user_setting = user_settings[0]
        self.assertEqual(user_setting.telegram_chat, chat_id)
        self.assertEqual(user_setting.user, self.user)
