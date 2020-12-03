import factory
from faker import Factory

from notification.models import UserSetting, UserFreeCarrier, UserTelegramBotChatId

faker = Factory.create()

# class AlertFactory(factory.DjangoModelFactory):
#     class Meta:
#         model = SystemNotification
#
#     @factory.post_generation
#     def devices(self, create, extracted, **kwargs):
#         if not create:
#             # Simple build, do nothing.
#             return
#
#         if extracted:
#             # A list of groups were passed in, use them
#             for device in extracted:
#                 self.devices.add(device)

class UserSettingFactory(factory.DjangoModelFactory):
    class Meta:
        model = UserSetting


class UserFreeCarrierFactory(factory.DjangoModelFactory):
    class Meta:
        model = UserFreeCarrier


class UserTelegramBotChatIdFactory(factory.DjangoModelFactory):
    class Meta:
        model = UserTelegramBotChatId

