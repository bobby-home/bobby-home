import paho.mqtt.client as mqtt
import os
import ssl
from camera.camera_manager import CameraManager


class MqttCamera():
    """
    This class synchronise the alarm status with MQTT.
    If we receive a message to switch on/off the alarm, we're doing it here.
    """
    def __init__(self, camera_manager: CameraManager):
        self._camera_manager = camera_manager
        self._mqtt_client = self._mqtt_connect()

    def _mqtt_on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        client.subscribe(os.environ['MQTT_ALARM_CAMERA_TOPIC'])

    def _mqtt_on_message(self, client, userdata, msg):
        message = msg.payload.decode()

        print(f"I've received a message: {message}")

        if message == 'True':
            print('waking up the alarm system.')
            self._camera_manager.running = True
        elif message == 'False':
            print('turning off the alarm')
            self._camera_manager.running = False

    def _mqtt_connect(self) -> mqtt.Client:
        print('mqtt connection')
        client = mqtt.Client()
        client.username_pw_set(os.environ['MQTT_USER'], os.environ['MQTT_PASSWORD'])

        client.connect(os.environ['MQTT_HOSTNAME'], int(os.environ['MQTT_PORT']), keepalive=60)

        client.on_connect = self._mqtt_on_connect
        client.on_message = self._mqtt_on_message

        client.loop_forever()
        return client

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

