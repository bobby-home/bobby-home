import numpy as np
import cv2


def contour_collision(frame, contour1, contour2) -> bool:
    """Detect a collision between 2 contours. If the contours have the exact same position, it's still returning true.

    Args:
        frame ([type]): the base frame
        contour1 ([type]):
        contour2 ([type]):

    Returns:
        bool: True if collision, false otherwise.
    """

    # create an image filled with zeros, single-channel, same size as img.
    blank_frame = np.zeros(frame.shape[0:2])

    # copy each of the contours (assuming there's just two) to its own image. 
    # Just fill with a "1".
    img_contour1 = cv2.drawContours(blank_frame.copy(), [contour1], 0, 1, thickness=-1)
    img_contour2 = cv2.drawContours(blank_frame.copy(), [contour2], 0, 1, thickness=-1)

    intersection = np.logical_and(img_contour1, img_contour2)
    return intersection.any()
