import pygame, math, itertools

WIDTH, HEIGHT = 320, 180  # design res
WATER_Y = 90  # baseline water line (in pixels)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


class Water:
    def __init__(self):
        self.phase = 0
        self.col_top = (64, 156, 215)  # sky-blue crest
        self.col_body = (14, 110, 192)  # mid-blue
        self.col_deep = (5, 54, 148)  # deep blue

    def update(self, dt: float):
        self.phase += dt * 0.8  # wave speed

    def draw(self, surf: pygame.Surface):
        # 1-pixel-tall strips form a sine wave
        for y in range(HEIGHT - WATER_Y):
            wave = int(4 * math.sin((y * 0.1) + self.phase))
            colour = lerp(self.col_body, self.col_deep, y / (HEIGHT - WATER_Y))
            pygame.draw.line(
                surf, colour, (0 + wave, WATER_Y + y), (WIDTH + wave, WATER_Y + y)
            )
        # thin highlight at crest
        pygame.draw.line(surf, self.col_top, (0, WATER_Y - 1), (WIDTH, WATER_Y - 1))


water = Water()

pygame.init()
WIN = pygame.display.set_mode((WIDTH * 4, HEIGHT * 4), pygame.SCALED)  # auto-upscale
GAME = pygame.Surface((WIDTH, HEIGHT)).convert()

clock = pygame.time.Clock()
running = True

while running:
    dt = clock.tick(60) / 1000  # seconds
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    # -- update phase --
    water.update(dt)

    # -- draw phase (bottom → top) --
    GAME.fill((84, 175, 245))  # sky gradient could replace this
    water.draw(GAME)

    # upscale once and display
    pygame.transform.scale(GAME, WIN.get_size(), WIN)
    pygame.display.flip()

pygame.quit()
