import sys
import random
from collections import defaultdict
from math import sqrt

from dataclasses import dataclass

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

NUM_DROPS = 1000


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
    radius: float
    x_vel: float = 0.0
    y_vel: float = 0.0


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

    # map drops
    map_: dict[tuple[int, int], list[Drop]] = defaultdict(list)
    for drop in drops:
        x, y = drop.x // SCALE, drop.y // SCALE
        map_[x, y].append(drop)

    # move position
    for drops_region in map_.values():
        for idx, drop in enumerate(drops_region):
            new_x = drop.x + drop.x_vel * (time_delta / 1000)
            new_y = drop.y + drop.y_vel * (time_delta / 1000)
            for other_idx, other_drop in enumerate(drops_region):
                if idx == other_idx:
                    continue
                center_distance = sqrt(
                    (new_x - other_drop.x) ** 2 + (new_y - other_drop.y) ** 2
                )
                if center_distance <= other_drop.radius:
                    # normalized overlap
                    # overlap = (other_drop.radius - center_distance) / other_drop.radius
                    x_diff = new_x - other_drop.x
                    y_diff = new_y - other_drop.y
                    x_component = (other_drop.radius - x_diff) / other_drop.radius
                    y_component = (other_drop.radius - y_diff) / other_drop.radius
                    drop.x_vel += -x_component
                    drop.y_vel += -y_component
                    other_drop.x_vel += x_component
                    other_drop.y_vel += y_component
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

    return [drop for drops in map_.values() for drop in drops], map_


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
            random.randint(5, 6),
            x_vel=random.randint(-100, 100),
        )
        for _ in range(NUM_DROPS)
    ]

    gs = GameState(drops=drops)
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

        gs.drops, map_ = drop_update(gs.drops, time_delta)
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
            scaled_surface, (*Color.BLUE, 50), coord_flip(drop.x, drop.y), drop.radius
        )
        pygame.draw.circle(
            scaled_surface, (*Color.BLUE, 255), coord_flip(drop.x, drop.y), 1
        )

    mc.screen.fill(Color.WHITE)  # to clear alpha stuff
    mc.screen.blit(scaled_surface, (0, 0))

    pygame.display.flip()


if __name__ == "__main__":
    main()
