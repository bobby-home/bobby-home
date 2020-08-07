import paho.mqtt.client as mqtt
import ssl
from camera.camera_manager import CameraManager
import json


class MqttStatusCamera():
    """
    This class synchronise the alarm status with MQTT.
    If we receive a message to switch on/off the alarm, we're doing it here.
    """
    def __init__(self, mqtt_client, camera_manager: CameraManager, MQTT_ALARM_CAMERA_TOPIC: str):
        self._camera_manager = camera_manager

        mqtt_client.subscribe(MQTT_ALARM_CAMERA_TOPIC)
        mqtt_client.message_callback_add(MQTT_ALARM_CAMERA_TOPIC, self._switch_on_or_off_alarm)

        mqtt_client.publish('ask/status/alarm', payload=True)

    def _switch_on_or_off_alarm(self, client, userdata, msg):
        message = msg.payload.decode()

        print(f"I've received a message: {message}")

        if message == 'True':
            print('waking up the alarm system.')
            self._camera_manager.running = True
        elif message == 'False':
            print('turning off the alarm')
            self._camera_manager.running = False
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

