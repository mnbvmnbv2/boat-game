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

NUM_DROPS = 250


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
class GameState:
    drops_pos: np.ndarray
    drops_vel: np.ndarray
    drops_radius: np.ndarray





def update(gs: GameState, time_delta: int) -> GameState:
    # add accelleration
    gs.drops_vel[:, 1] -= G * (time_delta / 1000)

    # move position
    new_pos = gs.drops_pos + gs.drops_vel * (time_delta / 1000)
    for i in range(NUM_DROPS):
        for j in range(NUM_DROPS):
            if i == j:
                continue
            center_distance = sqrt((new_pos[i, 0] - new_pos[j, 0]) ** 2 + (new_pos[i, 1] - new_pos[j, 1]) ** 2)
            if center_distance <= (gs.drops_radius[i] + gs.drops_radius[j]):
                gs.drops_vel[i] = -gs.drops_vel[i] / 2
                break

    out_right = new_pos[:,0] + gs.drops_radius >= WINDOW_SIZE[0]
    out_left = new_pos[:,0] - gs.drops_radius < 0
    out_horizontal = np.bitwise_or(out_left, out_right)
    out_top = new_pos[:,1] - gs.drops_radius < 0
    out_bottom = new_pos[:,1] + gs.drops_radius >= WINDOW_SIZE[1]
    out_vertical = np.bitwise_or(out_top, out_bottom)
    gs.drops_vel[out_horizontal, 0] = 0
    gs.drops_pos[out_right, 0] = WINDOW_SIZE[0] - gs.drops_radius[out_right]
    gs.drops_pos[out_left, 0] = gs.drops_radius[out_left]
    gs.drops_vel[out_vertical, 1] = 0
    gs.drops_pos[out_bottom, 1] = WINDOW_SIZE[1] - gs.drops_radius[out_bottom]
    gs.drops_pos[out_top, 1] = gs.drops_radius[out_top]
    gs.drops_pos = gs.drops_pos + gs.drops_vel * (time_delta / 1000)

    return gs


def main():
    mc = View(
        pygame.display.set_mode(WINDOW_SIZE),
        pygame.Surface((WIDTH, HEIGHT)),
        pygame.time.Clock(),
        0,
    )

    xs = np.random.randint(0, WINDOW_SIZE[0], (NUM_DROPS,))
    ys = np.random.randint(0, WINDOW_SIZE[1], (NUM_DROPS,))

    gs = GameState(
        drops_vel=np.zeros((NUM_DROPS, 2)),
        drops_pos=np.stack((xs, ys), axis=1),
        drops_radius=np.random.randint(1, 5, (NUM_DROPS)),
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
        gs = update(gs, time_delta)

        # write fps on screen
        fps = int(mc.clock.get_fps())
        pygame.display.set_caption(f"Boat Game - FPS: {fps}")


def draw(mc: View, gs: GameState) -> None:
    scaled_surface = pygame.transform.scale(mc.game_surface, WINDOW_SIZE)

    draw_y = WINDOW_SIZE[1] - gs.drops_pos[:, 1]

    for i in range(NUM_DROPS):
        pygame.draw.circle(
            scaled_surface, Color.BLUE, (gs.drops_pos[i, 0], draw_y[i]), gs.drops_radius[i]
        )

    mc.screen.blit(scaled_surface, (0, 0))

    pygame.display.flip()


if __name__ == "__main__":
    main()
