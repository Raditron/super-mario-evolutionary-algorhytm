"""Blocks: Mario bumps them from below; ? blocks and the multi-coin brick give coins,
the hidden block appears, and an enemy on a bumped block is defeated (#18, spec sections 1 and 5)."""

import pytest

from mario.constants.physics import SUBPIXELS_PER_PIXEL
from mario.level.tile_kind import TileKind
from mario.simulation.attempt import Attempt
from mario.simulation.attempt_result import DefeatMethod, EndReason, GameEvent, GameEventKind
from mario.snapshots.world_snapshot import HudSnapshot, WorldSnapshot
from tests.game.helpers import GROUND_TOP_ROW, HOLD_JUMP, HOLD_NOTHING, HOLD_RIGHT, build_level, goomba_spawn

# The level data's characters (mario/level/world_1_1.toml).
COIN_QUESTION_BLOCK = "?"
BRICK = "B"
POWER_UP_QUESTION_BLOCK = "M"
STARMAN_BRICK = "S"
MULTI_COIN_BRICK = "C"
HIDDEN_ONE_UP_BLOCK = "U"

# Small Mario spawns with his centre in column 3. A block 4 tiles above the
# ground (row 9, as in 1-1's low row) is in reach of a standing jump.
MARIO_SPAWN_COLUMN = 3
LOW_BLOCK_ROW = 9
COIN_POINTS = 200
TILE_PIXELS = 16
# A block just above small Mario's head (his top is at y = 194, the row's bottom at 192),
# so he can hit it again and again quickly.
HEAD_HEIGHT_BLOCK_ROW = 11
# The multi-coin brick keeps giving coins for 11 interval ticks of 21 ticks after its
# first hit (BrickCoinTimer = $0B, docs/research/world-1-1-layout.md).
MULTI_COIN_TICKS = 11 * 21
TICK_LIMIT = 2000
# A brick platform over Mario's head with a Goomba walking left along it, from just
# past the screen's right edge, where it activates.
BRICK_PLATFORM = {(column, LOW_BLOCK_ROW): BRICK for column in range(20)}
GOOMBA_ON_PLATFORM_X = 17 * TILE_PIXELS
# Mario's head reaches the low row about 10 ticks into a jump, while the Goomba walks
# 5 px: jumping when its centre is this far right of his column puts it on his block.
GOOMBA_LEAD_PIXELS = 4
BUMPED_ENEMY_POINTS = 100                      # GiveOEPoints
# A bumped block starts up at 2 px/f and falls back under 0x50/256 px/f^2 of gravity
# (BumpBlock, ImposeGravityBlock), worked out by hand: its offset each tick from the
# bump on, in whole pixels (rounded down, as positions are), until it is back in place.
BOUNCE_OFFSETS_PIXELS = [-2, -4, -6, -7, -7, -8, -8, -8, -7, -6, -5, -4, -2]
# After a bump, no block can be bumped for 16 ticks (BlockBounceTimer = $10).
BOUNCE_LOCKOUT_TICKS = 16
PIT_RIGHT_OF_SPAWN = range(10, 14)


def jump_until_the_head_hits(attempt: Attempt) -> None:
    attempt.step(HOLD_JUMP)
    while attempt.mario.velocity_y < 0:
        attempt.step(HOLD_JUMP)


def whole_speed_y_pixels(attempt: Attempt) -> int:
    return attempt.mario.velocity_y // SUBPIXELS_PER_PIXEL


def jump_in_place(attempt: Attempt) -> None:
    """One standing jump with jump held, until Mario is back on the ground."""
    attempt.step(HOLD_JUMP)
    while not attempt.mario.is_on_ground:
        attempt.step(HOLD_JUMP)
    attempt.step(HOLD_NOTHING)


def walk_into_the_pit(attempt: Attempt) -> None:
    while not attempt.is_over:
        attempt.step(HOLD_RIGHT)


def tile_kind_in_snapshot(attempt: Attempt, column: int, row: int) -> TileKind:
    tiles = WorldSnapshot.of(attempt).tiles
    return tiles.rows[row][column - tiles.first_column]


def bounce_offset_in_snapshot(attempt: Attempt, column: int, row: int) -> int | None:
    """How far the block is raised, or None once it isn't bouncing."""
    offsets = {(block.column, block.row): block.offset_y_pixels
               for block in WorldSnapshot.of(attempt).bouncing_blocks}
    return offsets.get((column, row))


def event_kinds(attempt: Attempt) -> list[GameEventKind]:
    return [event.kind for event in attempt.events]


def test_a_coin_question_block_gives_exactly_one_coin_counted_in_the_hud_and_the_result():
    attempt = Attempt(build_level(pit_columns=PIT_RIGHT_OF_SPAWN,
                                  blocks={(MARIO_SPAWN_COLUMN, LOW_BLOCK_ROW): COIN_QUESTION_BLOCK}))
    jump_in_place(attempt)
    jump_in_place(attempt)
    assert event_kinds(attempt) == [GameEventKind.HIT_QUESTION_BLOCK, GameEventKind.COLLECTED_COIN,
                                    GameEventKind.SCORED_POINTS]
    assert HudSnapshot.of(attempt).coins == 1
    walk_into_the_pit(attempt)
    result = attempt.result()
    assert (result.coins_collected, result.final_score) == (1, COIN_POINTS)


def test_a_hit_coin_question_block_shows_as_used_in_the_snapshot():
    attempt = Attempt(build_level(blocks={(MARIO_SPAWN_COLUMN, LOW_BLOCK_ROW): COIN_QUESTION_BLOCK}))
    assert tile_kind_in_snapshot(attempt, MARIO_SPAWN_COLUMN, LOW_BLOCK_ROW) is TileKind.COIN_QUESTION_BLOCK
    jump_in_place(attempt)
    assert tile_kind_in_snapshot(attempt, MARIO_SPAWN_COLUMN, LOW_BLOCK_ROW) is TileKind.USED_BLOCK


def test_bumping_a_block_stops_marios_rise_dead_but_a_used_block_pushes_him_down():
    """BumpBlock sets his speed to 0; a used block, like a hard one, sets it to 1 px/f (NYSpd)."""
    attempt = Attempt(build_level(blocks={(MARIO_SPAWN_COLUMN, LOW_BLOCK_ROW): COIN_QUESTION_BLOCK}))
    jump_until_the_head_hits(attempt)
    assert whole_speed_y_pixels(attempt) == 0
    while not attempt.mario.is_on_ground:
        attempt.step(HOLD_NOTHING)
    jump_until_the_head_hits(attempt)
    assert whole_speed_y_pixels(attempt) == 1


def test_small_mario_only_bumps_a_plain_brick():
    attempt = Attempt(build_level(blocks={(MARIO_SPAWN_COLUMN, LOW_BLOCK_ROW): BRICK}))
    jump_until_the_head_hits(attempt)
    assert whole_speed_y_pixels(attempt) == 0
    jump_in_place(attempt)
    assert tile_kind_in_snapshot(attempt, MARIO_SPAWN_COLUMN, LOW_BLOCK_ROW) is TileKind.BRICK
    assert attempt.events == []


@pytest.mark.parametrize("block, events", [
    (POWER_UP_QUESTION_BLOCK, [GameEventKind.HIT_QUESTION_BLOCK]),
    (STARMAN_BRICK, []),
])
def test_a_power_up_question_block_and_the_starman_brick_turn_used_when_hit(block, events):
    """What their items do is tested with the items (test_power_ups.py, test_starman.py)."""
    attempt = Attempt(build_level(blocks={(MARIO_SPAWN_COLUMN, LOW_BLOCK_ROW): block}))
    jump_in_place(attempt)
    jump_in_place(attempt)
    assert tile_kind_in_snapshot(attempt, MARIO_SPAWN_COLUMN, LOW_BLOCK_ROW) is TileKind.USED_BLOCK
    assert event_kinds(attempt) == events


def coin_ticks(attempt: Attempt) -> list[int]:
    return [event.tick for event in attempt.events if event.kind is GameEventKind.COLLECTED_COIN]


def test_the_multi_coin_brick_gives_coins_until_its_timer_runs_out_then_one_more_and_is_used():
    attempt = Attempt(build_level(blocks={(MARIO_SPAWN_COLUMN, HEAD_HEIGHT_BLOCK_ROW): MULTI_COIN_BRICK}))
    while (tile_kind_in_snapshot(attempt, MARIO_SPAWN_COLUMN, HEAD_HEIGHT_BLOCK_ROW) is TileKind.MULTI_COIN_BRICK
           and attempt.ticks_elapsed < TICK_LIMIT):
        jump_in_place(attempt)
    ticks = coin_ticks(attempt)
    assert tile_kind_in_snapshot(attempt, MARIO_SPAWN_COLUMN, HEAD_HEIGHT_BLOCK_ROW) is TileKind.USED_BLOCK
    assert len(ticks) > 2
    assert ticks[-2] - ticks[0] < MULTI_COIN_TICKS <= ticks[-1] - ticks[0]
    jump_in_place(attempt)
    assert coin_ticks(attempt) == ticks
    assert GameEventKind.HIT_QUESTION_BLOCK not in event_kinds(attempt)


def test_no_block_can_be_bumped_until_the_last_bump_has_finished():
    """A head hit during the lockout stops Mario as a hard block would (NYSpd)."""
    attempt = Attempt(build_level(blocks={(MARIO_SPAWN_COLUMN, HEAD_HEIGHT_BLOCK_ROW): MULTI_COIN_BRICK}))
    jump_until_the_head_hits(attempt)
    first_bump_tick = attempt.ticks_elapsed
    while not attempt.mario.is_on_ground:
        attempt.step(HOLD_NOTHING)
    attempt.step(HOLD_NOTHING)
    jump_until_the_head_hits(attempt)
    assert attempt.ticks_elapsed - first_bump_tick < BOUNCE_LOCKOUT_TICKS
    assert (len(coin_ticks(attempt)), whole_speed_y_pixels(attempt)) == (1, 1)
    while attempt.ticks_elapsed - first_bump_tick < BOUNCE_LOCKOUT_TICKS or not attempt.mario.is_on_ground:
        attempt.step(HOLD_NOTHING)
    jump_until_the_head_hits(attempt)
    assert len(coin_ticks(attempt)) == 2


def test_an_unrevealed_hidden_block_cannot_be_stood_on():
    bridge_over_the_pit = {(column, GROUND_TOP_ROW): HIDDEN_ONE_UP_BLOCK for column in PIT_RIGHT_OF_SPAWN}
    attempt = Attempt(build_level(pit_columns=PIT_RIGHT_OF_SPAWN, blocks=bridge_over_the_pit))
    walk_into_the_pit(attempt)
    assert attempt.result().end_reason is EndReason.FELL_IN_PIT


def test_an_unrevealed_hidden_block_cannot_be_walked_into():
    block_column = MARIO_SPAWN_COLUMN + 3
    attempt = Attempt(build_level(blocks={(block_column, GROUND_TOP_ROW - 1): HIDDEN_ONE_UP_BLOCK}))
    while attempt.mario.hitbox().x_pixels <= (block_column + 1) * TILE_PIXELS and attempt.ticks_elapsed < TICK_LIMIT:
        attempt.step(HOLD_RIGHT)
    assert attempt.mario.hitbox().x_pixels > (block_column + 1) * TILE_PIXELS
    assert attempt.events == []


def test_hitting_the_hidden_block_from_below_reveals_it_and_makes_it_solid():
    attempt = Attempt(build_level(blocks={(MARIO_SPAWN_COLUMN, LOW_BLOCK_ROW): HIDDEN_ONE_UP_BLOCK}))
    jump_until_the_head_hits(attempt)
    assert whole_speed_y_pixels(attempt) == 0
    assert event_kinds(attempt) == [GameEventKind.HIT_HIDDEN_BLOCK]
    assert tile_kind_in_snapshot(attempt, MARIO_SPAWN_COLUMN, LOW_BLOCK_ROW) is TileKind.USED_BLOCK
    while not attempt.mario.is_on_ground:
        attempt.step(HOLD_NOTHING)
    jump_until_the_head_hits(attempt)
    assert whole_speed_y_pixels(attempt) == 1
    assert event_kinds(attempt) == [GameEventKind.HIT_HIDDEN_BLOCK]


def test_a_bumped_block_bounces_up_and_back_into_place():
    attempt = Attempt(build_level(blocks={(MARIO_SPAWN_COLUMN, LOW_BLOCK_ROW): BRICK}))
    assert bounce_offset_in_snapshot(attempt, MARIO_SPAWN_COLUMN, LOW_BLOCK_ROW) is None
    jump_until_the_head_hits(attempt)
    offsets = []
    while (offset := bounce_offset_in_snapshot(attempt, MARIO_SPAWN_COLUMN, LOW_BLOCK_ROW)) is not None:
        offsets.append(offset)
        attempt.step(HOLD_NOTHING)
    assert offsets == BOUNCE_OFFSETS_PIXELS


def goomba_centre_x(attempt: Attempt) -> int:
    hitbox = attempt.enemies.active[0].hitbox()
    return hitbox.x_pixels + hitbox.width_pixels // 2


def bump_the_goomba_walking_over_marios_block() -> Attempt:
    attempt = Attempt(build_level(blocks=BRICK_PLATFORM,
                                  enemy_spawns=(goomba_spawn(GOOMBA_ON_PLATFORM_X, LOW_BLOCK_ROW - 1),)))
    jump_at_x = (MARIO_SPAWN_COLUMN + 1) * TILE_PIXELS + GOOMBA_LEAD_PIXELS
    while not attempt.enemies.active or goomba_centre_x(attempt) > jump_at_x:
        attempt.step(HOLD_NOTHING)
    jump_until_the_head_hits(attempt)
    while not attempt.events and attempt.ticks_elapsed < TICK_LIMIT:
        attempt.step(HOLD_NOTHING)
    return attempt


def test_a_goomba_standing_on_a_bumped_block_is_defeated():
    attempt = bump_the_goomba_walking_over_marios_block()
    tick = attempt.events[0].tick
    assert attempt.events == [GameEvent(tick, GameEventKind.DEFEATED_ENEMY, DefeatMethod.BUMPED),
                              GameEvent(tick, GameEventKind.SCORED_POINTS, BUMPED_ENEMY_POINTS)]
    assert [enemy.is_defeated for enemy in WorldSnapshot.of(attempt).enemies] == [True]


def test_a_bumped_goomba_flies_away_from_mario_through_the_tiles_and_out_of_play():
    attempt = bump_the_goomba_walking_over_marios_block()
    goomba = attempt.enemies.active[0]
    start_x, start_y = goomba.hitbox().x_pixels, goomba.hitbox().y_pixels
    attempt.step(HOLD_NOTHING)
    assert goomba.hitbox().x_pixels > start_x and goomba.hitbox().y_pixels < start_y
    while attempt.enemies.active and attempt.ticks_elapsed < TICK_LIMIT:
        attempt.step(HOLD_NOTHING)
    assert attempt.enemies.active == [] and not attempt.is_over
