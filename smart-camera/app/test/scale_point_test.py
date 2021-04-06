import unittest
import numpy as np
from image_processing.contour import create_contour_from_points
from image_processing.scale import scale_point


class ScalePointTestCase(unittest.TestCase):

    def test_yolo(self):
        roi_points = np.array([[30,88], [118, 88], [118, 20], [30, 20]])
        roi_contours = create_contour_from_points(roi_points)

        new_contour = [scale_point(300, 300, 330, 330, x, y) for [[x, y]] in roi_contours]
        print(roi_contours)
        print(new_contour)
