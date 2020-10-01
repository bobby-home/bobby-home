import numpy as np

from camera.camera_analyze import CameraAnalyzeObject
from roi.roi import ROI
from camera.detect_motion import ObjectBoundingBox
from image_processing.contour import create_contour_from_points
from image_processing.contour_collision import contour_collision
from image_processing.scale import scale_point


class ROICamera(CameraAnalyzeObject):
    def __init__(self, roi: ROI):
        self._contours, (self._contour_image_width, self._contour_image_height) = roi.get_contours()
        self._prev_image_width = None
        self._prev_image_height = None
        self._scaled_contours = None

    def is_object_considered(self, frame: np.ndarray, object_bounding_box: ObjectBoundingBox):
        image_height, image_width = frame.shape[0:2]

        if image_width != self._prev_image_width or image_height != self._prev_image_height:
            self._scaled_contours = [scale_point(self._contour_image_width, self._contour_image_height, image_width, image_height, x, y) for [[x, y]] in self._contours]
            self._scaled_contours = create_contour_from_points(np.array(self._scaled_contours))

        return contour_collision(frame, self._scaled_contours, object_bounding_box.contours)
