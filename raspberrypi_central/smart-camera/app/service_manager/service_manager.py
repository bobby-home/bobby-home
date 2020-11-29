from abc import ABC, abstractmethod


class RunService(ABC):

    @abstractmethod
    def prepare_run(self, data = None):
        pass

    @abstractmethod
    def run(self, *args) -> None:
        pass

    @abstractmethod
    def is_restart_necessary(self, data) -> bool:
        pass

    @abstractmethod
    def stop(self, *args) -> None:
        pass
