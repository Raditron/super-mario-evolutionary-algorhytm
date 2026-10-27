"""Big Mario whose box has come inside a solid tile, by growing or standing up
under it: the original's head and side probes get him out (PlayerBGCollision,
ImpedePlayerMove; #19, docs/research/smb-physics-constants.md)."""

from mario.controller.controller_state import ControllerState
from mario.simulation.attempt import Attempt
from mario.simulation.attempt_result import GameEventKind
from tests.game.helpers import (
    GROUND_TOP_ROW,
    HOLD_JUMP,
    HOLD_NOTHING,
    HOLD_RIGHT,
    HOLD_RIGHT_RUN,
    big_mario_attempt,
    build_level,
)

HOLD_DOWN = ControllerState.bitmask(down=True)
COIN_QUESTION_BLOCK = "?"
TILE_PIXELS = 16
GROUND_Y = GROUND_TOP_ROW * TILE_PIXELS
MARIO_WIDTH = 12
SMALL_MARIO_HEIGHT = 14
BIG_MARIO_HEIGHT = 28
# Small Mario spawns with his box over columns 2 and 3. A block over column 3
# whose bottom is 2 px above his head lets him stand under it small, not big.
MARIO_SPAWN_COLUMN = 3
LOW_CEILING_ROW = GROUND_TOP_ROW - 2
LOW_CEILING_LEFT_X = MARIO_SPAWN_COLUMN * TILE_PIXELS
LOW_BLOCK_ROW = 9
LOW_BLOCK_BOTTOM_Y = (LOW_BLOCK_ROW + 1) * TILE_PIXELS
# His head probe hits a tile it is at least 4 px into (HeadChk: low nybble >= 4).
HEAD_PROBE_MIN_DEPTH_PIXELS = 4
# A two-tile low ceiling further right, that big Mario slides under crouching.
CROUCH_CEILING_COLUMNS = range(6, 8)
CROUCH_CEILING_LEFT_X = CROUCH_CEILING_COLUMNS.start * TILE_PIXELS
CROUCH_CEILING_RIGHT_X = CROUCH_CEILING_COLUMNS.stop * TILE_PIXELS
TICK_LIMIT = 400


def grow_now(attempt: Attempt) -> None:
    """Grow as a Super Mushroom makes him, wherever he is, and wait out the freeze."""
    attempt.mario.grow()
    while attempt.mario.is_changing_size:
        attempt.step(HOLD_NOTHING)


def box(attempt: Attempt) -> tuple[int, int, int, int]:
    hitbox = attempt.mario.hitbox()
    return hitbox.x_pixels, hitbox.y_pixels, hitbox.width_pixels, hitbox.height_pixels


def overlaps_tile(attempt: Attempt, column: int, row: int) -> bool:
    x, y, width, height = box(attempt)
    return (x < (column + 1) * TILE_PIXELS and x + width > column * TILE_PIXELS
            and y < (row + 1) * TILE_PIXELS and y + height > row * TILE_PIXELS)


def test_mario_who_grows_under_a_low_block_is_pushed_out_from_under_it_a_pixel_a_tick():
    """Only his right side is under the block, so he is pushed left."""
    attempt = Attempt(build_level(hard_blocks=frozenset({(MARIO_SPAWN_COLUMN, LOW_CEILING_ROW)})))
    start_x = box(attempt)[0]
    grow_now(attempt)
    xs = []
    for _ in range(start_x - (LOW_CEILING_LEFT_X - MARIO_WIDTH) + 2):
        attempt.step(HOLD_NOTHING)
        xs.append(box(attempt)[0])
    clear_x = LOW_CEILING_LEFT_X - MARIO_WIDTH
    assert xs == list(range(start_x - 1, clear_x - 1, -1)) + [clear_x] * 2
    assert box(attempt)[1:] == (GROUND_Y - BIG_MARIO_HEIGHT, MARIO_WIDTH, BIG_MARIO_HEIGHT)


def test_mario_who_grows_in_mid_air_under_a_block_falls_out_of_it_pushed_aside():
    """Grown just after his head bumped it, his box's top is inside the block. Its
    right side is, so he is pushed left a pixel a tick while his upper side probe
    is still in it, and falls clear."""
    attempt = Attempt(build_level(hard_blocks=frozenset({(MARIO_SPAWN_COLUMN, LOW_BLOCK_ROW)})))
    attempt.step(HOLD_JUMP)
    while attempt.mario.velocity_y < 0:
        attempt.step(HOLD_JUMP)
    grow_now(attempt)
    grown_x, grown_y, _, _ = box(attempt)
    assert overlaps_tile(attempt, MARIO_SPAWN_COLUMN, LOW_BLOCK_ROW)
    xs = [grown_x]
    while (len(xs) == 1 or not attempt.mario.is_on_ground) and attempt.ticks_elapsed < TICK_LIMIT:
        attempt.step(HOLD_NOTHING)
        assert box(attempt)[1] >= grown_y
        xs.append(box(attempt)[0])
    assert xs[1] == grown_x - 1
    assert all(later - earlier in (0, -1) for earlier, later in zip(xs, xs[1:]))
    assert box(attempt)[1] + BIG_MARIO_HEIGHT == GROUND_Y
    assert not overlaps_tile(attempt, MARIO_SPAWN_COLUMN, LOW_BLOCK_ROW)


def test_mario_who_grows_rising_into_a_block_hits_it_with_his_head_and_rises_no_further():
    """His head probe is inside the ? block, so he bumps it (PlayerHeadCollision)."""
    attempt = Attempt(build_level(blocks={(MARIO_SPAWN_COLUMN, LOW_BLOCK_ROW): COIN_QUESTION_BLOCK}))
    grown_top_y_below_the_block = LOW_BLOCK_BOTTOM_Y - HEAD_PROBE_MIN_DEPTH_PIXELS
    attempt.step(HOLD_JUMP)
    while box(attempt)[1] - (BIG_MARIO_HEIGHT - SMALL_MARIO_HEIGHT) > grown_top_y_below_the_block:
        attempt.step(HOLD_JUMP)
    assert attempt.mario.velocity_y < 0 and not attempt.events
    grow_now(attempt)
    grown_y = box(attempt)[1]
    attempt.step(HOLD_NOTHING)
    assert [event.kind for event in attempt.events][:1] == [GameEventKind.HIT_QUESTION_BLOCK]
    while not attempt.mario.is_on_ground and attempt.ticks_elapsed < TICK_LIMIT:
        assert box(attempt)[1] >= grown_y
        attempt.step(HOLD_NOTHING)


def crouch_slide_under_the_ceiling() -> Attempt:
    """Big Mario runs at the low ceiling and crouches just before it, sliding under."""
    attempt = big_mario_attempt(build_level(
        hard_blocks=frozenset({(column, LOW_CEILING_ROW) for column in CROUCH_CEILING_COLUMNS})))
    while box(attempt)[0] + MARIO_WIDTH < CROUCH_CEILING_LEFT_X - TILE_PIXELS // 2:
        attempt.step(HOLD_RIGHT_RUN)
    while attempt.mario.whole_speed_x > 0:
        attempt.step(HOLD_DOWN)
    x, _, _, height = box(attempt)
    assert CROUCH_CEILING_LEFT_X <= x and x + MARIO_WIDTH <= CROUCH_CEILING_RIGHT_X
    assert height == SMALL_MARIO_HEIGHT
    return attempt


def test_big_mario_standing_up_under_a_low_ceiling_is_pushed_out_from_under_it_a_pixel_a_tick():
    """His left side is under it, which the original checks first: he is pushed right."""
    attempt = crouch_slide_under_the_ceiling()
    xs = [box(attempt)[0]]
    while xs[-1] < CROUCH_CEILING_RIGHT_X and attempt.ticks_elapsed < TICK_LIMIT:
        attempt.step(HOLD_NOTHING)
        xs.append(box(attempt)[0])
    assert xs == list(range(xs[0], CROUCH_CEILING_RIGHT_X + 1))
    attempt.step(HOLD_NOTHING)
    assert box(attempt) == (CROUCH_CEILING_RIGHT_X, GROUND_Y - BIG_MARIO_HEIGHT, MARIO_WIDTH, BIG_MARIO_HEIGHT)


def test_big_mario_standing_up_under_a_low_ceiling_can_walk_out_of_it_to_the_right():
    """Moving right, the original's push from his left side lets him go, and his
    right side is not checked that tick: no box edge stops him inside the ceiling."""
    attempt = crouch_slide_under_the_ceiling()
    previous_x = box(attempt)[0]
    while box(attempt)[0] < CROUCH_CEILING_RIGHT_X and attempt.ticks_elapsed < TICK_LIMIT:
        attempt.step(HOLD_RIGHT)
        assert box(attempt)[0] >= previous_x
        previous_x = box(attempt)[0]
    assert box(attempt)[0] >= CROUCH_CEILING_RIGHT_X
