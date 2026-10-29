"""The Starman (#21, spec sections 1, 4 and 5): the Starman brick releases one,
which bounces along; collecting it makes Mario invincible for a while, and
every enemy he touches then is defeated."""

from mario.level.static_level import EnemyKind, EnemySpawn, StaticLevel
from mario.simulation.attempt import Attempt
from mario.simulation.attempt_result import DefeatMethod, EndReason, GameEvent, GameEventKind
from mario.simulation.item_kind import ItemKind
from mario.snapshots.world_snapshot import EnemySnapshot, ItemSnapshot, PowerState, WorldSnapshot
from tests.game.helpers import (
    GROUND_TOP_ROW,
    HOLD_JUMP,
    HOLD_LEFT,
    HOLD_NOTHING,
    HOLD_RIGHT,
    build_level,
    goomba_spawn,
)

STARMAN_BRICK = "S"
# Small Mario spawns with his centre in column 3; a block at row 9 is in reach of a standing jump.
MARIO_SPAWN_COLUMN = 3
LOW_BLOCK_ROW = 9
TILE_PIXELS = 16
BLOCK_X = MARIO_SPAWN_COLUMN * TILE_PIXELS
BLOCK_Y = LOW_BLOCK_ROW * TILE_PIXELS
GROUND_Y = GROUND_TOP_ROW * TILE_PIXELS


def starman_brick_level(**level_options):
    blocks = {(MARIO_SPAWN_COLUMN, LOW_BLOCK_ROW): STARMAN_BRICK, **level_options.pop("blocks", {})}
    return build_level(blocks=blocks, **level_options)


def jump_until_the_head_hits(attempt: Attempt) -> None:
    attempt.step(HOLD_JUMP)
    while attempt.mario.velocity_y < 0:
        attempt.step(HOLD_JUMP)


def items_in(attempt: Attempt) -> tuple[ItemSnapshot, ...]:
    return WorldSnapshot.of(attempt).items


def test_hitting_the_starman_brick_releases_a_starman_inside_it():
    attempt = Attempt(starman_brick_level())
    jump_until_the_head_hits(attempt)
    assert [(item.kind, item.x_pixels, item.y_pixels) for item in items_in(attempt)] == [
        (ItemKind.STARMAN, BLOCK_X, BLOCK_Y)]


# It rises out of its block as every item does (1 px every 4 ticks, 16 px), then
# sets off right at 1 px/f (GrowThePowerUp: X speed $10).
TICKS_BEFORE_IT_MOVES = 17 * 4
STARMAN_PIXELS_PER_TICK = 1
STARMAN_SIZE_PIXELS = 16
# Landing, it jumps again at -3 px/f, then falls with gravity $1C/256 px/f^2
# (MoveJ_EnemyVertically, EnemyJump). Worked by hand: k ticks after the bounce
# its speed is -768 + 28k (in 1/256 px/f), negative for k = 0..27, so it rises
# (768 * 28 - 28 * 27 * 28 / 2) / 256 = 42.66 px, which its sub-pixel position
# floors to 42 or 43 whole pixels; it is back on the ground once
# -768 n + 14 n (n - 1) >= 0, on the 56th tick.
BOUNCE_SPEED_PIXELS_PER_TICK = -3
BOUNCE_RISE_PIXELS = (42, 43)
BOUNCE_TICKS = 56
# Its fall speed is capped at 3 px/f (SetHiMax), with ImposeGravity's quirk: the
# cap applies only once the speed's fraction reaches $80, so from 3 px/f it climbs
# 28/256 a tick to 3.44 px/f and is cut back on the 5th: 16.09 px every 5 ticks,
# so a fall at the cap drops 3 or 4 px a tick, 48 (48.28, floored by its sub-pixel
# position) or 49 px in 15 ticks.
FALL_PIXELS_PER_TICK_AT_THE_CAP = {3, 4}
TICKS_AT_THE_CAP = 15
FALL_PIXELS_IN_TICKS_AT_THE_CAP = (48, 49)
TICK_LIMIT = 1000


def release_the_starman(attempt: Attempt) -> None:
    """Bump the brick over Mario and wait until the Starman has risen out of it."""
    jump_until_the_head_hits(attempt)
    while items_in(attempt)[0].is_emerging:
        attempt.step(HOLD_NOTHING)


def starman_boxes(attempt: Attempt, ticks: int) -> list[tuple[int, int]]:
    """The Starman's box's top-left corner on each of the next ticks, Mario standing still."""
    boxes = []
    for _ in range(ticks):
        attempt.step(HOLD_NOTHING)
        (starman,) = items_in(attempt)
        boxes.append((starman.x_pixels, starman.y_pixels))
    return boxes


def test_out_of_its_block_the_starman_moves_right_at_one_pixel_per_tick():
    attempt = Attempt(starman_brick_level())
    release_the_starman(attempt)
    assert attempt.ticks_elapsed < TICKS_BEFORE_IT_MOVES + 10
    (starman,) = items_in(attempt)
    assert (starman.x_pixels, starman.y_pixels + STARMAN_SIZE_PIXELS) == (BLOCK_X, BLOCK_Y)
    xs = [x for x, _ in starman_boxes(attempt, 100)]
    assert xs == [BLOCK_X + STARMAN_PIXELS_PER_TICK * tick for tick in range(1, 101)]


def landing_ticks(bottoms: list[int]) -> list[int]:
    return [tick for tick, bottom in enumerate(bottoms) if bottom == GROUND_Y]


def test_the_starman_bounces_along_the_ground_at_3_pixels_per_tick():
    attempt = Attempt(starman_brick_level())
    release_the_starman(attempt)
    bottoms = [y + STARMAN_SIZE_PIXELS for _, y in starman_boxes(attempt, 270)]
    landings = landing_ticks(bottoms)
    assert len(landings) >= 4
    assert [later - earlier for earlier, later in zip(landings, landings[1:])] == [BOUNCE_TICKS] * (len(landings) - 1)
    for landing in landings[:-1]:
        assert bottoms[landing + 1] - bottoms[landing] == BOUNCE_SPEED_PIXELS_PER_TICK
        assert GROUND_Y - min(bottoms[landing:landing + BOUNCE_TICKS]) in BOUNCE_RISE_PIXELS


def test_the_starman_falls_at_most_at_its_3_pixels_per_tick_cap():
    """Off the brick and over a pit, it falls out of the level."""
    attempt = Attempt(starman_brick_level(pit_columns=range(MARIO_SPAWN_COLUMN + 1, MARIO_SPAWN_COLUMN + 20)))
    release_the_starman(attempt)
    ys = [items_in(attempt)[0].y_pixels]
    while items_in(attempt) and attempt.ticks_elapsed < TICK_LIMIT:
        ys.append(items_in(attempt)[0].y_pixels)
        attempt.step(HOLD_NOTHING)
    drops = [later - earlier for earlier, later in zip(ys, ys[1:])]
    assert ys[-1] > GROUND_Y
    assert set(drops[-TICKS_AT_THE_CAP:]) == FALL_PIXELS_PER_TICK_AT_THE_CAP
    assert sum(drops[-TICKS_AT_THE_CAP:]) in FALL_PIXELS_IN_TICKS_AT_THE_CAP


def test_the_starman_turns_around_at_a_wall():
    wall_column = MARIO_SPAWN_COLUMN + 8
    wall = frozenset((wall_column, row) for row in range(GROUND_TOP_ROW))
    attempt = Attempt(starman_brick_level(hard_blocks=wall))
    release_the_starman(attempt)
    xs = [x for x, _ in starman_boxes(attempt, 200)]
    turn = xs.index(max(xs))
    assert max(xs) == wall_column * TILE_PIXELS - STARMAN_SIZE_PIXELS
    assert xs[turn + 1:turn + 11] == [max(xs) - STARMAN_PIXELS_PER_TICK * tick for tick in range(1, 11)]


def test_rising_the_starman_goes_up_into_a_block_over_it_it_has_no_head_probe():
    """A row of blocks with 3 tiles of air under it stops none of its bounces."""
    blocks_row = GROUND_TOP_ROW - 4
    ceiling = frozenset((column, blocks_row) for column in range(MARIO_SPAWN_COLUMN + 2, MARIO_SPAWN_COLUMN + 30))
    attempt = Attempt(starman_brick_level(hard_blocks=ceiling))
    release_the_starman(attempt)
    boxes = starman_boxes(attempt, 270)
    bottoms = [y + STARMAN_SIZE_PIXELS for _, y in boxes]
    landings = landing_ticks(bottoms)
    for landing in landings[:-1]:
        assert GROUND_Y - min(bottoms[landing:landing + BOUNCE_TICKS]) in BOUNCE_RISE_PIXELS
    assert min(y for _, y in boxes[landings[0]:]) < (blocks_row + 1) * TILE_PIXELS


# Collecting it scores 1000, as every item but the 1-UP does (HandlePowerUpCollision:
# floatey number $06).
STARMAN_POINTS = 1000


def collect_the_starman(attempt: Attempt) -> None:
    """Release the Starman, then walk right after it until Mario touches it."""
    release_the_starman(attempt)
    while GameEventKind.COLLECTED_STARMAN not in [event.kind for event in attempt.events]:
        assert attempt.ticks_elapsed < TICK_LIMIT and not attempt.is_over
        attempt.step(HOLD_RIGHT)


def test_collecting_the_starman_scores_1000_and_makes_small_mario_invincible():
    attempt = Attempt(starman_brick_level())
    assert not WorldSnapshot.of(attempt).mario.is_invincible
    collect_the_starman(attempt)
    tick = attempt.ticks_elapsed
    assert attempt.events[-2:] == [GameEvent(tick, GameEventKind.COLLECTED_STARMAN),
                                   GameEvent(tick, GameEventKind.SCORED_POINTS, STARMAN_POINTS)]
    assert items_in(attempt) == ()
    mario = WorldSnapshot.of(attempt).mario
    assert mario.is_invincible and mario.power_state is PowerState.SMALL
    assert not attempt.mario.is_changing_power_state


# A Goomba walking left from just off the screen; Mario has the Starman before they meet.
GOOMBA_START_X = 300
# An enemy an invincible Mario touches is defeated as if hit by a shell or a
# bumped block (EColl, ShellOrBlockDefeat): a Goomba scores 100.
GOOMBA_STARMAN_POINTS = 100


def enemies_in(attempt: Attempt) -> tuple[EnemySnapshot, ...]:
    return WorldSnapshot.of(attempt).enemies


def walk_right_until_an_enemy_is_defeated(attempt: Attempt) -> None:
    while not any(enemy.is_defeated for enemy in enemies_in(attempt)):
        assert attempt.ticks_elapsed < TICK_LIMIT and not attempt.is_over
        attempt.step(HOLD_RIGHT)


def test_while_invincible_walking_into_a_goomba_defeats_it_and_mario_takes_no_damage():
    attempt = Attempt(starman_brick_level(enemy_spawns=(goomba_spawn(GOOMBA_START_X),)))
    collect_the_starman(attempt)
    events_before = len(attempt.events)
    walk_right_until_an_enemy_is_defeated(attempt)
    tick = attempt.ticks_elapsed
    assert attempt.events[events_before:] == [
        GameEvent(tick, GameEventKind.DEFEATED_ENEMY, DefeatMethod.STARMAN),
        GameEvent(tick, GameEventKind.SCORED_POINTS, GOOMBA_STARMAN_POINTS)]
    (goomba,) = enemies_in(attempt)
    goomba_y = goomba.y_pixels
    attempt.step(HOLD_RIGHT)
    assert enemies_in(attempt)[0].y_pixels < goomba_y          # it jumps away, out of the level
    for _ in range(60):
        attempt.step(HOLD_RIGHT)
    assert not attempt.is_over
    assert WorldSnapshot.of(attempt).mario.power_state is PowerState.SMALL


# The invincibility lasts $23 interval ticks of 21 ticks (StarInvincibleTimer),
# the longest the interval clock allows: 735 ticks from the tick he collects it.
INVINCIBLE_TICKS = 0x23 * 21
# A Goomba far right, which only appears once Mario has walked a long way.
FAR_GOOMBA_X = 1200
LONG_TICK_LIMIT = 3000


def is_invincible(attempt: Attempt) -> bool:
    return WorldSnapshot.of(attempt).mario.is_invincible


def test_the_invincibility_runs_out_after_735_ticks_and_then_a_goomba_kills_small_mario_again():
    attempt = Attempt(starman_brick_level(enemy_spawns=(goomba_spawn(FAR_GOOMBA_X),)))
    collect_the_starman(attempt)
    for _ in range(INVINCIBLE_TICKS - 1):
        attempt.step(HOLD_NOTHING)
    assert is_invincible(attempt)
    attempt.step(HOLD_NOTHING)
    assert not is_invincible(attempt)
    while not attempt.is_over and attempt.ticks_elapsed < LONG_TICK_LIMIT:
        attempt.step(HOLD_RIGHT)
    assert attempt.result().end_reason is EndReason.DIED_TO_ENEMY
    assert not any(event.detail is DefeatMethod.STARMAN for event in attempt.events)



# --- Invincible Mario and the other enemies, and pits ---------------------------------------

# A Koopa, walking or in its shell, scores 200 (ShellOrBlockDefeat: floatey number $02).
KOOPA_STARMAN_POINTS = 200
KOOPA_START_X = 288
# Jumping in place when an enemy walking at him is this close lands Mario on top of it.
STOMP_JUMP_DISTANCE_PIXELS = 16
# A 2-tile pipe right of the Koopa's start, which a kicked shell comes back from.
PIPE_COLUMN = 20
PIPE = {(PIPE_COLUMN, GROUND_TOP_ROW - 2): "{", (PIPE_COLUMN + 1, GROUND_TOP_ROW - 2): "}",
        (PIPE_COLUMN, GROUND_TOP_ROW - 1): "[", (PIPE_COLUMN + 1, GROUND_TOP_ROW - 1): "]"}
PIT_COLUMNS = range(8, 12)


def koopa_spawn(x_pixels: int) -> EnemySpawn:
    return EnemySpawn(EnemyKind.KOOPA, x_pixels, GROUND_TOP_ROW - 1, x_pixels)


def invincible_mario_attempt(level: StaticLevel) -> Attempt:
    """An Attempt whose Mario is invincible from the start, as a Starman makes him
    (the tests above collect a real one), stepped once for its enemies to appear."""
    attempt = Attempt(level)
    attempt.mario.become_invincible()
    attempt.step(HOLD_NOTHING)
    return attempt


def step_until(attempt: Attempt, buttons: int, condition) -> None:
    while not condition():
        assert attempt.ticks_elapsed < TICK_LIMIT and not attempt.is_over
        attempt.step(buttons)


def gap_to_the_enemy(attempt: Attempt) -> int:
    """From Mario's right edge to the enemy's left edge."""
    return enemies_in(attempt)[0].x_pixels - attempt.mario.hitbox().right_x_pixels


def events_since(attempt: Attempt, events_before: int) -> list[GameEvent]:
    return attempt.events[events_before:]


def starman_defeat_events(tick: int, points: int) -> list[GameEvent]:
    return [GameEvent(tick, GameEventKind.DEFEATED_ENEMY, DefeatMethod.STARMAN),
            GameEvent(tick, GameEventKind.SCORED_POINTS, points)]


def test_while_invincible_landing_on_a_goomba_defeats_it_rather_than_stomping_it():
    attempt = invincible_mario_attempt(build_level(enemy_spawns=(goomba_spawn(GOOMBA_START_X),)))
    step_until(attempt, HOLD_NOTHING, lambda: gap_to_the_enemy(attempt) <= STOMP_JUMP_DISTANCE_PIXELS)
    step_until(attempt, HOLD_JUMP, lambda: enemies_in(attempt)[0].is_defeated)
    assert attempt.mario.velocity_y > 0                        # no stomp bounce
    assert events_since(attempt, 0) == starman_defeat_events(attempt.ticks_elapsed, GOOMBA_STARMAN_POINTS)


def test_while_invincible_walking_into_a_koopa_defeats_it():
    attempt = invincible_mario_attempt(build_level(enemy_spawns=(koopa_spawn(KOOPA_START_X),)))
    step_until(attempt, HOLD_RIGHT, lambda: enemies_in(attempt)[0].is_defeated)
    assert events_since(attempt, 0) == starman_defeat_events(attempt.ticks_elapsed, KOOPA_STARMAN_POINTS)
    assert enemies_in(attempt)[0].is_shell                     # it falls out of the level flipped
    for _ in range(60):
        attempt.step(HOLD_RIGHT)
    assert not attempt.is_over


def stomp_the_koopa_and_land_left_of_its_shell(attempt: Attempt) -> None:
    attempt.step(HOLD_NOTHING)
    step_until(attempt, HOLD_NOTHING, lambda: gap_to_the_enemy(attempt) <= STOMP_JUMP_DISTANCE_PIXELS)
    step_until(attempt, HOLD_JUMP, lambda: enemies_in(attempt)[0].is_shell)
    attempt.step(HOLD_LEFT)
    step_until(attempt, HOLD_LEFT, lambda: attempt.mario.is_on_ground)


def test_while_invincible_touching_a_still_shell_defeats_it_rather_than_kicking_it():
    attempt = Attempt(build_level(enemy_spawns=(koopa_spawn(KOOPA_START_X),)))
    stomp_the_koopa_and_land_left_of_its_shell(attempt)
    attempt.mario.become_invincible()
    events_before = len(attempt.events)
    step_until(attempt, HOLD_RIGHT, lambda: enemies_in(attempt)[0].is_defeated)
    assert events_since(attempt, events_before) == starman_defeat_events(attempt.ticks_elapsed,
                                                                         KOOPA_STARMAN_POINTS)


def test_while_invincible_a_moving_shell_that_hits_mario_is_defeated():
    attempt = Attempt(build_level(enemy_spawns=(koopa_spawn(KOOPA_START_X),), blocks=PIPE))
    stomp_the_koopa_and_land_left_of_its_shell(attempt)
    step_until(attempt, HOLD_RIGHT, lambda: GameEventKind.KICKED_SHELL in [event.kind for event in attempt.events])
    shell_xs = [enemies_in(attempt)[0].x_pixels]
    while len(shell_xs) < 2 or shell_xs[-1] >= shell_xs[-2]:  # until it comes back from the pipe
        attempt.step(HOLD_NOTHING)
        shell_xs.append(enemies_in(attempt)[0].x_pixels)
    attempt.mario.become_invincible()
    events_before = len(attempt.events)
    step_until(attempt, HOLD_NOTHING, lambda: enemies_in(attempt)[0].is_defeated)
    assert events_since(attempt, events_before) == starman_defeat_events(attempt.ticks_elapsed,
                                                                         KOOPA_STARMAN_POINTS)
    for _ in range(60):
        attempt.step(HOLD_NOTHING)
    assert not attempt.is_over


def test_a_pit_still_kills_an_invincible_mario():
    attempt = invincible_mario_attempt(build_level(pit_columns=PIT_COLUMNS))
    while not attempt.is_over and attempt.ticks_elapsed < TICK_LIMIT:
        attempt.step(HOLD_RIGHT)
    assert is_invincible(attempt)
    assert attempt.result().end_reason is EndReason.FELL_IN_PIT
