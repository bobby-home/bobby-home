import re
import os
from os import path
import logging

from alarm.business import in_motion
import alarm.utils.video_processing as video_processing
import notification.tasks as notification

LOGGER = logging.getLogger(__name__)


class CameraVideo:
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
        return path.join(CameraVideo.REMOTE_VIDEO_FOLDER, filename)

    @staticmethod
    def _raw_video_file(name: str) -> str:
        return f'{name}{CameraVideo.RAW_EXT}'

    @staticmethod
    def _get_split_number(video_ref: str) -> int:
        split_number_pattern = r"(?P<split_number>[0-9]+$)"
        split_number_re = re.search(split_number_pattern, video_ref)
        if split_number_re is None:
            raise ValueError(f'Wrong video_ref format: {video_ref}.')

        split_number = split_number_re.group()
        return int(split_number)

    def camera_video(self, device_id: str, video_ref: str) -> None:
        is_same_device = self._device_id == device_id

        raw_video_file = self._local_video_path(self._raw_video_file(video_ref))
        output_video_file = self._local_video_path(f'{video_ref}.mp4')

        split_number = self._get_split_number(video_ref)

        # need to download raw file from remote.
        if not is_same_device:
            remote_raw_video_file = self._remote_video_path(self._raw_video_file(video_ref))
            video_processing.retrieve_video_remotely(remote_raw_video_file, raw_video_file, device_id)

        # first split, merge before video and received video.
        if split_number == 0:
            video_ref_before_motion = f'{video_ref}-before'
            raw_video_file_before_motion = self._local_video_path(f'{video_ref_before_motion}.h264')
            raw_merged_video_file = self._local_video_path(f'{video_ref}-merged.h264')

            # need to download the "-before" video.
            if not is_same_device:
                remote_raw_video_file_before_motion = self._remote_video_path(f'{video_ref_before_motion}.h264')
                video_processing.retrieve_video_remotely(self._remote_video_path(remote_raw_video_file_before_motion), raw_video_file_before_motion, device_id)

            video_processing.merge_videos([raw_video_file_before_motion, raw_video_file], raw_merged_video_file)

            video_processing.h264_to_mp4(raw_merged_video_file, output_video_file)
        else:
            video_processing.h264_to_mp4(raw_video_file, output_video_file)

        LOGGER.info(f'video to mp4 ok - {output_video_file}')

        notification.send_video(output_video_file)
        in_motion.save_camera_video(video_ref)

def camera_video_factory():
    videos_folder = os.environ['VIDEO_FOLDER']
    device_id = os.environ['DEVICE_ID']

    return CameraVideo(videos_folder, device_id)
