"""The green Koopa and its shell (#22, spec sections 1, 4 and 5): it walks off
ledges; a stomp leaves a still shell, a touch kicks it, a moving shell defeats
the enemies it hits, bounces off walls and hurts Mario, and a still shell nobody
touches wakes back into a Koopa."""

from mario.constants.physics import INTERVAL_TIMER_TICKS, SHELL_REVIVAL_TICKS, SUBPIXEL_BITS
from mario.level.static_level import EnemyKind, EnemySpawn
from mario.simulation.attempt import Attempt
from mario.simulation.attempt_tiles import AttemptTiles
from mario.simulation.enemy_collision_check import EnemyCollisionCheck
from mario.simulation.koopa import Koopa
from mario.simulation.mario import Mario
from mario.constants.observation import ENEMY_CELL, OBSERVATION_TOP_ROW
from mario.simulation.attempt_result import DefeatMethod, EndReason, GameEvent, GameEventKind
from mario.simulation.observation_builder import ObservationBuilder
from mario.snapshots.world_snapshot import EnemySnapshot, WorldSnapshot
from mario.controller.controller_state import ControllerState
from tests.game.helpers import (
    GROUND_TOP_ROW,
    HOLD_JUMP,
    HOLD_LEFT,
    HOLD_NOTHING,
    HOLD_RIGHT,
    big_mario_attempt,
    build_level,
    fire_mario_attempt,
)

TILE_PIXELS = 16
KOOPA_SIZE_PIXELS = 16                       # its box, walking or in its shell
KOOPA_WALK_PIXELS_PER_TWO_TICKS = 1          # 0.5 px/f (KOOPA_WALK_SPEED)
KOOPA_START_X = 288
# A ledge of hard blocks the Koopa starts on, its left end at column 12.
LEDGE_ROW = 9
LEDGE = frozenset((column, LEDGE_ROW) for column in range(12, 20))
LEDGE_LEFT_X = 12 * TILE_PIXELS
GROUND_TOP_Y = GROUND_TOP_ROW * TILE_PIXELS
# A row of bricks at row 9 over Mario's start (column 3), as in the block tests.
LOW_BLOCK_ROW = 9
BRICK_PLATFORM = {(column, LOW_BLOCK_ROW): "B" for column in range(20)}
MARIO_SPAWN_COLUMN = 3
KOOPA_ON_PLATFORM_X = 17 * TILE_PIXELS
# Mario jumps once the Koopa's centre is this far into the column right of his.
KOOPA_LEAD_PIXELS = 4
BUMPED_ENEMY_POINTS = 100                    # GiveOEPoints
TICK_LIMIT = 2000
HOLD_RUN = ControllerState.bitmask(run=True)
# A Koopa hit by a fireball, walking or in its shell, scores 200 (ShellOrBlockDefeat).
KOOPA_FIREBALL_POINTS = 200
# Mario shoots once the Koopa is this near, well within a fireball's reach.
SHOOTING_RANGE_X = 150
# Jumping in place when a walking Koopa is this close lands Mario on top of it.
STOMP_JUMP_DISTANCE_PIXELS = 16
FIRST_STOMP_POINTS = 100                     # the stomp chain's first step, as for a Goomba
STOMP_BOUNCE_PIXELS_PER_TICK = -4            # SBnce
KICKED_SHELL_PIXELS_PER_TICK = 3             # KickedShellXSpdData $30
# Kicking a shell scores the score table's step 3 past the stomp chain: 400 once
# Mario has landed (HandlePECollisions).
KICK_POINTS_AFTER_LANDING = 400
# A Goomba walking towards the kicked shell from further right, shown at once;
# they meet on the screen (an enemy off it is never hit).
GOOMBA_IN_THE_SHELLS_PATH_X = 500
# A moving shell's defeats climb the score table from its step 4 (ShellCollisions:
# floatey number ShellChainCounter + 4).
FIRST_SHELL_DEFEAT_POINTS = 500
# A 2-tile pipe right of the Koopa's start, its left side at x = 320.
PIPE_COLUMN = 20
PIPE_LEFT_X = PIPE_COLUMN * TILE_PIXELS
PIPE = {(PIPE_COLUMN, GROUND_TOP_ROW - 2): "{", (PIPE_COLUMN + 1, GROUND_TOP_ROW - 2): "}",
        (PIPE_COLUMN, GROUND_TOP_ROW - 1): "[", (PIPE_COLUMN + 1, GROUND_TOP_ROW - 1): "]"}
# A still shell wakes 16 interval ticks of 21 ticks after the stomp (RevivalRateData,
# the longest the interval clock allows), walking at 0.5 px/f, rightwards on an
# even tick (ReviveStunned, RevivedXSpeed by FrameCounter bit 0).
SHELL_WAKE_TICKS = SHELL_REVIVAL_TICKS
# Kicked with 2 interval ticks left before it wakes (22 to 42 ticks), a shell scores
# 500 (KickedShellPtsData).
NEARLY_AWAKE_TICKS_LEFT = 2 * INTERVAL_TIMER_TICKS
NEARLY_AWAKE_KICK_POINTS = 500
# Kicked with its interval timer at 0, as a Koopa never stomped has it, a shell
# scores 8000 (KickedShellPtsData $0A).
TIMER_RUN_OUT_KICK_POINTS = 8000
ENEMY_CHECK_TICK = 2                         # Mario is checked against enemies on even ticks
# Walking right from a standstill and letting go this close to the shell, Mario
# coasts to a stop a few pixels short of it.
COAST_TO_THE_SHELL_GAP_PIXELS = 14
# A pit far right of the Koopa's start, for a kicked shell to fall into; in the
# air a moving shell slides at only 1.5 px/f (XSpeedAdderData takes 24 off its 48).
FAR_PIT_COLUMNS = range(25, 31)
AIRBORNE_SHELL_PIXELS_PER_TWO_TICKS = 3
FALLEN_PIXELS = 4                            # far enough below the ground's top to be falling
# Jumping in place when the shell, back from the pipe, is this close lands Mario on it.
MOVING_SHELL_STOMP_JUMP_DISTANCE_PIXELS = 36


def koopa_spawn(x_pixels: int, resting_row: int = GROUND_TOP_ROW - 1) -> EnemySpawn:
    return EnemySpawn(EnemyKind.KOOPA, x_pixels, resting_row, x_pixels)


def enemies_in(attempt: Attempt) -> tuple[EnemySnapshot, ...]:
    return WorldSnapshot.of(attempt).enemies


def test_a_koopa_appears_with_a_16_by_16_box_and_walks_left_at_half_a_pixel_a_tick():
    attempt = Attempt(build_level(enemy_spawns=(koopa_spawn(KOOPA_START_X),)))
    attempt.step(HOLD_NOTHING)
    (koopa,) = enemies_in(attempt)
    assert (koopa.kind, koopa.x_pixels, koopa.width_pixels, koopa.height_pixels) == (
        EnemyKind.KOOPA, KOOPA_START_X, KOOPA_SIZE_PIXELS, KOOPA_SIZE_PIXELS)
    assert not koopa.is_defeated and not koopa.is_shell
    for _ in range(20):
        attempt.step(HOLD_NOTHING)
    assert enemies_in(attempt)[0].x_pixels == KOOPA_START_X - 10 * KOOPA_WALK_PIXELS_PER_TWO_TICKS


def test_a_green_koopa_walks_off_a_ledge_rather_than_turning_at_it():
    attempt = Attempt(build_level(hard_blocks=LEDGE, enemy_spawns=(koopa_spawn(KOOPA_START_X, LEDGE_ROW - 1),)))
    attempt.step(HOLD_NOTHING)
    step_until(attempt, HOLD_NOTHING, lambda: enemies_in(attempt)[0].y_pixels + KOOPA_SIZE_PIXELS == GROUND_TOP_Y)
    koopa = enemies_in(attempt)[0]
    assert koopa.x_pixels < LEDGE_LEFT_X - KOOPA_SIZE_PIXELS
    attempt.step(HOLD_NOTHING)
    attempt.step(HOLD_NOTHING)
    assert enemies_in(attempt)[0].x_pixels == koopa.x_pixels - KOOPA_WALK_PIXELS_PER_TWO_TICKS


def koopa_attempt(*more_spawns: EnemySpawn, koopa_x: int = KOOPA_START_X, **level_options) -> Attempt:
    return Attempt(build_level(enemy_spawns=(koopa_spawn(koopa_x), *more_spawns), **level_options))


def the_koopa(attempt: Attempt) -> EnemySnapshot:
    (koopa,) = [enemy for enemy in enemies_in(attempt) if enemy.kind is EnemyKind.KOOPA]
    return koopa


def step_until(attempt: Attempt, buttons: int, condition) -> None:
    while not condition() and not attempt.is_over:
        attempt.step(buttons)


def gap_to_the_koopa(attempt: Attempt) -> int:
    """From Mario's right edge to the Koopa's left edge."""
    return the_koopa(attempt).x_pixels - attempt.mario.hitbox().right_x_pixels


def stomp_the_approaching_koopa(attempt: Attempt) -> None:
    """Stand still until the Koopa walks within jumping distance, then jump onto it, holding jump."""
    attempt.step(HOLD_NOTHING)
    step_until(attempt, HOLD_NOTHING, lambda: gap_to_the_koopa(attempt) <= STOMP_JUMP_DISTANCE_PIXELS)
    step_until(attempt, HOLD_JUMP, lambda: the_koopa(attempt).is_shell)


def test_stomping_a_koopa_leaves_a_still_shell_and_bounces_mario():
    attempt = koopa_attempt()
    stomp_the_approaching_koopa(attempt)
    stomp_tick = attempt.ticks_elapsed
    assert not attempt.is_over
    assert attempt.events == [GameEvent(stomp_tick, GameEventKind.DEFEATED_ENEMY, DefeatMethod.STOMP),
                              GameEvent(stomp_tick, GameEventKind.SCORED_POINTS, FIRST_STOMP_POINTS)]
    assert attempt.mario.velocity_y >> SUBPIXEL_BITS == STOMP_BOUNCE_PIXELS_PER_TICK
    shell = the_koopa(attempt)
    assert shell.is_shell and not shell.is_defeated
    attempt.step(HOLD_LEFT)
    step_until(attempt, HOLD_LEFT, lambda: attempt.mario.is_on_ground)
    for _ in range(30):
        attempt.step(HOLD_NOTHING)
    assert the_koopa(attempt) == shell


def kicked_shell_events(attempt: Attempt) -> list[GameEvent]:
    return [event for event in attempt.events if event.kind is GameEventKind.KICKED_SHELL]


def stomp_then_land_left_of_the_shell(attempt: Attempt) -> None:
    stomp_the_approaching_koopa(attempt)
    attempt.step(HOLD_LEFT)
    step_until(attempt, HOLD_LEFT, lambda: attempt.mario.is_on_ground)


def test_walking_into_a_still_shell_kicks_it_away_at_3_pixels_a_tick_unharmed():
    attempt = koopa_attempt()
    stomp_then_land_left_of_the_shell(attempt)
    events_before_the_kick = len(attempt.events)
    step_until(attempt, HOLD_RIGHT, lambda: kicked_shell_events(attempt))
    kick_tick = attempt.ticks_elapsed
    assert attempt.events[events_before_the_kick:] == [
        GameEvent(kick_tick, GameEventKind.KICKED_SHELL),
        GameEvent(kick_tick, GameEventKind.SCORED_POINTS, KICK_POINTS_AFTER_LANDING)]
    kicked_x = the_koopa(attempt).x_pixels
    for _ in range(10):
        attempt.step(HOLD_NOTHING)
    shell = the_koopa(attempt)
    assert shell.is_shell and not shell.is_defeated
    assert shell.x_pixels == kicked_x + 10 * KICKED_SHELL_PIXELS_PER_TICK
    assert not attempt.is_over


def goomba_in_the_shells_path() -> EnemySpawn:
    return EnemySpawn(EnemyKind.GOOMBA, GOOMBA_IN_THE_SHELLS_PATH_X, GROUND_TOP_ROW - 1, KOOPA_START_X)


def kick_the_shell_right(attempt: Attempt) -> None:
    stomp_then_land_left_of_the_shell(attempt)
    step_until(attempt, HOLD_RIGHT, lambda: kicked_shell_events(attempt))


def goombas_in(attempt: Attempt) -> list[EnemySnapshot]:
    return [enemy for enemy in enemies_in(attempt) if enemy.kind is EnemyKind.GOOMBA]


def test_a_moving_shell_defeats_a_goomba_in_its_path_and_slides_on():
    attempt = koopa_attempt(goomba_in_the_shells_path())
    kick_the_shell_right(attempt)
    events_before = len(attempt.events)
    step_until(attempt, HOLD_NOTHING, lambda: goombas_in(attempt)[0].is_defeated)
    hit_tick = attempt.ticks_elapsed
    assert attempt.events[events_before:] == [
        GameEvent(hit_tick, GameEventKind.DEFEATED_ENEMY, DefeatMethod.KICKED_SHELL),
        GameEvent(hit_tick, GameEventKind.SCORED_POINTS, FIRST_SHELL_DEFEAT_POINTS)]
    shell_x = the_koopa(attempt).x_pixels
    attempt.step(HOLD_NOTHING)
    assert the_koopa(attempt).x_pixels == shell_x + KICKED_SHELL_PIXELS_PER_TICK
    step_until(attempt, HOLD_NOTHING, lambda: not goombas_in(attempt))
    assert not attempt.is_over


def test_a_moving_shell_turns_around_at_a_pipe():
    attempt = koopa_attempt(blocks=PIPE)
    kick_the_shell_right(attempt)
    shell_xs = [the_koopa(attempt).x_pixels]
    while len(shell_xs) < 2 or shell_xs[-1] >= shell_xs[-2]:
        attempt.step(HOLD_NOTHING)
        shell_xs.append(the_koopa(attempt).x_pixels)
    assert max(shell_xs) == PIPE_LEFT_X - KOOPA_SIZE_PIXELS
    for _ in range(5):
        attempt.step(HOLD_NOTHING)
        shell_xs.append(the_koopa(attempt).x_pixels)
    assert [later - earlier for earlier, later in zip(shell_xs[-6:], shell_xs[-5:])] == [
        -KICKED_SHELL_PIXELS_PER_TICK] * 5


def test_a_moving_shell_that_hits_small_mario_ends_the_attempt_with_died_to_enemy():
    attempt = koopa_attempt(blocks=PIPE)
    kick_the_shell_right(attempt)
    step_until(attempt, HOLD_NOTHING, lambda: False)
    assert attempt.result().end_reason is EndReason.DIED_TO_ENEMY
    assert the_koopa(attempt).is_shell
    assert the_koopa(attempt).x_pixels < PIPE_LEFT_X - 100


def test_stomping_a_moving_shell_stops_it():
    attempt = koopa_attempt(blocks=PIPE)
    kick_the_shell_right(attempt)
    step_until(attempt, HOLD_NOTHING, lambda: the_koopa(attempt).x_pixels == PIPE_LEFT_X - KOOPA_SIZE_PIXELS)
    step_until(attempt, HOLD_NOTHING, lambda: gap_to_the_koopa(attempt)
               <= MOVING_SHELL_STOMP_JUMP_DISTANCE_PIXELS)
    events_before = len(attempt.events)
    step_until(attempt, HOLD_JUMP, lambda: len(attempt.events) > events_before)
    stomp_tick = attempt.ticks_elapsed
    assert attempt.events[events_before:] == [
        GameEvent(stomp_tick, GameEventKind.DEFEATED_ENEMY, DefeatMethod.STOMP),
        GameEvent(stomp_tick, GameEventKind.SCORED_POINTS, FIRST_STOMP_POINTS)]
    stopped = the_koopa(attempt)
    for _ in range(4):
        attempt.step(HOLD_JUMP)
        assert the_koopa(attempt) == stopped


def test_a_still_shell_nobody_touches_wakes_into_a_walking_koopa_after_the_originals_delay():
    attempt = koopa_attempt()
    stomp_then_land_left_of_the_shell(attempt)
    stomp_tick = attempt.events[0].tick
    shell = the_koopa(attempt)
    while attempt.ticks_elapsed < stomp_tick + SHELL_WAKE_TICKS - 1:
        attempt.step(HOLD_NOTHING)
        assert the_koopa(attempt) == shell
    attempt.step(HOLD_NOTHING)
    woken = the_koopa(attempt)
    assert not woken.is_shell and not woken.is_defeated
    assert woken.x_pixels == shell.x_pixels
    for _ in range(20):
        attempt.step(HOLD_NOTHING)
    assert the_koopa(attempt).x_pixels == shell.x_pixels + 10 * KOOPA_WALK_PIXELS_PER_TWO_TICKS
    assert not attempt.is_over


def test_kicking_a_shell_about_to_wake_scores_by_its_time_left():
    attempt = koopa_attempt()
    stomp_then_land_left_of_the_shell(attempt)
    stomp_tick = attempt.events[0].tick
    step_until(attempt, HOLD_NOTHING, lambda: attempt.mario.whole_speed_x == 0)
    step_until(attempt, HOLD_RIGHT, lambda: gap_to_the_koopa(attempt)
               <= COAST_TO_THE_SHELL_GAP_PIXELS)
    while attempt.ticks_elapsed < stomp_tick + SHELL_WAKE_TICKS - NEARLY_AWAKE_TICKS_LEFT:
        attempt.step(HOLD_NOTHING)
    assert not kicked_shell_events(attempt)
    step_until(attempt, HOLD_RIGHT, lambda: kicked_shell_events(attempt))
    kick_tick = attempt.ticks_elapsed
    assert kick_tick < stomp_tick + SHELL_WAKE_TICKS - NEARLY_AWAKE_TICKS_LEFT // 2
    assert attempt.events[-1] == GameEvent(kick_tick, GameEventKind.SCORED_POINTS, NEARLY_AWAKE_KICK_POINTS)


def bump_the_koopa_walking_over_marios_block() -> Attempt:
    attempt = Attempt(build_level(blocks=BRICK_PLATFORM,
                                  enemy_spawns=(koopa_spawn(KOOPA_ON_PLATFORM_X, LOW_BLOCK_ROW - 1),)))
    jump_at_x = (MARIO_SPAWN_COLUMN + 1) * TILE_PIXELS + KOOPA_LEAD_PIXELS
    attempt.step(HOLD_NOTHING)
    step_until(attempt, HOLD_NOTHING, lambda: the_koopa(attempt).x_pixels + KOOPA_SIZE_PIXELS // 2 <= jump_at_x)
    attempt.step(HOLD_JUMP)
    step_until(attempt, HOLD_JUMP, lambda: attempt.mario.velocity_y >= 0)
    step_until(attempt, HOLD_NOTHING, lambda: attempt.events or attempt.ticks_elapsed > TICK_LIMIT)
    return attempt


def test_a_koopa_on_a_bumped_block_is_flipped_into_its_shell_and_hops_away_from_mario():
    """Only stunned, not defeated (HandleEToBGCollision, SetStun): it lands as a still shell."""
    attempt = bump_the_koopa_walking_over_marios_block()
    tick = attempt.events[0].tick
    assert attempt.events == [GameEvent(tick, GameEventKind.SCORED_POINTS, BUMPED_ENEMY_POINTS)]
    bumped = the_koopa(attempt)
    assert bumped.is_shell and not bumped.is_defeated
    attempt.step(HOLD_NOTHING)
    assert the_koopa(attempt).x_pixels > bumped.x_pixels and the_koopa(attempt).y_pixels < bumped.y_pixels
    platform_top_y = LOW_BLOCK_ROW * TILE_PIXELS
    step_until(attempt, HOLD_NOTHING, lambda: the_koopa(attempt).y_pixels + KOOPA_SIZE_PIXELS == platform_top_y)
    landed = the_koopa(attempt)
    for _ in range(30):
        attempt.step(HOLD_NOTHING)
    assert the_koopa(attempt) == landed


def test_a_fireball_defeats_a_koopa_for_200_points():
    attempt = fire_mario_attempt(build_level(enemy_spawns=(koopa_spawn(KOOPA_START_X),)))
    step_until(attempt, HOLD_NOTHING, lambda: enemies_in(attempt) and the_koopa(attempt).x_pixels <= SHOOTING_RANGE_X)
    attempt.step(HOLD_RUN)
    step_until(attempt, HOLD_NOTHING,
               lambda: any(event.kind is GameEventKind.DEFEATED_ENEMY for event in attempt.events))
    tick = attempt.ticks_elapsed
    assert attempt.events[-2:] == [GameEvent(tick, GameEventKind.DEFEATED_ENEMY, DefeatMethod.FIREBALL),
                                   GameEvent(tick, GameEventKind.SCORED_POINTS, KOOPA_FIREBALL_POINTS)]
    assert the_koopa(attempt).is_defeated and the_koopa(attempt).is_shell    # drawn flipped in its shell
    step_until(attempt, HOLD_NOTHING, lambda: not enemies_in(attempt))
    assert not attempt.is_over


def test_a_moving_shell_that_hits_big_mario_makes_him_small():
    attempt = big_mario_attempt(build_level(blocks=PIPE, enemy_spawns=(koopa_spawn(KOOPA_START_X),)))
    kick_the_shell_right(attempt)
    events_before = len(attempt.events)
    step_until(attempt, HOLD_NOTHING, lambda: len(attempt.events) > events_before)
    assert attempt.events[events_before:] == [GameEvent(attempt.ticks_elapsed, GameEventKind.TOOK_DAMAGE)]
    assert not attempt.is_over


def test_a_moving_shell_in_the_air_slides_at_half_its_speed():
    attempt = koopa_attempt(pit_columns=FAR_PIT_COLUMNS)
    kick_the_shell_right(attempt)
    standing_y = GROUND_TOP_Y - KOOPA_SIZE_PIXELS
    step_until(attempt, HOLD_NOTHING, lambda: the_koopa(attempt).y_pixels > standing_y + FALLEN_PIXELS)
    falling = the_koopa(attempt)
    for _ in range(10):
        attempt.step(HOLD_NOTHING)
    assert the_koopa(attempt).x_pixels - falling.x_pixels == 5 * AIRBORNE_SHELL_PIXELS_PER_TWO_TICKS


def test_a_shell_shows_as_an_enemy_in_the_observation():
    level = build_level(enemy_spawns=(koopa_spawn(KOOPA_START_X),))
    attempt = Attempt(level)
    stomp_then_land_left_of_the_shell(attempt)
    builder = ObservationBuilder(level)
    observation, window_first_column = builder.build_with_first_column(attempt)
    shell = the_koopa(attempt)
    shell_centre_row = (shell.y_pixels + shell.height_pixels // 2) // TILE_PIXELS
    shell_centre_column = (shell.x_pixels + shell.width_pixels // 2) // TILE_PIXELS
    grid = builder.grid_of(observation)
    assert grid[shell_centre_row - OBSERVATION_TOP_ROW][shell_centre_column - window_first_column] == ENEMY_CELL


def kick_points_touching(koopa: Koopa, mario: Mario) -> tuple[int | None, ...]:
    """What Mario's touch scores, the Koopa moved onto him, at one enemy check."""
    koopa.x, koopa.y = mario.x, mario.y
    return EnemyCollisionCheck().step(ENEMY_CHECK_TICK, mario, [koopa]).points_per_kick


def test_kicking_a_never_stomped_koopa_flipped_by_a_bumped_block_while_it_hops_scores_8000():
    """Its EnemyIntervalTimer was never set (InitNormalEnemy; EraseEnemyObject
    clears it) and SetStun leaves it be, so HandlePECollisions reads 0."""
    mario = Mario()
    koopa = Koopa(koopa_spawn(KOOPA_START_X))
    koopa.bump_from_below(mario.x)
    assert koopa.can_be_kicked
    assert kick_points_touching(koopa, mario) == (TIMER_RUN_OUT_KICK_POINTS,)
    assert koopa.is_moving_shell


def test_a_shells_revival_timer_runs_down_while_it_slides_so_a_later_bump_and_kick_score_by_it():
    """DecTimers runs every EnemyIntervalTimer down, whatever the enemy is doing."""
    tiles = AttemptTiles(build_level())
    mario = Mario()
    koopa = Koopa(koopa_spawn(KOOPA_START_X))
    koopa.stomp()
    koopa.kick(mario.x)
    for tick in range(SHELL_REVIVAL_TICKS - NEARLY_AWAKE_TICKS_LEFT):
        koopa.step(tiles, tick)
    koopa.bump_from_below(mario.x)
    assert kick_points_touching(koopa, mario) == (NEARLY_AWAKE_KICK_POINTS,)
