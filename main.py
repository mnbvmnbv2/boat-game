import sys
import random
from math import sqrt

from dataclasses import dataclass

import numpy as np
import pygame

# Screen dimensions
pygame.init()

info = pygame.display.Info()
SCALE = 20
WIDTH = 48
HEIGHT = 36
WINDOW_SIZE = WIDTH * SCALE, HEIGHT * SCALE

FRAME_RATE_UPDATE = 5  # input in ms
FPS = 1000 // FRAME_RATE_UPDATE

G = 360.0

NUM_DROPS = 500


class Color:
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    BLACK = (0, 0, 0)


COLORS = {k: v for k, v in vars(Color).items() if isinstance(v, tuple)}
del COLORS["WHITE"]


@dataclass
class View:
    screen: pygame.Surface
    game_surface: pygame.Surface
    clock: pygame.time.Clock
    current_time: int = 0


@dataclass
class Drop:
    x: float
    y: float
    radius: float
    x_vel: float = 0.0
    y_vel: float = 0.0
    color: tuple[int, int, int] = Color.RED


@dataclass
class GameState:
    drops: list[Drop]


def coord_flip(x: float, y: float) -> tuple[float, float]:
    y = WINDOW_SIZE[1] - y
    return x, y


def drop_update(drops: list[Drop], time_delta: int) -> list[Drop]:
    # add accelleration
    for drop in drops:
        drop.y_vel -= G * (time_delta / 1000)

    # move position
    for idx, drop in enumerate(drops):
        new_x = drop.x + drop.x_vel * (time_delta / 1000)
        new_y = drop.y + drop.y_vel * (time_delta / 1000)
        for other_idx, other_drop in enumerate(drops):
            if idx == other_idx:
                continue
            center_distance = sqrt((new_x - other_drop.x) ** 2 + (new_y - other_drop.y) ** 2)
            if center_distance <= (drop.radius + other_drop.radius):
                drop.x_vel = -drop.x_vel / 2
                drop.y_vel = -drop.y_vel / 2
                break

        out_right = new_x + drop.radius >= WINDOW_SIZE[0]
        out_left = new_x - drop.radius < 0
        if out_right or out_left:
            drop.x_vel = 0
            drop.x = max(drop.radius, min(WINDOW_SIZE[0] - drop.radius, new_x))
        out_top = new_y - drop.radius < 0
        out_bottom = new_y + drop.radius >= WINDOW_SIZE[1]
        if out_bottom or out_top:
            drop.y_vel = 0
            drop.y = max(drop.radius, min(WINDOW_SIZE[1] - drop.radius, new_y))
        drop.x += drop.x_vel * (time_delta / 1000)
        drop.y += drop.y_vel * (time_delta / 1000)

    return drops


def main():
    mc = View(
        pygame.display.set_mode(WINDOW_SIZE),
        pygame.Surface((WIDTH, HEIGHT)),
        pygame.time.Clock(),
        0,
    )

    drops = []
    for i in range(NUM_DROPS):
        drops.append(
            Drop(
                random.randint(0, WINDOW_SIZE[0]),
                random.randint(0, WINDOW_SIZE[1]),
                random.randint(1, 4),
                x_vel=random.randint(-100, 100),
                color=random.choice(list(COLORS.values())),
            )
        )

    gs = GameState(
        drops=drops,
    )
    pygame.display.set_caption("Boat Game")

    # Main game loop
    while True:
        time_delta = mc.clock.tick(1000 // FRAME_RATE_UPDATE)
        mc.current_time += time_delta
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        mc.game_surface.fill(Color.WHITE)

        draw(mc, gs)
        gs.drops = drop_update(gs.drops, time_delta)

        # write fps on screen
        fps = int(mc.clock.get_fps())
        pygame.display.set_caption(f"Boat Game - FPS: {fps}")


def draw(mc: View, gs: GameState) -> None:
    scaled_surface = pygame.transform.scale(mc.game_surface, WINDOW_SIZE)

    for drop in gs.drops:
        pygame.draw.circle(
            scaled_surface, drop.color, coord_flip(drop.x, drop.y), drop.radius
        )

    mc.screen.blit(scaled_surface, (0, 0))

    pygame.display.flip()


if __name__ == "__main__":
    main()
