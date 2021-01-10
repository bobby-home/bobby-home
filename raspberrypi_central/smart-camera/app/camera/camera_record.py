import multiprocessing as mp
from abc import ABC, abstractmethod


class CameraRecorder(ABC):

    @abstractmethod
    def start_recording(self, video_ref: str) -> None:
        pass

    @abstractmethod
    def stop_recording(self) -> None:
        pass


class CameraRecord(CameraRecorder):
    def __init__(self, record_event: mp.Event, queue: mp.Queue):
        self.queue = queue
        self.record_event = record_event

    def stop_recording(self):
        self.record_event.clear()

    def start_recording(self, video_ref):
        self.record_event.set()
        self.queue.put(video_ref)
