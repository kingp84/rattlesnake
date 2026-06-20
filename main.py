import pygame
import random
import os
from pygame.locals import *

pygame.init()
pygame.mixer.init()

# -----------------------------
# WINDOW + CLOCK
# -----------------------------
WIDTH, HEIGHT = 1000, 500
surface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rattlesnake")
clock = pygame.time.Clock()

# -----------------------------
# CONSTANTS
# -----------------------------
SEG_SIZE = 40
WALL_THICKNESS = 40
PLAY_MIN = WALL_THICKNESS
PLAY_MAX_X = WIDTH - WALL_THICKNESS - SEG_SIZE
PLAY_MAX_Y = HEIGHT - WALL_THICKNESS - SEG_SIZE
FONT = pygame.font.SysFont("arial", 24, bold=True)
BIG_FONT = pygame.font.SysFont("arial", 48, bold=True)
HIGH_SCORE_FILE = "highscore.txt"

# -----------------------------
# LOAD HIGH SCORE
# -----------------------------
def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, "r") as f:
                return int(f.read().strip())
        except:
            return 0
    return 0

def save_high_score(score):
    with open(HIGH_SCORE_FILE, "w") as f:
        f.write(str(score))

high_score = load_high_score()

# -----------------------------
# LOAD IMAGES
# -----------------------------
background = pygame.image.load("resources/background.png").convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

snake_head_original = pygame.image.load("resources/rattlesnake-head.png").convert_alpha()
snake_head_original = pygame.transform.scale(snake_head_original, (SEG_SIZE, SEG_SIZE))

snake_body_original = pygame.image.load("resources/rattlesnake-body.png").convert_alpha()
snake_body_original = pygame.transform.scale(snake_body_original, (SEG_SIZE, SEG_SIZE))

snake_tail_original = pygame.image.load("resources/rattlesnake-tail.png").convert_alpha()
snake_tail_original = pygame.transform.scale(snake_tail_original, (SEG_SIZE, SEG_SIZE))

apple_img = pygame.image.load("resources/apple.png").convert_alpha()
apple_img = pygame.transform.scale(apple_img, (30, 30))

# -----------------------------
# LOAD SOUNDS
# -----------------------------
pygame.mixer.music.load("resources/bg-music.ogg")
crash_sound = pygame.mixer.Sound("resources/crash.ogg")
dying_sound = pygame.mixer.Sound("resources/dying.ogg")

# -----------------------------
# ROTATION HELPERS
# -----------------------------
def rotate_head(direction):
    if direction == "LEFT":
        return pygame.transform.rotate(snake_head_original, 0)
    if direction == "UP":
        return pygame.transform.rotate(snake_head_original, 90)
    if direction == "RIGHT":
        return pygame.transform.rotate(snake_head_original, 180)
    if direction == "DOWN":
        return pygame.transform.rotate(snake_head_original, -90)

def rotate_segment(original, prev, curr):
    px, py = prev
    cx, cy = curr
    if px < cx:
        return pygame.transform.rotate(original, 0)
    if px > cx:
        return pygame.transform.rotate(original, 180)
    if py < cy:
        return pygame.transform.rotate(original, 90)
    if py > cy:
        return pygame.transform.rotate(original, -90)
    return original

# -----------------------------
# GAME STATE SETUP
# -----------------------------
def new_game():
    global snake_segments, direction, score, apple_pos, game_over
    global speed, speed_increment, max_speed, movement_started

    center_x = WIDTH // 2
    center_y = HEIGHT // 2

    snake_segments = [(center_x, center_y)]
    direction = "LEFT"
    score = 0
    game_over = False
    movement_started = False

    apple_pos = (
        random.randrange(PLAY_MIN + SEG_SIZE, PLAY_MAX_X - SEG_SIZE + 1, SEG_SIZE),
        random.randrange(PLAY_MIN + SEG_SIZE, PLAY_MAX_Y - SEG_SIZE + 1, SEG_SIZE)
    )

    speed = 5
    speed_increment = 0.5
    max_speed = 15

    pygame.mixer.music.play(-1)

new_game()

# -----------------------------
# BUTTONS
# -----------------------------
button_width, button_height = 180, 50
new_game_button_rect = pygame.Rect(WIDTH // 2 - button_width - 20, HEIGHT // 2 + 40, button_width, button_height)
reset_hs_button_rect = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 + 40, button_width, button_height)

# -----------------------------
# MAIN LOOP
# -----------------------------
running = True
while running:
    clock.tick(speed)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            if not game_over:
                if event.key == pygame.K_UP and direction != "DOWN":
                    direction = "UP"
                    movement_started = True
                elif event.key == pygame.K_DOWN and direction != "UP":
                    direction = "DOWN"
                    movement_started = True
                elif event.key == pygame.K_LEFT and direction != "RIGHT":
                    direction = "LEFT"
                    movement_started = True
                elif event.key == pygame.K_RIGHT and direction != "LEFT":
                    direction = "RIGHT"
                    movement_started = True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if game_over:
                if new_game_button_rect.collidepoint(event.pos):
                    new_game()
                elif reset_hs_button_rect.collidepoint(event.pos):
                    high_score = 0
                    save_high_score(high_score)

    if not game_over:

        # Always get current head position
        head_x, head_y = snake_segments[0]

        if movement_started:
            if direction == "UP":
                head_y -= SEG_SIZE
            elif direction == "DOWN":
                head_y += SEG_SIZE
            elif direction == "LEFT":
                head_x -= SEG_SIZE
            elif direction == "RIGHT":
                head_x += SEG_SIZE

        new_head = (head_x, head_y)

        # WALL COLLISION
        if head_x < PLAY_MIN or head_x > PLAY_MAX_X or head_y < PLAY_MIN or head_y > PLAY_MAX_Y:
            game_over = True
            pygame.mixer.music.stop()
            crash_sound.play()

        else:
            # SELF COLLISION (ignore head itself)
            if new_head in snake_segments[1:]:
                game_over = True
                pygame.mixer.music.stop()
                dying_sound.play()
            else:
                snake_segments.insert(0, new_head)

                apple_rect = pygame.Rect(apple_pos[0], apple_pos[1], 30, 30)
                head_rect = pygame.Rect(head_x, head_y, SEG_SIZE, SEG_SIZE)

                if head_rect.colliderect(apple_rect):
                    score += 10
                    if score > high_score:
                        high_score = score
                        save_high_score(high_score)

                    apple_pos = (
                        random.randrange(PLAY_MIN + SEG_SIZE, PLAY_MAX_X - SEG_SIZE + 1, SEG_SIZE),
                        random.randrange(PLAY_MIN + SEG_SIZE, PLAY_MAX_Y - SEG_SIZE + 1, SEG_SIZE)
                    )

                    snake_segments.append(snake_segments[-1])
                    speed = min(speed + speed_increment, max_speed)

                else:
                    snake_segments.pop()

    # DRAW EVERYTHING
    surface.blit(background, (0, 0))

    score_text = FONT.render(f"Score: {score}", True, (255, 255, 255))
    hs_text = FONT.render(f"High Score: {high_score}", True, (255, 215, 0))

    pygame.draw.rect(surface, (0, 0, 0), (10, 10, 200, 35))
    pygame.draw.rect(surface, (0, 0, 0), (220, 10, 260, 35))
    pygame.draw.rect(surface, (255, 255, 255), (10, 10, 200, 35), 2)
    pygame.draw.rect(surface, (255, 255, 255), (220, 10, 260, 35), 2)

    surface.blit(score_text, (20, 15))
    surface.blit(hs_text, (230, 15))
    surface.blit(apple_img, apple_pos)

    # DRAW SNAKE
    if snake_segments:
        head_img = rotate_head(direction)
        surface.blit(head_img, snake_segments[0])

        if len(snake_segments) > 2:
            for i in range(1, len(snake_segments) - 1):
                body_img = rotate_segment(snake_body_original, snake_segments[i - 1], snake_segments[i])
                surface.blit(body_img, snake_segments[i])

        if len(snake_segments) > 1:
            tail_img = rotate_segment(snake_tail_original, snake_segments[-2], snake_segments[-1])
            surface.blit(tail_img, snake_segments[-1])

    # GAME OVER OVERLAY
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        go_text = BIG_FONT.render("GAME OVER", True, (255, 0, 0))
        go_rect = go_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
        surface.blit(go_text, go_rect)

        pygame.draw.rect(surface, (50, 150, 50), new_game_button_rect)
        pygame.draw.rect(surface, (200, 50, 50), reset_hs_button_rect)
        pygame.draw.rect(surface, (255, 255, 255), new_game_button_rect, 2)
        pygame.draw.rect(surface, (255, 255, 255), reset_hs_button_rect, 2)

        ng_text = FONT.render("New Game", True, (255, 255, 255))
        rh_text = FONT.render("Reset High Score", True, (255, 255, 255))

        surface.blit(ng_text, (new_game_button_rect.x + 25, new_game_button_rect.y + 12))
        surface.blit(rh_text, (reset_hs_button_rect.x + 10, reset_hs_button_rect.y + 12))

    pygame.display.update()

pygame.quit()
