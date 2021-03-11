from django.contrib import admin

from notification.models import UserFreeCarrier, UserTelegramBotChatId, UserSetting, SystemNotification

admin.site.register(UserFreeCarrier)
admin.site.register(UserTelegramBotChatId)
admin.site.register(UserSetting)
admin.site.register(SystemNotification)
