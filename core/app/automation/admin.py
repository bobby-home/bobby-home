from automation.models import ActionMqttPublish, Automation, MqttClient
from django.contrib import admin


admin.site.register(Automation)
admin.site.register(MqttClient)
admin.site.register(ActionMqttPublish)
