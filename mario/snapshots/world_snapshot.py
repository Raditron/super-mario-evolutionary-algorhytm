"""What a renderer may see of an Attempt on one tick. Renderers read only these."""

from dataclasses import dataclass

from mario.constants.level import SCREEN_WIDTH_PIXELS, TILE_SIZE_PIXELS
from mario.level.static_level import EnemyKind
from mario.level.tile_kind import TileKind
from mario.simulation.attempt import Attempt
from mario.simulation.enemy import Enemy
from mario.simulation.mario import Mario

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

    @classmethod
    def of(cls, mario: Mario) -> "MarioSnapshot":
        hitbox = mario.hitbox()
        return cls(hitbox.x_pixels, hitbox.y_pixels, hitbox.width_pixels, hitbox.height_pixels)


@dataclass(frozen=True)
class EnemySnapshot:
    """One enemy's hitbox, in level pixels, and whether it has been defeated."""
    kind: EnemyKind
    x_pixels: int
    y_pixels: int
    width_pixels: int
    height_pixels: int
    is_defeated: bool

    @classmethod
    def of(cls, enemy: Enemy) -> "EnemySnapshot":
        hitbox = enemy.hitbox()
        return cls(enemy.kind, hitbox.x_pixels, hitbox.y_pixels, hitbox.width_pixels, hitbox.height_pixels,
                   enemy.is_defeated)


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
    enemies: tuple[EnemySnapshot, ...]
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
        return cls(
            tick=attempt.ticks_elapsed,
            screen_left_x_pixels=screen_left_x_pixels,
            tiles=VisibleTiles(first_column, rows),
            mario=MarioSnapshot.of(attempt.mario),
            enemies=tuple(EnemySnapshot.of(enemy) for enemy in attempt.enemies.active),
            hud=hud if hud is not None else HudSnapshot.of(attempt),
        )
