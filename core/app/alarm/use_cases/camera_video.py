from devices.models import Device
from alarm.use_cases.data import InMotionVideoData
import re
import os
from os import path
import logging

from alarm.business import in_motion
import alarm.utils.video_processing as video_processing
import notification.tasks as notification

LOGGER = logging.getLogger(__name__)

def camera_video(in_data: InMotionVideoData) -> None:
    device = Device.objects.with_type().get(device_id=in_data.device_id)
    device_type = device.device_type.type.lower()

    if "raspberry" in device_type:
        rpi_camera_video_factory().camera_video(in_data)

class RPICameraVideo:
    REMOTE_VIDEO_FOLDER = '/var/lib/camera/media/'
    RAW_EXT = '.h264'

    def __init__(self, videos_folder: str, device_id: str):
        self._videos_folder = videos_folder
        self._device_id = device_id

    def _local_video_path(self, filename: str) -> str:
        """Get the local absolute path of filename.

        Parameters
        ----------
        filename : str

        Returns
        -------
        str
        """
        return path.join(self._videos_folder, filename)

    @staticmethod
    def _remote_video_path(filename: str) -> str:
        """Get the remote absolute path of filename.

        Parameters
        ----------
        filename : str

        Returns
        -------
        str
        """
        return path.join(RPICameraVideo.REMOTE_VIDEO_FOLDER, filename)

    @staticmethod
    def _raw_video_file(name: str) -> str:
        return f'{name}{RPICameraVideo.RAW_EXT}'


    def camera_video(self, in_data: InMotionVideoData) -> None:
        is_same_device = self._device_id == in_data.device_id

        raw_video_file = self._local_video_path(self._raw_video_file(in_data.video_ref))
        output_video_file = self._local_video_path(f'{in_data.video_ref}.mp4')

        # need to download raw file from remote.
        if not is_same_device:
            remote_raw_video_file = self._remote_video_path(self._raw_video_file(in_data.video_ref))
            video_processing.retrieve_video_remotely(remote_raw_video_file, raw_video_file, in_data.device_id)

        # first split, merge before video and received video.
        if in_data.video_split_number == 0:
            video_ref_before_motion = f'{in_data.video_ref}-before'
            raw_video_file_before_motion = self._local_video_path(f'{video_ref_before_motion}.h264')
            raw_merged_video_file = self._local_video_path(f'{in_data.video_ref}-merged.h264')

            # need to download the "-before" video.
            if not is_same_device:
                remote_raw_video_file_before_motion = self._remote_video_path(f'{video_ref_before_motion}.h264')
                video_processing.retrieve_video_remotely(
                        self._remote_video_path(remote_raw_video_file_before_motion),
                        raw_video_file_before_motion, in_data.device_id
                )

            video_processing.merge_videos([raw_video_file_before_motion, raw_video_file], raw_merged_video_file)

            video_processing.h264_to_mp4(raw_merged_video_file, output_video_file)
        else:
            video_processing.h264_to_mp4(raw_video_file, output_video_file)

        LOGGER.info(f'video to mp4 ok - {output_video_file}')

        notification.send_video(output_video_file)
        in_motion.save_camera_video(in_data)

def rpi_camera_video_factory():
    videos_folder = os.environ['VIDEO_FOLDER']
    device_id = os.environ['DEVICE_ID']

    return RPICameraVideo(videos_folder, device_id)
