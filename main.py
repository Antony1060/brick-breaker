import os
import random
from typing import List, Set
import pygame

from objects import Ball
from slopeable_rect import SlopableRect

pygame.init()

WIDTH = 1280
HEIGHT = 720
TARGET_FPS = 60
COLOR_BG = (10, 13, 19)
COLOR_WHITE = (218, 218, 218)
LINE_WIDTH = 200
LINE_HEIGHT = 10
LINE_VELOCITY = 16

CUBE_WIDTH = 10
CUBE_HEIGHT = 10
CUBE_PADDING = 10
CUBE_COUNT_PER_ROW = (WIDTH - CUBE_PADDING) // (CUBE_WIDTH + CUBE_PADDING)
CUBE_COUNT = CUBE_COUNT_PER_ROW * 10

BALL_HEIGHT = 12

POWERUP_CHANCE = 10
POWERUP_HEIGHT = 20
POWERUP_VELOCITY = 4

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Igra")

POWERUP_SPLIT_IMG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "split.png")), (POWERUP_HEIGHT, POWERUP_HEIGHT))
POWERUP_TRIPLE_DOWN_IMG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "triple_down.png")), (POWERUP_HEIGHT, POWERUP_HEIGHT))

LINE = SlopableRect(WIDTH / 2 - LINE_WIDTH / 2, HEIGHT - 20 - LINE_HEIGHT, LINE_WIDTH, LINE_HEIGHT)

def on_ball_draw(win, x, y, r):
    pygame.draw.circle(win, COLOR_WHITE, (x, y), r)

def on_powerup_split_pickup(powerup):
    POWERUPS.remove(powerup)
    for ball in BALLS.copy():
        if len(BALLS) > 200:
            return
        for i in range(-6, 7, 12):
            BALLS.add(Ball(ball.x, ball.y, ball.radius, i, -6, on_ball_draw))

def on_powerup_triple_pickup(powerup):
    POWERUPS.remove(powerup)
    if len(BALLS) > 200:
        return
    for i in range(-6, 7, 6):
        BALLS.add(Ball(LINE.x + LINE.width / 2 - BALL_HEIGHT / 2, LINE.y - BALL_HEIGHT, BALL_HEIGHT / 2, i, -6, on_ball_draw))

def on_cube_colide(cube: SlopableRect):
    CUBES.remove(cube)
    if random.randint(1, 100) <= POWERUP_CHANCE:
        if random.choice([True, False]):
            POWERUPS.add(Ball(cube.x - (POWERUP_HEIGHT - cube.width) / 2, cube.y - (POWERUP_HEIGHT - cube.height) / 2, POWERUP_HEIGHT / 2, 0, POWERUP_VELOCITY, \
                lambda win, x, y, r: win.blit(POWERUP_SPLIT_IMG, (x - r, y - r)), on_powerup_split_pickup))
        else:
            POWERUPS.add(Ball(cube.x - (POWERUP_HEIGHT - cube.width) / 2, cube.y - (POWERUP_HEIGHT - cube.height) / 2, POWERUP_HEIGHT / 2, 0, POWERUP_VELOCITY, \
                lambda win, x, y, r: win.blit(POWERUP_TRIPLE_DOWN_IMG, (x - r, y - r)), on_powerup_triple_pickup))

POWERUPS: Set[Ball] = set()
BALLS = {Ball(WIDTH / 2 - BALL_HEIGHT / 2, LINE.y - BALL_HEIGHT, BALL_HEIGHT / 2, 6, 6, on_ball_draw)}
CUBES = {SlopableRect(CUBE_PADDING + (i % CUBE_COUNT_PER_ROW) * (CUBE_PADDING + CUBE_WIDTH), CUBE_PADDING + (i // CUBE_COUNT_PER_ROW) * (CUBE_PADDING + CUBE_HEIGHT) , CUBE_WIDTH, CUBE_HEIGHT, on_cube_colide) for i in range(CUBE_COUNT)}

def handle_ball_movement(ball: Ball, obstables: List[SlopableRect], src_set: Set[Ball]):
    if (ball.x + BALL_HEIGHT) >= WIDTH or ball.x <= 0:
        ball.velocity_x *= -1
    
    if ball.y <= 0:
        ball.velocity_y *= -1

    if ball.y > HEIGHT:
        src_set.remove(ball)

    ball.tick(obstables)

def draw_state():
    WIN.fill(COLOR_BG)
    pygame.draw.rect(WIN, COLOR_WHITE, LINE)

    for cube in CUBES:
        pygame.draw.rect(WIN, COLOR_WHITE, cube)

    for ball in BALLS:
        ball.draw(WIN)

    for powerup in POWERUPS:
        powerup.draw(WIN)

    pygame.display.update()

def handle_event(event: pygame.event.Event) -> bool:
    if event.type == pygame.QUIT:
        return False

    return True

def handle_keypresses(keypresses):
    if keypresses[pygame.K_d]:
        LINE.x = max(0, min(WIDTH - LINE_WIDTH, LINE.x + LINE_VELOCITY))
    elif keypresses[pygame.K_a]:
        LINE.x = max(0, min(WIDTH - LINE_WIDTH, LINE.x - LINE_VELOCITY))

def main():
    clock = pygame.time.Clock()
    running = True
    while running:
        clock.tick(TARGET_FPS)
        for event in pygame.event.get():
            running = handle_event(event)
        
        handle_keypresses(pygame.key.get_pressed())
        LINE._calc_slopes()

        if len(BALLS) <= 0:
            running = False

        for ball in BALLS.copy():
            handle_ball_movement(ball, list(CUBES) + [LINE], BALLS)

        for powerup in POWERUPS.copy():
            handle_ball_movement(powerup, [LINE], POWERUPS)

        draw_state()

if __name__ == "__main__":
    main()