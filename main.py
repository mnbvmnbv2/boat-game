import sys
import random
from collections import defaultdict
from math import sqrt

from dataclasses import dataclass

import pygame

# Screen dimensions
pygame.init()

info = pygame.display.Info()
SCALE = 10
WIDTH = 48 * 2
HEIGHT = 36 * 2
WINDOW_SIZE = WIDTH * SCALE, HEIGHT * SCALE

FRAME_RATE_UPDATE = 10  # input in ms
FPS = 1000 // FRAME_RATE_UPDATE

G = 360.0
REPULSIVE_FORCE = 1.0

NUM_DROPS = 1000

FIXED_DT = 1.0 / 240.0
MAX_STEPS_PER_FRAME = 8

RADIUS = 10


class Color:
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    BLACK = (0, 0, 0)


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
    x_vel: float = 0.0
    y_vel: float = 0.0


@dataclass
class GameState:
    drops: list[Drop]


def coord_flip(x: float, y: float) -> tuple[float, float]:
    y = WINDOW_SIZE[1] - y
    return x, y


def resolve_collision(a: Drop, b: Drop) -> None:
    if sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2) <= RADIUS:
        x_diff = a.x - b.x
        y_diff = a.y - b.y
        x_component = (RADIUS - x_diff) / RADIUS
        y_component = (RADIUS - y_diff) / RADIUS
        a.x_vel += -x_component * REPULSIVE_FORCE
        a.y_vel += -y_component * REPULSIVE_FORCE
        b.x_vel += x_component * REPULSIVE_FORCE
        b.y_vel += y_component * REPULSIVE_FORCE
        a.x += -x_component * 0.9
        a.y += -y_component * 0.9
        b.x += x_component * 0.9
        b.y += y_component * 0.9


def drop_update(drops: list[Drop], dt: float) -> list[Drop]:
    random.shuffle(drops)
    # map drops
    map_: dict[tuple[int, int], list[int]] = defaultdict(list)
    for i, drop in enumerate(drops):
        map_[drop.x // SCALE, drop.y // SCALE].append(i)

    # move position
    for region in map_.values():
        for drop_idx in region:
            drop = drops[drop_idx]
            drop.y_vel -= G * dt
            new_x = drop.x + drop.x_vel * dt
            new_y = drop.y + drop.y_vel * dt
            if new_x + RADIUS >= WINDOW_SIZE[0] or new_x - RADIUS < 0:
                drop.x_vel = -drop.x_vel * 0.05
                new_x = max(RADIUS, min(WINDOW_SIZE[0] - RADIUS, new_x))
            if new_y + RADIUS >= WINDOW_SIZE[1] or new_y - RADIUS < 0:
                drop.y_vel = -drop.y_vel * 0.05
                new_y = max(RADIUS, min(WINDOW_SIZE[1] - RADIUS, new_y))
            drop.x, drop.y = new_x, new_y

            # neighbour region
            for other_idx in region:
                if drop_idx <= other_idx:
                    continue
                resolve_collision(drop, drops[other_idx])

    return drops, map_


def main():
    mc = View(
        pygame.display.set_mode(WINDOW_SIZE),
        pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA),
        pygame.time.Clock(),
        0,
    )

    drops = [
        Drop(
            random.randint(0, WINDOW_SIZE[0]),
            random.randint(0, WINDOW_SIZE[1]),
            x_vel=random.randint(-100, 100),
        )
        for _ in range(NUM_DROPS)
    ]

    gs = GameState(drops=drops)
    pygame.display.set_caption("Boat Game")

    accumulator = 0.0

    # Main game loop
    while True:
        frame_ms = mc.clock.tick(1000 // FRAME_RATE_UPDATE)
        dt_sec = frame_ms / 1000.0
        mc.current_time += frame_ms
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        accumulator += dt_sec
        steps = 0
        map_ = None
        while accumulator >= FIXED_DT and steps < MAX_STEPS_PER_FRAME:
            gs.drops, map_ = drop_update(gs.drops, FIXED_DT)
            accumulator -= FIXED_DT
            steps += 1

        if map_ is None:
            _, map_ = drop_update(gs.drops, 0.0)
        draw(mc, gs, map_)

        # write fps on screen
        fps = int(mc.clock.get_fps())
        pygame.display.set_caption(f"Boat Game - FPS: {fps}")


def draw(mc: View, gs: GameState, map_: dict) -> None:
    mc.game_surface.fill((*Color.WHITE, 255))

    # for (cx, cy), drops in map_.items():
    #     alpha = int(255 * len(drops) / 7)
    #     color = (*Color.BLUE, min(255, alpha))
    #     coord = (cx, HEIGHT - cy - 1)
    #     mc.game_surface.set_at(coord, color)
    scaled_surface = pygame.transform.scale(mc.game_surface, WINDOW_SIZE)
    for drop in gs.drops:
        pygame.draw.circle(
            scaled_surface, (*Color.BLUE, 50), coord_flip(drop.x, drop.y), RADIUS
        )
        pygame.draw.circle(
            scaled_surface, (*Color.BLUE, 255), coord_flip(drop.x, drop.y), 1
        )

    mc.screen.fill(Color.WHITE)  # to clear alpha stuff
    mc.screen.blit(scaled_surface, (0, 0))

    pygame.display.flip()


if __name__ == "__main__":
    main()
