import io
import os

from camera.camera_factory import camera_factory
from camera.dumb_camera import DumbCamera
from camera_analyze.all_analyzer import NoAnalyzer
from camera_analyze.camera_analyzer import Consideration
from mqtt.mqtt_client import get_mqtt


def extract_data_from_topic(topic: str):
    split = topic.split('/')

    return {
        'device_id': split[2]
    }

device_id = os.environ['DEVICE_ID']

mqtt_client = get_mqtt(f'{device_id}-analyzer')
mqtt_client.connect()

consideration = Consideration(type='full')
analyzer = NoAnalyzer(consideration)

camera = camera_factory(get_mqtt, analyzer)
camera.start()

def on_picture(client, userdata, message):
    data = extract_data_from_topic(message.topic)
    from_device_id = data['device_id']

    image = io.BytesIO(message.payload)
    print(f'on picture {type(image)} {image}')

    camera.process_frame(image, from_device_id)

mqtt_client.client.subscribe(f'{DumbCamera.PICTURE_TOPIC}/+', qos=1)
mqtt_client.client.message_callback_add(f'{DumbCamera.PICTURE_TOPIC}/+', on_picture)

mqtt_client.client.loop_forever()
