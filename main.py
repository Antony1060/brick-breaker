import pygame
import os
import random

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

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Igra")

BALL_IMG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "circle.png")), (BALL_HEIGHT, BALL_HEIGHT))

BALLS = [[pygame.rect.Rect(WIDTH / 2 - BALL_HEIGHT / 2, HEIGHT - 20 - LINE_HEIGHT - BALL_HEIGHT, BALL_HEIGHT, BALL_HEIGHT), random.choice([1, -1]) * 4, random.choice([-3, -4, -5, -6])]]
CUBES = [pygame.rect.Rect(CUBE_PADDING + (i % CUBE_COUNT_PER_ROW) * (CUBE_PADDING + CUBE_WIDTH), CUBE_PADDING + (i // CUBE_COUNT_PER_ROW) * (CUBE_PADDING + CUBE_HEIGHT) , CUBE_WIDTH, CUBE_HEIGHT) for i in range(CUBE_COUNT)]

LINE = pygame.rect.Rect(WIDTH / 2 - LINE_WIDTH / 2, HEIGHT - 20 - LINE_HEIGHT, LINE_WIDTH, LINE_HEIGHT)

def handle_ball_movement(ball_tuple):
    ball = ball_tuple[0]

    if (ball.x + BALL_HEIGHT) >= WIDTH or ball.x <= 0:
        ball_tuple[1] *= -1
    
    if ball.y <= 0:
        ball_tuple[2] *= -1

    if LINE.colliderect(ball):
        ball_tuple[2] *= -1

def draw_state():
    WIN.fill(COLOR_BG)
    pygame.draw.rect(WIN, COLOR_WHITE, LINE)

    for cube in CUBES:
        pygame.draw.rect(WIN, COLOR_WHITE, cube)

    for ball in BALLS:
        handle_ball_movement(ball)
        ball[0].x += ball[1]
        ball[0].y += ball[2]
        WIN.blit(BALL_IMG, (ball[0].x, ball[0].y))

    pygame.display.update()

def handle_event(event: pygame.event.Event) -> bool:
    if event.type == pygame.QUIT:
        return False

    return True

def handle_keypresses(keypresses):
    if keypresses[pygame.K_d]:
        LINE.x = max(20, min(WIDTH - LINE_WIDTH - 20, LINE.x + LINE_VELOCITY))
    elif keypresses[pygame.K_a]:
        LINE.x = max(20, min(WIDTH - LINE_WIDTH - 20, LINE.x - LINE_VELOCITY))

def main():
    clock = pygame.time.Clock()
    running = True
    while running:
        clock.tick(TARGET_FPS)
        for event in pygame.event.get():
            running = handle_event(event)
        
        handle_keypresses(pygame.key.get_pressed())
        
        draw_state()

if __name__ == "__main__":
    main()