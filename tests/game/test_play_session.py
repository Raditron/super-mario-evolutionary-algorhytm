"""PlaySession: lives, the score and coins carried across them, and the checkpoint (#16)."""

from mario.constants.level import (
    CHECKPOINT_LEFT_X_PIXELS,
    LEVEL_TIMER_START_UNITS,
    MARIO_START_SPRITE_X_PIXELS,
    SMALL_MARIO_HITBOX_OFFSET_X_PIXELS,
)
from mario.constants.scoring import COIN_POINTS, COINS_PER_EXTRA_LIFE, STARTING_LIVES
from mario.constants.training import STALL_LIMIT_TICKS
from mario.constants.view import DEBUG_RECENT_GAME_EVENT_TICKS
from mario.modes.play_session import PlaySession
from mario.simulation.attempt_result import EndReason, GameEvent, GameEventKind
from tests.game.helpers import HOLD_NOTHING, HOLD_RIGHT_RUN, build_level, goomba_spawn

PIT_BEFORE_THE_CHECKPOINT = range(10, 14)
PIT_PAST_THE_CHECKPOINT = range(100, 104)
STOMP_POINTS = 100


def lose_a_life(session: PlaySession) -> EndReason:
    """Run right until the current life ends; return how it ended."""
    attempt = session.attempt
    while session.attempt is attempt:
        session.step(HOLD_RIGHT_RUN)
    return attempt.end_reason


def starts_at_the_beginning(session: PlaySession) -> bool:
    return session.attempt.scroll.left_x_pixels == 0


def starts_at_the_checkpoint(session: PlaySession) -> bool:
    start_x = CHECKPOINT_LEFT_X_PIXELS + MARIO_START_SPRITE_X_PIXELS + SMALL_MARIO_HITBOX_OFFSET_X_PIXELS
    return (session.attempt.scroll.left_x_pixels, session.attempt.mario.pixel_x) == (
        CHECKPOINT_LEFT_X_PIXELS, start_x)


def test_a_game_starts_with_three_lives_at_the_beginning():
    session = PlaySession(build_level())
    assert (session.lives, session.score, session.coins) == (STARTING_LIVES, 0, 0)
    assert starts_at_the_beginning(session)


def test_each_death_costs_a_life_and_starts_a_fresh_attempt():
    session = PlaySession(build_level(pit_columns=PIT_BEFORE_THE_CHECKPOINT))
    assert lose_a_life(session) is EndReason.FELL_IN_PIT
    assert session.lives == STARTING_LIVES - 1
    assert session.attempt.ticks_elapsed == 0
    assert session.attempt.level_timer.time_left == LEVEL_TIMER_START_UNITS


def test_dying_to_a_goomba_costs_a_life_and_the_next_life_has_its_goombas_back():
    session = PlaySession(build_level(enemy_spawns=(goomba_spawn(400),)))
    assert lose_a_life(session) is EndReason.DIED_TO_ENEMY
    assert session.lives == STARTING_LIVES - 1
    assert session.attempt.enemies.active == []
    assert lose_a_life(session) is EndReason.DIED_TO_ENEMY


def test_a_death_before_the_checkpoint_restarts_at_the_beginning():
    session = PlaySession(build_level(pit_columns=PIT_BEFORE_THE_CHECKPOINT))
    lose_a_life(session)
    assert starts_at_the_beginning(session)


def test_a_death_once_the_screen_has_reached_the_checkpoint_restarts_there():
    session = PlaySession(build_level(pit_columns=PIT_PAST_THE_CHECKPOINT))
    lose_a_life(session)
    assert starts_at_the_checkpoint(session)
    lose_a_life(session)
    assert starts_at_the_checkpoint(session)


def test_losing_the_last_life_starts_a_new_game():
    session = PlaySession(build_level(pit_columns=PIT_PAST_THE_CHECKPOINT))
    for _ in range(STARTING_LIVES - 1):
        session.attempt.scoreboard.collect_coin(session.attempt.ticks_elapsed)
        lose_a_life(session)
    assert session.lives == 1
    lose_a_life(session)
    assert (session.lives, session.score, session.coins) == (STARTING_LIVES, 0, 0)
    assert starts_at_the_beginning(session)


def test_score_and_coins_carry_across_lives():
    session = PlaySession(build_level(pit_columns=PIT_BEFORE_THE_CHECKPOINT))
    session.attempt.scoreboard.score_points(STOMP_POINTS, session.attempt.ticks_elapsed)
    lose_a_life(session)
    session.attempt.scoreboard.collect_coin(session.attempt.ticks_elapsed)
    assert (session.score, session.coins) == (STOMP_POINTS + COIN_POINTS, 1)
    hud = session.snapshot().hud
    assert (hud.score, hud.coins, hud.time_left) == (STOMP_POINTS + COIN_POINTS, 1, LEVEL_TIMER_START_UNITS)


def test_every_100_coins_give_a_life_and_the_coin_count_restarts():
    session = PlaySession(build_level(pit_columns=PIT_BEFORE_THE_CHECKPOINT))
    coins_in_first_life = COINS_PER_EXTRA_LIFE - 1
    for _ in range(coins_in_first_life):
        session.attempt.scoreboard.collect_coin(session.attempt.ticks_elapsed)
    assert session.lives == STARTING_LIVES
    lose_a_life(session)
    session.attempt.scoreboard.collect_coin(session.attempt.ticks_elapsed)
    assert (session.lives, session.coins) == (STARTING_LIVES, 0)


def test_play_has_no_stall_rule():
    session = PlaySession(build_level())
    for _ in range(10 * STALL_LIMIT_TICKS):
        session.step(HOLD_NOTHING)
    assert (session.lives, session.attempt.ticks_elapsed) == (STARTING_LIVES, 10 * STALL_LIMIT_TICKS)


def test_the_play_snapshot_carries_the_observation_for_the_debug_view():
    session = PlaySession(build_level())
    observation = session.snapshot().observation
    assert observation.first_column == 0      # Mario's centre is in column 3, 3 columns behind
    assert observation.cells[-1] == (1,) * 13  # the ground row
    assert observation.cells[:-1] == ((0,) * 13,) * 11
    assert observation.state_numbers == (0, 0, 1, 1)


def test_the_play_snapshot_carries_the_recent_game_events():
    session = PlaySession(build_level())
    session.attempt.scoreboard.score_points(STOMP_POINTS, session.attempt.ticks_elapsed)
    for _ in range(DEBUG_RECENT_GAME_EVENT_TICKS - 1):
        session.step(HOLD_NOTHING)
    assert session.snapshot().recent_events == (GameEvent(0, GameEventKind.SCORED_POINTS, STOMP_POINTS),)
    session.step(HOLD_NOTHING)
    assert session.snapshot().recent_events == ()
