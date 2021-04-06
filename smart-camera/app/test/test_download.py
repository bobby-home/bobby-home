import os
from unittest import TestCase

from utils.download import get_file

from object_detection.download_model import download_model


class TestDownload(TestCase):
    def setUp(self) -> None:
        pass

    def test_download_model(self):
        tflite_file, labels_file = download_model('archive.zip', cache_dir='/tmp/.models')
        print(tflite_file, labels_file)

        self.assertTrue(os.path.isfile(tflite_file))
        self.assertTrue(os.path.isfile(labels_file))

    def test_download(self):
        model_name = 'archive.zip'
        url = 'http://storage.googleapis.com/download.tensorflow.org/models/tflite/coco_ssd_mobilenet_v1_1.0_quant_2018_06_29.zip'
        file_hash = 'a809cd290b4d6a2e8a9d5dad076e0bd695b8091974e0eed1052b480b2f21b6dc'

        dir = '/tmp/.models'
        os.makedirs(dir)

        archive = get_file(
            cache_dir='/tmp/.models',
            fname=model_name,
            origin=url,
            extract=True,
            file_hash=file_hash)

        self.assertTrue(os.path.isfile(archive))
        self.assertTrue(os.path.isfile(f'{dir}/detect.tflite'))

        labels = get_file(
            cache_dir='/tmp/.models',
            fname='coco_labels.txt',
            origin='https://dl.google.com/coral/canned_models/coco_labels.txt'
        )

        self.assertTrue(os.path.isfile(labels))

    def test_download_wrong_downloaded_hash(self):
        model_name = 'archive.zip'
        url = 'http://storage.googleapis.com/download.tensorflow.org/models/tflite/coco_ssd_mobilenet_v1_1.0_quant_2018_06_29.zip'
        file_hash = 'fake_hash'

        with self.assertRaises(Exception) as context:
            archive = get_file(
                cache_dir='/tmp/.models',
                fname=model_name,
                origin=url,
                extract=True,
                file_hash=file_hash)
