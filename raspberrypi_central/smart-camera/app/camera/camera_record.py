import multiprocessing as mp
from abc import ABC, abstractmethod
import re
from typing import Tuple, Optional


class CameraRecorder(ABC):

    @abstractmethod
    def start_recording(self, video_ref: str) -> None:
        pass

    @abstractmethod
    def stop_recording(self) -> None:
        pass


class CameraRecord(CameraRecorder):
    SPLIT_RECORDING_TASK = 'split_recording'

    @staticmethod
    def is_split_recording_task(record_event_ref: str) -> Optional[str]:
        match = re.search(f'^{CameraRecord.SPLIT_RECORDING_TASK}/', record_event_ref)
        if match:
            video_ref = record_event_ref[:match.start()] + record_event_ref[match.end():]
            return video_ref

        return None

    def __init__(self, record_event: mp.Event, queue: mp.Queue):
        self.queue = queue
        self.record_event = record_event

    def stop_recording(self):
        # clear doesn't throw if the event is not True. It turns it to False even if it's already False.
        self.record_event.clear()

    def start_recording(self, video_ref):
        self.record_event.set()
        self.queue.put_nowait(video_ref)

    def split_recording(self, video_ref):
        if self.record_event.is_set():
            self.queue.put(f'{CameraRecord.SPLIT_RECORDING_TASK}/{video_ref}')
