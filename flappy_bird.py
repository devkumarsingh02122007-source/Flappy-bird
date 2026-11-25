
import sys
import random
import pygame

# Constants (PS-45 Specifications)
WINDOW_WIDTH, WINDOW_HEIGHT, GROUND_Y = 400, 600, 600
BIRD_SIZE, BIRD_START_X, BIRD_START_Y = 30, 100, 300
GRAVITY, FLAP_VELOCITY = 1, -10
PIPE_WIDTH, PIPE_GAP, PIPE_SPEED, PIPE_SPAWN_INTERVAL = 60, 150, 3, 90
FPS = 60

# Colors
COLOR_SKY, COLOR_SKY_BOTTOM = (110, 195, 220), (195, 235, 245)
COLOR_BIRD, COLOR_BIRD_OUTLINE = (250, 205, 30), (50, 30, 10)
COLOR_BIRD_EYE, COLOR_BIRD_PUPIL = (255, 255, 255), (20, 20, 20)
COLOR_BIRD_BEAK, COLOR_BIRD_WING = (245, 110, 30), (230, 160, 20)
COLOR_PIPE, COLOR_PIPE_DARK = (85, 185, 45), (55, 130, 30)
COLOR_PIPE_LIGHT, COLOR_PIPE_OUTLINE = (145, 225, 90), (30, 70, 20)
COLOR_GROUND_GRASS = (100, 180, 40)
COLOR_WHITE, COLOR_BLACK, COLOR_SHADOW, COLOR_GAMEOVER = (255, 255, 255), (0, 0, 0), (40, 40, 50), (235, 50, 40)


class Bird:
    def __init__(self, x=BIRD_START_X, y=BIRD_START_Y):
        self.x, self.y, self.velocity = x, y, 0
        self.width = self.height = BIRD_SIZE
        self.rect = pygame.Rect(x, y, BIRD_SIZE, BIRD_SIZE)

    def flap(self):
        """SPACE sets velocity = -10 before the frame update."""
        self.velocity = FLAP_VELOCITY

    def update_physics(self):
        """Each frame: velocity += 1, then y += velocity."""
        self.velocity += GRAVITY
        self.y += self.velocity
        self.rect.topleft = (int(self.x), int(self.y))

    def reset(self):
        self.x, self.y, self.velocity = BIRD_START_X, BIRD_START_Y, 0
        self.rect.topleft = (int(self.x), int(self.y))

    def draw(self, surface):
        bx, by = self.rect.x, self.rect.y
        wing_y = by + (10 if self.velocity < 0 else 14)
        for color, rect, width in [
            (COLOR_BIRD, (bx, by, self.width, self.height), 0),
            (COLOR_BIRD_OUTLINE, (bx, by, self.width, self.height), 2),
            (COLOR_BIRD_WING, (bx + 4, wing_y, 14, 10), 0),
            (COLOR_BIRD_OUTLINE, (bx + 4, wing_y, 14, 10), 1),
        ]:
            pygame.draw.ellipse(surface, color, rect, width)
        pygame.draw.circle(surface, COLOR_BIRD_EYE, (bx + 20, by + 10), 5)
        pygame.draw.circle(surface, COLOR_BIRD_OUTLINE, (bx + 20, by + 10), 5, 1)
        pygame.draw.circle(surface, COLOR_BIRD_PUPIL, (bx + 22, by + 10), 2)
        beak = [(bx + 22, by + 13), (bx + 30, by + 17), (bx + 22, by + 21)]
        pygame.draw.polygon(surface, COLOR_BIRD_BEAK, beak)
        pygame.draw.polygon(surface, COLOR_BIRD_OUTLINE, beak, 1)


class Pipe:
    def __init__(self, x=WINDOW_WIDTH, gap_y=None):
        self.x, self.width, self.gap, self.passed = x, PIPE_WIDTH, PIPE_GAP, False
        self.gap_y = random.randint(50, GROUND_Y - self.gap - 50) if gap_y is None else gap_y
        self.update_rects()

    def update_rects(self):
        self.top_rect = pygame.Rect(self.x, 0, self.width, self.gap_y)
        bottom_y = self.gap_y + self.gap
        self.bot_rect = pygame.Rect(self.x, bottom_y, self.width, max(0, GROUND_Y - bottom_y))

    def update(self):
        self.x -= PIPE_SPEED
        self.update_rects()

    def collides_with(self, bird_rect):
        """Detect collision with pipes using Rect.colliderect()."""
        return self.top_rect.colliderect(bird_rect) or self.bot_rect.colliderect(bird_rect)

    def draw(self, surface):
        self._draw_pipe_section(surface, self.top_rect, is_top=True)
        self._draw_pipe_section(surface, self.bot_rect, is_top=False)

    def _draw_pipe_section(self, surface, rect, is_top=False):
        if rect.height <= 0:
            return
        cap_h, over = 24, 4
        cap_y = rect.bottom - cap_h if is_top else rect.y
        cap_rect = pygame.Rect(rect.x - over, cap_y, rect.width + over * 2, cap_h)
        for r in (rect, cap_rect):
            pygame.draw.rect(surface, COLOR_PIPE, r)
            pygame.draw.line(surface, COLOR_PIPE_LIGHT, (r.x + 4, r.y), (r.x + 4, r.bottom), 3)
            pygame.draw.line(surface, COLOR_PIPE_DARK, (r.right - 5, r.y), (r.right - 5, r.bottom), 4)
            pygame.draw.rect(surface, COLOR_PIPE_OUTLINE, r, 2)


class FlappyBirdGame:
    def __init__(self, headless=False):
        self.headless = headless
        if not headless:
            pygame.init()
            pygame.font.init()
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            pygame.display.set_caption("Flappy Bird Clone - PS No. 45")
            self.clock = pygame.time.Clock()
            self.font_large = pygame.font.SysFont("impact", 42)
            self.font_medium = pygame.font.SysFont("impact", 26)
            self.font_small = pygame.font.SysFont("arial", 16, bold=True)

        self.bird = Bird()
        self.pipes, self.score, self.frame_count = [], 0, 0
        self.game_over, self.game_over_reason, self.running = False, "", True

    def reset(self):
        """Resets the game to initial state for restart."""
        self.bird.reset()
        self.pipes.clear()
        self.score = self.frame_count = 0
        self.game_over, self.game_over_reason = False, ""
        print(">> Game restarted! Bird at (x=100, y=300), Score=0")

    def handle_input(self, key):
        """SPACE flaps (or restarts on Game Over); other keys are ignored."""
        if key == pygame.K_SPACE:
            self.reset() if self.game_over else self.bird.flap()

    def check_collisions(self):
        """Checks ground (bottom >= 600), top edge (top < 0), and pipes (colliderect)."""
        r = self.bird.rect
        reason = None
        if r.bottom >= GROUND_Y:
            reason = "Collision with ground | Game Over"
        elif r.top < 0:
            reason = "Bird left the screen at the top | Game Over"
        elif any(p.collides_with(r) for p in self.pipes):
            reason = "Collision with pipe | Game Over"
        if reason:
            self.game_over, self.game_over_reason = True, reason
            return True
        return False

    def update_frame(self):
        """Advances game by exactly one frame."""
        if self.game_over:
            return
        self.bird.update_physics()
        if self.check_collisions():
            print(f">> {self.game_over_reason} (Final Score: {self.score})")
            return

        self.frame_count += 1
        if self.frame_count % PIPE_SPAWN_INTERVAL == 0:
            self.pipes.append(Pipe(x=WINDOW_WIDTH))

        for pipe in self.pipes:
            pipe.update()
            if not pipe.passed and (pipe.x + pipe.width) < self.bird.x:
                pipe.passed = True
                self.score += 1
                print(f">> Pipe passed | Score: {self.score}")

        self.pipes = [p for p in self.pipes if p.x + p.width > 0]

    def render_text_with_shadow(self, text, font, color, shadow_color, pos, align="center"):
        txt, sh = font.render(text, True, color), font.render(text, True, shadow_color)
        x, y = pos
        if align == "center":
            w, h = txt.get_size()
            x, y = x - w // 2, y - h // 2
        self.screen.blit(sh, (x + 2, y + 2))
        self.screen.blit(txt, (x, y))

    def draw(self):
        if self.headless:
            return
        self.screen.fill(COLOR_SKY)
        pygame.draw.rect(self.screen, COLOR_SKY_BOTTOM, (0, 350, WINDOW_WIDTH, 250))

        for cx, cy, cr in [(80, 100, 35), (115, 90, 45), (150, 100, 35), (280, 140, 30), (310, 130, 40), (340, 140, 30)]:
            pygame.draw.circle(self.screen, COLOR_WHITE, (cx, cy), cr)
        for bx, bw, bh in [(30, 40, 70), (90, 50, 95), (160, 45, 60), (230, 55, 80), (310, 40, 100)]:
            pygame.draw.rect(self.screen, (170, 215, 225), (bx, GROUND_Y - bh, bw, bh))

        for pipe in self.pipes:
            pipe.draw(self.screen)
        pygame.draw.line(self.screen, (50, 35, 15), (0, GROUND_Y - 2), (WINDOW_WIDTH, GROUND_Y - 2), 3)
        self.bird.draw(self.screen)

        if not self.game_over:
            self.render_text_with_shadow(str(self.score), self.font_large, COLOR_WHITE, COLOR_SHADOW, (WINDOW_WIDTH // 2, 60))
            self.render_text_with_shadow("SPACE: Flap", self.font_small, (240, 240, 240), COLOR_SHADOW, (WINDOW_WIDTH // 2, 100))
        else:
            overlay = pygame.Surface((320, 180), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            pygame.draw.rect(overlay, COLOR_WHITE, (0, 0, 320, 180), 2, border_radius=12)
            self.screen.blit(overlay, (40, 200))
            self.render_text_with_shadow("GAME OVER", self.font_large, COLOR_GAMEOVER, COLOR_SHADOW, (WINDOW_WIDTH // 2, 235))
            self.render_text_with_shadow(f"Score: {self.score}", self.font_medium, COLOR_WHITE, COLOR_SHADOW, (WINDOW_WIDTH // 2, 280))
            self.render_text_with_shadow("Press SPACE to Restart", self.font_small, (255, 220, 80), COLOR_SHADOW, (WINDOW_WIDTH // 2, 335))

        pygame.display.flip()

    def run(self):
        """Main game loop."""
        print("==========================================================")
        print(" Starting Flappy Bird Game (PS No. 45 - Python 3 / Pygame)")
        print(" Window: 400x600 | Bird: 30x30 at (100, 300) | Ground: y=600")
        print(" Controls: SPACE = Flap / Restart, ESC = Exit")
        print("==========================================================")

        while self.running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_input(event.key)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_input(pygame.K_SPACE)
            self.update_frame()
            self.draw()

        pygame.quit()
        sys.exit()


def run_all_test_cases():
    """Runs and prints the 4 test cases specified in the university problem statement (PS-45)."""
    print("\n" + "=" * 65)
    print(" EXECUTING TEST CASES AS PER UNIVERSITY SPECIFICATION (PS-45)")
    print("=" * 65)
    all_passed = True

    def report(label, passed):
        nonlocal all_passed
        print(f">> {label} Result: {'PASSED' if passed else 'FAILED'}")
        all_passed = all_passed and passed

    # Test Case 1: Normal Input
    print("\n--- Test Case 1: Normal Input ---")
    bird = Bird(x=100, y=300)
    bird.update_physics()
    v1, y1 = bird.velocity, bird.y
    print(f"Frame 1: velocity = {v1} | y = {y1}")
    bird.update_physics()
    v2, y2 = bird.velocity, bird.y
    print(f"Frame 2: velocity = {v2} | y = {y2}")
    report("Test Case 1", v1 == 1 and y1 == 301 and v2 == 2 and y2 == 303)

    # Test Case 2: Boundary / Minimum Input
    print("\n--- Test Case 2: Boundary / Minimum Input ---")
    game_a = FlappyBirdGame(headless=True)
    game_a.bird.y = 570
    game_a.bird.rect.topleft = (100, 570)
    collided_ground = game_a.check_collisions()
    reason_a = game_a.game_over_reason
    print(f"(a) Bird y = 570: bottom edge is {game_a.bird.rect.bottom}")
    print(f"    Output: {reason_a}")
    tc2a_ok = collided_ground and game_a.game_over and "ground" in reason_a.lower()

    game_b = FlappyBirdGame(headless=True)
    game_b.bird.y = 5
    game_b.bird.rect.topleft = (100, 5)
    game_b.handle_input(pygame.K_SPACE)
    game_b.update_frame()
    vb, yb = game_b.bird.velocity, game_b.bird.y
    reason_b = game_b.game_over_reason
    print(f"(b) Bird y = 5, SPACE pressed -> velocity = {vb} | y = {yb}")
    print(f"    Output: {reason_b}")
    tc2b_ok = vb == -9 and yb == -4 and game_b.game_over and "top" in reason_b.lower()
    report("Test Case 2", tc2a_ok and tc2b_ok)

    # Test Case 3: Invalid Input
    print("\n--- Test Case 3: Invalid Input ---")
    game_3 = FlappyBirdGame(headless=True)
    game_3.handle_input(pygame.K_z)
    game_3.update_frame()
    v3, y3 = game_3.bird.velocity, game_3.bird.y
    print(f"Key pressed: Z -> Key ignored | velocity = {v3} | y = {y3}")
    report("Test Case 3", v3 == 1 and y3 == 301)

    # Test Case 4: Different Valid Scenario
    print("\n--- Test Case 4: Different Valid Scenario ---")
    bird_4a = Bird(x=100, y=300)
    bird_4a.velocity = 5
    bird_4a.flap()
    bird_4a.update_physics()
    v4a, y4a = bird_4a.velocity, bird_4a.y
    print(f"(a) Bird y = 300, velocity = 5, SPACE pressed -> velocity = {v4a} | y = {y4a} (bird moves up)")
    tc4a_ok = v4a == -9 and y4a == 291

    game_4b = FlappyBirdGame(headless=True)
    game_4b.pipes.append(Pipe(x=39, gap_y=200))
    game_4b.bird.y = 250
    for p in game_4b.pipes:
        if not p.passed and (p.x + p.width) < game_4b.bird.x:
            p.passed = True
            game_4b.score += 1
    print("(b) Pipe at x = 39 (width 60), bird x = 100 -> Pipe right edge = 99 < 100")
    print(f"    Output: Pipe passed | Score: {game_4b.score}")
    report("Test Case 4", tc4a_ok and game_4b.score == 1)

    print("\n" + "=" * 65)
    print(" ALL 4 TEST CASES PASSED STRICTLY ACCORDING TO SPECIFICATIONS!" if all_passed else " SOME TEST CASES FAILED!")
    print("=" * 65 + "\n")
    return all_passed


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["--test", "-t", "test"]:
        run_all_test_cases()
    else:
        FlappyBirdGame().run()
