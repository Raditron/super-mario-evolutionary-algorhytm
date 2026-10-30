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


# The bonus room, decoded for #23 (docs/research/world-1-1-layout.md, "The bonus room").
BONUS_ROOM_WIDTH_TILES = 16
BONUS_ROOM_COINS_BY_ROW = {5: range(5, 10), 7: range(4, 11), 9: range(4, 11)}


def test_the_warp_pipe_is_pipe_57(world_1_1):
    assert world_1_1.warp_pipe.left_column == 57


def test_the_bonus_room_is_one_screen_holding_19_coins(world_1_1):
    room = world_1_1.bonus_room.tiles
    assert (room.width_tiles, room.height_tiles) == (BONUS_ROOM_WIDTH_TILES, LEVEL_HEIGHT_TILES)
    coins = {(column, row) for row in range(room.height_tiles) for column in range(room.width_tiles)
             if room.tile_kind(column, row) is TileKind.COIN}
    assert coins == {(column, row) for row, columns in BONUS_ROOM_COINS_BY_ROW.items() for column in columns}
    assert len(coins) == 19
    assert not any(room.is_solid(column, row) for column, row in coins)


def test_the_bonus_room_has_a_brick_wall_a_brick_block_under_a_brick_ceiling_and_a_floor(world_1_1):
    room = world_1_1.bonus_room.tiles
    assert all(room.tile_kind(0, row) is TileKind.BRICK for row in range(2, 13))
    assert all(room.tile_kind(column, row) is TileKind.BRICK
               for column in range(4, 11) for row in (2, 10, 11, 12))
    assert all(room.tile_kind(column, row) is TileKind.GROUND for column in range(16) for row in (13, 14))
    assert not any(room.is_solid(column, row) for column in (1, 2, 3, 11, 12) for row in range(13))


def test_the_bonus_room_exit_pipe_has_its_mouth_at_13_12_and_leads_back_to_page_10(world_1_1):
    room = world_1_1.bonus_room
    assert (room.exit_pipe_mouth_column, room.exit_pipe_mouth_row) == (13, 12)
    assert all(room.tiles.tile_kind(column, row) is TileKind.SIDE_PIPE for column in (13, 14) for row in (11, 12))
    assert all(room.tiles.is_solid(column, row) for column in (13, 14) for row in (11, 12))
    assert all(room.tiles.tile_kind(15, row) is TileKind.PIPE for row in range(2, 13))
    assert room.return_page == 10
