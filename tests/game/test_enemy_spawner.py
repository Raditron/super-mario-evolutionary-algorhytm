"""Enemy activation (#17, spec section 4): in list order, once in range past the screen's right edge."""

from mario.constants.level import SCREEN_WIDTH_PIXELS, SCROLL_STOP_LEFT_X_PIXELS
from mario.level.static_level import EnemyKind, EnemySpawn
from mario.simulation.enemy_spawner import EnemySpawner

# Where 1-1's 16 Goombas start, in level pixels: singles at 16 * data column,
# pairs at 16 * (data column - 3) and 16 * (data column - 1.5) (docs/research/world-1-1-layout.md).
WORLD_1_1_GOOMBA_START_X = [352, 640, 816, 840, 1280, 1312, 1552, 1576,
                            1824, 1848, 1984, 2008, 2048, 2072, 2784, 2808]
GROUND_GOOMBA_START_Y = 12 * 16 - 8           # resting on row 13, spawned 8 px above it
BRICK_GOOMBA_START_Y = 4 * 16 - 8             # resting on the upper bricks (row 5)
ACTIVATION_RANGE_PIXELS = 48


def screen_right_edge(screen_left_x: int) -> int:
    return screen_left_x + SCREEN_WIDTH_PIXELS - 1


def test_sweeping_the_screen_across_1_1_activates_all_16_goombas_at_their_spawn_positions(world_1_1):
    spawner = EnemySpawner(world_1_1.enemy_spawns)
    goombas = []
    for screen_left_x in range(SCROLL_STOP_LEFT_X_PIXELS + 1):
        goombas += [enemy for enemy in spawner.activate_due(screen_left_x) if enemy.kind is EnemyKind.GOOMBA]
    assert [goomba.hitbox().x_pixels for goomba in goombas] == WORLD_1_1_GOOMBA_START_X
    assert [goomba.hitbox().y_pixels for goomba in goombas] == (
        [GROUND_GOOMBA_START_Y] * 4 + [BRICK_GOOMBA_START_Y] * 2 + [GROUND_GOOMBA_START_Y] * 10)


def test_a_single_enemy_activates_once_its_x_is_48_px_past_the_screens_right_edge():
    spawner = EnemySpawner((EnemySpawn(EnemyKind.GOOMBA, 400, 12, 400),))
    activation_left_x = 400 - ACTIVATION_RANGE_PIXELS - (SCREEN_WIDTH_PIXELS - 1)
    assert spawner.activate_due(activation_left_x - 1) == []
    assert len(spawner.activate_due(activation_left_x)) == 1
    assert spawner.activate_due(activation_left_x + 1) == []


def test_a_goomba_pair_activates_together_when_its_data_column_comes_into_range(world_1_1):
    first_pair = world_1_1.enemy_spawns[2:4]
    spawner = EnemySpawner(first_pair)
    data_column_x = 54 * 16
    activation_left_x = data_column_x - ACTIVATION_RANGE_PIXELS - (SCREEN_WIDTH_PIXELS - 1)
    assert spawner.activate_due(activation_left_x - 1) == []
    pair = spawner.activate_due(activation_left_x)
    assert [goomba.hitbox().x_pixels for goomba in pair] == [816, 840]
    # The first Goomba of a pair appears at the screen's right edge, as in the original.
    assert pair[0].hitbox().x_pixels == screen_right_edge(activation_left_x)


def test_enemies_activate_in_list_order_and_one_already_passed_is_skipped_for_good():
    spawns = (EnemySpawn(EnemyKind.GOOMBA, 300, 12, 300), EnemySpawn(EnemyKind.GOOMBA, 1000, 12, 1000))
    spawner = EnemySpawner(spawns)
    # Starting with the screen past the first enemy (as from the checkpoint) skips it.
    assert spawner.activate_due(200) == []
    assert [goomba.hitbox().x_pixels for goomba in spawner.activate_due(1000 - 303)] == [1000]
