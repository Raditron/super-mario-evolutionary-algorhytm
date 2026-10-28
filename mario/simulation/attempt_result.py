"""What the game reports about an Attempt (#5): its end reason, its game events and its result."""

from dataclasses import dataclass
from enum import StrEnum


class EndReason(StrEnum):
    DIED_TO_ENEMY = "died_to_enemy"
    FELL_IN_PIT = "fell_in_pit"
    STALLED = "stalled"
    TIMER_RAN_OUT = "timer_ran_out"
    REACHED_FLAG = "reached_flag"


class GameEventKind(StrEnum):
    DEFEATED_ENEMY = "defeated_enemy"
    KICKED_SHELL = "kicked_shell"
    HIT_QUESTION_BLOCK = "hit_question_block"
    BROKE_BRICK = "broke_brick"
    COLLECTED_COIN = "collected_coin"
    COLLECTED_MUSHROOM = "collected_mushroom"
    COLLECTED_FIRE_FLOWER = "collected_fire_flower"
    COLLECTED_STARMAN = "collected_starman"
    COLLECTED_ONE_UP = "collected_one_up"
    SHOT_FIREBALL = "shot_fireball"
    TOOK_DAMAGE = "took_damage"
    HIT_HIDDEN_BLOCK = "hit_hidden_block"
    ENTERED_PIPE = "entered_pipe"
    EXITED_PIPE = "exited_pipe"
    SCORED_POINTS = "scored_points"


class DefeatMethod(StrEnum):
    """How an enemy was defeated: the detail of a defeated_enemy game event."""
    STOMP = "stomp"
    FIREBALL = "fireball"
    BUMPED = "bumped"


@dataclass(frozen=True)
class GameEvent:
    tick: int
    kind: GameEventKind
    detail: str | int | None = None


@dataclass(frozen=True)
class AttemptResult:
    end_reason: EndReason
    furthest_x: int
    ticks_elapsed: int
    final_score: int
    coins_collected: int
    events: tuple[GameEvent, ...]
