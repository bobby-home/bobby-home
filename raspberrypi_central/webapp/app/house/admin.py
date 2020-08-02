from django.contrib import admin
from house.models import House, Location, TelegramBot, TelegramBotChatId

# Register your models here.
admin.site.register(House)
admin.site.register(Location)
admin.site.register(TelegramBot)
admin.site.register(TelegramBotChatId)
