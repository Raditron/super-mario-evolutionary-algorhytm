from mario.constants.level import LEVEL_HEIGHT_TILES, LEVEL_WIDTH_TILES
from mario.level.static_level import EnemyKind, PipeDestination
from mario.level.tile_kind import TileKind


def test_world_1_1_is_224_by_15_tiles(world_1_1):
    assert (world_1_1.width_tiles, world_1_1.height_tiles) == (LEVEL_WIDTH_TILES, LEVEL_HEIGHT_TILES)


def test_world_1_1_has_its_blocks(world_1_1):
    kinds = [block.kind for block in world_1_1.blocks]
    assert kinds.count(TileKind.COIN_QUESTION_BLOCK) == 10
    assert kinds.count(TileKind.POWER_UP_QUESTION_BLOCK) == 3
    assert kinds.count(TileKind.STARMAN_BRICK) == 1
    assert kinds.count(TileKind.MULTI_COIN_BRICK) == 1
    assert kinds.count(TileKind.HIDDEN_ONE_UP_BLOCK) == 1
    assert kinds.count(TileKind.BRICK) == 28


def test_world_1_1_has_six_pipes_and_one_leads_to_the_bonus_room(world_1_1):
    assert [pipe.left_column for pipe in world_1_1.pipes] == [28, 38, 46, 57, 163, 179]
    assert [pipe.left_column for pipe in world_1_1.pipes
            if pipe.leads_to is PipeDestination.BONUS_ROOM] == [57]


def test_world_1_1_has_sixteen_goombas_and_one_koopa(world_1_1):
    kinds = [spawn.kind for spawn in world_1_1.enemy_spawns]
    assert kinds.count(EnemyKind.GOOMBA) == 16
    assert kinds.count(EnemyKind.KOOPA) == 1


def test_goomba_pairs_sit_three_and_one_and_a_half_tiles_before_their_data_column(world_1_1):
    pair_x_pixels = [spawn.x_pixels for spawn in world_1_1.enemy_spawns][2:4]
    assert pair_x_pixels == [16 * (54 - 3), 16 * 54 - 24]


def test_tiles_outside_the_grid_are_walls_at_the_sides_and_open_above_and_below(world_1_1):
    assert world_1_1.is_solid(-1, 13)
    assert world_1_1.is_solid(LEVEL_WIDTH_TILES, 13)
    assert not world_1_1.is_solid(10, -1)
    assert not world_1_1.is_solid(10, LEVEL_HEIGHT_TILES)


def test_hidden_block_and_flagpole_are_not_solid_yet(world_1_1):
    assert world_1_1.tile_kind(64, 8) is TileKind.HIDDEN_ONE_UP_BLOCK
    assert not world_1_1.is_solid(64, 8)
    assert not world_1_1.is_solid(198, 5)
    assert world_1_1.is_solid(198, 12)
