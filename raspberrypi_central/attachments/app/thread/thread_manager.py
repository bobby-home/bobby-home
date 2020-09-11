from multiprocessing import Process


class ThreadManager:

    def __init__(self, instance_factory):
        self._is_running = False
        self._process = None
        self.instance = instance_factory()

    def _start_process(self):
        if (self._process is None):
            print('Launch object detection thread')
            self._process = Process(target=self.instance.start)
            self._process.start()

    def _stop_process(self):
        if (self._process):
            print('Stop object detection thread')
            self._process.terminate()
            self._process = None

    @property
    def running(self):
        return self._is_running

    @running.setter
    def running(self, running):
        self._is_running = running
        if running is True:
            self._start_process()
        elif running is False:
            self._stop_process()
