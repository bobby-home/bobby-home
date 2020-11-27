from enum import Enum, unique


@unique
class ROITypes(Enum):
    """
    Warning: don't change these values blindly!
    It could break the whole alarm system.
    These values are used (hard coded) by the smart-camera service.
    We might need to share code between the web and smart-camera service to avoid this kind of issue.
    But this won't happen if you don't change these values without changing smart-camera accordingly.
    """
    RECTANGLES = 'rectangles'
    FULL = 'full'
