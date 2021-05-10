from automation.models import ActionMqttPublish, Automation, MqttClient
from faker import Factory
import factory


faker = Factory.create()


class MqttClientFactory(factory.DjangoModelFactory):
    class Meta:
        model = MqttClient
    
    # can't make it works host = faker.providers.internet.ar_AA.Provider.ipv4()
    host = 'mqtt_broker'
    username = factory.Sequence(lambda n: "mqtt_user_%03d" % n)


class AutomationFactory(factory.DjangoModelFactory):
    class Meta:
        model = Automation

    trigger_name = factory.Sequence(lambda n: "Trigger name %03d" % n)
    title = factory.Faker('sentence', nb_words=5)
    description = factory.Faker('sentence', nb_words=20)

class ActionMqttPublishFactory(factory.DjangoModelFactory):
    class Meta:
        model = ActionMqttPublish

    topic = factory.Sequence(lambda n: "/some/mqtt/topic/%03d" % n)
