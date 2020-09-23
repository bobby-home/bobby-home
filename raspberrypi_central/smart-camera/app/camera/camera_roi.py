import numpy as np
from abc import ABC, abstractmethod
from camera.detect_motion import ObjectBoundingBox
from camera.camera_analyze import CameraAnalyzeObject
from image_processing.scale import scale_point
from image_processing.contour import create_contour_from_points
from image_processing.contour_collision import contour_collision
from typing import Tuple


class ROI(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def getContours(self) -> Tuple[np.ndarray, Tuple[float, float]]:
        pass


class RectangleROI(ROI):
    def __init__(self, x: float, y: float, w: float, h: float):
        super().__init__()

    def getContours(self):
        x = 128
        y = 185
        w = 81
        h = 76
        old_img_width = 300
        old_image_height = 300

        x1, y1 = (x, y + h)
        x2, y2 = (x + w, y + h)
        x3, y3 = (x + w, y)
        x4, y4 = (x, y)

        points = np.array([[x1,y1], [x2,y2], [x3,y3], [x4,y4]])

        # points to contour: https://stackoverflow.com/a/24174904
        return points.reshape((-1,1,2)).astype(np.int32), (old_img_width, old_image_height)


class ROICamera(CameraAnalyzeObject):
    def __init__(self, roi: ROI):
        self._contours, (self._contour_image_width, self._contour_image_height) = roi.getContours()
        self._prev_image_width = None
        self._prev_image_height = None
        self._scaled_contours = None

    def is_object_considered(self, frame: np.ndarray, object_bounding_box: ObjectBoundingBox):
        image_height, image_width = frame.shape[0:2]

        if image_width != self._prev_image_width or image_height != self._prev_image_height:
            self._scaled_contours = [scale_point(self._contour_image_width, self._contour_image_height, image_width, image_height, x, y) for [[x, y]] in self._contours]
            self._scaled_contours = create_contour_from_points(np.array(self._scaled_contours))

        return contour_collision(frame, self._scaled_contours, object_bounding_box.contours)
