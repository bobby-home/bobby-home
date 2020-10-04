from typing import List

import numpy as np

from camera.camera_analyze import CameraAnalyzeObject, Consideration
from roi.roi import ROI
from camera.detect_motion import ObjectBoundingBox
from image_processing.contour import create_contour_from_points
from image_processing.contour_collision import contour_collision
from image_processing.scale import scale_point


class ROICamera(CameraAnalyzeObject):
    def __init__(self, roi: ROI):
        self._roi = roi
        self._contours, (self._contour_image_width, self._contour_image_height) = roi.get_contours()
        self._prev_image_width = None
        self._prev_image_height = None
        self._scaled_contours = None

    def is_object_considered(self, frame: np.ndarray, object_bounding_box: ObjectBoundingBox) -> List[Consideration]:
        image_height, image_width = frame.shape[0:2]

        if image_width != self._prev_image_width or image_height != self._prev_image_height:
            self._scaled_contours = [scale_point(self._contour_image_width, self._contour_image_height, image_width, image_height, x, y) for [[x, y]] in self._contours]
            self._scaled_contours = create_contour_from_points(np.array(self._scaled_contours))

        if contour_collision(frame, self._scaled_contours, object_bounding_box.contours):
            return [self._roi.consideration]

        return []


class IsConsideredByAnyAnalyzer(CameraAnalyzeObject):
    def __init__(self, analyzers: List[CameraAnalyzeObject]):
        self._analyzers = analyzers

    def is_object_considered(self, frame: np.ndarray, object_bounding_box: ObjectBoundingBox) -> List[Consideration]:
        for analyzer in self._analyzers:
            r = analyzer.is_object_considered(frame, object_bounding_box)
            if len(r) > 0:
                return r

        return []
