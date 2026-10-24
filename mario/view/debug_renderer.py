"""The Debug view: the level as the game treats it, as coloured, filled hitboxes."""

import pygame

from mario.constants.level import TILE_SIZE_PIXELS
from mario.constants.view import (
    BRICK_COLOUR,
    CASTLE_STOPPER_COLOUR,
    FLAGPOLE_COLOUR,
    GROUND_COLOUR,
    HARD_BLOCK_COLOUR,
    HIDDEN_BLOCK_COLOUR,
    MARIO_COLOUR,
    PIPE_COLOUR,
    QUESTION_BLOCK_COLOUR,
    SKY_COLOUR,
)
from mario.level.tile_kind import TileKind
from mario.snapshots.world_snapshot import WorldSnapshot

TILE_COLOURS = {
    TileKind.GROUND: GROUND_COLOUR,
    TileKind.HARD_BLOCK: HARD_BLOCK_COLOUR,
    TileKind.BRICK: BRICK_COLOUR,
    TileKind.COIN_QUESTION_BLOCK: QUESTION_BLOCK_COLOUR,
    TileKind.POWER_UP_QUESTION_BLOCK: QUESTION_BLOCK_COLOUR,
    TileKind.STARMAN_BRICK: BRICK_COLOUR,
    TileKind.MULTI_COIN_BRICK: BRICK_COLOUR,
    TileKind.HIDDEN_ONE_UP_BLOCK: HIDDEN_BLOCK_COLOUR,
    TileKind.PIPE: PIPE_COLOUR,
    TileKind.FLAGPOLE: FLAGPOLE_COLOUR,
    TileKind.CASTLE_STOPPER: CASTLE_STOPPER_COLOUR,
}


class DebugRenderer:
    def draw(self, snapshot: WorldSnapshot, screen: pygame.Surface) -> None:
        screen.fill(SKY_COLOUR)
        self._draw_tiles(snapshot, screen)
        mario = snapshot.mario
        screen.fill(MARIO_COLOUR, pygame.Rect(mario.x_pixels - snapshot.screen_left_x_pixels,
                                              mario.y_pixels, mario.width_pixels, mario.height_pixels))

    @staticmethod
    def _draw_tiles(snapshot: WorldSnapshot, screen: pygame.Surface) -> None:
        tiles = snapshot.tiles
        for row, kinds in enumerate(tiles.rows):
            for column_offset, kind in enumerate(kinds):
                colour = TILE_COLOURS.get(kind)
                if colour is None:
                    continue
                screen_x = (tiles.first_column + column_offset) * TILE_SIZE_PIXELS - snapshot.screen_left_x_pixels
                screen.fill(colour, pygame.Rect(screen_x, row * TILE_SIZE_PIXELS,
                                                TILE_SIZE_PIXELS, TILE_SIZE_PIXELS))
