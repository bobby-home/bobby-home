from unittest import TestCase
from unittest.mock import Mock

from camera.camera_analyze import Consideration
from camera.run_camera import roi_camera_from_args, RunSmartCamera
from camera_analyze.all_analyzer import NoAnalyzer
from camera_analyze.roi_analyzer import IsConsideredByAnyAnalyzer, ROICamera
from roi.roi import RectangleROI


class RunCamera(TestCase):
    def setUp(self) -> None:
        self.camera_factory = Mock()
        self.video_stream = Mock()

    def test_is_restart_necessary(self):
        payload = {
            'rois': {
                'rectangles': [
                    {"id": 3, "x": 5, "y": 7, "w": 10, "h": 20},
                    {"id": 4, "x": 50, "y": 70, "w": 100, "h": 200},
                ],
                'definition_width': 300,
                'definition_height': 300
            }
        }

        run = RunSmartCamera(self.camera_factory, self.video_stream)
        run.prepare_run(payload)

        self.assertFalse(run.is_restart_necessary(payload))

        payload['rois']['rectangles'].pop()
        self.assertTrue(run.is_restart_necessary(payload))



class ROICameraFromData(TestCase):

    def test_no_analyzer(self):
        payload = {
            'rois': {
                'full': True
            }
        }

        result = roi_camera_from_args(payload)
        self.assertIsInstance(result, NoAnalyzer)
        self.assertEqual(result._consideration.type, 'full')

    def test_rectangle_analyzers(self):
        payload = {
            'rois': {
                'rectangles': [
                    {"id": 3, "x": 5, "y": 7, "w": 10, "h": 20},
                    {"id": 4, "x": 50, "y": 70, "w": 100, "h": 200},
                ],
                'definition_width': 300,
                'definition_height': 300
            }
        }

        result = roi_camera_from_args(payload)
        self.assertIsInstance(result, IsConsideredByAnyAnalyzer)

        self.assertEqual(len(result._analyzers), 2)
        for analyzer, rectangle in zip(result._analyzers, payload['rois']['rectangles']):
            self.assertIsInstance(analyzer, ROICamera)
            self.assertIsInstance(analyzer._roi, RectangleROI)

            expected = {
                **rectangle,
                'consideration': Consideration(type='rectangle', id=rectangle['id']),
                'definition_width': payload['rois']['definition_width'],
                'definition_height': payload['rois']['definition_height'],
            }
            expected.pop('id', None)

            self.assertEqual(analyzer._roi.__dict__, expected)
