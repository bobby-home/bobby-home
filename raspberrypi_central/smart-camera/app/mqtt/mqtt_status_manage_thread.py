import struct
import json
from typing import Optional

from loggers import LOGGER
from mqtt.mqtt_client import MqttClient
from service_manager.runnable import Runnable


class MqttStatusManageThread:
    """
    This class synchronise the alarm status with MQTT.
    If we receive a message to switch on/off the alarm, we're doing it here.
    """
    def __init__(self, device_id: Optional[str], service_name: str, mqtt_client: MqttClient, thread_manager: Runnable, status_json=False):
        self._thread_manager = thread_manager
        self._service_name = service_name
        self._status_json = status_json

        self._device_id = device_id

        if device_id:
            mqtt_topic = f'status/{service_name}/{device_id}'
            mqtt_client.connect_keep_status(service_name, device_id)
        else:
            # generic, connect for every devices.
            mqtt_topic = f'status/{service_name}/+'
            mqtt_client.connect()
            mqtt_client.client.loop_start()

        mqtt_client.client.subscribe(mqtt_topic, qos=1)
        mqtt_client.client.message_callback_add(mqtt_topic, self._switch_on_or_off)

    @staticmethod
    def _get_device_id_from_topic(topic: str) -> str:
        split = topic.split('/')

        return split[2]

    def _switch_on_or_off(self, client, userdata, msg) -> None:
        device_id = self._device_id or self._get_device_id_from_topic(msg.topic)

        """
        MQTT callback to decide to call on/off based on received mqtt payload.

        Parameters
        ----------
        client
        userdata
        msg

        Returns
        -------
        None
        """
        message = msg.payload
        data = None

        if self._status_json is True:
            try:
                message = json.loads(message)
            except json.JSONDecodeError:
                LOGGER.critical(f'Cannot decode json {message} for service {self._service_name}')
                return

            status = message['status']

            if 'data' in message:
                data = message['data']

        else:
            try:
                # unpack always return a tuple (False,) or (True,) because we pack only one value.
                status = struct.unpack('?', message)
                if len(status) != 1:
                    raise TypeError(f'{message} should be of size one when unpacked but got {status}')
                else:
                    status = status[0]
            except (struct.error, TypeError):
                LOGGER.critical(f'Cannot decode binary {message} for service {self._service_name}')
                return

        LOGGER.info(f'Receive status {status} for {self._service_name} with data {data}')

        if status:
            self._thread_manager.run(device_id, True, data=data)
        else:
            self._thread_manager.run(device_id, False)


def mqtt_status_manage_thread_factory(*args, **kwargs):
    return MqttStatusManageThread(*args, **kwargs)

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
