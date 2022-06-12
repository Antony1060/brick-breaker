from re import I
from typing import List
import math

EPSILON = 1e-10

class Point:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return f"Point{{{self.x},{self.y}}}"

    def __repr__(self) -> str:
        return self.__str__()

    def __iter__(self):
        return iter((self.x, self.y))


class Slope:

    def __init__(self, direction_coefficient, y_shift):
        self.direction_coefficient = direction_coefficient
        self.y_shift = y_shift

    @staticmethod
    def from_points(first: Point, second: Point):
        k = (second.y - first.y) / (second.x - first.x + EPSILON)
        l = -(k * first.x) + first.y

        return Slope(k, l)

    def solve_for(self, x: int) -> int:
        return self.direction_coefficient * x + self.y_shift

    def __str__(self) -> str:
        return f"Slope{{y={self.direction_coefficient:.2f}x+{self.y_shift:.2f}}}"

    def __repr__(self) -> str:
        return self.__str__()


class Circle:

    def __init__(self, center: Point, radius: int):
        self.center = center
        self.radius = radius

    # src = https://www.wolframalpha.com/input?i2d=true&i=Power%5B%5C%2840%29x+-+p%5C%2841%29%2C2%5D+%2B+Power%5B%5C%2840%29%5C%2840%29kx+%2B+l%5C%2841%29+-+q%5C%2841%29%2C2%5D+%3D+Power%5Br%2C2%5D
    def slope_intersection(self, slope: Slope) -> List[Point]:
        k = slope.direction_coefficient
        l = slope.y_shift

        p, q = self.center
        r = self.radius

        psq = p**2
        qsq = q**2
        rsq = r**2
        ksq = k**2
        lsq = l**2

        under_root = -ksq * psq + ksq * rsq - 2 * k * l * p + 2 * k * p * q - lsq + 2 * l * q - qsq + rsq
        if under_root < 0:
            return []

        raw_root = math.sqrt(under_root)
        possible_roots = [raw_root] if raw_root == 0 else [-raw_root, raw_root]

        solutions = []
        for root in possible_roots:
            x = (root - k * l + k * q + p) / (ksq + 1)
            solutions.append(Point(x, slope.solve_for(x)))

        return solutions

    def __str__(self) -> str:
        return f"Circle{{(x - {self.center.x})^2+(y - {self.center.y})^2={self.radius}^2}}"

    def __repr__(self) -> str:
        return self.__str__()