import struct

class MqttStatus():
    def __init__(self, mqtt_client):
        self._mqtt_client = mqtt_client

    def publish(self, topic, message: bool):
        status_bytes = struct.pack('?', message)
        print(f'send status: {status_bytes} on {topic}')
        self._mqtt_client.publish(topic, status_bytes, qos=1, retain=True)
