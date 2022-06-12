from typing import Dict, List
import pygame
from geometry import Point, Slope

class_id = 0

ALL_RECTANGLES: List[List[pygame.Rect]] = [[] for _ in range(1280)]
SUPPORT_LIST = [0] * 1280

class SlopableRect(pygame.rect.Rect):

    def __init__(self, left: int, top: int, width: int, height: int, on_colide = None):
        super().__init__(left, top, width, height)
        self.slopes: Dict[str, Slope] = {}
        self.points: Dict[str, (Point, Point)] = {}
        self.on_colide = on_colide

        global class_id, ALL_RECTANGLES
        self.hash = class_id
        class_id += 1
        ALL_RECTANGLES[self.left].append(self)

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
        ps1 = Point(self.x, self.y)
        ps2 = Point(self.x + self.width, self.y)
        ps3 = Point(self.x + self.width, self.y + self.height)
        ps4 = Point(self.x, self.y + self.height)

        self.points = {
            "top": (ps1, ps2),
            "right": (ps2, ps3),
            "bottom": (ps3, ps4),
            "left": (ps4, ps1)
        }

        self.slopes = dict([(side, Slope.from_points(*points)) for side, points in self.points.items()])

    def destroy(self):
        ALL_RECTANGLES[self.left].remove(self)

    def __hash__(self):
        return self.hash