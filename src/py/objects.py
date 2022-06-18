import math
from typing import Callable, List, Set
import pygame
from slopeable_rect import ALL_RECTANGLES, SUPPORT_LIST, SlopableRect
import c_collision

def num_between(num, bound1, bound2):
    return (bound1 - num) * (bound2 - num) <= 0

BALL_SPEED = 6

def binear_search_by_y(lookup: List[SlopableRect], lower_bound: int) -> int:
        left = 0
        right = len(lookup)
        mid = 0

        while left < right:
            mid = left + (right - left) // 2
            if lookup[mid].y >= lower_bound:
                right = mid - 1
            else:
                left = mid + 1
        
        return mid

class Ball(pygame.Rect):

    def __init__(self, left, top, radius, vel_x, vel_y, on_draw: Callable[[pygame.Surface, int, int, int], None], on_colide = None):
        super().__init__(left, top, radius * 2, radius * 2)
        self.radius = int(radius)
        self.on_draw = on_draw
        self.velocity_x = vel_x
        self.velocity_y = vel_y
        self.on_colide = on_colide

    def draw(self, surface: pygame.Surface):
        self.on_draw(surface, self.centerx, self.centery, self.radius)
    
    def __update_if_colided(self, obstacle: SlopableRect) -> bool:
        collision = c_collision.detect_collision(self.centerx, self.centery, self.radius, obstacle)

        if not collision:
            return False

        side, point = collision

        if self.on_colide:
            self.on_colide(self)

        if obstacle.on_colide:
            obstacle.on_colide(obstacle)

        if side in ["top", "bottom"]:
            relativeIntersect = (obstacle.x + (obstacle.width / 2)) - point.x
            normalizedIntersect = relativeIntersect / (obstacle.width / 2)
            angle = normalizedIntersect * math.radians(75)

            self.velocity_x = BALL_SPEED * math.sin(angle)
            if side == "top":
                self.velocity_y = -BALL_SPEED * math.cos(angle)
            else:
                self.velocity_y = BALL_SPEED * math.cos(angle)
        else:
            relativeIntersect = (obstacle.y + (obstacle.height / 2)) - point.y
            normalizedIntersect = relativeIntersect / (obstacle.height / 2)
            angle = normalizedIntersect * math.radians(75)

            self.velocity_y = BALL_SPEED * math.sin(angle)
            if side == "left":
                self.velocity_x = -BALL_SPEED * math.cos(angle)
            else:
                self.velocity_x = BALL_SPEED * math.cos(angle)

        return True

    def tick(self, obstacles: Set[SlopableRect], extra: Set[SlopableRect] = set()):
        self.x += self.velocity_x
        self.y += self.velocity_y

        i = max(0, self.x - 10)
        while i < min(1280, self.x + self.width + 10):
            i = min(self.x + self.width + 10, SUPPORT_LIST[i])
            j = binear_search_by_y(ALL_RECTANGLES[i], self.y - 10)
            while j < len(ALL_RECTANGLES[i]):
                obstacle = ALL_RECTANGLES[i][j]
                if obstacle.y > self.y + self.height + 10:
                    break
                
                if obstacle in obstacles and self.__update_if_colided(obstacle):
                    break

                j += 1
            i += 1

        for obstacle in extra:
            self.__update_if_colided(obstacle)

    def __hash__(self):
        return id(self)        
