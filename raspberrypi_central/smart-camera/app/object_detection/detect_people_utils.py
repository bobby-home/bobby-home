from functools import partial

import numpy as np

from image_processing.scale import scale_point
from object_detection.model import BoundingBox, BoundingBoxPointAndSize
from operator import itemgetter


def bounding_box_size(bounding_box: BoundingBox) -> BoundingBoxPointAndSize:
    """
    xmax >= xmin and ymax >= ymin
    Validation has been done in BoundingBox class.
    """
    delta_x = bounding_box.xmax - bounding_box.xmin
    delta_y = bounding_box.ymax - bounding_box.ymin

    return BoundingBoxPointAndSize(x=bounding_box.xmin, y=bounding_box.ymin, w=delta_x, h=delta_y)


def resize_bounding_box(old_img_width: float, old_img_height: float, new_img_width: float, new_img_height: float, bounding_box: BoundingBox) -> BoundingBox:
    local_scale_point = partial(scale_point, old_img_width, old_img_height, new_img_width, new_img_height)

    xmin, ymin = local_scale_point(bounding_box.xmin, bounding_box.ymin)
    xmax, ymax = local_scale_point(bounding_box.xmax, bounding_box.ymax)

    return BoundingBox(xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax)


def bounding_box_from_point_and_size(bounding_box: BoundingBoxPointAndSize) -> BoundingBox:
    xmin = bounding_box.x
    ymin = bounding_box.y

    xmax = xmin + bounding_box.w
    ymax = ymin + bounding_box.h

    return BoundingBox(xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax)


def get_bounding_box_contours(bounding_box: BoundingBox):
    xmin, ymin, xmax, ymax = itemgetter('xmin', 'ymin', 'xmax', 'ymax')(bounding_box)

    # construction of the contours
    # List of (x,y) points in clockwise order <!>
    x1 = xmin
    y1 = ymax

    x2 = xmax
    y2 = ymax

    x3 = xmax
    y3 = ymin

    x4 = xmin
    y4 = ymin

    points = np.array([[x1, y1], [x2, y2], [x3, y3], [x4, y4]])

    # https://stackoverflow.com/a/24174904
    return points.reshape((-1, 1, 2)).astype(np.int32)
