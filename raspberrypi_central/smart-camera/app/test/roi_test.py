import unittest
import cv2
import numpy as np
from functools import partial
from image_processing.contour import create_contour_from_points
from image_processing.contour_collision import contour_collision


class ContourTestCase(unittest.TestCase):

    def test_contour_collision_exact_same_position(self):
        frame_width = 600
        frame_height = 400

        frame = np.zeros((frame_height, frame_width, 1), np.uint8)

        roi_points = np.array([[30,88], [118, 88], [118, 20], [118, 20]])
        roi_contours = create_contour_from_points(roi_points)

        motions_points = roi_points
        motion_contours = create_contour_from_points(motions_points)

        is_collision = contour_collision(frame, roi_contours, motion_contours)

        self.assertTrue(is_collision)
