"""Which animation frame Mario and the enemies show, as the game picks it and
their snapshots carry it to the Sprite view (#57): Mario's pose and walking
frame (ProcessPlayerAction, AnimationControl, GetPlayerAnimSpeed), an enemy's
walking frame (CheckForSecondFrame)."""

import pytest

from mario.constants.animation import (
    ENEMY_FIRST_WALK_FRAME,
    ENEMY_SECOND_WALK_FRAME,
    ENEMY_WALK_FRAME_TICK_BIT,
    FIRST_WALK_FRAME,
    RUN_ANIMATION_SPEED,
    RUN_TICKS_PER_WALK_FRAME,
    SLOW_TICKS_PER_WALK_FRAME,
    WALK_ANIMATION_SPEED,
    WALK_FRAME_COUNT,
    WALK_TICKS_PER_WALK_FRAME,
)
from mario.constants.physics import NES_X_SPEED_UNIT
from mario.controller.controller_state import LEFT, ControllerState
from mario.modes.play_session import PlaySession
from mario.simulation.attempt import Attempt
from mario.simulation.attempt_tiles import AttemptTiles
from mario.simulation.goomba import Goomba
from mario.simulation.mario import MovementState
from mario.simulation.mario_animation import MarioAnimation, MarioPose
from mario.snapshots.world_snapshot import AgentSnapshot, EnemySnapshot, MarioSnapshot, WorldSnapshot
from tests.game.helpers import (
    HOLD_JUMP,
    HOLD_LEFT,
    HOLD_NOTHING,
    HOLD_RIGHT,
    HOLD_RIGHT_RUN,
    big_mario_attempt,
    build_level,
    goomba_spawn,
)
from tests.game.test_end_of_level import (
    FLAG_BOTTOM_Y_PIXELS,
    MARIO_ON_THE_POLE_X_PIXELS,
    play_out_the_end_of_the_level,
    run_to_the_flagpole,
)

HOLD_DOWN = ControllerState.bitmask(down=True)
HOLD_DOWN_JUMP = ControllerState.bitmask(down=True, jump=True)
# Long enough to reach the top speed of a walk or a run from standing.
TICKS_TO_TOP_SPEED = 90
# A few walk cycles, at any speed.
TICKS_WATCHED = 3 * WALK_FRAME_COUNT * SLOW_TICKS_PER_WALK_FRAME
TICKS_IN_THE_AIR = 5
# The ground ends at this column; walking right from the start, Mario walks off it.
LEDGE_COLUMN = 8
TICKS_FALLING_WATCHED = 6
# A Goomba spawned just past the screen's right edge is active from the first tick.
GOOMBA_SPAWN_X_PIXELS = 260
# Watched over several cycles of the enemies' 16-tick walk.
ENEMY_TICKS_WATCHED = 64


def walk_frames_shown(animation: MarioAnimation, ticks: int) -> list[int]:
    frames = []
    for _ in range(ticks):
        animation.show(MarioPose.WALKING)
        frames.append(animation.walk_frame)
    return frames


def frame_runs(frames: list[int]) -> list[tuple[int, int]]:
    """The frames as (frame, how many ticks in a row it showed)."""
    runs = []
    for frame in frames:
        if runs and runs[-1][0] == frame:
            runs[-1] = (frame, runs[-1][1] + 1)
        else:
            runs.append((frame, 1))
    return runs


@pytest.mark.parametrize("x_speed_absolute, ticks_per_walk_frame", [
    pytest.param(RUN_ANIMATION_SPEED, RUN_TICKS_PER_WALK_FRAME, id="running"),
    pytest.param(RUN_ANIMATION_SPEED - NES_X_SPEED_UNIT, WALK_TICKS_PER_WALK_FRAME, id="walking fast"),
    pytest.param(WALK_ANIMATION_SPEED, WALK_TICKS_PER_WALK_FRAME, id="walking"),
    pytest.param(WALK_ANIMATION_SPEED - NES_X_SPEED_UNIT, SLOW_TICKS_PER_WALK_FRAME, id="walking slowly"),
])
def test_the_walk_shows_frames_1_2_3_each_for_as_many_ticks_as_his_speed_gives(x_speed_absolute,
                                                                               ticks_per_walk_frame):
    """The first frame shows once and the walk steps at once, its timer starting at 0."""
    animation = MarioAnimation()
    animation.choose_walk_speed(x_speed_absolute)
    frames = walk_frames_shown(animation, 1 + 2 * WALK_FRAME_COUNT * ticks_per_walk_frame)
    assert frames[0] == FIRST_WALK_FRAME
    assert frames[1:] == [frame for _ in range(2) for frame in (2, 3, 1) for _ in range(ticks_per_walk_frame)]


@pytest.mark.parametrize("buttons, ticks_per_walk_frame", [
    pytest.param(HOLD_RIGHT_RUN, RUN_TICKS_PER_WALK_FRAME, id="running"),
    pytest.param(HOLD_RIGHT, WALK_TICKS_PER_WALK_FRAME, id="walking"),
])
def test_his_legs_move_faster_at_running_speed(flat_level, buttons, ticks_per_walk_frame):
    attempt = Attempt(flat_level)
    for _ in range(TICKS_TO_TOP_SPEED):
        attempt.step(buttons)
    frames = []
    for _ in range(TICKS_WATCHED):
        attempt.step(buttons)
        snapshot = MarioSnapshot.of(attempt.mario)
        assert snapshot.pose is MarioPose.WALKING
        frames.append(snapshot.walk_frame)
    whole_runs = frame_runs(frames)[1:-1]
    assert {ticks for _, ticks in whole_runs} == {ticks_per_walk_frame}
    assert [frame for frame, _ in whole_runs[:WALK_FRAME_COUNT]] in ([1, 2, 3], [2, 3, 1], [3, 1, 2])


def test_he_stands_with_no_speed_and_nothing_held(flat_level):
    attempt = Attempt(flat_level)
    attempt.step(HOLD_NOTHING)
    assert (MarioSnapshot.of(attempt.mario).pose, MarioSnapshot.of(attempt.mario).walk_frame) == (
        MarioPose.STANDING, FIRST_WALK_FRAME)


def test_in_the_air_he_shows_the_jump_frame_and_walks_again_once_landed(flat_level):
    attempt = Attempt(flat_level)
    for _ in range(TICKS_IN_THE_AIR):
        attempt.step(HOLD_RIGHT)
    for _ in range(TICKS_IN_THE_AIR):
        attempt.step(HOLD_RIGHT | HOLD_JUMP)
        assert MarioSnapshot.of(attempt.mario).pose is MarioPose.JUMPING
    while not attempt.mario.is_on_ground:
        attempt.step(HOLD_RIGHT)
    attempt.step(HOLD_RIGHT)
    assert MarioSnapshot.of(attempt.mario).pose is MarioPose.WALKING


def test_big_mario_holding_down_crouches_on_the_ground_and_in_a_jump(flat_level):
    attempt = big_mario_attempt(flat_level)
    attempt.step(HOLD_DOWN)
    assert MarioSnapshot.of(attempt.mario).pose is MarioPose.CROUCHING
    attempt.step(HOLD_DOWN_JUMP)
    attempt.step(HOLD_DOWN_JUMP)
    assert attempt.mario.movement_state is MovementState.JUMPING
    assert MarioSnapshot.of(attempt.mario).pose is MarioPose.CROUCHING


def test_running_and_then_holding_the_other_way_he_skids_until_he_turns_round(flat_level):
    attempt = Attempt(flat_level)
    for _ in range(TICKS_TO_TOP_SPEED):
        attempt.step(HOLD_RIGHT_RUN)
    attempt.step(HOLD_LEFT)
    assert MarioSnapshot.of(attempt.mario).pose is MarioPose.SKIDDING
    poses = []
    for _ in range(TICKS_TO_TOP_SPEED):
        attempt.step(HOLD_LEFT)
        poses.append(MarioSnapshot.of(attempt.mario).pose)
    assert attempt.mario.moving_direction == LEFT
    assert poses[-1] is MarioPose.WALKING


def test_walking_off_a_ledge_he_keeps_the_walking_frame_he_had():
    attempt = Attempt(build_level(pit_columns=range(LEDGE_COLUMN, LEDGE_COLUMN + 4)))
    while attempt.mario.movement_state is not MovementState.FALLING:
        attempt.step(HOLD_RIGHT)
    frames = set()
    for _ in range(TICKS_FALLING_WATCHED):
        attempt.step(HOLD_RIGHT)
        snapshot = MarioSnapshot.of(attempt.mario)
        assert snapshot.pose is MarioPose.WALKING
        frames.add(snapshot.walk_frame)
    assert len(frames) == 1


def test_while_his_power_state_changes_he_stands_and_his_walk_starts_again_from_its_first_frame(flat_level):
    attempt = Attempt(flat_level)
    while MarioSnapshot.of(attempt.mario).walk_frame == FIRST_WALK_FRAME:
        attempt.step(HOLD_RIGHT)
    attempt.mario.grow()
    while attempt.mario.is_changing_power_state:
        attempt.step(HOLD_RIGHT)
        snapshot = MarioSnapshot.of(attempt.mario)
        assert (snapshot.pose, snapshot.walk_frame) == (MarioPose.STANDING, FIRST_WALK_FRAME)
    attempt.step(HOLD_RIGHT)
    snapshot = MarioSnapshot.of(attempt.mario)
    assert (snapshot.pose, snapshot.walk_frame) == (MarioPose.WALKING, FIRST_WALK_FRAME)


def test_an_agent_carries_his_marios_frame(flat_level):
    attempt = Attempt(flat_level)
    attempt.step(HOLD_RIGHT | HOLD_JUMP)
    assert AgentSnapshot.of(0, attempt).mario.pose is MarioPose.JUMPING


def test_on_the_pole_he_keeps_one_walking_frame_and_walking_to_the_castle_his_legs_move(world_1_1):
    session = PlaySession(world_1_1)
    run_to_the_flagpole(session)
    snapshots = play_out_the_end_of_the_level(session)
    slide = [snapshot.mario for snapshot in snapshots if snapshot.flag.y_pixels < FLAG_BOTTOM_Y_PIXELS]
    assert {(mario.pose, mario.walk_frame) for mario in slide[1:]} == {(MarioPose.WALKING, FIRST_WALK_FRAME)}
    walking = [snapshot.mario for snapshot in snapshots if snapshot.mario.x_pixels > MARIO_ON_THE_POLE_X_PIXELS]
    assert {mario.walk_frame for mario in walking if mario.pose is MarioPose.WALKING} == {1, 2, 3}


# --- The enemies ---------------------------------------------------------------------------


def test_a_walking_enemy_shows_its_second_frame_on_ticks_with_the_frame_bit_clear(world_1_1):
    goomba = Goomba(world_1_1.enemy_spawns[0])
    tiles = AttemptTiles(world_1_1)
    for tick in range(1, ENEMY_TICKS_WATCHED + 1):
        goomba.step(tiles, tick)
        expected = ENEMY_FIRST_WALK_FRAME if tick & ENEMY_WALK_FRAME_TICK_BIT else ENEMY_SECOND_WALK_FRAME
        assert EnemySnapshot.of(goomba).walk_frame == expected


def test_an_enemys_walk_stops_while_the_game_stands_still():
    attempt = Attempt(build_level(enemy_spawns=(goomba_spawn(GOOMBA_SPAWN_X_PIXELS),)))
    attempt.step(HOLD_NOTHING)
    assert len(attempt.enemies.active) == 1
    frame_before = WorldSnapshot.of(attempt).enemies[0].walk_frame
    attempt.mario.grow()
    frames = set()
    while attempt.mario.is_changing_power_state:
        attempt.step(HOLD_NOTHING)
        frames.add(WorldSnapshot.of(attempt).enemies[0].walk_frame)
    assert frames == {frame_before}
