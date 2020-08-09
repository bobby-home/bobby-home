from django.contrib import admin
from notification import models

admin.site.register(models.UserFreeCarrier)
admin.site.register(models.UserTelegramBotChatId)
admin.site.register(models.UserSetting)
