import ctypes

from geometry import Point, Slope

class CPoint(ctypes.Structure):
    _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double)]

    @staticmethod
    def from_python(point: Point):
        p = CPoint()
        p.x = point.x
        p.y = point.y

        return p

    def to_python(self) -> Point:
        return Point(self.x, self.y)

class CSlope(ctypes.Structure):
    _fields_ = [("k", ctypes.c_double), ("l", ctypes.c_double)]

    @staticmethod
    def from_python(slope: Slope):
        s = CSlope()
        s.k = slope.direction_coefficient
        s.l = slope.y_shift

        return s

class CRect(ctypes.Structure):
    _fields_ = [("x", ctypes.c_int), ("y", ctypes.c_int), ("width", ctypes.c_int), ("height", ctypes.c_int), ("points", (CPoint * 2) * 4), ("slopes", CSlope * 4)]

class CollisonResult(ctypes.Structure):
    _fields_ = [("side", ctypes.c_char_p), ("point", CPoint)]