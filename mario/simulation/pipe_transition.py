"""The warp pipe's way into the bonus room and the exit pipe's way out (#23), as
the original plays them (docs/research/world-1-1-layout.md, "The bonus room").

Going in, Mario stands on the warp pipe and presses down (HandlePipeEntry): he
sinks into it; the area changes, and he drops into the room. Coming out, he walks
into the exit pipe's mouth: he walks on into the pipe; the area changes, and he
rises out of the level's pipe. Each of these is a PipeTransition, during which he
can't be controlled: one tick at a time until it is over. area_after is the area
the Attempt then moves him to, None for none.
"""

from abc import ABC, abstractmethod

from mario.constants.level import TILE_SIZE_PIXELS, TILE_SIZE_SUBPIXELS
from mario.constants.warp_pipe import (
    BONUS_ROOM_CONTROL_SPRITE_Y_PIXELS,
    EXIT_PIPE_WALK_SPEED,
    EXIT_PIPE_WALK_STOP_SPRITE_X_MULTIPLE_PIXELS,
    EXIT_PIPE_WALK_TICKS,
    LEFT_FOOT_PROBE_SPRITE_X_PIXELS,
    PIPE_WIDTH_TILES,
    RETURN_CONTROL_SPRITE_Y_PIXELS,
    RIGHT_FOOT_PROBE_SPRITE_X_PIXELS,
    RISING_SUBPIXELS_PER_TICK,
    SINKING_SUBPIXELS_PER_TICK,
    SINKING_TICKS,
)
from mario.controller.controller_state import NO_DIRECTION, RIGHT, ControllerState
from mario.level.static_level import BonusRoom, Pipe
from mario.simulation.area import Area
from mario.simulation.attempt_tiles import AttemptTiles
from mario.simulation.mario import Mario

NO_BUTTONS = ControllerState(ControllerState.bitmask())


def steps_into_warp_pipe(mario: Mario, controller: ControllerState, warp_pipe: Pipe | None) -> bool:
    """HandlePipeEntry: standing on the warp pipe's top, he holds down with neither
    left nor right, each of his foot probes over its own column of the pipe."""
    if warp_pipe is None or not controller.down or controller.direction != NO_DIRECTION:
        return False
    if not mario.is_on_ground or mario.feet_y != warp_pipe.top_row * TILE_SIZE_SUBPIXELS:
        return False
    left_foot_column = (mario.sprite_x_pixels + LEFT_FOOT_PROBE_SPRITE_X_PIXELS) // TILE_SIZE_PIXELS
    right_foot_column = (mario.sprite_x_pixels + RIGHT_FOOT_PROBE_SPRITE_X_PIXELS) // TILE_SIZE_PIXELS
    return (left_foot_column, right_foot_column) == (warp_pipe.left_column,
                                                     warp_pipe.left_column + PIPE_WIDTH_TILES - 1)


def walks_into_exit_pipe(mario: Mario, bonus_room: BonusRoom) -> bool:
    """On the ground and holding right (so facing right), his box against the
    mouth's lower tile: the original's side probe meeting its metatile ($1f)."""
    hitbox = mario.hitbox()
    mouth_top_y_pixels = bonus_room.exit_pipe_mouth_row * TILE_SIZE_PIXELS
    return (mario.is_on_ground and mario.held_direction == RIGHT
            and hitbox.right_x_pixels == bonus_room.exit_pipe_mouth_column * TILE_SIZE_PIXELS
            and hitbox.y_pixels < mouth_top_y_pixels + TILE_SIZE_PIXELS
            and hitbox.bottom_y_pixels > mouth_top_y_pixels)


class PipeTransition(ABC):
    area_after: Area | None = None

    @property
    @abstractmethod
    def is_over(self) -> bool: ...

    @abstractmethod
    def step(self) -> None:
        """One tick of it."""


class SinkingIntoWarpPipe(PipeTransition):
    """VerticalPipeEntry: down a pixel a tick, behind the pipe, until the area changes."""
    area_after = Area.BONUS_ROOM

    def __init__(self, mario: Mario):
        self._mario = mario
        self._ticks_left = SINKING_TICKS

    @property
    def is_over(self) -> bool:
        return self._ticks_left == 0

    def step(self) -> None:
        self._mario.move_through_tiles(0, SINKING_SUBPIXELS_PER_TICK)
        self._ticks_left -= 1


class DroppingIntoBonusRoom(PipeTransition):
    """PlayerEntrance: he moves as if no button were pressed, falling, until his
    sprite is low enough; on that tick he stands ready, and control returns the next."""

    def __init__(self, mario: Mario, tiles: AttemptTiles):
        self._mario = mario
        self._tiles = tiles
        self._is_over = False

    @property
    def is_over(self) -> bool:
        return self._is_over

    def step(self) -> None:
        if self._mario.sprite_y_pixels < BONUS_ROOM_CONTROL_SPRITE_Y_PIXELS:
            self._mario.step(NO_BUTTONS, self._tiles)
        else:
            self._is_over = True


class WalkingIntoExitPipe(PipeTransition):
    """SideExitPipeEntry, EnterSidePipe: right through the pipe's tiles, behind
    them, until his sprite's x is on the tile grid; then he stands until the area changes."""
    area_after = Area.LEVEL

    def __init__(self, mario: Mario):
        self._mario = mario
        self._ticks_left = EXIT_PIPE_WALK_TICKS

    @property
    def is_over(self) -> bool:
        return self._ticks_left == 0

    def step(self) -> None:
        if self._mario.sprite_x_pixels % EXIT_PIPE_WALK_STOP_SPRITE_X_MULTIPLE_PIXELS:
            self._mario.move_through_tiles(EXIT_PIPE_WALK_SPEED, 0)
        self._ticks_left -= 1


class RisingOutOfPipe(PipeTransition):
    """EntrMode2: up a pixel a tick, from below the screen and behind the pipe, until
    he stands on its top."""

    def __init__(self, mario: Mario):
        self._mario = mario
        self._is_over = False

    @property
    def is_over(self) -> bool:
        return self._is_over

    def step(self) -> None:
        self._mario.move_through_tiles(0, -RISING_SUBPIXELS_PER_TICK)
        self._is_over = self._mario.sprite_y_pixels <= RETURN_CONTROL_SPRITE_Y_PIXELS
