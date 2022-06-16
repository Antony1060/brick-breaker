import pygame
from typing import Dict, List, Literal, Union
from geometry import Point, Slope

ALL_RECTANGLES: List[List[pygame.Rect]] = [[] for _ in range(1280)]
SUPPORT_LIST = [0] * 1280

class SlopableRect(pygame.rect.Rect):

    def __init__(self, left: int, top: int, width: int, height: int, on_colide = None):
        super().__init__(left, top, width, height)
        self.slopes: Dict[str, Slope] = {}
        self.points: Dict[str, (Point, Point)] = {}
        self.on_colide = on_colide

        global ALL_RECTANGLES
        ALL_RECTANGLES[self.x].append(self)

        self._calc_slopes()

    @staticmethod
    def optimize():
        for items in ALL_RECTANGLES:
            items.sort(key=lambda it: it.y)

        last_index = 1279
        for i in range(1280 - 1, -1, -1):
            if len(ALL_RECTANGLES[i]) > 0:
                last_index = i
            SUPPORT_LIST[i] = last_index

    def _calc_slopes(self):
        p1 = Point(self.x, self.y)
        p2 = Point(self.x + self.width, self.y)
        p3 = Point(self.x + self.width, self.y + self.height)
        p4 = Point(self.x, self.y + self.height)

        self.points = {
            "top": (p1, p2),
            "right": (p2, p3),
            "bottom": (p3, p4),
            "left": (p4, p1)
        }

        self.slopes = dict([(side, Slope.from_points(*points)) for side, points in self.points.items()])

        # for C
        self.point_list = [p1.x, p1.y, p3.x, p3.y]
        self.slope_list = [*self.slopes["top"], *self.slopes["right"], *self.slopes["bottom"], *self.slopes["left"]]
        # self.cpoints = [[CPoint.from_python(p1), CPoint.from_python(p2)], [CPoint.from_python(p3), CPoint.from_python(p4)], [CPoint.from_python(p4), CPoint.from_python(p1)], [CPoint.from_python(p2), CPoint.from_python(p3)]]
        # self.cslopes = [CSlope.from_python(Slope.from_points(*points)) for points in self.point_list]


    def destroy(self):
        ALL_RECTANGLES[self.left].remove(self)

    def __hash__(self):
        return id(self)