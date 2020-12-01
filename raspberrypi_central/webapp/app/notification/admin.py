from django.contrib import admin

from .models.user_notifications import UserFreeCarrier, UserSetting, UserTelegramBotChatId
from .models.notifications import SystemNotification

admin.site.register(UserFreeCarrier)
admin.site.register(UserTelegramBotChatId)
admin.site.register(UserSetting)
admin.site.register(SystemNotification)
