"""What a renderer may see of an Attempt on one tick. Renderers read only these."""

from dataclasses import dataclass
from enum import StrEnum

from mario.constants.level import SCREEN_WIDTH_PIXELS, TILE_SIZE_PIXELS
from mario.constants.snapshots import RECENT_GAME_EVENT_TICKS
from mario.controller.controller_state import RIGHT
from mario.level.static_level import EnemyKind
from mario.level.tile_kind import TileKind
from mario.simulation.attempt import Attempt
from mario.simulation.attempt_result import EndReason
from mario.simulation.enemy import Enemy
from mario.simulation.fireball import Fireball
from mario.simulation.flagpole import Flag
from mario.simulation.item import Item
from mario.simulation.mario import Mario
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
    """One enemy's hitbox, in level pixels, whether it has been defeated, and
    whether it is a Koopa's shell."""
    kind: EnemyKind
    x_pixels: int
    y_pixels: int
    width_pixels: int
    height_pixels: int
    is_defeated: bool
    is_shell: bool = False

    @classmethod
    def of(cls, enemy: Enemy) -> "EnemySnapshot":
        hitbox = enemy.hitbox()
        return cls(enemy.kind, hitbox.x_pixels, hitbox.y_pixels, hitbox.width_pixels, hitbox.height_pixels,
                   enemy.is_defeated, enemy.is_shell)


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
class FireballSnapshot:
    """One of Mario's fireballs: its box in level pixels, and whether it is exploding."""
    x_pixels: int
    y_pixels: int
    width_pixels: int
    height_pixels: int
    is_exploding: bool

    @classmethod
    def of(cls, fireball: Fireball) -> "FireballSnapshot":
        hitbox = fireball.hitbox()
        return cls(hitbox.x_pixels, hitbox.y_pixels, hitbox.width_pixels, hitbox.height_pixels,
                   fireball.is_exploding)


@dataclass(frozen=True)
class FlagSnapshot:
    """The flag on the flagpole: its top-left corner, in level pixels."""
    x_pixels: int
    y_pixels: int

    @classmethod
    def of(cls, flag: Flag) -> "FlagSnapshot":
        return cls(flag.x_pixels, flag.y_pixels)


@dataclass(frozen=True)
class HudSnapshot:
    """The numbers the HUD shows: score, coins and the level timer's time left."""
    score: int
    coins: int
    time_left: int

    @classmethod
    def of(cls, attempt: Attempt) -> "HudSnapshot":
        """The attempt's own numbers. From the flagpole touch on, the score shows the
        touch's points only as they arrive, and the time counts down into it."""
        score, time_left = attempt.scoreboard.score, attempt.level_timer.time_left
        if attempt.end_of_level is not None:
            score -= attempt.end_of_level.points_still_to_count
            time_left = attempt.end_of_level.time_left
        return cls(score, attempt.scoreboard.coins, time_left)


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


class Area(StrEnum):
    """Where in the game an agent's Mario is."""
    LEVEL = "level"
    # The bonus room joins with #23, and with it the rule that ranks him there as
    # being at the warp pipe's column (AgentSnapshot.ranking_x_pixels).


@dataclass(frozen=True)
class AgentSnapshot:
    """One agent of a watched generation on one tick: his Mario's hitbox and power
    state, which way he faces, where he is, and whether he is still in his attempt
    or has reached the flag.

    Which way he faces is kept for the texture pass (spec section 12): until
    Mario's sprites get a facing, neither view draws one, for the followed agent
    or for a ghost, so a ghost is drawn just as the followed agent is."""
    agent_index: int                                  # his index within the generation
    mario: MarioSnapshot
    faces_right: bool
    area: Area
    is_in_attempt: bool
    reached_flag: bool

    @classmethod
    def of(cls, agent_index: int, attempt: Attempt) -> "AgentSnapshot":
        return cls(agent_index, MarioSnapshot.of(attempt.mario), attempt.mario.facing_direction == RIGHT, Area.LEVEL,
                   not attempt.is_over, attempt.end_reason is EndReason.REACHED_FLAG)

    @property
    def ranking_x_pixels(self) -> int:
        """How far right he counts when the followed agent and the ghosts are chosen:
        his level x. This is the seam for the bonus room (#23): there, he is to
        count as being at the warp pipe's column, 57."""
        return self.mario.x_pixels


@dataclass(frozen=True)
class GenerationProgress:
    """The HUD's line while a generation is watched: how many of its agents are
    still in their attempt, and how many have reached the flag."""
    generation: int
    alive: int
    population_size: int
    reached_flag: int


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
    fireballs: tuple[FireballSnapshot, ...] = ()
    flag: FlagSnapshot | None = None                  # None in a level without a flagpole
    observation: ObservationSnapshot | None = None
    recent_events: tuple[GameEvent, ...] = ()        # oldest first
    ghosts: tuple[AgentSnapshot, ...] = ()           # watched generations: other agents, the rightmost first
    generation_progress: GenerationProgress | None = None

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
            fireballs=tuple(FireballSnapshot.of(fireball) for fireball in attempt.fireballs.active),
            flag=FlagSnapshot.of(attempt.flag) if attempt.flag is not None else None,
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
