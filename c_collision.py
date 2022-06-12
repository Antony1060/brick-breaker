import ctypes
import os
from typing import Tuple

from geometry import Circle, Point
from slopeable_rect import SlopableRect
from c_types import CPoint, CSlope, CRect, CollisonResult

clib = ctypes.CDLL(os.path.abspath("./circle_rect_collision.so"))

__detect_collision = clib.detect_collision
__detect_collision.restype = ctypes.POINTER(CollisonResult)
__detect_collision.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, CRect]

def c_detect_collision(c_x, c_y, c_r, rect: SlopableRect) -> None | Tuple[str, Point]:
    c_rect = CRect()
    c_rect.x = rect.x
    c_rect.y = rect.y
    c_rect.width = rect.width
    c_rect.height = rect.height
    c_rect.points = ((CPoint * 2) * len(rect.cpoints))(*[(CPoint * 2)(*i) for i in rect.cpoints])
    c_rect.slopes = (CSlope * len(rect.cslopes))(*rect.cslopes)

    collision_result_ptr = __detect_collision(c_x, c_y, c_r, c_rect)
    if not collision_result_ptr:
        return None
    
    result = (collision_result_ptr.contents.side.decode("utf-8"), collision_result_ptr.contents.point.to_python())
    clib.free_mem(collision_result_ptr)
    return result
