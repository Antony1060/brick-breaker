from tkinter import OFF
from typing import Dict
import pygame
from geometry import Point, Slope

class_id = 0

class SlopableRect(pygame.rect.Rect):

    def __init__(self, left: float, top: float, width: float, height: float, on_colide = None):
        super().__init__(left, top, width, height)
        self.slopes: Dict[str, Slope] = {}
        self.points: Dict[str, (Point, Point)] = {}
        self.on_colide = on_colide

        global class_id
        self.hash = class_id
        class_id += 1

        self._calc_slopes()

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

    def __hash__(self):
        return self.hash