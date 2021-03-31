import logging
import os
import traceback
import logging_loki
from multiprocessing import Queue

LOKI_HOSTNAME = os.environ['LOKI_HOSTNAME']
LOKI_PORT = os.environ['LOKI_PORT']

handler = logging_loki.LokiQueueHandler(
    Queue(-1),
    url=f'http://{LOKI_HOSTNAME}:{LOKI_PORT}/loki/api/v1/push',
    # tags={'container_name': 'dumb_camera'},
    # auth=("username", "password"),
    version="1",
)

logger = logging.getLogger('dumb_camera')
logger.addHandler(handler)

device_id = None

# sys.excepthook = my_exception_hook does not work for this case (the loki request is not sent).
try:
    from service_manager.run_dumb_camera import RunDumbCamera
    from mqtt.mqtt_manage_runnable import MqttManageRunnable
    from thread.thread_manager import ThreadManager
    from mqtt.mqtt_client import get_mqtt

    device_id = os.environ['DEVICE_ID']

    camera_mqtt_client = get_mqtt(f"{device_id}-dumb-camera-manager")

    camera_manager = ThreadManager(RunDumbCamera())

    MqttManageRunnable(device_id, 'camera', camera_mqtt_client, camera_manager, status_json=True)

    camera_mqtt_client.client.loop_forever()
except BaseException as e:
    tags = {}
    if device_id:
        tags['device'] = device_id

    logger.error(traceback.format_exc(),
                 extra={'tags': tags})

    raise
