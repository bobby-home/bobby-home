from abc import ABC, abstractmethod


class RunService(ABC):

    @abstractmethod
    def prepare_run(self, *args):
        pass

    @abstractmethod
    def run(self, *args) -> None:
        pass

    def is_restart_necessary(self, *args) -> bool:
        pass

    @abstractmethod
    def stop(self, *args) -> None:
        pass
