import dataclasses
import unittest

from object_detection.detect_people_utils import bounding_box_size, bounding_box_from_point_and_size
from object_detection.model import BoundingBox, BoundingBoxPointAndSize


class DetectPeopleTestCase(unittest.TestCase):
    def test_bounding_box_size(self):
        width = 285
        height = 204

        ymin = 94
        xmin = 6

        bounding_box = BoundingBox(ymin, xmin, ymin+height, xmin+width)
        with_size = bounding_box_size(bounding_box)
        self.assertEqual(dataclasses.asdict(with_size), {'x': xmin, 'y': ymin, 'w': width, 'h': height})

    def test_bounding_box_from_point_and_size(self):
        width = 285
        height = 204

        ymin = 94
        xmin = 6

        bounding_box = BoundingBoxPointAndSize(x=xmin, y=ymin, w=width, h=height)
        only_points = bounding_box_from_point_and_size(bounding_box)

        self.assertEqual(dataclasses.asdict(only_points), {'ymin': ymin, 'xmin': xmin, 'ymax': ymin + height, 'xmax': xmin + width})
