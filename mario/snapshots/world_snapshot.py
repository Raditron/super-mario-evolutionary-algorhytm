"""What a renderer may see of an Attempt on one tick. Renderers read only these."""

from dataclasses import dataclass

from mario.constants.level import SCREEN_WIDTH_PIXELS, TILE_SIZE_PIXELS
from mario.constants.physics import SUBPIXEL_BITS
from mario.level.tile_kind import TileKind
from mario.simulation.attempt import Attempt

# A screen scrolled part-way into a tile shows one column more than it is wide.
VISIBLE_COLUMNS = SCREEN_WIDTH_PIXELS // TILE_SIZE_PIXELS + 1


@dataclass(frozen=True)
class VisibleTiles:
    first_column: int
    rows: tuple[tuple[TileKind, ...], ...]


@dataclass(frozen=True)
class MarioSnapshot:
    """Mario's hitbox, in level pixels."""
    x_pixels: int
    y_pixels: int
    width_pixels: int
    height_pixels: int


@dataclass(frozen=True)
class HudSnapshot:
    """The numbers the HUD shows: score, coins and the level timer's time left."""
    score: int
    coins: int
    time_left: int

    @classmethod
    def of(cls, attempt: Attempt) -> "HudSnapshot":
        return cls(attempt.scoreboard.score, attempt.scoreboard.coins, attempt.level_timer.time_left)


@dataclass(frozen=True)
class WorldSnapshot:
    tick: int
    screen_left_x_pixels: int
    tiles: VisibleTiles
    mario: MarioSnapshot
    hud: HudSnapshot

    @classmethod
    def of(cls, attempt: Attempt, hud: HudSnapshot | None = None) -> "WorldSnapshot":
        """The attempt as a renderer sees it. The HUD shows the attempt's own
        numbers unless a mode passes its own (PlaySession carries them across lives)."""
        screen_left_x_pixels = attempt.scroll.left_x_pixels
        first_column = screen_left_x_pixels // TILE_SIZE_PIXELS
        level = attempt.level
        rows = tuple(tuple(level.tile_kind(column, row)
                           for column in range(first_column, first_column + VISIBLE_COLUMNS))
                     for row in range(level.height_tiles))
        mario = attempt.mario
        return cls(
            tick=attempt.ticks_elapsed,
            screen_left_x_pixels=screen_left_x_pixels,
            tiles=VisibleTiles(first_column, rows),
            mario=MarioSnapshot(mario.pixel_x, mario.pixel_y, mario.width >> SUBPIXEL_BITS,
                                mario.height >> SUBPIXEL_BITS),
            hud=hud if hud is not None else HudSnapshot.of(attempt),
        )
