import ccollision
from slopeable_rect import SlopableRect

if __name__ == "__main__":
    r = SlopableRect(910, 390, 10, 10)

    print(ccollision.detect_collision(922, 402, 6, r))