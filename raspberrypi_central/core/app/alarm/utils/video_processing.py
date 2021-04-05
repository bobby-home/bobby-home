import os
from typing import List
from pathlib import Path


def retrieve_video_remotely(remote_raw_video_file: str, local_dest: str, device_id: str) -> None:
    """

    Parameters
    ----------
    remote_raw_video_file : str
    local_dest : str
        Output folder of rsync. Every file that will be sync will go to this folder.
    device_id : str

    Returns
    -------
    None
    """

    # --remove-source-files removes file from the source
    # used to clean the file from the remote because it is not necessary to keep it once it has been downloaded.
    command = f"rsync -avt --remove-source-files pi@{device_id}:{remote_raw_video_file} {local_dest}"
    os.system(command)


def merge_videos(videos_path: List[str], output_video_path: str) -> None:
    if len(videos_path) < 1:
        return None

    command_file = f'-add {videos_path[0]}'
    for video_path in videos_path[1:]:
        command_file += f' -cat {video_path}'

    command = f'MP4Box {command_file} {output_video_path} > /dev/null 2>&1'

    result = os.system(command)
    if result != 0:
        raise Exception(f'{command} did not exited successfully.')


def h264_to_mp4(input_path: str, output_path: str, delete_input: bool = False) -> None:
    """Convert raw h264 'input_path' to mp4 in 'output_path' or in 'input_path' with .mp4 extension.

    Parameters
    ----------
    input_path : str
    output_path : str
    delete_input : bool
        Either or not the input should be deleted after processing.

    Raises
    ------
    Exception
        If underlying MP4Box command is not exited normally,
            probably something went wrong and the file is not converted.

    Returns
    -------
    str
        The path to the newly (converted) video.
    """

    # MP4Box redirect everything to stderr (even if no error).
    # so we redirect stderr to stdout to /dev/null
    # so nothing is printed to avoid logs pollution.
    # if an error happens, we catch it thanks to the result.
    if not Path(input_path).is_file():
        raise FileNotFoundError(f'{input_path} does not exist.')

    command = f'MP4Box -add {input_path} {output_path} > /dev/null 2>&1'

    # warning: call could be problematic in Celery tasks.
    result = os.system(command)
    if result != 0:
        raise Exception(f'{command} did not exited successfully.')

    if delete_input is True:
        os.remove(input_path)
