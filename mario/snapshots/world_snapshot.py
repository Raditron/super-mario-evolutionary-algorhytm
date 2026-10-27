"""What a renderer may see of an Attempt on one tick. Renderers read only these."""

from dataclasses import dataclass

from mario.constants.level import SCREEN_WIDTH_PIXELS, TILE_SIZE_PIXELS
from mario.constants.snapshots import RECENT_GAME_EVENT_TICKS
from mario.level.static_level import EnemyKind
from mario.level.tile_kind import TileKind
from mario.simulation.attempt import Attempt
from mario.simulation.enemy import Enemy
from mario.simulation.mario import Mario
from mario.simulation.item import Item
from mario.simulation.observation_builder import ObservationBuilder

# The game's vocabulary a snapshot carries, handed on so that the view needs
# nothing from the simulation (spec section 3).
from mario.simulation.attempt_result import GameEvent as GameEvent
from mario.simulation.item_kind import ItemKind as ItemKind
from mario.simulation.mario import PowerState as PowerState

# A screen scrolled part-way into a tile shows one column more than it is wide.
VISIBLE_COLUMNS = SCREEN_WIDTH_PIXELS // TILE_SIZE_PIXELS + 1


@dataclass(frozen=True)
class VisibleTiles:
    first_column: int
    rows: tuple[tuple[TileKind, ...], ...]


@dataclass(frozen=True)
class BouncingBlockSnapshot:
    """A block bumped from below, raised this many pixels above its place."""
    column: int
    row: int
    offset_y_pixels: int


@dataclass(frozen=True)
class MarioSnapshot:
    """Mario's hitbox, in level pixels (while he grows or shrinks, the box of the
    animation frame showing), his power state, and whether he can't be hurt."""
    x_pixels: int
    y_pixels: int
    width_pixels: int
    height_pixels: int
    power_state: PowerState = PowerState.SMALL
    is_invulnerable: bool = False

    @classmethod
    def of(cls, mario: Mario) -> "MarioSnapshot":
        hitbox = mario.hitbox()
        return cls(hitbox.x_pixels, hitbox.y_pixels, hitbox.width_pixels, hitbox.height_pixels,
                   mario.power_state, mario.is_invulnerable)


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
class ItemSnapshot:
    """One item's hitbox, in level pixels, and whether it is still rising out of its block."""
    kind: ItemKind
    x_pixels: int
    y_pixels: int
    width_pixels: int
    height_pixels: int
    is_emerging: bool

    @classmethod
    def of(cls, item: Item) -> "ItemSnapshot":
        hitbox = item.hitbox()
        return cls(item.kind, hitbox.x_pixels, hitbox.y_pixels, hitbox.width_pixels, hitbox.height_pixels,
                   item.is_emerging)


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
class ObservationSnapshot:
    """The followed agent's Observation, laid out as its window over the level."""
    first_column: int                                 # the level column of the window's left cells
    cells: tuple[tuple[float, ...], ...]              # rows from the top, each from left to right
    state_numbers: tuple[float, ...]                  # in the Observation's order

    @classmethod
    def of(cls, attempt: Attempt, builder: ObservationBuilder) -> "ObservationSnapshot":
        observation, first_column = builder.build_with_first_column(attempt)
        return cls(first_column, tuple(map(tuple, builder.grid_of(observation).tolist())),
                   tuple(builder.state_numbers_of(observation).tolist()))


@dataclass(frozen=True)
class WorldSnapshot:
    tick: int
    screen_left_x_pixels: int
    tiles: VisibleTiles
    mario: MarioSnapshot
    enemies: tuple[EnemySnapshot, ...]
    hud: HudSnapshot
    bouncing_blocks: tuple[BouncingBlockSnapshot, ...] = ()
    items: tuple[ItemSnapshot, ...] = ()
    observation: ObservationSnapshot | None = None
    recent_events: tuple[GameEvent, ...] = ()        # oldest first

    @classmethod
    def of(cls, attempt: Attempt, hud: HudSnapshot | None = None,
           observation_builder: ObservationBuilder | None = None) -> "WorldSnapshot":
        """The attempt as a renderer sees it. The HUD shows the attempt's own
        numbers unless a mode passes its own (PlaySession carries them across lives).
        Given a builder, it also holds Mario's Observation for the Debug view."""
        screen_left_x_pixels = attempt.scroll.left_x_pixels
        first_column = screen_left_x_pixels // TILE_SIZE_PIXELS
        tiles = attempt.tiles
        rows = tuple(tuple(tiles.tile_kind(column, row)
                           for column in range(first_column, first_column + VISIBLE_COLUMNS))
                     for row in range(tiles.height_tiles))
        return cls(
            tick=attempt.ticks_elapsed,
            screen_left_x_pixels=screen_left_x_pixels,
            tiles=VisibleTiles(first_column, rows),
            mario=MarioSnapshot.of(attempt.mario),
            enemies=tuple(EnemySnapshot.of(enemy) for enemy in attempt.enemies.active),
            hud=hud if hud is not None else HudSnapshot.of(attempt),
            bouncing_blocks=tuple(BouncingBlockSnapshot(block.column, block.row, block.offset_y_pixels)
                                  for block in attempt.blocks.bouncing),
            items=tuple(ItemSnapshot.of(item) for item in attempt.items.active),
            observation=(ObservationSnapshot.of(attempt, observation_builder)
                         if observation_builder is not None else None),
            recent_events=_recent_events(attempt),
        )


def _recent_events(attempt: Attempt) -> tuple[GameEvent, ...]:
    """The game events of the last few seconds, read back from the newest."""
    oldest_recent_tick = attempt.ticks_elapsed - RECENT_GAME_EVENT_TICKS
    recent_count = 0
    for event in reversed(attempt.events):
        if event.tick <= oldest_recent_tick:
            break
        recent_count += 1
    return tuple(attempt.events[len(attempt.events) - recent_count:])
