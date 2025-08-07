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


class Color:
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    BLACK = (0, 0, 0)


COLORS = {k: v for k, v in vars(Color).items() if isinstance(v, tuple)}
del COLORS["WHITE"]
print(list(COLORS.values()))


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
    grid: np.ndarray
    drops: list[Drop]


def coord_flip(x: float, y: float) -> tuple[float, float]:
    y = WINDOW_SIZE[1] - y
    return x, y


def sand_update(grid: np.ndarray) -> np.ndarray:
    occupied = np.where(grid)
    h, w = np.shape(grid)

    under = (
        np.clip(occupied[0] + 1, a_min=0, a_max=h - 1),
        np.clip(occupied[1], a_min=0, a_max=w - 1),
    )
    under_right = (
        np.clip(occupied[0] + 1, a_min=0, a_max=h - 1),
        np.clip(occupied[1] + 1, a_min=0, a_max=w - 1),
    )
    under_left = (
        np.clip(occupied[0] + 1, a_min=0, a_max=h - 1),
        np.clip(occupied[1] - 1, a_min=0, a_max=w - 1),
    )

    for idx in range(len(occupied[0])):
        # These should be references, calculated once.
        free_under = 1 - grid[under]
        free_under_right = 1 - grid[under_right]
        free_under_left = 1 - grid[under_left]
        if free_under[idx]:
            grid[occupied[0][idx], occupied[1][idx]] = 0
            grid[under[0][idx], under[1][idx]] = 1
            continue
        if free_under_right[idx]:
            grid[occupied[0][idx], occupied[1][idx]] = 0
            grid[under_right[0][idx], under_right[1][idx]] = 1
            continue
        if free_under_left[idx]:
            grid[occupied[0][idx], occupied[1][idx]] = 0
            grid[under_left[0][idx], under_left[1][idx]] = 1
            continue

    return grid


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
            if sqrt((new_x - other_drop.x) ** 2 + (new_y - other_drop.y) ** 2) <= (
                drop.radius + other_drop.radius
            ):
                drop.x_vel = -drop.x_vel
                drop.y_vel = -drop.y_vel
                break

        if new_x + drop.radius >= WINDOW_SIZE[0] or new_x - drop.radius < 0:
            drop.x_vel = -drop.x_vel
        if new_y + drop.radius >= WINDOW_SIZE[1] or new_y - drop.radius < 0:
            drop.y_vel = -drop.y_vel
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
    for i in range(12):
        drops.append(
            Drop(
                random.randint(0, 600),
                random.randint(0, 400),
                random.randint(3, 20),
                x_vel=random.randint(-100, 100),
                color=random.choice(list(COLORS.values())),
            )
        )

    gs = GameState(
        # grid=np.random.randint(0, 2, (HEIGHT, WIDTH)),
        grid=np.zeros((HEIGHT, WIDTH)),
        # drops=[
        #     Drop(250, 100, 8, x_vel=44),
        #     Drop(450, 190, 12, x_vel=-12),
        #     Drop(100, 270, 19, x_vel=88, color=Color.BLUE),
        # ],
        drops=drops,
    )
    # print(gs.grid)
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
        gs.grid = sand_update(gs.grid)
        gs.drops = drop_update(gs.drops, time_delta)


def draw(mc: View, gs: GameState) -> None:
    # background
    occupied = np.where(gs.grid)
    for idx in range(len(occupied[0])):
        y = occupied[0][idx]
        x = occupied[1][idx]
        pygame.draw.rect(mc.game_surface, Color.GRAY, (x, y, 1, 1))

    scaled_surface = pygame.transform.scale(mc.game_surface, WINDOW_SIZE)

    for drop in gs.drops:
        pygame.draw.circle(
            scaled_surface, drop.color, coord_flip(drop.x, drop.y), drop.radius
        )

    mc.screen.blit(scaled_surface, (0, 0))

    pygame.display.flip()


if __name__ == "__main__":
    main()
