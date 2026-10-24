"""Each Attempt owns its Goombas: they appear as the screen scrolls, and Mario
stomps them or dies to them (#17, spec sections 4 and 5)."""

from mario.constants.level import SCREEN_WIDTH_PIXELS
from mario.constants.physics import STOMP_MIN_FALL_SPEED, STOMPED_GOOMBA_TICKS, SUBPIXEL_BITS
from mario.controller.controller_state import ControllerState
from mario.level.static_level import EnemyKind, EnemySpawn
from mario.simulation.attempt import Attempt
from mario.simulation.attempt_result import DefeatMethod, EndReason, GameEvent, GameEventKind
from mario.snapshots.world_snapshot import EnemySnapshot, WorldSnapshot
from tests.game.helpers import (
    GROUND_TOP_ROW,
    HOLD_JUMP,
    HOLD_NOTHING,
    HOLD_RIGHT,
    HOLD_RIGHT_RUN,
    build_level,
    goomba_spawn,
)

HOLD_RIGHT_JUMP = ControllerState.bitmask(right=True, jump=True)
HOLD_RIGHT_RUN_JUMP = ControllerState.bitmask(right=True, run=True, jump=True)

ACTIVATION_RANGE_PIXELS = 48
REMOVAL_RANGE_PIXELS = 72
FELL_OUT_HITBOX_Y = 256 + 8                  # the sprite's top at y = 256; the hitbox starts 8 px lower
# A long platform of hard blocks at row 9 that Mario runs under while a Goomba walks on top.
PLATFORM = frozenset((column, 9) for column in range(5, 60))
# Jumping in place when a walking Goomba is this close lands Mario on top of it.
STOMP_JUMP_DISTANCE_PIXELS = 16
FIRST_STOMP_POINTS = 100
# From these distances, the bounce off one Goomba carries Mario onto the next.
CHAIN_JUMP_DISTANCE_PIXELS = 8
SAME_TICK_JUMP_DISTANCE_PIXELS = 2
GOOMBA_TO_JUMP_AT_X = 600
JUMP_TEST_TICK_LIMIT = 600
STOMP_BOUNCE_PIXELS_PER_TICK = -4


def enemies_in(attempt: Attempt) -> tuple[EnemySnapshot, ...]:
    return WorldSnapshot.of(attempt).enemies


def touching(snapshot: WorldSnapshot) -> bool:
    mario = snapshot.mario
    return any(mario.x_pixels < goomba.x_pixels + goomba.width_pixels
               and goomba.x_pixels < mario.x_pixels + mario.width_pixels
               and mario.y_pixels < goomba.y_pixels + goomba.height_pixels
               and goomba.y_pixels < mario.y_pixels + mario.height_pixels
               for goomba in snapshot.enemies)


def jump_onto_approaching_goomba(attempt: Attempt, jump_distance_pixels: int) -> None:
    """Stand still until the first Goomba walks within the distance of Mario, then jump, holding jump."""
    def goomba_distance() -> int:
        return enemies_in(attempt)[0].x_pixels - attempt.mario.hitbox().right_x_pixels

    while not enemies_in(attempt) or goomba_distance() > jump_distance_pixels:
        attempt.step(HOLD_NOTHING)
    attempt.step(HOLD_JUMP)


def step_until_an_event(attempt: Attempt, buttons: int) -> None:
    while not attempt.events and not attempt.is_over:
        attempt.step(buttons)


def jump_at_goomba(move: int, move_and_jump: int, jump_distance_pixels: int) -> Attempt:
    """Move right; jump once the Goomba is within the distance, holding jump in the air,
    until the first game event, the end, or Mario has passed the Goomba."""
    attempt = Attempt(build_level(enemy_spawns=(goomba_spawn(GOOMBA_TO_JUMP_AT_X),)))
    jumped = False
    while not attempt.events and not attempt.is_over and attempt.ticks_elapsed < JUMP_TEST_TICK_LIMIT:
        goombas = enemies_in(attempt)
        in_range = goombas and goombas[0].x_pixels - attempt.mario.hitbox().right_x_pixels <= jump_distance_pixels
        jumping = (in_range and not jumped) or (jumped and not attempt.mario.is_on_ground)
        jumped = jumped or jumping
        attempt.step(move_and_jump if jumping else move)
    return attempt


def goomba_row(first_x: int, spacing_pixels: int, count: int) -> tuple[EnemySpawn, ...]:
    """Goombas in a row, all activating when the first does."""
    return tuple(EnemySpawn(EnemyKind.GOOMBA, first_x + index * spacing_pixels, GROUND_TOP_ROW - 1, first_x)
                 for index in range(count))


def points_scored(attempt: Attempt) -> list[tuple[int, int]]:
    return [(event.tick, event.detail) for event in attempt.events if event.kind is GameEventKind.SCORED_POINTS]


def stomps(attempt: Attempt) -> int:
    return sum(event.kind is GameEventKind.DEFEATED_ENEMY and event.detail == DefeatMethod.STOMP
               for event in attempt.events)


def test_a_goomba_appears_at_its_spawn_x_once_the_screen_scrolls_it_into_range():
    attempt = Attempt(build_level(enemy_spawns=(goomba_spawn(400),)))
    while not enemies_in(attempt):
        screen_left_x_before = attempt.scroll.left_x_pixels
        attempt.step(HOLD_RIGHT_RUN)
    assert screen_left_x_before + SCREEN_WIDTH_PIXELS - 1 + ACTIVATION_RANGE_PIXELS < 400
    assert attempt.scroll.left_x_pixels + SCREEN_WIDTH_PIXELS - 1 + ACTIVATION_RANGE_PIXELS >= 400
    (goomba,) = enemies_in(attempt)
    assert (goomba.kind, goomba.x_pixels, goomba.width_pixels, goomba.height_pixels) == (
        EnemyKind.GOOMBA, 400, 16, 16)
    assert not goomba.is_defeated


def test_an_enemy_well_off_the_left_of_the_screen_is_removed():
    level = build_level(hard_blocks=PLATFORM, enemy_spawns=(goomba_spawn(640, resting_row=8),))
    attempt = Attempt(level)
    seen = []
    while not seen or enemies_in(attempt):
        if enemies_in(attempt):
            seen.append((enemies_in(attempt)[0].x_pixels, attempt.scroll.left_x_pixels))
        attempt.step(HOLD_RIGHT_RUN)
    last_x, screen_left_x_then = seen[-1]
    assert last_x >= screen_left_x_then - REMOVAL_RANGE_PIXELS
    assert last_x - 1 < attempt.scroll.left_x_pixels - REMOVAL_RANGE_PIXELS
    assert not attempt.is_over


def test_walking_into_a_goomba_ends_the_attempt_with_died_to_enemy():
    attempt = Attempt(build_level(enemy_spawns=(goomba_spawn(400),)))
    while not attempt.is_over:
        attempt.step(HOLD_RIGHT)
    result = attempt.result()
    assert result.end_reason is EndReason.DIED_TO_ENEMY
    mario = attempt.mario.hitbox()
    (goomba,) = enemies_in(attempt)
    assert mario.right_x_pixels > goomba.x_pixels and mario.bottom_y_pixels > goomba.y_pixels
    assert result.events == ()


def test_a_goomba_walking_into_mario_standing_still_kills_him():
    attempt = Attempt(build_level(enemy_spawns=(goomba_spawn(288),)))
    while not attempt.is_over:
        attempt.step(HOLD_NOTHING)
    assert attempt.result().end_reason is EndReason.DIED_TO_ENEMY


def test_the_mario_enemy_check_runs_only_on_every_other_tick():
    death_ticks = []
    deaths_a_tick_after_touching = 0
    for goomba_x in range(400, 416):
        attempt = Attempt(build_level(enemy_spawns=(goomba_spawn(goomba_x),)))
        touched_last_tick = False
        while not attempt.is_over:
            attempt.step(HOLD_RIGHT)
            if not attempt.is_over:
                touched_last_tick = touching(WorldSnapshot.of(attempt))
        death_ticks.append(attempt.ticks_elapsed)
        deaths_a_tick_after_touching += touched_last_tick
    assert all(tick % 2 == 0 for tick in death_ticks)
    # On some runs Mario and the Goomba already touched on the odd tick before, unchecked.
    assert 0 < deaths_a_tick_after_touching < len(death_ticks)


def test_stomping_a_goomba_defeats_it_and_bounces_mario_at_minus_4_px_per_tick():
    attempt = Attempt(build_level(enemy_spawns=(goomba_spawn(288),)))
    jump_onto_approaching_goomba(attempt, STOMP_JUMP_DISTANCE_PIXELS)
    step_until_an_event(attempt, HOLD_JUMP)
    assert not attempt.is_over
    stomp_tick = attempt.ticks_elapsed
    assert attempt.events == [GameEvent(stomp_tick, GameEventKind.DEFEATED_ENEMY, DefeatMethod.STOMP),
                              GameEvent(stomp_tick, GameEventKind.SCORED_POINTS, FIRST_STOMP_POINTS)]
    assert attempt.scoreboard.score == FIRST_STOMP_POINTS
    assert attempt.mario.velocity_y >> SUBPIXEL_BITS == STOMP_BOUNCE_PIXELS_PER_TICK
    (goomba,) = enemies_in(attempt)
    assert goomba.is_defeated


def test_a_stomped_goomba_lies_squashed_harmlessly_then_disappears():
    attempt = Attempt(build_level(enemy_spawns=(goomba_spawn(288),)))
    jump_onto_approaching_goomba(attempt, STOMP_JUMP_DISTANCE_PIXELS)
    step_until_an_event(attempt, HOLD_JUMP)
    stomp_tick = attempt.ticks_elapsed
    squashed = enemies_in(attempt)
    while attempt.ticks_elapsed < stomp_tick + STOMPED_GOOMBA_TICKS - 1:
        attempt.step(HOLD_NOTHING)              # Mario lands on and stands in the squashed Goomba
        assert enemies_in(attempt) == squashed
    assert touching(WorldSnapshot.of(attempt))
    attempt.step(HOLD_NOTHING)
    assert enemies_in(attempt) == ()
    assert not attempt.is_over


def test_coming_down_on_a_goomba_from_any_walking_or_running_jump_stomps_it():
    """Mario falls up to about 9 px between two checks, more than half a Goomba,
    so a stomp cannot depend on where his feet are when the check comes (EnemyStomped)."""
    stomped = 0
    for move, move_and_jump in ((HOLD_RIGHT, HOLD_RIGHT_JUMP), (HOLD_RIGHT_RUN, HOLD_RIGHT_RUN_JUMP)):
        for jump_distance in range(0, 140, 4):
            attempt = jump_at_goomba(move, move_and_jump, jump_distance)
            if attempt.is_over:
                assert attempt.mario.velocity_y < STOMP_MIN_FALL_SPEED, (move, jump_distance)
            stomped += stomps(attempt)
    assert stomped > 0


def test_touching_a_goomba_while_rising_kills_small_mario():
    attempt = Attempt(build_level(enemy_spawns=(goomba_spawn(288),)))
    jump_onto_approaching_goomba(attempt, jump_distance_pixels=0)
    step_until_an_event(attempt, HOLD_JUMP)
    assert attempt.result().end_reason is EndReason.DIED_TO_ENEMY
    assert attempt.mario.velocity_y < 0


def test_consecutive_stomps_without_landing_score_the_original_rising_chain():
    attempt = Attempt(build_level(enemy_spawns=goomba_row(270, 24, 3)))
    jump_onto_approaching_goomba(attempt, CHAIN_JUMP_DISTANCE_PIXELS)
    step_until_an_event(attempt, HOLD_JUMP)
    while stomps(attempt) < 3 and not attempt.is_over:
        attempt.step(HOLD_RIGHT)               # each bounce carries Mario onto the next Goomba
    assert [points for _, points in points_scored(attempt)] == [100, 200, 400]
    assert not attempt.is_over


def test_landing_restarts_the_stomp_chain():
    attempt = Attempt(build_level(enemy_spawns=goomba_row(270, 100, 2)))
    jump_onto_approaching_goomba(attempt, CHAIN_JUMP_DISTANCE_PIXELS)
    step_until_an_event(attempt, HOLD_JUMP)
    while not attempt.mario.is_on_ground:
        attempt.step(HOLD_NOTHING)
    while stomps(attempt) < 2 and not attempt.is_over:
        live_goombas = [goomba for goomba in enemies_in(attempt) if not goomba.is_defeated]
        close = live_goombas[0].x_pixels - attempt.mario.hitbox().right_x_pixels <= CHAIN_JUMP_DISTANCE_PIXELS
        attempt.step(HOLD_JUMP if close else HOLD_NOTHING)
    assert [points for _, points in points_scored(attempt)] == [100, 100]


def test_stomping_two_goombas_on_the_same_tick_scores_100_then_400():
    attempt = Attempt(build_level(enemy_spawns=goomba_row(270, 20, 2)))
    jump_onto_approaching_goomba(attempt, SAME_TICK_JUMP_DISTANCE_PIXELS)
    step_until_an_event(attempt, HOLD_JUMP)
    (first_tick, _), (second_tick, _) = scored = points_scored(attempt)
    assert first_tick == second_tick
    assert [points for _, points in scored] == [100, 400]
    assert not attempt.is_over


def test_a_goomba_that_falls_into_a_pit_is_removed_once_below_the_screen():
    attempt = Attempt(build_level(pit_columns=range(14, 16), enemy_spawns=(goomba_spawn(288),)))
    attempt.step(HOLD_NOTHING)
    lowest_y = 0
    while enemies_in(attempt):
        lowest_y = enemies_in(attempt)[0].y_pixels
        attempt.step(HOLD_NOTHING)
    assert FELL_OUT_HITBOX_Y - 4 <= lowest_y < FELL_OUT_HITBOX_Y
    assert not attempt.is_over
