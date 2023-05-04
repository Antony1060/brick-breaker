import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../build/")))

try:
    import ccollision
except:
    print("C sources not compiled! Run `make build`")
    exit(1)

from typing import Literal, Set, Union
import pygame
import random
import time

from objects import Ball
from slopeable_rect import SlopableRect

pygame.init()

MODE_EXTREME = "BB_EXTREME" in os.environ
MODE_TEST = "BB_TEST" in os.environ

WIDTH = 1280
HEIGHT = 1000 if MODE_EXTREME else 720
TARGET_FPS = 60
COLOR_BG = (10, 13, 19)
COLOR_TEXT_BG = (0, 0, 0)
COLOR_WHITE = (218, 218, 218)
LINE_WIDTH = WIDTH if MODE_TEST else 200
LINE_HEIGHT = 10
LINE_VELOCITY = 16

CUBE_WIDTH = 10
CUBE_HEIGHT = 10
CUBE_PADDING = 10
CUBE_COUNT_PER_ROW = (WIDTH - CUBE_PADDING) // (CUBE_WIDTH + CUBE_PADDING)
CUBE_COUNT = CUBE_COUNT_PER_ROW * (40 if MODE_EXTREME else 20)

BALL_HEIGHT = 12

POWERUP_CHANCE = 40 if MODE_EXTREME else 20
POWERUP_HEIGHT = 20
POWERUP_VELOCITY = 4

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Brick breaker")

POWERUP_SPLIT_IMG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "split.png")), (POWERUP_HEIGHT, POWERUP_HEIGHT))
POWERUP_TRIPLE_DOWN_IMG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "triple_down.png")), (POWERUP_HEIGHT, POWERUP_HEIGHT))

LINE = SlopableRect(WIDTH / 2 - LINE_WIDTH / 2, HEIGHT - 20 - LINE_HEIGHT, LINE_WIDTH, LINE_HEIGHT)

TITLE_FONT = pygame.font.Font(pygame.font.get_default_font(), 32)
SUBTITLE_FONT = pygame.font.Font(pygame.font.get_default_font(), 24)
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

def pad_rect(rect: pygame.Rect, padding: int):
    rect.x -= padding
    rect.y -= padding
    rect.width += padding * 2
    rect.height += padding * 2

def handle_ball_movement(ball: Ball, obstables: Set[SlopableRect], src_set: Set[Ball]):
    if (ball.x + BALL_HEIGHT) >= WIDTH or ball.x <= 0:
        ball.velocity_x *= -1
    
    if ball.y <= 0:
        ball.velocity_y *= -1

    if ball.y > HEIGHT:
        src_set.remove(ball)

    ball.tick(obstables, {LINE})

def draw_state(game_state, stats):
    WIN.fill(COLOR_BG)
    pygame.draw.rect(WIN, COLOR_WHITE, LINE)

    for cube in CUBES:
        pygame.draw.rect(WIN, COLOR_WHITE, cube)

    for ball in BALLS:
        ball.draw(WIN)

    for powerup in POWERUPS:
        powerup.draw(WIN)

    if game_state in ["won", "lost"]:
        title_state_text = TITLE_FONT.render(f"You {game_state}!", True, COLOR_WHITE)
        subtitle_state_text = SUBTITLE_FONT.render((f"{len(CUBES)} cubes left. " if game_state == "lost" else "") + "Press any key to exit.", True, COLOR_WHITE)

        title_rect = title_state_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 20))
        subtitle_rect = subtitle_state_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 20))

        title_rect_copy, subtitle_rect_copy = title_rect.copy(), subtitle_rect.copy()

        pad_rect(title_rect_copy, 10)
        pad_rect(subtitle_rect_copy, 10)

        pygame.draw.rect(WIN, COLOR_TEXT_BG, title_rect_copy, border_radius=4)
        pygame.draw.rect(WIN, COLOR_TEXT_BG, subtitle_rect_copy, border_radius=4)
        WIN.blit(title_state_text, title_rect)
        WIN.blit(subtitle_state_text, subtitle_rect)

    ## rendering stats
    tpt, avg_tpt, max_tpt, fps, computation_fps = stats
    tpt_text = MONOSPACE_FONT.render(f"TPT: {tpt:.6f}ms", False, COLOR_WHITE)
    avg_tpt_text = MONOSPACE_FONT.render(f"Avg TPT: {avg_tpt:.6f}ms", False, COLOR_WHITE)
    max_tpt_text = MONOSPACE_FONT.render(f"Max TPT: {max_tpt:.6f}ms", False, COLOR_WHITE)
    fps_text = MONOSPACE_FONT.render(f"FPS: {fps:.0f}fps", False, COLOR_WHITE)
    computation_fps_text = MONOSPACE_FONT.render(f"Computation FPS: {computation_fps:.0f}fps", False, COLOR_WHITE)
    WIN.blit(tpt_text, [20, HEIGHT - 20 - 100, 400, 20])
    WIN.blit(avg_tpt_text, [20, HEIGHT - 20 - 80, 400, 20])
    WIN.blit(max_tpt_text, [20, HEIGHT - 20 - 60, 400, 20])
    WIN.blit(fps_text, [20, HEIGHT - 20 - 40, 400, 20])
    WIN.blit(computation_fps_text, [20, HEIGHT - 20 - 20, 400, 20])

    pygame.display.update()

def handle_event(event: pygame.event.Event, game_state: Union[Literal["playing"], Literal["won"], Literal["lost"]]) -> bool:
    if event.type == pygame.KEYUP and game_state != "playing":
        return False

    if event.type == pygame.QUIT:
        return False

    return True

def adjust_line_position(keypresses):
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

    game_state: Union[Literal["playing"], Literal["won"], Literal["lost"]] = "playing"
    try:
        while running:
            clock.tick(TARGET_FPS)
            start = time.perf_counter_ns()
            for event in pygame.event.get():
                running = handle_event(event, game_state)
            
            keypresses = pygame.key.get_pressed()

            if game_state != "playing":
                draw_state(game_state, (tpt, total_tpt / tpt_cnt, max_tpt, clock.get_fps(), prev_computation_fps))
                continue

            if len(CUBES) <= 10 and MODE_TEST:
                break

            if len(CUBES) <= 0:
                game_state = "won"
                continue

            if len(BALLS) <= 0:
                game_state = "lost"
                continue

            adjust_line_position(keypresses)
            LINE._calc_slopes()

            for ball in BALLS.copy():
                handle_ball_movement(ball, CUBES, BALLS)

            for powerup in POWERUPS.copy():
                handle_ball_movement(powerup, {}, POWERUPS)

            end = time.perf_counter_ns()
            tpt = (end - start) / 1e6
            total_tpt += tpt
            tpt_cnt += 1
            max_tpt = max(tpt, max_tpt)

            prev_computation_fps = (prev_computation_fps * 60 + (1 / (tpt / 1000))) / 61

            draw_state(game_state, (tpt, total_tpt / tpt_cnt, max_tpt, clock.get_fps(), prev_computation_fps))
    except KeyboardInterrupt:
        pass

    print("\n---------------- Stats ----------------")
    print(f"{max_tpt=}ms")
    print(f"avg_tpt={total_tpt / tpt_cnt}ms")
    print("---------------------------------------")

if __name__ == "__main__":
    main()
