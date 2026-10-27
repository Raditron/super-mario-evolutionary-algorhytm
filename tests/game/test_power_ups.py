"""Power-ups: the Super Mushroom a power-up ? block releases, Mario growing when he
collects it, and the hidden block's 1-UP mushroom (#19, spec sections 1 and 5)."""

from mario.simulation.attempt import Attempt
from mario.simulation.attempt_result import GameEvent, GameEventKind
from mario.simulation.mario import PowerState
from mario.simulation.mushroom import ItemKind
from mario.snapshots.world_snapshot import ItemSnapshot, WorldSnapshot
from tests.game.helpers import (
    GROUND_TOP_ROW,
    HOLD_JUMP,
    HOLD_NOTHING,
    HOLD_RIGHT,
    big_mario_attempt,
    build_level,
    goomba_spawn,
)

POWER_UP_QUESTION_BLOCK = "M"
HIDDEN_ONE_UP_BLOCK = "U"
# Small Mario spawns with his centre in column 3; a block at row 9 is in reach of a standing jump.
MARIO_SPAWN_COLUMN = 3
LOW_BLOCK_ROW = 9
TILE_PIXELS = 16
BLOCK_X = MARIO_SPAWN_COLUMN * TILE_PIXELS
BLOCK_Y = LOW_BLOCK_ROW * TILE_PIXELS
GROUND_Y = GROUND_TOP_ROW * TILE_PIXELS
TICK_LIMIT = 600
# The mushroom rises 1 px every 4 ticks for 16 px, then sets off right one step
# later (GrowThePowerUp: 17 steps of 4 frames), at 1 px/f (docs/research/smb-physics-constants.md).
EMERGE_PIXELS = 16
TICKS_PER_EMERGE_PIXEL = 4
TICKS_BEFORE_IT_MOVES = 17 * TICKS_PER_EMERGE_PIXEL
POWER_UP_POINTS = 1000                                  # HandlePowerUpCollision: floatey number $06
# Small Mario's box is 12 x 14; big Mario's is 28 tall, from his head probe at
# sprite y + 4 to his feet (BlockBufferAdderData). The intermediate grow frame is
# drawn 21 tall, midway between them.
MARIO_WIDTH = 12
SMALL_MARIO_HEIGHT = 14
BIG_MARIO_HEIGHT = 28
INTERMEDIATE_MARIO_HEIGHT = 21
# Growing freezes the game for 59 ticks (TimerControl from $FF down to $C4). His
# size flips on the 7th ($F8); from then on each animation frame shows for 4
# ticks, small, intermediate or big, as ChangeSizeOffsetAdder lists them.
GROW_TICKS = 59
GROW_FLIP_TICK = 7
GROW_ANIMATION = ([SMALL_MARIO_HEIGHT, INTERMEDIATE_MARIO_HEIGHT] * 3
                  + [BIG_MARIO_HEIGHT, SMALL_MARIO_HEIGHT, INTERMEDIATE_MARIO_HEIGHT, BIG_MARIO_HEIGHT])
GROW_HEIGHTS_BY_TICK = ([SMALL_MARIO_HEIGHT] * (GROW_FLIP_TICK - 1)
                        + [height for height in GROW_ANIMATION for _ in range(TICKS_PER_EMERGE_PIXEL)])
GROW_HEIGHTS_BY_TICK += [BIG_MARIO_HEIGHT] * (GROW_TICKS - len(GROW_HEIGHTS_BY_TICK))
# A Goomba walking left from just off screen, turned back by a wall well right of
# where Mario catches the mushroom.
GOOMBA_START_X = 290
GOOMBA_PEN_WALL = (14, GROUND_TOP_ROW - 1)
PIT_FAR_RIGHT = range(40, 44)


def jump_until_the_head_hits(attempt: Attempt) -> None:
    attempt.step(HOLD_JUMP)
    while attempt.mario.velocity_y < 0:
        attempt.step(HOLD_JUMP)


def items_in(attempt: Attempt) -> tuple[ItemSnapshot, ...]:
    return WorldSnapshot.of(attempt).items


def item_positions(attempt: Attempt) -> list[tuple[int, int]]:
    return [(item.x_pixels, item.y_pixels) for item in items_in(attempt)]


def event_kinds(attempt: Attempt) -> list[GameEventKind]:
    return [event.kind for event in attempt.events]


def mario_box(attempt: Attempt) -> tuple[int, int, int, int]:
    mario = WorldSnapshot.of(attempt).mario
    return mario.x_pixels, mario.y_pixels, mario.width_pixels, mario.height_pixels


def collect_the_item(attempt: Attempt, collected: GameEventKind) -> None:
    """Bump the block over Mario, wait for the item to rise out of it, then walk
    right after it until he touches it."""
    jump_until_the_head_hits(attempt)
    while items_in(attempt) and items_in(attempt)[0].is_emerging:
        attempt.step(HOLD_NOTHING)
    while collected not in event_kinds(attempt) and attempt.ticks_elapsed < TICK_LIMIT:
        attempt.step(HOLD_RIGHT)


def test_small_mario_hitting_a_power_up_block_releases_a_super_mushroom_inside_it():
    attempt = Attempt(build_level(blocks={(MARIO_SPAWN_COLUMN, LOW_BLOCK_ROW): POWER_UP_QUESTION_BLOCK}))
    assert items_in(attempt) == ()
    jump_until_the_head_hits(attempt)
    assert [item.kind for item in items_in(attempt)] == [ItemKind.SUPER_MUSHROOM]
    assert item_positions(attempt) == [(BLOCK_X, BLOCK_Y)]


def test_the_mushroom_rises_out_of_its_block_then_moves_right_at_one_pixel_per_tick():
    attempt = Attempt(build_level(blocks={(MARIO_SPAWN_COLUMN, LOW_BLOCK_ROW): POWER_UP_QUESTION_BLOCK}))
    jump_until_the_head_hits(attempt)
    positions = []
    for _ in range(TICKS_BEFORE_IT_MOVES + 3):
        attempt.step(HOLD_NOTHING)
        positions.append(item_positions(attempt)[0])
    # The hit tick is the mushroom's first tick, so it is 4 ticks old 3 ticks after the hit.
    rise_by_tick = [BLOCK_Y - y for _, y in positions]
    assert rise_by_tick[:9] == [0, 0, 1, 1, 1, 1, 2, 2, 2]
    fully_risen_index = EMERGE_PIXELS * TICKS_PER_EMERGE_PIXEL - 2
    assert rise_by_tick[fully_risen_index - 1:] == [EMERGE_PIXELS - 1] + [EMERGE_PIXELS] * 9
    moved_by_tick = [x - BLOCK_X for x, _ in positions]
    assert moved_by_tick == [0] * (TICKS_BEFORE_IT_MOVES - 1) + [1, 2, 3, 4]


def test_the_mushroom_falls_off_its_block_and_turns_around_at_a_wall():
    wall_column = MARIO_SPAWN_COLUMN + 6
    attempt = Attempt(build_level(blocks={(MARIO_SPAWN_COLUMN, LOW_BLOCK_ROW): POWER_UP_QUESTION_BLOCK},
                                  hard_blocks=frozenset({(wall_column, GROUND_TOP_ROW - 1)})))
    jump_until_the_head_hits(attempt)
    positions = [item_positions(attempt)[0]]
    while positions[-1][0] >= max(x for x, _ in positions) and attempt.ticks_elapsed < TICK_LIMIT:
        attempt.step(HOLD_NOTHING)
        positions.append(item_positions(attempt)[0])
    resting_on_the_ground_y = GROUND_Y - TILE_PIXELS
    assert positions[-1][1] == resting_on_the_ground_y
    assert max(x for x, _ in positions) == (wall_column - 1) * TILE_PIXELS
    assert positions[-1][0] < positions[-2][0]


def test_collecting_the_mushroom_scores_1000_points_and_makes_small_mario_big():
    attempt = Attempt(build_level(blocks={(MARIO_SPAWN_COLUMN, LOW_BLOCK_ROW): POWER_UP_QUESTION_BLOCK}))
    assert WorldSnapshot.of(attempt).mario.power_state is PowerState.SMALL
    collect_the_item(attempt, GameEventKind.COLLECTED_MUSHROOM)
    tick = attempt.ticks_elapsed
    assert attempt.events[-2:] == [GameEvent(tick, GameEventKind.COLLECTED_MUSHROOM),
                                   GameEvent(tick, GameEventKind.SCORED_POINTS, POWER_UP_POINTS)]
    assert items_in(attempt) == ()
    assert WorldSnapshot.of(attempt).mario.power_state is PowerState.BIG
    for _ in range(GROW_TICKS):
        attempt.step(HOLD_NOTHING)
    _, y, width, height = mario_box(attempt)
    assert (width, height, y + height) == (MARIO_WIDTH, BIG_MARIO_HEIGHT, GROUND_Y)


def test_while_mario_grows_the_game_stands_still_and_his_box_follows_the_grow_animation():
    attempt = Attempt(build_level(blocks={(MARIO_SPAWN_COLUMN, LOW_BLOCK_ROW): POWER_UP_QUESTION_BLOCK},
                                  hard_blocks=frozenset({GOOMBA_PEN_WALL}),
                                  enemy_spawns=(goomba_spawn(GOOMBA_START_X),)))
    collect_the_item(attempt, GameEventKind.COLLECTED_MUSHROOM)
    timer_before = attempt.level_timer.time_left
    goomba_before = WorldSnapshot.of(attempt).enemies[0].x_pixels
    boxes = []
    for _ in range(GROW_TICKS):
        attempt.step(HOLD_RIGHT)
        boxes.append(mario_box(attempt))
    assert {(x, y + height) for x, y, _, height in boxes} == {(boxes[0][0], GROUND_Y)}
    assert [height for _, _, _, height in boxes] == GROW_HEIGHTS_BY_TICK
    assert WorldSnapshot.of(attempt).enemies[0].x_pixels == goomba_before
    assert attempt.level_timer.time_left == timer_before
    attempt.step(HOLD_RIGHT)
    assert mario_box(attempt)[0] > boxes[0][0]


def test_a_mushroom_collected_while_big_scores_but_changes_nothing_until_the_fire_flower_is_built():
    attempt = big_mario_attempt(build_level(blocks={(MARIO_SPAWN_COLUMN, LOW_BLOCK_ROW): POWER_UP_QUESTION_BLOCK}))
    collect_the_item(attempt, GameEventKind.COLLECTED_MUSHROOM)
    assert attempt.events[-1] == GameEvent(attempt.ticks_elapsed, GameEventKind.SCORED_POINTS, POWER_UP_POINTS)
    assert not attempt.mario.is_changing_size
    assert WorldSnapshot.of(attempt).mario.power_state is PowerState.BIG


def test_the_hidden_block_releases_a_1_up_mushroom_that_moves_like_the_super_mushroom():
    attempt = Attempt(build_level(blocks={(MARIO_SPAWN_COLUMN, LOW_BLOCK_ROW): HIDDEN_ONE_UP_BLOCK}))
    jump_until_the_head_hits(attempt)
    assert [item.kind for item in items_in(attempt)] == [ItemKind.ONE_UP_MUSHROOM]
    for _ in range(TICKS_BEFORE_IT_MOVES):
        attempt.step(HOLD_NOTHING)
    assert item_positions(attempt) == [(BLOCK_X + 1, BLOCK_Y - EMERGE_PIXELS)]


def test_in_training_the_1_up_is_only_recorded_as_a_game_event():
    attempt = Attempt(build_level(blocks={(MARIO_SPAWN_COLUMN, LOW_BLOCK_ROW): HIDDEN_ONE_UP_BLOCK},
                                  pit_columns=PIT_FAR_RIGHT), ends_on_stall=True)
    collect_the_item(attempt, GameEventKind.COLLECTED_ONE_UP)
    while not attempt.is_over:
        attempt.step(HOLD_RIGHT)
    result = attempt.result()
    assert [event.kind for event in result.events] == [GameEventKind.HIT_HIDDEN_BLOCK, GameEventKind.COLLECTED_ONE_UP]
    assert result.final_score == 0
    assert WorldSnapshot.of(attempt).mario.power_state is PowerState.SMALL
