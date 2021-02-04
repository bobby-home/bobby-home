from django.contrib import admin
from house.models import House, Location, TelegramBot, TelegramBotStart

admin.site.register(House)
admin.site.register(Location)
admin.site.register(TelegramBot)
admin.site.register(TelegramBotStart)
