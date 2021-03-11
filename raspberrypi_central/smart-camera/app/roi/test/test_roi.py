from unittest import TestCase, skip
import numpy as np

from roi.roi import RectangleROI


class TestRectangleROI(TestCase):
    @skip
    def test_get_contours(self):
        x = 10
        y = 10
        w = 20
        h = 20
        definition_width = 400
        definition_height = 400

        roi = RectangleROI(x, y, w, h, definition_width, definition_height)
        contours = roi.get_contours()[0]

        expected = np.array([[[10, 30]], [[30, 30]], [[30, 10]], [[10, 10]]])

        np.testing.assert_array_equal(contours, expected)

    @skip
    def test_equals(self):
        x = 10
        y = 10
        w = 20
        h = 20
        definition_width = 400
        definition_height = 400

        roi1 = RectangleROI(x, y, w, h, definition_width, definition_height)
        roi2 = RectangleROI(x, y, w, h, definition_width, definition_height)
        roi3 = RectangleROI(x+5, y, w, h, definition_width, definition_height)
        roi4 = RectangleROI(x, y, w, h, definition_width, definition_height+2)

        self.assertTrue(roi1 == roi2)
        self.assertFalse(roi3 == roi2)
        self.assertFalse(roi2 == roi4)
