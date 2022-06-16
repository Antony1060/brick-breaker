from typing import Tuple, Union
import ccollision
from geometry import Point
from slopeable_rect import SlopableRect

def detect_collision(c_x, c_y, c_r, rect: SlopableRect) -> Union[None, Tuple[str, Point]]:
    c_res = ccollision.detect_collision((c_x, c_y, c_r), (rect.x, rect.y, rect.width, rect.height), rect.point_list, rect.slope_list)
    if not c_res:
        return None

    return (c_res[0], Point(c_res[1], c_res[2]))


