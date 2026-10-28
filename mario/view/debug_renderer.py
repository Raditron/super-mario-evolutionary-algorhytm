"""The Debug view: the level as the game treats it, as coloured, filled hitboxes
(the flag on the flagpole too), with the followed agent's Observation over it and
the recent game events."""

import pygame

from mario.constants.flagpole import FLAG_SIZE_PIXELS
from mario.constants.level import TILE_SIZE_PIXELS
from mario.constants.view import (
    DEFEATED_ENEMY_DRAWN_HEIGHT_PIXELS,
    EXPLODING_FIREBALL_COLOUR,
    FIREBALL_COLOUR,
    FLAG_COLOUR,
    INVULNERABLE_MARIO_DRAWN_EVERY_TICKS,
    SKY_COLOUR,
)
from mario.snapshots.world_snapshot import EnemySnapshot, FireballSnapshot, ItemSnapshot, WorldSnapshot
from mario.view.debug_text import DebugText
from mario.view.game_event_feed import GameEventFeed
from mario.view.hitbox_colours import ENEMY_COLOURS, ITEM_COLOURS, MARIO_COLOURS, SHELL_COLOURS, TILE_COLOURS
from mario.view.observation_overlay import ObservationOverlay


class DebugRenderer:
    """Needs pygame's fonts initialised (the Window does it)."""

    def __init__(self):
        debug_text = DebugText()
        self._observation_overlay = ObservationOverlay(debug_text)
        self._game_event_feed = GameEventFeed(debug_text)

    def draw(self, snapshot: WorldSnapshot, screen: pygame.Surface) -> None:
        """Items still rising out of their block are drawn behind it, as in the original."""
        screen.fill(SKY_COLOUR)
        for item in snapshot.items:
            if item.is_emerging:
                self._draw_item(item, snapshot.screen_left_x_pixels, screen)
        self._draw_tiles(snapshot, screen)
        if snapshot.flag is not None:
            _fill_level_box(screen, FLAG_COLOUR, snapshot.screen_left_x_pixels, snapshot.flag.x_pixels,
                            snapshot.flag.y_pixels, FLAG_SIZE_PIXELS, FLAG_SIZE_PIXELS)
        for item in snapshot.items:
            if not item.is_emerging:
                self._draw_item(item, snapshot.screen_left_x_pixels, screen)
        for enemy in snapshot.enemies:
            self._draw_enemy(enemy, snapshot.screen_left_x_pixels, screen)
        for fireball in snapshot.fireballs:
            self._draw_fireball(fireball, snapshot.screen_left_x_pixels, screen)
        mario = snapshot.mario
        if not mario.is_invulnerable or snapshot.tick % INVULNERABLE_MARIO_DRAWN_EVERY_TICKS == 0:
            _fill_level_box(screen, MARIO_COLOURS[mario.power_state], snapshot.screen_left_x_pixels,
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
        """Its hitbox, a shell in the shell's colour; a defeated one flattened onto its feet."""
        drawn_height_pixels = DEFEATED_ENEMY_DRAWN_HEIGHT_PIXELS if enemy.is_defeated else enemy.height_pixels
        drawn_top_y_pixels = enemy.y_pixels + enemy.height_pixels - drawn_height_pixels
        colour = SHELL_COLOURS[enemy.kind] if enemy.is_shell else ENEMY_COLOURS[enemy.kind]
        _fill_level_box(screen, colour, screen_left_x_pixels,
                        enemy.x_pixels, drawn_top_y_pixels, enemy.width_pixels, drawn_height_pixels)

    @staticmethod
    def _draw_fireball(fireball: FireballSnapshot, screen_left_x_pixels: int, screen: pygame.Surface) -> None:
        colour = EXPLODING_FIREBALL_COLOUR if fireball.is_exploding else FIREBALL_COLOUR
        _fill_level_box(screen, colour, screen_left_x_pixels,
                        fireball.x_pixels, fireball.y_pixels, fireball.width_pixels, fireball.height_pixels)

    @staticmethod
    def _draw_item(item: ItemSnapshot, screen_left_x_pixels: int, screen: pygame.Surface) -> None:
        _fill_level_box(screen, ITEM_COLOURS[item.kind], screen_left_x_pixels,
                        item.x_pixels, item.y_pixels, item.width_pixels, item.height_pixels)


def _fill_level_box(screen: pygame.Surface, colour: tuple[int, int, int], screen_left_x_pixels: int,
                    level_x_pixels: int, y_pixels: int, width_pixels: int, height_pixels: int) -> None:
    """Fill a box given in level pixels, shifted onto the screen."""
    screen.fill(colour, pygame.Rect(level_x_pixels - screen_left_x_pixels, y_pixels, width_pixels, height_pixels))
