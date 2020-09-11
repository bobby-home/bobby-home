import json
import ssl
import paho.mqtt.client as mqtt
from thread.thread_manager import ThreadManager


class MqttStatusManageThread():
    """
    This class synchronise the alarm status with MQTT.
    If we receive a message to switch on/off the alarm, we're doing it here.
    """
    def __init__(self, mqtt_client, thread_manager: ThreadManager, mqtt_topic: str):
        self._thread_manager = thread_manager

        mqtt_topic = mqtt_topic.lstrip('/')

        mqtt_client.subscribe(mqtt_topic)
        mqtt_client.message_callback_add(mqtt_topic, self._switch_on_or_off)

        mqtt_client.publish(f'ask/{mqtt_topic}', payload=True)

    def _switch_on_or_off(self, client, userdata, msg):
        message = msg.payload.decode()

        print(f"I've received a message: {message}")

        if message == 'True':
            self._thread_manager.running = True
        elif message == 'False':
            self._thread_manager.running = False
        else:
            t = type(message)
            raise ValueError(f'Value ({t}) "{message}" incorrect')

# WIP: work with TLS.
# os.environ['REQUESTS_CA_BUNDLE'] = "/usr/local/share/ca-certificates/ca.cert"
# os.environ['REQUESTS_CA_BUNDLE'] = os.path.join(
#     '/etc/ssl/certs/',
#     'ca-certificates.crt')

# CA = "./ca.crt"
# CERT_FILE = "./test_client.crt"
# KEY_FILE = "./test_client.key"

# client.tls_set(ca_certs=CA, certfile=CERT_FILE,
#                 keyfile=KEY_FILE, tls_version=ssl.PROTOCOL_TLSv1_2)
# client.tls_insecure_set(True)

