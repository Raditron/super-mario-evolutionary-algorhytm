"""One of fire Mario's fireballs (the original's fireball object, FireballObjCore).

It flies at a steady speed the way Mario faced when he shot it, and falls with
its own gravity. Its position is the top-left corner of its 8 x 8 box, in
sub-pixels; it moves vertically first, then horizontally, as ImposeGravity and
MoveObjectHorizontally do.

Its one tile probe, just under its middle, is the original's (FireballBGCollision):
falling onto a solid tile it bounces, but a solid tile there while it rises, or
on the tick after a bounce (it flew into a wall), makes it explode. An
exploding fireball stays where it is until its explosion is over. One that
flies off the screen, or falls below it, is gone at once (its offscreen bits),
even on the tick it explodes.
"""

from mario.constants.level import (
    FIREBALL_BOUNCE_SNAP_PIXELS,
    FIREBALL_FELL_OUT_Y_PIXELS,
    FIREBALL_PROBE_X_PIXELS,
    FIREBALL_PROBE_Y_PIXELS,
    FIREBALL_REMOVAL_SCREEN_RIGHT_X_PIXELS,
    FIREBALL_SIZE_PIXELS,
    FIREBALL_START_OFFSET_X_PIXELS,
    TILE_SIZE_PIXELS,
)
from mario.constants.physics import (
    FIREBALL_BOUNCE_SPEED,
    FIREBALL_EXPLOSION_TICKS,
    FIREBALL_GRAVITY,
    FIREBALL_SPEED,
    FIREBALL_START_FALL_SPEED,
    FIREBALL_TERMINAL_FALL_SPEED,
    SUBPIXEL_BITS,
    SUBPIXEL_FRACTION_MASK,
    SUBPIXELS_PER_PIXEL,
    Y_SUBSPEED_MASK,
)
from mario.simulation.attempt_tiles import AttemptTiles
from mario.simulation.playfield import Playfield
from mario.simulation.gravity import add_gravity
from mario.simulation.hitbox import Hitbox


class Fireball:
    def __init__(self, mario_sprite_x_pixels: int, mario_sprite_y_pixels: int, direction: int):
        """Shot by Mario with his sprite at that position, facing that direction."""
        self.x = (mario_sprite_x_pixels + FIREBALL_START_OFFSET_X_PIXELS) * SUBPIXELS_PER_PIXEL
        self.y = mario_sprite_y_pixels * SUBPIXELS_PER_PIXEL
        self.velocity_x = direction * FIREBALL_SPEED
        self.velocity_y = FIREBALL_START_FALL_SPEED
        self._has_just_bounced = False               # FireballBouncingFlag
        self._explosion_ticks: int | None = None     # None until it explodes
        self._has_left_the_screen = False

    @property
    def pixel_x(self) -> int:
        return self.x >> SUBPIXEL_BITS

    @property
    def pixel_y(self) -> int:
        return self.y >> SUBPIXEL_BITS

    @property
    def is_exploding(self) -> bool:
        return self._explosion_ticks is not None

    @property
    def is_gone(self) -> bool:
        """Whether it has left play: off the screen, or its explosion over."""
        return self._has_left_the_screen or self._explosion_ticks == FIREBALL_EXPLOSION_TICKS

    def hitbox(self) -> Hitbox:
        return Hitbox(self.pixel_x, self.pixel_y, FIREBALL_SIZE_PIXELS, FIREBALL_SIZE_PIXELS)

    def step(self, playfield: Playfield) -> None:
        if self.is_exploding:
            self._explosion_ticks += 1
        else:
            self._fly(playfield)

    def _fly(self, playfield: Playfield) -> None:
        """One tick of flight, then its tile probe and the screen's edges."""
        self.y += self.velocity_y
        self.velocity_y = add_gravity(self.velocity_y, FIREBALL_GRAVITY, FIREBALL_TERMINAL_FALL_SPEED)
        self.x += self.velocity_x
        self._probe_tiles(playfield.tiles)
        screen_x_pixels = self.pixel_x - playfield.screen_left_x_pixels
        self._has_left_the_screen = (screen_x_pixels <= 0
                                     or screen_x_pixels >= FIREBALL_REMOVAL_SCREEN_RIGHT_X_PIXELS
                                     or self.pixel_y >= FIREBALL_FELL_OUT_Y_PIXELS)

    def explode(self) -> None:
        self._explosion_ticks = 0

    def _probe_tiles(self, tiles: AttemptTiles) -> None:
        probe_column = (self.pixel_x + FIREBALL_PROBE_X_PIXELS) // TILE_SIZE_PIXELS
        probe_row = (self.pixel_y + FIREBALL_PROBE_Y_PIXELS) // TILE_SIZE_PIXELS
        if not tiles.is_solid(probe_column, probe_row):
            self._has_just_bounced = False
        elif self.velocity_y < 0 or self._has_just_bounced:
            self.explode()
        else:
            self._bounce()

    def _bounce(self) -> None:
        """Up again, its y snapped down onto the pixel grid's multiples of 8."""
        self.velocity_y = FIREBALL_BOUNCE_SPEED + (self.velocity_y & Y_SUBSPEED_MASK)
        self._has_just_bounced = True
        snapped_y_pixels = self.pixel_y - self.pixel_y % FIREBALL_BOUNCE_SNAP_PIXELS
        self.y = snapped_y_pixels * SUBPIXELS_PER_PIXEL + (self.y & SUBPIXEL_FRACTION_MASK)
