"""The Debug view draws Goombas as coloured hitboxes, a squashed one flattened (#17),
the flag on the flagpole (#24), an invincible Mario in his own colour (#21), and
over them the followed agent's Observation and the recent game events (#25)."""

import pygame
import pytest

from mario.constants.level import (
    FIREBALL_SIZE_PIXELS,
    GOOMBA_HITBOX_HEIGHT_PIXELS,
    GOOMBA_HITBOX_WIDTH_PIXELS,
    LEVEL_TIMER_START_UNITS,
    ITEM_HITBOX_HEIGHT_PIXELS,
    ITEM_HITBOX_WIDTH_PIXELS,
    SCREEN_HEIGHT_PIXELS,
    SCREEN_WIDTH_PIXELS,
    SMALL_MARIO_HITBOX_HEIGHT_PIXELS,
    SMALL_MARIO_HITBOX_WIDTH_PIXELS,
    TILE_SIZE_PIXELS,
)
from mario.constants.observation import (
    EMPTY_CELL,
    ENEMY_CELL,
    OBSERVATION_BOTTOM_ROW,
    OBSERVATION_COLUMNS,
    OBSERVATION_ROWS,
    OBSERVATION_TOP_ROW,
    SOLID_CELL,
)
from mario.constants.view import (
    DEBUG_GAME_EVENT_LINES,
    DEBUG_GAME_EVENTS_TOP_LEFT,
    DEBUG_TEXT_LINE_PIXELS,
    EXPLODING_FIREBALL_COLOUR,
    FIREBALL_COLOUR,
    FLAG_COLOUR,
    FIRE_FLOWER_COLOUR,
    FIRE_MARIO_COLOUR,
    GOOMBA_COLOUR,
    INVINCIBLE_MARIO_COLOUR,
    KOOPA_COLOUR,
    KOOPA_SHELL_COLOUR,
    MARIO_COLOUR,
    OBSERVATION_ENEMY_TINT,
    OBSERVATION_SOLID_TINT,
    OBSERVATION_STATE_TEXT_TOP_LEFT,
    ONE_UP_MUSHROOM_COLOUR,
    SKY_COLOUR,
    STARMAN_COLOUR,
    SUPER_MUSHROOM_COLOUR,
    USED_BLOCK_COLOUR,
)
from mario.level.static_level import EnemyKind
from mario.level.tile_kind import TileKind
from mario.simulation.attempt_result import DefeatMethod, GameEvent, GameEventKind
from mario.simulation.item_kind import ItemKind
from mario.snapshots.world_snapshot import (
    EnemySnapshot,
    FireballSnapshot,
    FlagSnapshot,
    HudSnapshot,
    ItemSnapshot,
    MarioSnapshot,
    ObservationSnapshot,
    PowerState,
    VisibleTiles,
    WorldSnapshot,
)
from mario.view.debug_renderer import DebugRenderer

SCREEN_LEFT_X = 100
GOOMBA_X, GOOMBA_Y = 300, 120                 # in level pixels, clear of the ground and Mario
GOOMBA_RIGHT_X = GOOMBA_X + GOOMBA_HITBOX_WIDTH_PIXELS - 1    # its hitbox's last column of pixels
GOOMBA_BOTTOM_Y = GOOMBA_Y + GOOMBA_HITBOX_HEIGHT_PIXELS - 1  # and last row
# An Observation window starting at level column 8 (screen x 28), with one solid
# cell and one enemy cell on its fourth row (screen row 5).
WINDOW_FIRST_COLUMN = 8
SOLID_CELL_AT, ENEMY_CELL_AT, EMPTY_CELL_AT = (3, 2), (3, 4), (3, 6)
STANDING_STILL = (0.0, 0.0, 1.0, 1.0)
HALF_TILE_PIXELS = TILE_SIZE_PIXELS // 2
MARIO_Y_PIXELS = OBSERVATION_BOTTOM_ROW * TILE_SIZE_PIXELS - SMALL_MARIO_HITBOX_HEIGHT_PIXELS  # on the ground


@pytest.fixture(autouse=True, scope="module")
def fonts():
    pygame.font.init()
    yield
    pygame.font.quit()


def snapshot_with(enemies: tuple[EnemySnapshot, ...] = (), observation: ObservationSnapshot | None = None,
                  recent_events: tuple[GameEvent, ...] = (), items: tuple[ItemSnapshot, ...] = (),
                  fireballs: tuple[FireballSnapshot, ...] = (),
                  flag: FlagSnapshot | None = None,
                  tiles: VisibleTiles = VisibleTiles(0, ()), tick: int = 0,
                  mario_is_invulnerable: bool = False,
                  mario_power_state: PowerState = PowerState.SMALL,
                  mario_is_invincible: bool = False) -> WorldSnapshot:
    """A screen with no tiles, Mario at its left, and what is given."""
    return WorldSnapshot(tick=tick, screen_left_x_pixels=SCREEN_LEFT_X, tiles=tiles,
                         mario=MarioSnapshot(SCREEN_LEFT_X, MARIO_Y_PIXELS, SMALL_MARIO_HITBOX_WIDTH_PIXELS,
                                             SMALL_MARIO_HITBOX_HEIGHT_PIXELS, mario_power_state,
                                             is_invulnerable=mario_is_invulnerable,
                                             is_invincible=mario_is_invincible),
                         enemies=enemies, hud=HudSnapshot(0, 0, LEVEL_TIMER_START_UNITS),
                         items=items, fireballs=fireballs, flag=flag, observation=observation,
                         recent_events=recent_events)


def drawn(snapshot: WorldSnapshot) -> pygame.Surface:
    screen = pygame.Surface((SCREEN_WIDTH_PIXELS, SCREEN_HEIGHT_PIXELS))
    DebugRenderer().draw(snapshot, screen)
    return screen


def goomba_snapshot(is_defeated: bool) -> EnemySnapshot:
    return EnemySnapshot(EnemyKind.GOOMBA, GOOMBA_X, GOOMBA_Y, GOOMBA_HITBOX_WIDTH_PIXELS,
                         GOOMBA_HITBOX_HEIGHT_PIXELS, is_defeated)


def drawn_with(goomba: EnemySnapshot) -> pygame.Surface:
    return drawn(snapshot_with(enemies=(goomba,)))


def colour_at(screen: pygame.Surface, level_x: int, y: int) -> tuple[int, int, int]:
    return tuple(screen.get_at((level_x - SCREEN_LEFT_X, y)))[:3]


def observation_with(state_numbers: tuple[float, ...] = STANDING_STILL) -> ObservationSnapshot:
    cells = [[EMPTY_CELL] * OBSERVATION_COLUMNS for _ in range(OBSERVATION_ROWS)]
    cells[SOLID_CELL_AT[0]][SOLID_CELL_AT[1]] = SOLID_CELL
    cells[ENEMY_CELL_AT[0]][ENEMY_CELL_AT[1]] = ENEMY_CELL
    return ObservationSnapshot(WINDOW_FIRST_COLUMN, tuple(map(tuple, cells)), state_numbers)


def cell_centre_x(column: int) -> int:
    """The level x of the middle of the window's column."""
    return (WINDOW_FIRST_COLUMN + column) * TILE_SIZE_PIXELS + HALF_TILE_PIXELS


def cell_centre_y(row: int) -> int:
    """The y of the middle of the window's row."""
    return (OBSERVATION_TOP_ROW + row) * TILE_SIZE_PIXELS + HALF_TILE_PIXELS


def cell_centre_colour(screen: pygame.Surface, cell: tuple[int, int]) -> tuple[int, int, int]:
    row, column = cell
    return colour_at(screen, cell_centre_x(column), cell_centre_y(row))


def changed_rows(first: pygame.Surface, second: pygame.Surface) -> set[int]:
    return {y for x in range(SCREEN_WIDTH_PIXELS) for y in range(SCREEN_HEIGHT_PIXELS)
            if first.get_at((x, y)) != second.get_at((x, y))}


def test_a_goomba_is_drawn_as_its_hitbox_in_the_goomba_colour():
    screen = drawn_with(goomba_snapshot(is_defeated=False))
    assert colour_at(screen, GOOMBA_X, GOOMBA_Y) == GOOMBA_COLOUR
    assert colour_at(screen, GOOMBA_RIGHT_X, GOOMBA_BOTTOM_Y) == GOOMBA_COLOUR
    assert colour_at(screen, GOOMBA_RIGHT_X + 1, GOOMBA_Y) == SKY_COLOUR
    assert colour_at(screen, GOOMBA_X, GOOMBA_Y - 1) == SKY_COLOUR


def test_a_squashed_goomba_is_drawn_flattened_onto_its_feet():
    screen = drawn_with(goomba_snapshot(is_defeated=True))
    assert colour_at(screen, GOOMBA_X, GOOMBA_Y) == SKY_COLOUR
    assert colour_at(screen, GOOMBA_X, GOOMBA_BOTTOM_Y) == GOOMBA_COLOUR


@pytest.mark.parametrize("is_shell, colour", [(False, KOOPA_COLOUR), (True, KOOPA_SHELL_COLOUR)])
def test_a_koopa_and_its_shell_are_drawn_as_its_hitbox_each_in_its_colour(is_shell, colour):
    screen = drawn_with(EnemySnapshot(EnemyKind.KOOPA, GOOMBA_X, GOOMBA_Y, GOOMBA_HITBOX_WIDTH_PIXELS,
                                      GOOMBA_HITBOX_HEIGHT_PIXELS, is_defeated=False, is_shell=is_shell))
    assert colour_at(screen, GOOMBA_X, GOOMBA_Y) == colour
    assert colour_at(screen, GOOMBA_RIGHT_X, GOOMBA_BOTTOM_Y) == colour
    assert colour_at(screen, GOOMBA_RIGHT_X + 1, GOOMBA_Y) == SKY_COLOUR
    assert colour_at(screen, GOOMBA_X, GOOMBA_Y - 1) == SKY_COLOUR


def mushroom_snapshot(kind: ItemKind, is_emerging: bool = False) -> ItemSnapshot:
    return ItemSnapshot(kind, GOOMBA_X, GOOMBA_Y, ITEM_HITBOX_WIDTH_PIXELS, ITEM_HITBOX_HEIGHT_PIXELS,
                        is_emerging)


@pytest.mark.parametrize("kind, colour", [(ItemKind.SUPER_MUSHROOM, SUPER_MUSHROOM_COLOUR),
                                          (ItemKind.ONE_UP_MUSHROOM, ONE_UP_MUSHROOM_COLOUR),
                                          (ItemKind.FIRE_FLOWER, FIRE_FLOWER_COLOUR),
                                          (ItemKind.STARMAN, STARMAN_COLOUR)])
def test_an_item_is_drawn_as_its_hitbox_in_its_kinds_colour(kind, colour):
    screen = drawn(snapshot_with(items=(mushroom_snapshot(kind),)))
    assert colour_at(screen, GOOMBA_X, GOOMBA_Y) == colour
    assert colour_at(screen, GOOMBA_RIGHT_X, GOOMBA_BOTTOM_Y) == colour
    assert colour_at(screen, GOOMBA_RIGHT_X + 1, GOOMBA_Y) == SKY_COLOUR


def test_a_mushroom_rising_out_of_its_block_is_drawn_behind_it():
    """Half risen: its top half shows above the block, its bottom half is hidden in it."""
    block_column, block_row = GOOMBA_X // TILE_SIZE_PIXELS, GOOMBA_Y // TILE_SIZE_PIXELS
    rows = tuple(tuple(TileKind.USED_BLOCK if (column, row) == (block_column, block_row) else TileKind.EMPTY
                       for column in range(block_column + 1)) for row in range(block_row + 1))
    half_risen = ItemSnapshot(ItemKind.SUPER_MUSHROOM, block_column * TILE_SIZE_PIXELS,
                              block_row * TILE_SIZE_PIXELS - HALF_TILE_PIXELS, ITEM_HITBOX_WIDTH_PIXELS,
                              ITEM_HITBOX_HEIGHT_PIXELS, is_emerging=True)
    screen = drawn(snapshot_with(items=(half_risen,), tiles=VisibleTiles(0, rows)))
    block_x, block_y = block_column * TILE_SIZE_PIXELS, block_row * TILE_SIZE_PIXELS
    assert colour_at(screen, block_x, block_y - 1) == SUPER_MUSHROOM_COLOUR
    assert colour_at(screen, block_x, block_y) == USED_BLOCK_COLOUR


@pytest.mark.parametrize("power_state, colour", [(PowerState.BIG, MARIO_COLOUR),
                                                 (PowerState.FIERY, FIRE_MARIO_COLOUR)])
def test_mario_is_drawn_in_his_power_states_colour(power_state, colour):
    screen = drawn(snapshot_with(mario_power_state=power_state))
    assert colour_at(screen, SCREEN_LEFT_X, MARIO_Y_PIXELS) == colour


@pytest.mark.parametrize("power_state", list(PowerState))
def test_an_invincible_mario_is_drawn_in_the_invincible_colour_whatever_his_power_state(power_state):
    screen = drawn(snapshot_with(mario_power_state=power_state, mario_is_invincible=True))
    assert colour_at(screen, SCREEN_LEFT_X, MARIO_Y_PIXELS) == INVINCIBLE_MARIO_COLOUR


@pytest.mark.parametrize("is_exploding, colour", [(False, FIREBALL_COLOUR), (True, EXPLODING_FIREBALL_COLOUR)])
def test_a_fireball_is_drawn_as_its_box_flying_or_exploding(is_exploding, colour):
    fireball = FireballSnapshot(GOOMBA_X, GOOMBA_Y, FIREBALL_SIZE_PIXELS, FIREBALL_SIZE_PIXELS, is_exploding)
    screen = drawn(snapshot_with(fireballs=(fireball,)))
    assert colour_at(screen, GOOMBA_X, GOOMBA_Y) == colour
    assert colour_at(screen, GOOMBA_X + FIREBALL_SIZE_PIXELS - 1, GOOMBA_Y + FIREBALL_SIZE_PIXELS - 1) == colour
    assert colour_at(screen, GOOMBA_X + FIREBALL_SIZE_PIXELS, GOOMBA_Y) == SKY_COLOUR


def test_the_flag_is_drawn_as_a_tile_sized_box_at_its_place():
    screen = drawn(snapshot_with(flag=FlagSnapshot(GOOMBA_X, GOOMBA_Y)))
    assert colour_at(screen, GOOMBA_X, GOOMBA_Y) == FLAG_COLOUR
    assert colour_at(screen, GOOMBA_X + TILE_SIZE_PIXELS - 1, GOOMBA_Y + TILE_SIZE_PIXELS - 1) == FLAG_COLOUR
    assert colour_at(screen, GOOMBA_X + TILE_SIZE_PIXELS, GOOMBA_Y) == SKY_COLOUR
    assert colour_at(screen, GOOMBA_X, GOOMBA_Y + TILE_SIZE_PIXELS) == SKY_COLOUR


def test_invulnerable_mario_blinks_drawn_only_on_even_ticks():
    mario_x = SCREEN_LEFT_X
    assert colour_at(drawn(snapshot_with(tick=0, mario_is_invulnerable=True)), mario_x, MARIO_Y_PIXELS) == MARIO_COLOUR
    assert colour_at(drawn(snapshot_with(tick=1, mario_is_invulnerable=True)), mario_x, MARIO_Y_PIXELS) == SKY_COLOUR
    assert colour_at(drawn(snapshot_with(tick=1)), mario_x, MARIO_Y_PIXELS) == MARIO_COLOUR


def test_the_observation_window_is_drawn_translucent_over_the_level_each_cell_tinted_by_its_value():
    screen = drawn(snapshot_with(observation=observation_with()))
    solid, enemy, empty = (cell_centre_colour(screen, cell) for cell in (SOLID_CELL_AT, ENEMY_CELL_AT, EMPTY_CELL_AT))
    assert len({solid, enemy, empty, SKY_COLOUR}) == 4
    assert solid != OBSERVATION_SOLID_TINT and enemy != OBSERVATION_ENEMY_TINT
    window_left_x = WINDOW_FIRST_COLUMN * TILE_SIZE_PIXELS
    window_top_y = OBSERVATION_TOP_ROW * TILE_SIZE_PIXELS
    assert colour_at(screen, window_left_x - 1, cell_centre_y(SOLID_CELL_AT[0])) == SKY_COLOUR  # left of it
    assert colour_at(screen, cell_centre_x(0), window_top_y - 1) == SKY_COLOUR                  # above it


def test_no_observation_draws_no_window():
    screen = drawn(snapshot_with())
    assert cell_centre_colour(screen, SOLID_CELL_AT) == SKY_COLOUR


def test_the_four_state_numbers_are_written_on_their_own_line():
    standing = drawn(snapshot_with(observation=observation_with()))
    jumping = drawn(snapshot_with(observation=observation_with((0.5, -0.75, 0.625, 0.0))))
    text_top = OBSERVATION_STATE_TEXT_TOP_LEFT[1]
    assert changed_rows(standing, jumping)
    assert changed_rows(standing, jumping) <= set(range(text_top, text_top + DEBUG_TEXT_LINE_PIXELS))


def test_the_recent_game_events_and_points_scored_are_listed_newest_last():
    stomp = (GameEvent(30, GameEventKind.DEFEATED_ENEMY, DefeatMethod.STOMP),
             GameEvent(30, GameEventKind.SCORED_POINTS, 100))
    listed = drawn(snapshot_with(recent_events=stomp))
    events_top = DEBUG_GAME_EVENTS_TOP_LEFT[1]
    assert changed_rows(drawn(snapshot_with()), listed)
    assert changed_rows(drawn(snapshot_with()), listed) <= set(
        range(events_top, events_top + DEBUG_GAME_EVENT_LINES * DEBUG_TEXT_LINE_PIXELS))
    many = tuple(GameEvent(tick, GameEventKind.SCORED_POINTS, 100) for tick in range(DEBUG_GAME_EVENT_LINES + 1))
    assert not changed_rows(drawn(snapshot_with(recent_events=many)),
                            drawn(snapshot_with(recent_events=many[1:])))
