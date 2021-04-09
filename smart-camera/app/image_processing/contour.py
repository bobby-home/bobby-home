import numpy as np


def create_contour_from_points(points: np.ndarray) -> np.ndarray:
    """Allows you to create a contour from an np array of points.

    Args:
        points (np.ndarray): points that we want to create the contours from.

    Returns:
        np.ndarray: the contours, opencv compatible.
    """
    # https://stackoverflow.com/a/24174904
    return points.reshape((-1,1,2)).astype(np.int32)
