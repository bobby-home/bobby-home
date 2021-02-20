import os
from typing import Tuple, Optional

from utils.download import get_file


def download_model(model_name: str = 'archive.zip', cache_dir: Optional[str] = None) -> Tuple[str, str]:
    if cache_dir is None:
        cache_dir = os.environ['TF_MODELS_FOLDER']

    # on your machine download the archive and get its checksum:
    # `sha256sum ./mobilenet_v2_1.0_224.tgz`
    url = 'https://storage.googleapis.com/download.tensorflow.org/models/tflite_11_05_08/mobilenet_v2_1.0_224.tgz'
    model_archive_file_hash = 'a9fce7e2db6389dfa1e640a9c98a6f29a55e482e463c5f01c377a19806f66ee2'
    label_file_hash = '93f235896748537fc71325a070ee32e9a0afda2481ceb943559325619763fa6d'

    archive = get_file(
        cache_dir=cache_dir,
        fname=model_name,
        origin=url,
        extract=True,
        file_hash=model_archive_file_hash)

    labels = get_file(
        cache_dir=cache_dir,
        fname='coco_labels.txt',
        origin='https://dl.google.com/coral/canned_models/coco_labels.txt',
        file_hash=label_file_hash
    )

    return f'{cache_dir}/detect.tflite', labels
