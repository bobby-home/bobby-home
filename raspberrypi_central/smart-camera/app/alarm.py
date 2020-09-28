import os

from camera.camera_roi import RectangleROI, ROICamera
from mqtt.mqtt_status_manage_thread import mqtt_status_manage_thread_factory
from thread.thread_manager import ThreadManager
from camera.camera_factory import camera_factory
from camera.play_sound import PlaySound
from mqtt.mqtt_client import get_mqtt_client
from camera.videostream import VideoStream


device_id = os.environ['DEVICE_ID']

mqtt_client = get_mqtt_client(f"{device_id}-rpi4-alarm-motion")


def run(*args, **kwargs):
    camera_roi = None
    if args:
        args = args[0]
        rectangle_roi = RectangleROI(x=args['x'], y=args['y'], w=args['w'], h=args['h'], definition_width=args['definition_width'], definition_height=args['definition_height'])
        camera_roi = ROICamera(rectangle_roi)

    camera = camera_factory(get_mqtt_client, camera_roi)

    camera_width = 640
    camera_height = 480

    # TODO: see issue #78
    VideoStream(camera.process_frame, resolution=(
        camera_width, camera_height), framerate=1, usePiCamera=False)


manager = ThreadManager(run)
mqtt_status_manage_thread_factory(device_id, 'camera', mqtt_client, manager, status_json=True)


def run_sound(*args, **kwargs):
    PlaySound()


sound_manager = ThreadManager(run_sound)
mqtt_status_manage_thread_factory(device_id, 'speaker', mqtt_client, sound_manager)

mqtt_client.loop_forever()
