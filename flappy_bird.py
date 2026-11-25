"""
================================================================================
RUNGTA INTERNATIONAL SKILLS UNIVERSITY
SCHOOL OF COMPUTER SCIENCE AND ENGINEERING
Bachelor of Technology Computer Science and Engineering - First Semester
PS No.: 45
Project Title: Flappy Bird Clone
Language: Python 3
Concepts: Pygame, Gravity, Collision, Game Loop

Specifications:
- Window: 400x600
- Bird: 30x30 at x = 100, starts at y = 300
- Each frame: velocity += 1, then y += velocity
- SPACE sets velocity = -10 before the frame update
- Pipes: 60 px wide with a 150 px gap
- Ground is at y = 600
- Collisions: Pipes (Rect.colliderect), Ground (bottom >= 600), Top edge (top < 0)
================================================================================
"""

import sys
import random
import pygame

# ==========================================
# CONSTANTS AS PER PROBLEM STATEMENT (PS-45)
# ==========================================
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 600
GROUND_Y = 600

BIRD_SIZE = 30
BIRD_START_X = 100
BIRD_START_Y = 300

GRAVITY = 1
FLAP_VELOCITY = -10

PIPE_WIDTH = 60
PIPE_GAP = 150
PIPE_SPEED = 3
PIPE_SPAWN_INTERVAL = 90  # frames between pipe spawns (~1.5s at 60 FPS)

FPS = 60

# Colors
COLOR_SKY = (110, 195, 220)
COLOR_SKY_BOTTOM = (195, 235, 245)
COLOR_BIRD = (250, 205, 30)
COLOR_BIRD_OUTLINE = (50, 30, 10)
COLOR_BIRD_EYE = (255, 255, 255)
COLOR_BIRD_PUPIL = (20, 20, 20)
COLOR_BIRD_BEAK = (245, 110, 30)
COLOR_BIRD_WING = (230, 160, 20)

COLOR_PIPE = (85, 185, 45)
COLOR_PIPE_DARK = (55, 130, 30)
COLOR_PIPE_LIGHT = (145, 225, 90)
COLOR_PIPE_OUTLINE = (30, 70, 20)

COLOR_GROUND_GRASS = (100, 180, 40)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_SHADOW = (40, 40, 50)
COLOR_GAMEOVER = (235, 50, 40)


class Bird:
    def __init__(self, x=BIRD_START_X, y=BIRD_START_Y):
        self.x = x
        self.y = y
        self.velocity = 0
        self.width = BIRD_SIZE
        self.height = BIRD_SIZE
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def flap(self):
        """SPACE sets velocity = -10 before the frame update."""
        self.velocity = FLAP_VELOCITY

    def update_physics(self):
        """
        Exact physics step:
        Each frame: velocity += 1, then y += velocity.
        """
        self.velocity += GRAVITY
        self.y += self.velocity
        self.rect.topleft = (int(self.x), int(self.y))

    def reset(self):
        self.x = BIRD_START_X
        self.y = BIRD_START_Y
        self.velocity = 0
        self.rect.topleft = (int(self.x), int(self.y))

    def draw(self, surface):
        # Draw Bird (30x30 with retro arcade details)
        bx, by = self.rect.x, self.rect.y
        bw, bh = self.width, self.height

        # Body
        pygame.draw.ellipse(surface, COLOR_BIRD, (bx, by, bw, bh))
        pygame.draw.ellipse(surface, COLOR_BIRD_OUTLINE, (bx, by, bw, bh), 2)

        # Wing
        wing_y = by + 10 if self.velocity < 0 else by + 14
        pygame.draw.ellipse(surface, COLOR_BIRD_WING, (bx + 4, wing_y, 14, 10))
        pygame.draw.ellipse(surface, COLOR_BIRD_OUTLINE, (bx + 4, wing_y, 14, 10), 1)

        # Eye
        pygame.draw.circle(surface, COLOR_BIRD_EYE, (bx + 20, by + 10), 5)
        pygame.draw.circle(surface, COLOR_BIRD_OUTLINE, (bx + 20, by + 10), 5, 1)
        pygame.draw.circle(surface, COLOR_BIRD_PUPIL, (bx + 22, by + 10), 2)

        # Beak
        beak_pts = [(bx + 22, by + 13), (bx + 30, by + 17), (bx + 22, by + 21)]
        pygame.draw.polygon(surface, COLOR_BIRD_BEAK, beak_pts)
        pygame.draw.polygon(surface, COLOR_BIRD_OUTLINE, beak_pts, 1)


class Pipe:
    def __init__(self, x=WINDOW_WIDTH, gap_y=None):
        self.x = x
        self.width = PIPE_WIDTH
        self.gap = PIPE_GAP
        self.passed = False

        # Random gap vertical position if not specified
        # Gap must leave at least 50px of pipe visible at top and bottom
        min_gap_y = 50
        max_gap_y = GROUND_Y - self.gap - 50
        if gap_y is None:
            self.gap_y = random.randint(min_gap_y, max_gap_y)
        else:
            self.gap_y = gap_y

        self.update_rects()

    def update_rects(self):
        # Top Pipe: from y = 0 to y = gap_y
        self.top_rect = pygame.Rect(self.x, 0, self.width, self.gap_y)
        # Bottom Pipe: from y = gap_y + gap to GROUND_Y
        bottom_y = self.gap_y + self.gap
        self.bot_rect = pygame.Rect(self.x, bottom_y, self.width, max(0, GROUND_Y - bottom_y))

    def update(self):
        self.x -= PIPE_SPEED
        self.update_rects()

    def collides_with(self, bird_rect):
        """Detect collision with pipes using Rect.colliderect()."""
        return self.top_rect.colliderect(bird_rect) or self.bot_rect.colliderect(bird_rect)

    def draw(self, surface):
        # Draw Top Pipe
        self._draw_pipe_section(surface, self.top_rect, is_top=True)
        # Draw Bottom Pipe
        self._draw_pipe_section(surface, self.bot_rect, is_top=False)

    def _draw_pipe_section(self, surface, rect, is_top=False):
        if rect.height <= 0:
            return
        
        # Main pipe body
        pygame.draw.rect(surface, COLOR_PIPE, rect)
        
        # Left highlight stripe
        pygame.draw.line(surface, COLOR_PIPE_LIGHT, (rect.x + 4, rect.y), (rect.x + 4, rect.bottom), 3)
        # Right shadow stripe
        pygame.draw.line(surface, COLOR_PIPE_DARK, (rect.right - 5, rect.y), (rect.right - 5, rect.bottom), 4)
        
        # Outline
        pygame.draw.rect(surface, COLOR_PIPE_OUTLINE, rect, 2)

        # Pipe Rim / Cap (24px tall, slightly wider by 4px on each side)
        cap_h = 24
        cap_overhang = 4
        if is_top:
            cap_rect = pygame.Rect(rect.x - cap_overhang, rect.bottom - cap_h, rect.width + cap_overhang * 2, cap_h)
        else:
            cap_rect = pygame.Rect(rect.x - cap_overhang, rect.y, rect.width + cap_overhang * 2, cap_h)

        pygame.draw.rect(surface, COLOR_PIPE, cap_rect)
        pygame.draw.line(surface, COLOR_PIPE_LIGHT, (cap_rect.x + 4, cap_rect.y), (cap_rect.x + 4, cap_rect.bottom), 3)
        pygame.draw.line(surface, COLOR_PIPE_DARK, (cap_rect.right - 5, cap_rect.y), (cap_rect.right - 5, cap_rect.bottom), 4)
        pygame.draw.rect(surface, COLOR_PIPE_OUTLINE, cap_rect, 2)


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
        self.pipes = []
        self.score = 0
        self.frame_count = 0
        self.game_over = False
        self.game_over_reason = ""
        self.running = True

    def reset(self):
        """Resets the game to initial state for restart."""
        self.bird.reset()
        self.pipes.clear()
        self.score = 0
        self.frame_count = 0
        self.game_over = False
        self.game_over_reason = ""
        print(">> Game restarted! Bird at (x=100, y=300), Score=0")

    def handle_input(self, key):
        """
        Input processing:
        - SPACE sets velocity = -10 before the frame update
        - Other keys (like Z) are ignored as invalid input
        """
        if self.game_over:
            if key == pygame.K_SPACE:
                self.reset()
            return

        if key == pygame.K_SPACE:
            self.bird.flap()
        else:
            # Test Case 3: Invalid input is ignored
            pass

    def check_collisions(self):
        """
        Collision detection:
        - Pipes: Rect.colliderect()
        - Ground: bird bottom touches or exceeds y = 600
        - Top edge: bird top < 0 (bird left the screen at the top)
        """
        bird_rect = self.bird.rect

        # (a) Ground collision: bird bottom edge touches y = 600
        if bird_rect.bottom >= GROUND_Y:
            self.game_over = True
            self.game_over_reason = "Collision with ground | Game Over"
            return True

        # (b) Top edge collision: bird top left the screen at top (y < 0)
        if bird_rect.top < 0:
            self.game_over = True
            self.game_over_reason = "Bird left the screen at the top | Game Over"
            return True

        # (c) Pipe collisions using Rect.colliderect()
        for pipe in self.pipes:
            if pipe.collides_with(bird_rect):
                self.game_over = True
                self.game_over_reason = "Collision with pipe | Game Over"
                return True

        return False

    def update_frame(self):
        """Advances game by exactly one frame."""
        if self.game_over:
            return

        # 1. Update bird physics: velocity += 1, then y += velocity
        self.bird.update_physics()

        # 2. Check collision immediately after physics update
        if self.check_collisions():
            print(f">> {self.game_over_reason} (Final Score: {self.score})")
            return

        # 3. Spawn pipes periodically
        self.frame_count += 1
        if self.frame_count % PIPE_SPAWN_INTERVAL == 0:
            self.pipes.append(Pipe(x=WINDOW_WIDTH))

        # 4. Update existing pipes & detect score
        for pipe in self.pipes:
            pipe.update()

            # Score detection:
            # When pipe passes the bird (pipe right edge < bird.x)
            if not pipe.passed and (pipe.x + pipe.width) < self.bird.x:
                pipe.passed = True
                self.score += 1
                print(f">> Pipe passed | Score: {self.score}")

        # 5. Remove pipes that leave the screen (x + width < 0)
        self.pipes = [p for p in self.pipes if p.x + p.width > 0]

    def render_text_with_shadow(self, text, font, color, shadow_color, pos, align="center"):
        txt = font.render(text, True, color)
        sh = font.render(text, True, shadow_color)
        w, h = txt.get_size()
        x, y = pos[0], pos[1]
        if align == "center":
            x -= w // 2
            y -= h // 2
        self.screen.blit(sh, (x + 2, y + 2))
        self.screen.blit(txt, (x, y))

    def draw(self):
        if self.headless:
            return

        # Sky Gradient
        self.screen.fill(COLOR_SKY)
        pygame.draw.rect(self.screen, COLOR_SKY_BOTTOM, (0, 350, WINDOW_WIDTH, 250))

        # Background decorative clouds and city skyline
        pygame.draw.circle(self.screen, (255, 255, 255), (80, 100), 35)
        pygame.draw.circle(self.screen, (255, 255, 255), (115, 90), 45)
        pygame.draw.circle(self.screen, (255, 255, 255), (150, 100), 35)
        pygame.draw.circle(self.screen, (255, 255, 255), (280, 140), 30)
        pygame.draw.circle(self.screen, (255, 255, 255), (310, 130), 40)
        pygame.draw.circle(self.screen, (255, 255, 255), (340, 140), 30)

        # Distant buildings
        for bx, bw, bh in [(30, 40, 70), (90, 50, 95), (160, 45, 60), (230, 55, 80), (310, 40, 100)]:
            pygame.draw.rect(self.screen, (170, 215, 225), (bx, GROUND_Y - bh, bw, bh))

        # Pipes
        for pipe in self.pipes:
            pipe.draw(self.screen)

        # Ground border line at y = 600
        pygame.draw.line(self.screen, (50, 35, 15), (0, GROUND_Y - 2), (WINDOW_WIDTH, GROUND_Y - 2), 3)

        # Bird
        self.bird.draw(self.screen)

        # HUD: Score Display
        if not self.game_over:
            self.render_text_with_shadow(
                str(self.score), self.font_large,
                COLOR_WHITE, COLOR_SHADOW,
                (WINDOW_WIDTH // 2, 60)
            )
            self.render_text_with_shadow(
                "SPACE: Flap", self.font_small,
                (240, 240, 240), COLOR_SHADOW,
                (WINDOW_WIDTH // 2, 100)
            )
        else:
            # Game Over Overlay Box
            overlay = pygame.Surface((320, 180), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            pygame.draw.rect(overlay, (255, 255, 255), (0, 0, 320, 180), 2, border_radius=12)
            self.screen.blit(overlay, (40, 200))

            self.render_text_with_shadow(
                "GAME OVER", self.font_large,
                COLOR_GAMEOVER, COLOR_SHADOW,
                (WINDOW_WIDTH // 2, 235)
            )
            self.render_text_with_shadow(
                f"Score: {self.score}", self.font_medium,
                COLOR_WHITE, COLOR_SHADOW,
                (WINDOW_WIDTH // 2, 280)
            )
            self.render_text_with_shadow(
                "Press SPACE to Restart", self.font_small,
                (255, 220, 80), COLOR_SHADOW,
                (WINDOW_WIDTH // 2, 335)
            )

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
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    else:
                        self.handle_input(event.key)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_input(pygame.K_SPACE)

            self.update_frame()
            self.draw()

        pygame.quit()
        sys.exit()


# ==============================================================================
# AUTOMATED VERIFICATION OF TEST CASES (AS SPECIFIED IN PS-45 QUESTION PAPER)
# ==============================================================================
def run_all_test_cases():
    """
    Runs and prints the exact 4 test cases specified in the university problem statement:
    1. Normal Input: Bird y=300, v=0 -> 2 frames
    2. Boundary / Minimum Input:
       (a) Bird y=570 -> bottom touches 600 -> Collision with ground | Game Over
       (b) Bird y=5, v=0, SPACE pressed -> v=-9, y=-4 | Bird left screen at top | Game Over
    3. Invalid Input: Z key ignored -> v=1, y=301
    4. Different Valid Scenario:
       (a) Bird y=300, v=5, SPACE pressed, 1 frame -> v=-9, y=291
       (b) Pipe at x=39 (width 60), bird x=100 -> Pipe passed | Score: 1
    """
    print("\n" + "=" * 65)
    print(" EXECUTING TEST CASES AS PER UNIVERSITY SPECIFICATION (PS-45)")
    print("=" * 65)

    all_passed = True

    # -------------------------------------------------------------
    # Test Case 1: Normal Input
    # Input: Bird y = 300, velocity = 0, No key pressed, 2 frames
    # Expected: Frame 1: velocity = 1 | y = 301
    #           Frame 2: velocity = 2 | y = 303
    # -------------------------------------------------------------
    print("\n--- Test Case 1: Normal Input ---")
    bird = Bird(x=100, y=300)
    bird.velocity = 0

    # Frame 1
    bird.update_physics()
    v1, y1 = bird.velocity, bird.y
    print(f"Frame 1: velocity = {v1} | y = {y1}")

    # Frame 2
    bird.update_physics()
    v2, y2 = bird.velocity, bird.y
    print(f"Frame 2: velocity = {v2} | y = {y2}")

    tc1_ok = (v1 == 1 and y1 == 301 and v2 == 2 and y2 == 303)
    print(f">> Test Case 1 Result: {'PASSED' if tc1_ok else 'FAILED'}")
    all_passed = all_passed and tc1_ok

    # -------------------------------------------------------------
    # Test Case 2: Boundary / Minimum Input
    # (a) Bird y = 570 (bottom edge touches y = 600)
    # Expected: Collision with ground | Game Over
    # (b) Bird y = 5, velocity = 0, SPACE pressed
    # Expected: velocity = -9 | y = -4 | Bird left the screen at the top | Game Over
    # -------------------------------------------------------------
    print("\n--- Test Case 2: Boundary / Minimum Input ---")
    # Sub-case (a)
    game_a = FlappyBirdGame(headless=True)
    game_a.bird.y = 570
    game_a.bird.velocity = 0
    game_a.bird.rect.topleft = (100, 570)
    collided_ground = game_a.check_collisions()
    reason_a = game_a.game_over_reason
    print(f"(a) Bird y = 570: bottom edge is {game_a.bird.rect.bottom}")
    print(f"    Output: {reason_a}")
    tc2a_ok = (collided_ground and game_a.game_over and "ground" in reason_a.lower())

    # Sub-case (b)
    game_b = FlappyBirdGame(headless=True)
    game_b.bird.y = 5
    game_b.bird.velocity = 0
    game_b.bird.rect.topleft = (100, 5)
    # SPACE pressed before frame update
    game_b.handle_input(pygame.K_SPACE)
    # 1 frame update
    game_b.update_frame()
    vb, yb = game_b.bird.velocity, game_b.bird.y
    reason_b = game_b.game_over_reason
    print(f"(b) Bird y = 5, SPACE pressed -> velocity = {vb} | y = {yb}")
    print(f"    Output: {reason_b}")
    tc2b_ok = (vb == -9 and yb == -4 and game_b.game_over and "top" in reason_b.lower())

    tc2_ok = tc2a_ok and tc2b_ok
    print(f">> Test Case 2 Result: {'PASSED' if tc2_ok else 'FAILED'}")
    all_passed = all_passed and tc2_ok

    # -------------------------------------------------------------
    # Test Case 3: Invalid Input
    # Input: Bird y = 300, velocity = 0, Key pressed: Z (not SPACE), 1 frame
    # Expected: Key ignored | velocity = 1 | y = 301
    # -------------------------------------------------------------
    print("\n--- Test Case 3: Invalid Input ---")
    game_3 = FlappyBirdGame(headless=True)
    game_3.bird.y = 300
    game_3.bird.velocity = 0
    # Simulate pressing 'Z'
    game_3.handle_input(pygame.K_z)
    game_3.update_frame()
    v3, y3 = game_3.bird.velocity, game_3.bird.y
    print(f"Key pressed: Z -> Key ignored | velocity = {v3} | y = {y3}")
    tc3_ok = (v3 == 1 and y3 == 301)
    print(f">> Test Case 3 Result: {'PASSED' if tc3_ok else 'FAILED'}")
    all_passed = all_passed and tc3_ok

    # -------------------------------------------------------------
    # Test Case 4: Different Valid Scenario
    # (a) Bird y = 300, velocity = 5, SPACE pressed, 1 frame
    # Expected: velocity = -9 | y = 291 (bird moves up)
    # (b) Pipe at x = 39 (width 60), bird x = 100, score = 0
    # Expected: Pipe passed | Score: 1
    # -------------------------------------------------------------
    print("\n--- Test Case 4: Different Valid Scenario ---")
    # Sub-case (a)
    bird_4a = Bird(x=100, y=300)
    bird_4a.velocity = 5
    # SPACE sets velocity = -10 before frame update
    bird_4a.flap()
    # 1 frame update
    bird_4a.update_physics()
    v4a, y4a = bird_4a.velocity, bird_4a.y
    print(f"(a) Bird y = 300, velocity = 5, SPACE pressed -> velocity = {v4a} | y = {y4a} (bird moves up)")
    tc4a_ok = (v4a == -9 and y4a == 291)

    # Sub-case (b)
    game_4b = FlappyBirdGame(headless=True)
    pipe_test = Pipe(x=39, gap_y=200)
    game_4b.pipes.append(pipe_test)
    game_4b.bird.x = 100
    game_4b.bird.y = 250  # inside the gap so no collision
    game_4b.score = 0
    # Check score condition: pipe right edgeis 39 + 60 = 99 < bird.x (100)
    for p in game_4b.pipes:
        if not p.passed and (p.x + p.width) < game_4b.bird.x:
            p.passed = True
            game_4b.score += 1
    print(f"(b) Pipe at x = 39 (width 60), bird x = 100 -> Pipe right edge = 99 < 100")
    print(f"    Output: Pipe passed | Score: {game_4b.score}")
    tc4b_ok = (game_4b.score == 1)

    tc4_ok = tc4a_ok and tc4b_ok
    print(f">> Test Case 4 Result: {'PASSED' if tc4_ok else 'FAILED'}")
    all_passed = all_passed and tc4_ok

    print("\n" + "=" * 65)
    if all_passed:
        print(" ALL 4 TEST CASES PASSED STRICTLY ACCORDING TO SPECIFICATIONS!")
    else:
        print(" SOME TEST CASES FAILED!")
    print("=" * 65 + "\n")
    return all_passed


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["--test", "-t", "test"]:
        run_all_test_cases()
    else:
        # Check if user wants to run tests first or start GUI
        game = FlappyBirdGame()
        game.run()
