"""Goombas walk, turn around at walls and fall, with the same tile collision as Mario (#17)."""

from mario.level.static_level import EnemyKind, EnemySpawn, StaticLevel
from mario.simulation.attempt_tiles import AttemptTiles
from mario.simulation.goomba import Goomba
from tests.game.helpers import GROUND_TOP_ROW, build_level

GROUND_TOP_Y = GROUND_TOP_ROW * 16
GOOMBA_SIZE = 16
SPAWN_DROP = 8
# Between 1-1's pipes at columns 38-39 and 46-47.
PIPE_38_RIGHT_X = 40 * 16
PIPE_46_LEFT_X = 46 * 16


def goomba_at(column: int, resting_row: int = GROUND_TOP_ROW - 1) -> Goomba:
    return Goomba(EnemySpawn(EnemyKind.GOOMBA, column * 16, resting_row, column * 16))


def step(goomba: Goomba, level: StaticLevel, ticks: int) -> list[tuple[int, int]]:
    """Step the Goomba; return its hitbox position after every tick."""
    tiles = AttemptTiles(level)
    positions = []
    for tick in range(1, ticks + 1):
        goomba.step(tiles, tick)
        positions.append((goomba.hitbox().x_pixels, goomba.hitbox().y_pixels))
    return positions


def test_a_goomba_drops_onto_the_ground_and_walks_left_at_half_a_pixel_per_tick(flat_level):
    goomba = goomba_at(20)
    assert goomba.hitbox().bottom_y_pixels == GROUND_TOP_Y - SPAWN_DROP
    positions = step(goomba, flat_level, 40)
    assert goomba.hitbox().bottom_y_pixels == GROUND_TOP_Y
    assert positions[-1][0] == 20 * 16 - 20
    assert positions[-1][0] - positions[-3][0] == -1


def test_a_goomba_falls_with_enemy_gravity_capped_near_3_px_per_tick():
    level = build_level(pit_columns=range(0, 120))
    goomba = goomba_at(20, resting_row=2)
    heights = [goomba.hitbox().y_pixels] + [y for _, y in step(goomba, level, 60)]
    fall_per_tick = [after - before for before, after in zip(heights, heights[1:])]
    # 0x3D / 256 px per tick per tick: the first pixel is crossed on the fourth tick.
    assert fall_per_tick[:4] == [0, 0, 0, 1]
    # The cap clamps to 3 px/f only once the fraction reaches half a pixel, so the
    # fall settles between 3 and 3.5 px per tick (MoveD_EnemyVertically).
    assert 3 * 30 <= sum(fall_per_tick[-30:]) <= 3 * 30 + 30 // 2


def test_goombas_turn_around_at_pipes(world_1_1):
    goomba = Goomba(world_1_1.enemy_spawns[1])
    assert goomba.hitbox().x_pixels == 40 * 16
    x_positions = [x for x, _ in step(goomba, world_1_1, 600)]
    assert min(x_positions) == PIPE_38_RIGHT_X
    assert max(x_positions) == PIPE_46_LEFT_X - GOOMBA_SIZE
    first_turn = x_positions.index(PIPE_38_RIGHT_X)
    assert x_positions[first_turn + 4] > PIPE_38_RIGHT_X


def test_goombas_fall_into_pits():
    level = build_level(pit_columns=range(8, 10))
    goomba = goomba_at(12)
    positions = step(goomba, level, 200)
    assert positions[-1][1] > level.height_tiles * 16
    x_when_below_the_ground_top = next(x for x, y in positions if y >= GROUND_TOP_Y)
    assert 8 * 16 <= x_when_below_the_ground_top <= 10 * 16 - GOOMBA_SIZE
