import pygame
import pygame.gfxdraw as gfx
import math
import random

"""
water_system.py – v2.2
======================
Patch notes
-----------
* **Fix** : swapped out `gfx.aalines` (doesn’t exist) for `pygame.draw.aalines`.
  Anti‑aliased outline and crest now render without crashing.
* No other functional changes.

Usage
-----
Run this file directly to see the demo:
    • **Left‑click**  → splash / cannonball impact.
    • **Right‑click** → cycle Calm → Breezy → Stormy sea states.
"""

WIDTH, HEIGHT = 320, 180  # internal resolution
WATER_Y = 90  # still‑water level (pixels from top)
POINT_SPACING = 4  # horizontal distance between sim points


# ──────────────────────────────────────────────────────────────────────────────
#  WEATHER PRESETS
# ──────────────────────────────────────────────────────────────────────────────
class Weather:
    def __init__(
        self,
        amp1,
        wave1,
        speed1,
        amp2,
        wave2,
        speed2,
        colour_top,
        colour_mid,
        colour_deep,
    ):
        self.amp1, self.wave1, self.speed1 = amp1, wave1, speed1
        self.amp2, self.wave2, self.speed2 = amp2, wave2, speed2
        self.col_top = pygame.Color(*colour_top)
        self.col_mid = pygame.Color(*colour_mid)
        self.col_deep = pygame.Color(*colour_deep)


CALM = Weather(2, 90, 0.10, 1, 45, 0.16, (84, 175, 245), (25, 117, 202), (8, 63, 158))
BREEZY = Weather(4, 60, 0.25, 2, 30, 0.31, (76, 165, 225), (20, 102, 188), (6, 52, 152))
STORMY = Weather(
    7, 40, 0.45, 3, 22, 0.60, (160, 200, 235), (35, 80, 150), (10, 35, 110)
)
NEXT_WEATHER = {CALM: BREEZY, BREEZY: STORMY, STORMY: CALM}


# ──────────────────────────────────────────────────────────────────────────────
#  WATER HEIGHT‑FIELD
# ──────────────────────────────────────────────────────────────────────────────
class Water:
    """1‑D spring‑mass chain with base swell and local disturbances."""

    def __init__(self, profile: Weather):
        self.set_profile(profile)
        self.num_pts = WIDTH // POINT_SPACING + 1
        self.y_disp = [0.0] * self.num_pts
        self.vel = [0.0] * self.num_pts
        # tuneables
        self.tension = 160.0
        self.spread = 50.0
        self.damp = 9.0
        self.ph1 = self.ph2 = 0.0

    def set_profile(self, profile: Weather):
        self.profile = profile

    # External interaction -------------------------------------------------
    def disturb(self, x: float, magnitude: float = 30.0):
        idx = int(x / POINT_SPACING)
        if 0 <= idx < self.num_pts:
            self.vel[idx] -= magnitude

    # Simulation -----------------------------------------------------------
    def update(self, dt: float):
        self.ph1 += self.profile.speed1 * dt
        self.ph2 += self.profile.speed2 * dt
        targets = [
            self.profile.amp1
            * math.sin(i * POINT_SPACING / self.profile.wave1 + self.ph1)
            + self.profile.amp2
            * math.sin(i * POINT_SPACING / self.profile.wave2 + self.ph2)
            for i in range(self.num_pts)
        ]
        for i in range(self.num_pts):
            force = self.tension * (self.y_disp[i] - targets[i])
            if i > 0:
                force += self.spread * (self.y_disp[i] - self.y_disp[i - 1])
            if i < self.num_pts - 1:
                force += self.spread * (self.y_disp[i] - self.y_disp[i + 1])
            self.vel[i] -= force * dt
            self.vel[i] *= math.exp(-self.damp * dt)
            self.y_disp[i] += self.vel[i] * dt

    # Rendering ------------------------------------------------------------
    def draw(self, surf: pygame.Surface):
        surface_pts = [
            (i * POINT_SPACING, WATER_Y + self.y_disp[i]) for i in range(self.num_pts)
        ]
        poly = surface_pts + [(WIDTH, HEIGHT), (0, HEIGHT)]

        # solid fill
        gfx.filled_polygon(surf, poly, self.profile.col_deep)

        # gradient by scanline (light → dark)
        body_h = HEIGHT - WATER_Y
        for dy in range(body_h):
            t = dy / body_h
            col = pygame.Color.lerp(self.profile.col_mid, self.profile.col_deep, t)
            surf.fill(col, (0, WATER_Y + dy, WIDTH, 1))

        # AA outline + crest highlight
        pygame.draw.aalines(surf, self.profile.col_mid, False, surface_pts)
        highlight = [(x, y - 1) for x, y in surface_pts]
        pygame.draw.aalines(surf, self.profile.col_top, False, highlight)


# ──────────────────────────────────────────────────────────────────────────────
#  SPLASH PARTICLES
# ──────────────────────────────────────────────────────────────────────────────
class SplashParticle(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float):
        super().__init__()
        self.image = pygame.Surface((2, 2), pygame.SRCALPHA)
        self.image.fill((230, 240, 255))
        self.rect = self.image.get_rect(center=(x, y))
        angle = random.uniform(-2.2, -1.0)
        speed = random.uniform(30, 90)
        self.vel = pygame.math.Vector2(speed * math.cos(angle), speed * math.sin(angle))
        self.gravity = 120
        self.life = 1.2

    def update(self, dt):
        self.vel.y += self.gravity * dt
        self.rect.x += self.vel.x * dt
        self.rect.y += self.vel.y * dt
        self.life -= dt
        if self.life <= 0:
            self.kill()


class SplashManager(pygame.sprite.Group):
    def __init__(self, water: Water):
        super().__init__()
        self.water = water

    def splash(self, x: float, magnitude: float = 38.0):
        self.water.disturb(x, magnitude)
        y_surface = WATER_Y + self.water.y_disp[int(x / POINT_SPACING)] - 2
        for _ in range(28):
            self.add(SplashParticle(x, y_surface))


# ──────────────────────────────────────────────────────────────────────────────
#  QUICK DEMO
# ──────────────────────────────────────────────────────────────────────────────


def main():
    pygame.init()
    window = pygame.display.set_mode((WIDTH * 4, HEIGHT * 4), pygame.SCALED)
    surf = pygame.Surface((WIDTH, HEIGHT)).convert()
    clock = pygame.time.Clock()

    water = Water(CALM)
    spl_mgr = SplashManager(water)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                x_int = e.pos[0] / (window.get_width() / WIDTH)
                spl_mgr.splash(x_int)
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 3:
                water.set_profile(NEXT_WEATHER[water.profile])

        water.update(dt)
        spl_mgr.update(dt)

        surf.fill((84, 175, 245))
        water.draw(surf)
        spl_mgr.draw(surf)

        pygame.transform.scale(surf, window.get_size(), window)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
