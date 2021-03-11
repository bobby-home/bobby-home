from multiprocessing import Process

from loggers import LOGGER
from service_manager.runnable import Runnable
from service_manager.service_manager import RunService


class ThreadManager(Runnable):

    def __init__(self, run_service: RunService):
        self._is_running = False
        self._process = None
        self._run_service = run_service

    def _start_process(self, data):
        if self._process is None:
            """
            Here we call a `run` function.
            But when we `_stop_process` we don't call any methods.
            So if the Process has to release something before we end it, we can't.
            TODO: Please see issue #79
            """
            self._run_service.prepare_run(data)

            self._process = Process(target=self._run_service.run)
            self._process.start()
            LOGGER.info(f'Start {self._run_service}.')

        elif self._run_service.is_restart_necessary(data):
            LOGGER.info(f'Restart {self._run_service} because restart is necessary (configuration data changed)')
            self._stop_process()
            self._start_process(data)
        else:
            LOGGER.info(f"Dit not restart because the configuration remains the same for {self._run_service}")

    def _stop_process(self):
        if self._process:
            LOGGER.info(f'Stop process for {self._run_service}')
            self._process.terminate()
            self._process = None

    @property
    def running(self):
        return self._is_running

    def run(self, _device_id: str, status: bool, data=None) -> None:
        self._is_running = status

        if status is True:
            self._start_process(data)
        elif status is False:
            self._stop_process()
