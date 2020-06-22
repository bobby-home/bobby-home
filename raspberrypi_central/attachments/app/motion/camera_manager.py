# Prototype for mx tech house
from multiprocessing import Process
from .camera_factory import camera_factory
import time


class CameraManager:

    def __init__(self, camera_factory):
        self._is_running = False
        self._process = None
        self.camera_factory = camera_factory

    def _start_process(self):
        if (self._process is None):
            instance = camera_factory()
            self._process = Process(target=instance.start)
            self._process.start()
    
    def _stop_process(self):
        if (self._process):
            self._process.terminate()
            self._process = None

    @property
    def running(self):
        return self._is_running
    
    @running.setter
    def running(self, running):
        print('running: ', running)
        self._is_running = running
        if running is True:
            self._start_process()
        elif running is False:
            self._stop_process()
