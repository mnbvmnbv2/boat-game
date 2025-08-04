import sys
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

FRAME_RATE_UPDATE = 20  # input in ms


class Color:
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)
    RED = (255, 0, 0)
    BLACK = (0, 0, 0)


@dataclass
class View:
    screen: pygame.Surface
    game_surface: pygame.Surface
    clock: pygame.time.Clock
    current_time: int = 0


@dataclass
class GameState:
    grid: np.ndarray


def update(grid: np.ndarray) -> np.ndarray:
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


def main():
    mc = View(
        pygame.display.set_mode(WINDOW_SIZE),
        pygame.Surface((WIDTH, HEIGHT)),
        pygame.time.Clock(),
        0,
    )
    gs = GameState(np.random.randint(0, 2, (HEIGHT, WIDTH)))
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
        gs.grid = update(gs.grid)


def draw(mc: View, gs: GameState) -> None:
    # background
    occupied = np.where(gs.grid)
    for idx in range(len(occupied[0])):
        y = occupied[0][idx]
        x = occupied[1][idx]
        pygame.draw.rect(mc.game_surface, Color.GRAY, (x, y, 1, 1))

    scaled_surface = pygame.transform.scale(mc.game_surface, WINDOW_SIZE)
    mc.screen.blit(scaled_surface, (0, 0))

    pygame.display.flip()


if __name__ == "__main__":
    main()
