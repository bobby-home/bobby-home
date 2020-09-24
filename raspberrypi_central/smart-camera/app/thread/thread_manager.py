from multiprocessing import Process
from typing import Callable
from functools import partial


class ThreadManager:

    def __init__(self, to_run: Callable[[None], None]):
        self._is_running = False
        self._process = None
        self._to_run = to_run

    def _start_process(self, *args, **kwargs):
        if (self._process is None):
            """
            Here we call a `run` function.
            But when we `_stop_process` we don't call any methods.
            So if the Process has to release something before we end it, we can't.
            TODO: Please see issue #79
            """
            to_run = partial(self._to_run, *args, **kwargs)

            self._process = Process(target=self._to_run)
            self._process.start()

    def _stop_process(self):
        if (self._process):
            self._process.terminate()
            self._process = None

    @property
    def running(self):
        return self._is_running

    def run(self, status: bool, *args, **kwargs):
        self._is_running = status
        if status is True:
            self._start_process(*args, **kwargs)
        elif status is False:
            self._stop_process()
