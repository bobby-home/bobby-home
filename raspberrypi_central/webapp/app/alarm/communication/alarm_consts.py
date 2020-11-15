from enum import Enum, unique


@unique
class ROITypes(Enum):
    RECTANGLES = 'rectangles'
    FULL = 'full'
