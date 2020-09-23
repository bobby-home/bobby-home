from typing import Tuple


def scale_point(old_img_width: float, old_img_height: float, new_img_width: float, new_img_height:float, x: float, y: float) -> Tuple[float, float]:
    """Allows you to scale points for a new image size.

    Args:
        old_img_width (float): 
        old_img_height (float): 
        new_img_width (float): 
        new_img_height (float): 
        x (float): 
        y (float): 

    Returns:
        Tuple[float, float]: new coordinates for x,y
    """
    new_x = (x / old_img_width) * new_img_width
    new_y = (y / old_img_height) * new_img_height

    return new_x, new_y
