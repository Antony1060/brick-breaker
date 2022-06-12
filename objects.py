import math
from typing import Callable, List, Tuple, Union
import pygame
from geometry import Circle, Point
from slopeable_rect import SlopableRect

def num_between(num, bound1, bound2):
    return (bound1 - num) * (bound2 - num) <= 0

class_id = 0

BALL_SPEED = 6

class Ball(pygame.Rect):

    def __init__(self, left, top, radius, vel_x, vel_y, on_draw: Callable[[pygame.Surface, int, int, int], None], on_colide = None):
        super().__init__(left, top, radius * 2, radius * 2)
        self.radius = radius
        self.on_draw = on_draw
        self.velocity_x = vel_x
        self.velocity_y = vel_y
        self.on_colide = on_colide
        global class_id
        self.hash = class_id
        class_id += 1

    def draw(self, surface: pygame.Surface):
        self.on_draw(surface, self.centerx, self.centery, self.radius)
    
    # returns True when the two are not colliding
    def __primitive_collison(self, rect: SlopableRect) -> bool:
        diff_x = abs(self.centerx - rect.centerx)
        diff_y = abs(self.centery - rect.centery)

        return self.radius + rect.width / 2 < diff_x and self.radius + rect.height / 2 < diff_y

    def detect_collision(self, rect: SlopableRect) -> Union[None, Tuple[str, Point]]:
        if self.__primitive_collison(rect):
            return None

        c_x, c_y = self.center
        circle = Circle(Point(c_x, c_y), self.radius)

        for side, slope in rect.slopes.items():
            intersections = circle.slope_intersection(slope)
            if len(intersections) != 2:
                continue

            inter_point1, inter_point2 = intersections
            p1, p2 = rect.points[side]

            if side in ["top", "bottom"]:
                if num_between(inter_point1.x, p1.x, p2.x):
                    return (side, inter_point1)
                elif num_between(inter_point2.x, p1.x, p2.x):
                    return (side, inter_point2)
            elif side in ["left", "right"]:
                if num_between(inter_point1.y, p1.y, p2.y):
                    return (side, inter_point1)
                elif num_between(inter_point2.y, p1.y, p2.y):
                    return (side, inter_point2)

            if (side in ["top", "bottom"] and (num_between(inter_point1.x, p1.x, p2.x) or num_between(inter_point2.x, p1.x, p2.x))) \
                or (side in ["left", "right"] and (num_between(inter_point1.y, p1.y, p2.y) or num_between(inter_point2.y, p1.y, p2.y))):
                return side

        return None

    def tick(self, obstacles: List[SlopableRect]):
        self.x += self.velocity_x
        self.y += self.velocity_y

        for obstacle in obstacles:
            collision = self.detect_collision(obstacle)
            if collision:
                side, point = collision

                if self.on_colide:
                    self.on_colide(self)

                if obstacle.on_colide:
                    obstacle.on_colide(obstacle)

                if side in ["top", "bottom"]:
                    relativeIntersect = (obstacle.x + (obstacle.width / 2)) - point.x
                    normalizedIntersect = relativeIntersect / (obstacle.width / 2)
                    angle = normalizedIntersect * math.radians(75)

                    if side == "top":
                        self.velocity_x = BALL_SPEED * math.sin(angle)
                        self.velocity_y = -BALL_SPEED * math.cos(angle)
                    else:
                        self.velocity_x = BALL_SPEED * math.sin(angle)
                        self.velocity_y = BALL_SPEED * math.cos(angle)
                else:
                    relativeIntersect = (obstacle.y + (obstacle.height / 2)) - point.y
                    normalizedIntersect = relativeIntersect / (obstacle.height / 2)
                    angle = normalizedIntersect * math.radians(75)

                    if side == "left":
                        self.velocity_x = -BALL_SPEED * math.cos(angle)
                        self.velocity_y = BALL_SPEED * math.sin(angle)
                    else:
                        self.velocity_x = BALL_SPEED * math.cos(angle)
                        self.velocity_y = BALL_SPEED * math.sin(angle)
                break

    def __hash__(self):
        return self.hash
        
