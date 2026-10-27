"""The fire flower: what a power-up ? block releases for big Mario, and fire Mario,
who becomes small again when an enemy hurts him (#20, spec sections 1 and 5)."""

from mario.simulation.attempt import Attempt
from mario.simulation.attempt_result import GameEvent, GameEventKind
from mario.simulation.item_kind import ItemKind
from mario.simulation.mario import PowerState
from mario.snapshots.world_snapshot import ItemSnapshot, WorldSnapshot
from tests.game.helpers import (
    GROUND_TOP_ROW,
    HOLD_JUMP,
    HOLD_NOTHING,
    HOLD_RIGHT,
    big_mario_attempt,
    build_level,
    fire_mario_attempt,
    goomba_spawn,
)

POWER_UP_QUESTION_BLOCK = "M"
# Mario spawns with his centre in column 3; a block at row 9 is in reach of a standing jump.
MARIO_SPAWN_COLUMN = 3
LOW_BLOCK_ROW = 9
TILE_PIXELS = 16
BLOCK_X = MARIO_SPAWN_COLUMN * TILE_PIXELS
BLOCK_Y = LOW_BLOCK_ROW * TILE_PIXELS
# An item rises out of its block 1 px every 4 ticks for 16 px; a mushroom sets off
# one step later (GrowThePowerUp), but the fire flower never moves (PowerUpObjHandler).
EMERGE_PIXELS = 16
TICKS_TO_EMERGE = 17 * 4
TICK_LIMIT = 600
ITEM_POINTS = 1000                                  # HandlePowerUpCollision: floatey number $06
# Catching fire freezes the game for 63 ticks (TimerControl from $FF down to $C0,
# PlayerFireFlower); his box stays big Mario's.
CATCH_FIRE_TICKS = 63
MARIO_WIDTH = 12
SMALL_MARIO_HEIGHT = 14
BIG_MARIO_HEIGHT = 28
# Getting hurt freezes the game for 55 ticks (TimerControl from $FF down to $C8).
SHRINK_TICKS = 55
# A Goomba walking left at Mario from just past the screen's right edge.
GOOMBA_AT_THE_SCREEN_EDGE_X = 260
GROUND_Y = GROUND_TOP_ROW * TILE_PIXELS
# An item released on the ground a few columns right of Mario, for him to walk into.
ITEM_ON_THE_GROUND = (6, GROUND_TOP_ROW - 1)
# A Goomba walking left from just off screen, turned back by a wall well right of Mario.
GOOMBA_START_X = 290
GOOMBA_PEN_WALL = (14, GROUND_TOP_ROW - 1)


def power_up_block_level():
    return build_level(blocks={(MARIO_SPAWN_COLUMN, LOW_BLOCK_ROW): POWER_UP_QUESTION_BLOCK})


def jump_until_the_head_hits(attempt: Attempt) -> None:
    attempt.step(HOLD_JUMP)
    while attempt.mario.velocity_y < 0:
        attempt.step(HOLD_JUMP)


def items_in(attempt: Attempt) -> tuple[ItemSnapshot, ...]:
    return WorldSnapshot.of(attempt).items


def test_big_mario_hitting_a_power_up_block_releases_a_fire_flower_inside_it():
    attempt = big_mario_attempt(power_up_block_level())
    jump_until_the_head_hits(attempt)
    assert [(item.kind, item.x_pixels, item.y_pixels) for item in items_in(attempt)] == [
        (ItemKind.FIRE_FLOWER, BLOCK_X, BLOCK_Y)]


def test_small_mario_hitting_the_same_block_still_gets_a_super_mushroom():
    attempt = Attempt(power_up_block_level())
    jump_until_the_head_hits(attempt)
    assert [item.kind for item in items_in(attempt)] == [ItemKind.SUPER_MUSHROOM]


def test_the_fire_flower_rises_out_of_its_block_like_a_mushroom_then_stays_where_it_is():
    attempt = big_mario_attempt(power_up_block_level())
    jump_until_the_head_hits(attempt)
    for _ in range(TICKS_TO_EMERGE):
        attempt.step(HOLD_NOTHING)
    risen = [(item.x_pixels, item.y_pixels, item.is_emerging) for item in items_in(attempt)]
    assert risen == [(BLOCK_X, BLOCK_Y - EMERGE_PIXELS, False)]
    for _ in range(TICKS_TO_EMERGE):
        attempt.step(HOLD_NOTHING)
    assert [(item.x_pixels, item.y_pixels) for item in items_in(attempt)] == [(BLOCK_X, BLOCK_Y - EMERGE_PIXELS)]



def event_kinds(attempt: Attempt) -> list[GameEventKind]:
    return [event.kind for event in attempt.events]


def mario_box(attempt: Attempt) -> tuple[int, int, int, int]:
    mario = WorldSnapshot.of(attempt).mario
    return mario.x_pixels, mario.y_pixels, mario.width_pixels, mario.height_pixels


def walk_into_an_item_on_the_ground(attempt: Attempt, kind: ItemKind, collected: GameEventKind) -> None:
    attempt.items.release(kind, *ITEM_ON_THE_GROUND)
    while collected not in event_kinds(attempt) and attempt.ticks_elapsed < TICK_LIMIT:
        attempt.step(HOLD_RIGHT)


def test_collecting_the_fire_flower_scores_1000_points_and_makes_big_mario_fiery():
    attempt = big_mario_attempt(build_level())
    walk_into_an_item_on_the_ground(attempt, ItemKind.FIRE_FLOWER, GameEventKind.COLLECTED_FIRE_FLOWER)
    tick = attempt.ticks_elapsed
    assert attempt.events[-2:] == [GameEvent(tick, GameEventKind.COLLECTED_FIRE_FLOWER),
                                   GameEvent(tick, GameEventKind.SCORED_POINTS, ITEM_POINTS)]
    assert items_in(attempt) == ()
    assert WorldSnapshot.of(attempt).mario.power_state is PowerState.FIERY


def test_while_mario_catches_fire_the_game_stands_still_and_his_box_stays_big():
    attempt = big_mario_attempt(build_level(hard_blocks=frozenset({GOOMBA_PEN_WALL}),
                                            enemy_spawns=(goomba_spawn(GOOMBA_START_X),)))
    walk_into_an_item_on_the_ground(attempt, ItemKind.FIRE_FLOWER, GameEventKind.COLLECTED_FIRE_FLOWER)
    timer_before = attempt.level_timer.time_left
    goomba_before = WorldSnapshot.of(attempt).enemies[0].x_pixels
    boxes = set()
    for _ in range(CATCH_FIRE_TICKS):
        attempt.step(HOLD_RIGHT)
        boxes.add(mario_box(attempt))
    x, y, width, height = boxes.pop()
    assert boxes == set() and (width, height, y + height) == (MARIO_WIDTH, BIG_MARIO_HEIGHT, GROUND_Y)
    assert WorldSnapshot.of(attempt).enemies[0].x_pixels == goomba_before
    assert attempt.level_timer.time_left == timer_before
    attempt.step(HOLD_RIGHT)
    assert mario_box(attempt)[0] > x


def test_a_super_mushroom_collected_by_big_mario_makes_him_fiery_too():
    """Shroom_Flower_PUp doesn't look at which of the two it was."""
    attempt = big_mario_attempt(build_level())
    walk_into_an_item_on_the_ground(attempt, ItemKind.SUPER_MUSHROOM, GameEventKind.COLLECTED_MUSHROOM)
    assert WorldSnapshot.of(attempt).mario.power_state is PowerState.FIERY


def test_a_fire_flower_collected_by_small_mario_only_makes_him_big():
    attempt = Attempt(build_level())
    walk_into_an_item_on_the_ground(attempt, ItemKind.FIRE_FLOWER, GameEventKind.COLLECTED_FIRE_FLOWER)
    assert GameEventKind.COLLECTED_FIRE_FLOWER in event_kinds(attempt)
    while attempt.mario.is_changing_size:
        attempt.step(HOLD_NOTHING)
    assert WorldSnapshot.of(attempt).mario.power_state is PowerState.BIG


def test_fire_mario_touched_by_a_goomba_becomes_small_and_survives():
    """ForceInjury sets PlayerStatus to small whether he was big or fiery."""
    attempt = fire_mario_attempt(build_level(enemy_spawns=(goomba_spawn(GOOMBA_AT_THE_SCREEN_EDGE_X),)))
    while GameEventKind.TOOK_DAMAGE not in event_kinds(attempt) and not attempt.is_over:
        attempt.step(HOLD_NOTHING)
    assert attempt.events == [GameEvent(attempt.ticks_elapsed, GameEventKind.TOOK_DAMAGE)]
    for _ in range(SHRINK_TICKS):
        attempt.step(HOLD_NOTHING)
    assert not attempt.is_over
    assert mario_box(attempt)[2:] == (MARIO_WIDTH, SMALL_MARIO_HEIGHT)
    assert WorldSnapshot.of(attempt).mario.power_state is PowerState.SMALL
