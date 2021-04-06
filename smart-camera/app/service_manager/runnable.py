from abc import ABC, abstractmethod


class Runnable(ABC):

    @abstractmethod
    def run(self, device_id: str, status: bool, data=None) -> None:
        pass
