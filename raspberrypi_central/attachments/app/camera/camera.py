from camera.motion import DetectMotion
from pathlib import Path 
from sound.sound import Sound

from celery import Celery

class Camera():
    def __init__(self):
        self.celery = Celery('tasks', broker='amqp://admin:mypass@rabbit:5672')

    def start(self):
        DetectMotion(self._presenceCallback)

    def _presenceCallback(self, presence: bool, picture_path: str):
        print(f'presence: {presence}')
        self.celery.send_task('security.camera_motion_detected', kwargs={'device_id': 'some device id here'})
        # s = Sound()
        # s.alarm()
