"""The Starman: an item that, once out of its block, bounces along (the original's
power-up type 2: PowerUpObjHandler runs MoveJumpingEnemy and EnemyJump for it).

It sets off right at 1 px/f, as a mushroom does, and falls with its own gravity.
No tile stops its box. Its probes alone act, as the original's: landing on a
solid tile under its foot probe, it jumps again at -3 px/f; a solid tile at its
side probe, on the side it moves to, turns it around. It has no head probe, so it
rises into a block over it. A bumped block under it does nothing to it: the
original runs no background check for it but these.
"""

from mario.constants.level import (
    ENEMY_LANDING_SPRITE_Y_IN_ROW_PIXELS,
    STARMAN_FOOT_PROBE_X_PIXELS,
    STARMAN_FOOT_PROBE_Y_PIXELS,
    STARMAN_LEFT_PROBE_X_PIXELS,
    STARMAN_RIGHT_PROBE_X_PIXELS,
    STARMAN_SIDE_PROBE_Y_PIXELS,
    TILE_SIZE_PIXELS,
)
from mario.constants.physics import (
    STARMAN_BOUNCE_SPEED,
    STARMAN_GRAVITY,
    STARMAN_LANDS_FROM_FALL_SPEED,
    STARMAN_LANDS_FROM_RISE_SPEED,
    STARMAN_SPEED,
    STARMAN_TERMINAL_FALL_SPEED,
    SUBPIXEL_BITS,
    SUBPIXEL_FRACTION_MASK,
    SUBPIXELS_PER_PIXEL,
)
from mario.simulation.attempt_result import GameEventKind
from mario.simulation.attempt_tiles import AttemptTiles
from mario.simulation.gravity import add_gravity, whole_speed_y
from mario.simulation.item import Item
from mario.simulation.item_kind import ItemKind


class Starman(Item):
    kind = ItemKind.STARMAN
    collected_event_kind = GameEventKind.COLLECTED_STARMAN

    def __init__(self, block_column: int, block_row: int):
        super().__init__(block_column, block_row)
        self.velocity_x = 0
        self.velocity_y = 0

    def step(self, tiles: AttemptTiles) -> None:
        if not self.is_emerging:
            self._bounce_along(tiles)
            return
        super().step(tiles)
        if not self.is_emerging:
            self.velocity_x = STARMAN_SPEED

    def _bounce_along(self, tiles: AttemptTiles) -> None:
        """MoveJumpingEnemy (down, then along), then EnemyJump's probes."""
        self.y += self.velocity_y
        self.velocity_y = add_gravity(self.velocity_y, STARMAN_GRAVITY, STARMAN_TERMINAL_FALL_SPEED)
        self.x += self.velocity_x
        if self._looks_for_a_landing and self._probe_finds_solid_tile(
                tiles, STARMAN_FOOT_PROBE_X_PIXELS, STARMAN_FOOT_PROBE_Y_PIXELS):
            self._land()
        side_probe_x_pixels = STARMAN_RIGHT_PROBE_X_PIXELS if self.velocity_x > 0 else STARMAN_LEFT_PROBE_X_PIXELS
        if self._probe_finds_solid_tile(tiles, side_probe_x_pixels, STARMAN_SIDE_PROBE_Y_PIXELS):
            self.velocity_x = -self.velocity_x

    @property
    def _looks_for_a_landing(self) -> bool:
        whole_speed = whole_speed_y(self.velocity_y)
        return whole_speed >= STARMAN_LANDS_FROM_FALL_SPEED or whole_speed <= STARMAN_LANDS_FROM_RISE_SPEED

    @property
    def _sprite_y_pixels(self) -> int:
        return (self.y >> SUBPIXEL_BITS) - self.hitbox_offset_y_pixels

    def _probe_finds_solid_tile(self, tiles: AttemptTiles, sprite_x_pixels: int, sprite_y_pixels: int) -> bool:
        """Whether the tile at this point of its sprite (whose x is its box's) is solid."""
        return tiles.is_solid(((self.x >> SUBPIXEL_BITS) + sprite_x_pixels) // TILE_SIZE_PIXELS,
                              (self._sprite_y_pixels + sprite_y_pixels) // TILE_SIZE_PIXELS)

    def _land(self) -> None:
        """EnemyLanding snaps its sprite's y onto the tile row, keeping its position's
        sub-pixel (YMF_Dummy), and zeroes its y speed and the speed's fraction
        (InitVStf); then it jumps again, at a speed with no fraction."""
        sprite_y_pixels = self._sprite_y_pixels
        landed_sprite_y_pixels = (sprite_y_pixels - sprite_y_pixels % TILE_SIZE_PIXELS
                                  + ENEMY_LANDING_SPRITE_Y_IN_ROW_PIXELS)
        self.y = ((landed_sprite_y_pixels + self.hitbox_offset_y_pixels) * SUBPIXELS_PER_PIXEL
                  + (self.y & SUBPIXEL_FRACTION_MASK))
        self.velocity_y = STARMAN_BOUNCE_SPEED
