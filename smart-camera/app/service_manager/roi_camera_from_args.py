from typing import List


from camera.camera_config import camera_config
from camera_analyze.all_analyzer import NoAnalyzer
from camera_analyze.camera_analyzer import CameraAnalyzer, Consideration
from camera_analyze.considered_by_any_analyzer import ConsideredByAnyAnalyzer
from camera_analyze.rectangle_roi_analyzer import CameraAnalyzerRectangleROI
from object_detection.detect_people_utils import bounding_box_from_point_and_size, resize_bounding_box
from object_detection.model import BoundingBoxPointAndSize
from roi.roi import RectangleROI


CAMERA_WIDTH = camera_config.camera_width
CAMERA_HEIGHT = camera_config.camera_height


def roi_camera_from_args(data = None) -> CameraAnalyzer:
    """
    I have to manage to have multiple CameraAnalyzeObject
    or... I might use another class to handle multiple camera analyze object,
    so I could do stuff like, if in CameraRectangleROI and it is not someone that I know (facial recognition), then we consider the people
    -> ring the alarm.
    """

    rois = data.get('rois', None)

    analyzers: List[CameraAnalyzer] = []

    if rois:
        if 'rectangles' in rois:
            rectangles = rois.get('rectangles')

            definition_width = rois['definition_width']
            definition_height = rois['definition_height']

            for rectangle in rectangles:
                consideration = Consideration(id=rectangle['id'], type='rectangles')

                bounding_box = BoundingBoxPointAndSize(x=rectangle['x'], y=rectangle['y'], w=rectangle['w'], h=rectangle['h'])
                bounding_box = bounding_box_from_point_and_size(bounding_box)

                if CAMERA_WIDTH != definition_width or CAMERA_HEIGHT != definition_height:
                    bounding_box = resize_bounding_box(old_img_width=definition_width, old_img_height=definition_height,
                                                       new_img_width=CAMERA_WIDTH, new_img_height=CAMERA_HEIGHT, bounding_box=bounding_box)

                rectangle_roi = RectangleROI(consideration, bounding_box)

                analyzer = CameraAnalyzerRectangleROI(rectangle_roi)
                analyzers.append(analyzer)

            return ConsideredByAnyAnalyzer(analyzers)

        if 'full' in rois:
            consideration = Consideration(type='full')
            return NoAnalyzer(consideration)

        raise ValueError(f"Can't find any supported rois in {rois}.")
    else:
        raise ValueError(f"Can't find the key 'rois' in {data}")
