import os
import random
from typing import Set
import pygame
import time

from objects import Ball
from slopeable_rect import SlopableRect

pygame.init()

WIDTH = 1280
HEIGHT = 1000
TARGET_FPS = 60
COLOR_BG = (10, 13, 19)
COLOR_WHITE = (218, 218, 218)
LINE_WIDTH = WIDTH
LINE_HEIGHT = 10
LINE_VELOCITY = 16

CUBE_WIDTH = 10
CUBE_HEIGHT = 10
CUBE_PADDING = 10
CUBE_COUNT_PER_ROW = (WIDTH - CUBE_PADDING) // (CUBE_WIDTH + CUBE_PADDING)
CUBE_COUNT = CUBE_COUNT_PER_ROW * 40

BALL_HEIGHT = 12

POWERUP_CHANCE = 60
POWERUP_HEIGHT = 20
POWERUP_VELOCITY = 4

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Igra")

POWERUP_SPLIT_IMG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "split.png")), (POWERUP_HEIGHT, POWERUP_HEIGHT))
POWERUP_TRIPLE_DOWN_IMG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "triple_down.png")), (POWERUP_HEIGHT, POWERUP_HEIGHT))

LINE = SlopableRect(WIDTH / 2 - LINE_WIDTH / 2, HEIGHT - 20 - LINE_HEIGHT, LINE_WIDTH, LINE_HEIGHT)

TPT_TEXT_RECT = pygame.rect.Rect(20, HEIGHT - 20 - 100, 400, 20)
AVG_TPT_TEXT_RECT = pygame.rect.Rect(20, HEIGHT - 20 - 80, 400, 20)
MAX_TPT_TEXT_RECT = pygame.rect.Rect(20, HEIGHT - 20 - 60, 400, 20)
FPT_TEXT_RECT = pygame.rect.Rect(20, HEIGHT - 20 - 40, 400, 20)
COMPUTATION_FPS_TEXT_RECT = pygame.rect.Rect(20, HEIGHT - 20 - 20, 400, 20)
MONOSPACE_FONT = pygame.font.SysFont("monospace", 20)

def on_ball_draw(win, x, y, r):
    pygame.draw.circle(win, COLOR_WHITE, (x, y), r)

def on_powerup_split_pickup(powerup):
    POWERUPS.remove(powerup)
    for ball in BALLS.copy():
        if len(BALLS) > 1e3:
            return
        for i in range(-6, 7, 12):
            BALLS.add(Ball(ball.x, ball.y, ball.radius, i, -6, on_ball_draw))

def on_powerup_triple_pickup(powerup):
    POWERUPS.remove(powerup)
    if len(BALLS) > 1e3:
        return
    for i in range(-6, 7, 6):
        BALLS.add(Ball(LINE.x + LINE.width / 2 - BALL_HEIGHT / 2, LINE.y - BALL_HEIGHT, BALL_HEIGHT / 2, i, -6, on_ball_draw))

def on_cube_colide(cube: SlopableRect):
    cube.destroy()
    CUBES.remove(cube)
    if random.randint(1, 100) <= POWERUP_CHANCE:
        if random.choice([True, False]):
            POWERUPS.add(Ball(cube.x - (POWERUP_HEIGHT - cube.width) / 2, cube.y - (POWERUP_HEIGHT - cube.height) / 2, POWERUP_HEIGHT / 2, 0, POWERUP_VELOCITY, \
                lambda win, x, y, r: win.blit(POWERUP_SPLIT_IMG, (x - r, y - r)), on_powerup_split_pickup))
        else:
            POWERUPS.add(Ball(cube.x - (POWERUP_HEIGHT - cube.width) / 2, cube.y - (POWERUP_HEIGHT - cube.height) / 2, POWERUP_HEIGHT / 2, 0, POWERUP_VELOCITY, \
                lambda win, x, y, r: win.blit(POWERUP_TRIPLE_DOWN_IMG, (x - r, y - r)), on_powerup_triple_pickup))

POWERUPS: Set[Ball] = set()
BALLS = {Ball(WIDTH / 2 - BALL_HEIGHT / 2, LINE.y - BALL_HEIGHT, BALL_HEIGHT / 2, 6, -6, on_ball_draw)}
CUBES = {SlopableRect(CUBE_PADDING + (i % CUBE_COUNT_PER_ROW) * (CUBE_PADDING + CUBE_WIDTH), CUBE_PADDING + (i // CUBE_COUNT_PER_ROW) * (CUBE_PADDING + CUBE_HEIGHT) , CUBE_WIDTH, CUBE_HEIGHT, on_cube_colide) for i in range(CUBE_COUNT)}

SlopableRect.optimize()

def handle_ball_movement(ball: Ball, obstables: Set[SlopableRect], src_set: Set[Ball]):
    if (ball.x + BALL_HEIGHT) >= WIDTH or ball.x <= 0:
        ball.velocity_x *= -1
    
    if ball.y <= 0:
        ball.velocity_y *= -1

    if ball.y > HEIGHT:
        src_set.remove(ball)

    ball.tick(obstables, {LINE})

def draw_state(tpt, avg_tpt, max_tpt, fps, computation_fps):
    WIN.fill(COLOR_BG)
    pygame.draw.rect(WIN, COLOR_WHITE, LINE)

    for cube in CUBES:
        pygame.draw.rect(WIN, COLOR_WHITE, cube)

    for ball in BALLS:
        ball.draw(WIN)

    for powerup in POWERUPS:
        powerup.draw(WIN)

    # drawing time per tick
    tpt_text = MONOSPACE_FONT.render(f"TPT: {tpt:.6f}ms", False, COLOR_WHITE)
    avg_tpt_text = MONOSPACE_FONT.render(f"Avg TPT: {avg_tpt:.6f}ms", False, COLOR_WHITE)
    max_tpt_text = MONOSPACE_FONT.render(f"Max TPT: {max_tpt:.6f}ms", False, COLOR_WHITE)
    fps_text = MONOSPACE_FONT.render(f"FPS: {fps:.0f}fps", False, COLOR_WHITE)
    computation_fps_text = MONOSPACE_FONT.render(f"Computation FPS: {computation_fps:.0f}fps", False, COLOR_WHITE)
    WIN.blit(tpt_text, TPT_TEXT_RECT)
    WIN.blit(avg_tpt_text, AVG_TPT_TEXT_RECT)
    WIN.blit(max_tpt_text, MAX_TPT_TEXT_RECT)
    WIN.blit(fps_text, FPT_TEXT_RECT)
    WIN.blit(computation_fps_text, COMPUTATION_FPS_TEXT_RECT)

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
    max_tpt = 0
    total_tpt = 0
    tpt_cnt = 0
    prev_computation_fps = 0
    worst_fps = TARGET_FPS * 2
    try:
        while running:
            clock.tick(TARGET_FPS)
            start = time.perf_counter_ns()
            for event in pygame.event.get():
                running = handle_event(event)
            
            handle_keypresses(pygame.key.get_pressed())
            LINE._calc_slopes()

            if len(BALLS) <= 0 or len(CUBES) <= 10:
                running = False

            for ball in BALLS.copy():
                handle_ball_movement(ball, CUBES, BALLS)

            for powerup in POWERUPS.copy():
                handle_ball_movement(powerup, {}, POWERUPS)

            end = time.perf_counter_ns()
            tpt = (end - start) / 1e6
            total_tpt += tpt
            tpt_cnt += 1
            max_tpt = max(tpt, max_tpt)
            if clock.get_fps() > 0:
                worst_fps = min(worst_fps, clock.get_fps())

            prev_computation_fps = (prev_computation_fps * 60 + (1 / (tpt / 1000))) / 61

            draw_state(tpt, total_tpt / tpt_cnt, max_tpt, clock.get_fps(), prev_computation_fps)
    except KeyboardInterrupt:
        pass

    print(max_tpt)
    print(worst_fps)
    # print("\n---------------- Stats ----------------")
    # print(f"{max_tpt=}ms")
    # print(f"avg_tpt={total_tpt / tpt_cnt}ms")
    # print("---------------------------------------")

if __name__ == "__main__":
    main()