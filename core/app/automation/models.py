from automation.actions import Triggers
from django.db import models
from django.utils.translation import gettext_lazy as _
from utils.django.models import ChoiceArrayField


class Automation(models.Model):
    trigger_name = ChoiceArrayField(
            models.CharField(
                max_length=100,
                choices=Triggers.choices()),
            help_text=_('Any of these trigger names will trigger this automation to run.')
        )

    title = models.CharField(max_length=100)
    description = models.CharField(max_length=400, default=None, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return _('%(title)s automation triggered by %(trigger_name)s.') % self.__dict__


class MqttClient(models.Model):
    host = models.CharField(max_length=100, help_text=_('The hostname or IP address of the remote broker.'))
    port = models.PositiveSmallIntegerField(default=1883, help_text=_('The network port of the server host to connect to.'))

    username = models.CharField(max_length=50)
    password = models.CharField(max_length=100, default=None, blank=True, null=True)

    def __str__(self):
        return _('Mqtt client for host %(host)s.') % self.__dict__ 


class ActionMqttPublish(models.Model):
    topic = models.CharField(max_length=100)
    payload_json = models.JSONField(default=None, blank=True, null=True)
    retain = models.BooleanField(default=False)
    qos = models.PositiveSmallIntegerField(default=1, help_text=_('The quality of service level to use.'))

    automation = models.ForeignKey(Automation, related_name='actions_mqtt_publish', on_delete=models.PROTECT)
    mqtt_client = models.ForeignKey(MqttClient, on_delete=models.PROTECT)
    last_run_datetime = models.DateTimeField(
            default=None,
            blank=True,
            null=True,
            editable=False,
            help_text=_('Datetime that the automation last triggered the action to run. '))

    def __str__(self):
        return _('Publish to %(topic)s') % self.__dict__
