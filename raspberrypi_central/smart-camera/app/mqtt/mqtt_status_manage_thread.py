import struct
from thread.thread_manager import ThreadManager
import logging


class MqttStatusManageThread():
    """
    This class synchronise the alarm status with MQTT.
    If we receive a message to switch on/off the alarm, we're doing it here.
    """
    def __init__(self, logger: logging, device_id: str, service_name: str, mqtt_client, thread_manager: ThreadManager):
        self._logger = logger
        self._thread_manager = thread_manager
        self._service_name = service_name

        mqtt_topic = f'status/{service_name}/{device_id}'

        mqtt_client.subscribe(mqtt_topic)
        mqtt_client.message_callback_add(mqtt_topic, self._switch_on_or_off)

        mqtt_client.publish(f'connected/{service_name}/{device_id}', payload=struct.pack('?', True), qos=1, retain=True)
        mqtt_client.will_set(f'connected/{service_name}/{device_id}', payload=struct.pack('?', False), qos=1, retain=True)

    def _switch_on_or_off(self, client, userdata, msg):
        message = msg.payload
        status = struct.unpack('?', message)[0]

        self._logger.info(f'Receive status {status} for {self._service_name}')

        if status:
            self._thread_manager.running = True
        else:
            self._thread_manager.running = False


def mqtt_status_manage_thread_factory(*args, **kargs):
    return MqttStatusManageThread(logging, *args, **kargs)

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
