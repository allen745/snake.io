import pygame
import random
import sys

# ── Settings ──────────────────────────────────────────────────────────────────
COLS, ROWS = 20, 20
CELL       = 28
WIDTH      = COLS * CELL       # 560
HEIGHT     = ROWS * CELL + 60  # 620  (60 px HUD)
FPS        = 10

# Colours
BG         = (10,  10,  10)
GRID       = (22,  22,  22)
HEAD       = (61,  255, 143)   # bright green
BODY_HI    = (0,   180, 90)
BODY_LO    = (0,   80,  40)
FOOD       = (255, 70,  70)
HUD_BG     = (14,  14,  14)
TEXT_GREEN = (61,  255, 143)
TEXT_WHITE = (230, 230, 230)
TEXT_DIM   = (80,  80,  80)
OVERLAY    = (0,   0,   0,  160)

# ── Helpers ───────────────────────────────────────────────────────────────────
def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i]-c1[i])*t) for i in range(3))

def random_food(snake):
    occupied = {(s[0], s[1]) for s in snake}
    while True:
        pos = (random.randint(0, COLS-1), random.randint(0, ROWS-1))
        if pos not in occupied:
            return pos

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("SNAKE")
    clock  = pygame.time.Clock()

    try:
        font_big  = pygame.font.SysFont("Courier New", 32, bold=True)
        font_med  = pygame.font.SysFont("Courier New", 18, bold=True)
        font_sm   = pygame.font.SysFont("Courier New", 13)
    except Exception:
        font_big  = pygame.font.SysFont(None, 32)
        font_med  = pygame.font.SysFont(None, 18)
        font_sm   = pygame.font.SysFont(None, 13)

    def new_game():
        snake  = [(10,10),(9,10),(8,10)]
        direc  = (1, 0)
        nxt    = (1, 0)
        food   = random_food(snake)
        return snake, direc, nxt, food, 0

    snake, direc, nxt_dir, food, score = new_game()
    hi_score  = 0
    state     = "start"   # start | playing | paused | over
    move_tick = pygame.USEREVENT + 1
    pygame.time.set_timer(move_tick, 1000 // FPS)

    # ── draw helpers ──────────────────────────────────────────────────────────
    def draw_grid():
        for x in range(0, WIDTH, CELL):
            pygame.draw.line(screen, GRID, (x, 60), (x, HEIGHT))
        for y in range(60, HEIGHT, CELL):
            pygame.draw.line(screen, GRID, (0, y), (WIDTH, y))

    def draw_food():
        cx = food[0]*CELL + CELL//2
        cy = food[1]*CELL + CELL//2 + 60
        pygame.draw.circle(screen, FOOD, (cx, cy), CELL//2 - 3)

    def draw_snake():
        n = len(snake)
        for i, (sx, sy) in enumerate(snake):
            t   = i / max(n-1, 1)
            col = HEAD if i == 0 else lerp_color(BODY_HI, BODY_LO, t)
            pad = 2 if i > 0 else 1
            rect = pygame.Rect(sx*CELL+pad, sy*CELL+pad+60, CELL-pad*2, CELL-pad*2)
            pygame.draw.rect(screen, col, rect, border_radius=3)

    def draw_hud():
        pygame.draw.rect(screen, HUD_BG, (0, 0, WIDTH, 60))
        pygame.draw.line(screen, GRID, (0, 59), (WIDTH, 59))
        sc_label = font_sm.render("SCORE", True, TEXT_GREEN)
        sc_val   = font_med.render(str(score), True, TEXT_WHITE)
        hi_label = font_sm.render("BEST", True, TEXT_GREEN)
        hi_val   = font_med.render(str(hi_score), True, TEXT_WHITE)
        screen.blit(sc_label, (20, 10))
        screen.blit(sc_val,   (20, 28))
        screen.blit(hi_label, (WIDTH-80, 10))
        screen.blit(hi_val,   (WIDTH-80, 28))

    def draw_overlay(title, subtitle):
        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        surf.fill(OVERLAY)
        screen.blit(surf, (0, 0))
        t1 = font_big.render(title,    True, HEAD)
        t2 = font_sm.render(subtitle,  True, TEXT_DIM)
        screen.blit(t1, t1.get_rect(center=(WIDTH//2, HEIGHT//2 - 18)))
        screen.blit(t2, t2.get_rect(center=(WIDTH//2, HEIGHT//2 + 22)))

    # ── game loop ─────────────────────────────────────────────────────────────
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if state in ("start", "over"):
                        snake, direc, nxt_dir, food, score = new_game()
                        state = "playing"
                    elif state == "playing":
                        state = "paused"
                    elif state == "paused":
                        state = "playing"

                if state == "playing":
                    if event.key == pygame.K_UP    and direc != (0, 1):  nxt_dir = (0,-1)
                    if event.key == pygame.K_DOWN  and direc != (0,-1):  nxt_dir = (0, 1)
                    if event.key == pygame.K_LEFT  and direc != (1, 0):  nxt_dir = (-1,0)
                    if event.key == pygame.K_RIGHT and direc != (-1,0):  nxt_dir = (1, 0)
                    if event.key == pygame.K_w     and direc != (0, 1):  nxt_dir = (0,-1)
                    if event.key == pygame.K_s     and direc != (0,-1):  nxt_dir = (0, 1)
                    if event.key == pygame.K_a     and direc != (1, 0):  nxt_dir = (-1,0)
                    if event.key == pygame.K_d     and direc != (-1,0):  nxt_dir = (1, 0)

            if event.type == move_tick and state == "playing":
                direc = nxt_dir
                hx, hy = snake[0][0]+direc[0], snake[0][1]+direc[1]
                hit_wall = not (0 <= hx < COLS and 0 <= hy < ROWS)
                hit_self = (hx, hy) in [(s[0],s[1]) for s in snake]
                if hit_wall or hit_self:
                    hi_score = max(hi_score, score)
                    state = "over"
                else:
                    snake.insert(0, (hx, hy))
                    if (hx, hy) == food:
                        score += 1
                        food = random_food(snake)
                    else:
                        snake.pop()

        # ── draw ──────────────────────────────────────────────────────────────
        screen.fill(BG)
        draw_grid()
        draw_food()
        draw_snake()
        draw_hud()

        if state == "start":
            draw_overlay("SNAKE", "Press SPACE or ENTER to start")
        elif state == "paused":
            draw_overlay("PAUSED", "Press SPACE to continue")
        elif state == "over":
            draw_overlay(f"GAME OVER  {score}", "Press SPACE to restart")

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()