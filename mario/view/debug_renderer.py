"""The Debug view: the level as the game treats it, as coloured, filled hitboxes,
with the followed agent's Observation over it and the recent game events."""

import pygame

from mario.constants.level import TILE_SIZE_PIXELS
from mario.constants.view import (
    BRICK_COLOUR,
    CASTLE_STOPPER_COLOUR,
    DEFEATED_ENEMY_DRAWN_HEIGHT_PIXELS,
    FLAGPOLE_COLOUR,
    GOOMBA_COLOUR,
    GROUND_COLOUR,
    HARD_BLOCK_COLOUR,
    HIDDEN_BLOCK_COLOUR,
    MARIO_COLOUR,
    PIPE_COLOUR,
    QUESTION_BLOCK_COLOUR,
    SKY_COLOUR,
    USED_BLOCK_COLOUR,
)
from mario.level.static_level import EnemyKind
from mario.level.tile_kind import TileKind
from mario.snapshots.world_snapshot import EnemySnapshot, WorldSnapshot
from mario.view.debug_text import DebugText
from mario.view.game_event_feed import GameEventFeed
from mario.view.observation_overlay import ObservationOverlay

TILE_COLOURS = {
    TileKind.GROUND: GROUND_COLOUR,
    TileKind.HARD_BLOCK: HARD_BLOCK_COLOUR,
    TileKind.BRICK: BRICK_COLOUR,
    TileKind.COIN_QUESTION_BLOCK: QUESTION_BLOCK_COLOUR,
    TileKind.POWER_UP_QUESTION_BLOCK: QUESTION_BLOCK_COLOUR,
    TileKind.STARMAN_BRICK: BRICK_COLOUR,
    TileKind.MULTI_COIN_BRICK: BRICK_COLOUR,
    TileKind.HIDDEN_ONE_UP_BLOCK: HIDDEN_BLOCK_COLOUR,
    TileKind.USED_BLOCK: USED_BLOCK_COLOUR,
    TileKind.PIPE: PIPE_COLOUR,
    TileKind.FLAGPOLE: FLAGPOLE_COLOUR,
    TileKind.CASTLE_STOPPER: CASTLE_STOPPER_COLOUR,
}


ENEMY_COLOURS = {
    EnemyKind.GOOMBA: GOOMBA_COLOUR,
}


class DebugRenderer:
    """Needs pygame's fonts initialised (the Window does it)."""

    def __init__(self):
        debug_text = DebugText()
        self._observation_overlay = ObservationOverlay(debug_text)
        self._game_event_feed = GameEventFeed(debug_text)

    def draw(self, snapshot: WorldSnapshot, screen: pygame.Surface) -> None:
        screen.fill(SKY_COLOUR)
        self._draw_tiles(snapshot, screen)
        for enemy in snapshot.enemies:
            self._draw_enemy(enemy, snapshot.screen_left_x_pixels, screen)
        mario = snapshot.mario
        _fill_level_box(screen, MARIO_COLOUR, snapshot.screen_left_x_pixels,
                        mario.x_pixels, mario.y_pixels, mario.width_pixels, mario.height_pixels)
        if snapshot.observation is not None:
            self._observation_overlay.draw(snapshot.observation, snapshot.screen_left_x_pixels, screen)
        self._game_event_feed.draw(snapshot.recent_events, screen)

    @staticmethod
    def _draw_tiles(snapshot: WorldSnapshot, screen: pygame.Surface) -> None:
        """Every tile in its place, a bouncing block raised above it."""
        tiles = snapshot.tiles
        bounce_offsets = {(block.column, block.row): block.offset_y_pixels for block in snapshot.bouncing_blocks}
        for row, kinds in enumerate(tiles.rows):
            for column_offset, kind in enumerate(kinds):
                colour = TILE_COLOURS.get(kind)
                if colour is None:
                    continue
                column = tiles.first_column + column_offset
                _fill_level_box(screen, colour, snapshot.screen_left_x_pixels,
                                column * TILE_SIZE_PIXELS, row * TILE_SIZE_PIXELS + bounce_offsets.get((column, row), 0),
                                TILE_SIZE_PIXELS, TILE_SIZE_PIXELS)

    @staticmethod
    def _draw_enemy(enemy: EnemySnapshot, screen_left_x_pixels: int, screen: pygame.Surface) -> None:
        """Its hitbox; a defeated one flattened onto its feet."""
        drawn_height_pixels = DEFEATED_ENEMY_DRAWN_HEIGHT_PIXELS if enemy.is_defeated else enemy.height_pixels
        drawn_top_y_pixels = enemy.y_pixels + enemy.height_pixels - drawn_height_pixels
        _fill_level_box(screen, ENEMY_COLOURS[enemy.kind], screen_left_x_pixels,
                        enemy.x_pixels, drawn_top_y_pixels, enemy.width_pixels, drawn_height_pixels)


def _fill_level_box(screen: pygame.Surface, colour: tuple[int, int, int], screen_left_x_pixels: int,
                    level_x_pixels: int, y_pixels: int, width_pixels: int, height_pixels: int) -> None:
    """Fill a box given in level pixels, shifted onto the screen."""
    screen.fill(colour, pygame.Rect(level_x_pixels - screen_left_x_pixels, y_pixels, width_pixels, height_pixels))
