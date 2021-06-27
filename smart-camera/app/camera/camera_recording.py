from datetime import datetime
from typing import Optional

from camera.camera_record import CameraRecorder
from utils.time import is_time_lapsed
from loggers import LOGGER


class NoCameraRecording:
    def start_recording(self, event_ref: str):
        pass

    def split_recording(self, event_ref: str) -> Optional[str]:
        pass
    
    def stop_recording(self, event_ref: str) -> Optional[str]:
        pass

class CameraRecording:
    """
    Class to manage CameraRecording.
    """
    SECONDS_FIRST_MOTION_VIDEO = 10
    SECONDS_MOTION_VIDEO = 60
    VIDEO = 'motion/video'

    def __init__(self, mqtt_client, device_id: str, camera_recorder: CameraRecorder):
        self.mqtt_client = mqtt_client
        self._device_id = device_id
        self._camera_recorder = camera_recorder

        self._first_video_recorded = False
        self._start_recording_time = None
        self._start_recording_split_time = None
        self._record_video_number = 0

    def _publish_video_event(self, video_ref: str) -> None:
        LOGGER.info(f'publish video {video_ref}')
        self.mqtt_client.publish(f'{self.VIDEO}/{self._device_id}/{video_ref}', qos=1)

    def start_recording(self, event_ref: str) -> None:
        LOGGER.info('start recording')

        if self._start_recording_time is None:
            self._start_recording_time = datetime.now()
            self._camera_recorder.start_recording(f'{event_ref}-{self._record_video_number}')

    def _split_recording(self, event_ref: str) -> str:
        """
        Order the CameraRecorder to record in a new file.
        Parameters
        ----------
        event_ref: The event_ref that causes the recording.

        Returns
        -------
        If the records has been split: the video_ref that has been created.
        Otherwise None.
        """
        old_video_ref = f'{event_ref}-{self._record_video_number}'

        self._record_video_number = self._record_video_number +1
        new_video_ref = f'{event_ref}-{self._record_video_number}'

        self._camera_recorder.split_recording(new_video_ref)

        return old_video_ref

    def split_recording(self, event_ref: str) -> None:
        """

        Parameters
        ----------
        event_ref: The event_ref that causes the recording.

        Returns
        -------
        If the records split: the video_ref.
        Otherwise None.
        """
        if self._start_recording_time is None:
            return None

        if self._first_video_recorded is False:
            time_lapsed = is_time_lapsed(self._start_recording_time, CameraRecording.SECONDS_FIRST_MOTION_VIDEO)

            if time_lapsed:
                self._first_video_recorded = True
                self._start_recording_split_time = datetime.now()

                old_video_ref = self._split_recording(event_ref)
                self._publish_video_event(old_video_ref)

                return None
        else:
            time_lapsed = is_time_lapsed(self._start_recording_split_time, CameraRecording.SECONDS_MOTION_VIDEO)
            if time_lapsed:
                self._start_recording_split_time = datetime.now()
                old_video_ref = self._split_recording(event_ref)
                self._publish_video_event(old_video_ref)

    def stop_recording(self, event_ref: str) -> None:
        """

        Parameters
        ----------
        event_ref: The event_ref that causes the recording.

        Returns
        -------
        If the records stop: the video_ref.
        Otherwise None.
        """

        LOGGER.info('stop recording')

        if self._start_recording_time is None:
            return None

        video_ref = f'{event_ref}-{self._record_video_number}'

        self._first_video_recorded = False
        self._start_recording_time = None
        self._start_recording_split_time = None
        self._record_video_number = 0

        self._camera_recorder.stop_recording()
        self._publish_video_event(video_ref)
        
        return video_ref
