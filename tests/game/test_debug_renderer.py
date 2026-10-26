"""The Debug view draws Goombas as coloured hitboxes, a squashed one flattened (#17),
and over them the followed agent's Observation and the recent game events (#25)."""

import pygame
import pytest

from mario.constants.level import SCREEN_HEIGHT_PIXELS, SCREEN_WIDTH_PIXELS
from mario.constants.view import (
    DEBUG_GAME_EVENT_LINES,
    DEBUG_GAME_EVENTS_TOP_LEFT,
    DEBUG_TEXT_LINE_PIXELS,
    GOOMBA_COLOUR,
    OBSERVATION_ENEMY_TINT,
    OBSERVATION_SOLID_TINT,
    OBSERVATION_STATE_TEXT_TOP_LEFT,
    SKY_COLOUR,
)
from mario.level.static_level import EnemyKind
from mario.simulation.attempt_result import DefeatMethod, GameEvent, GameEventKind
from mario.snapshots.world_snapshot import (
    EnemySnapshot,
    HudSnapshot,
    MarioSnapshot,
    ObservationSnapshot,
    VisibleTiles,
    WorldSnapshot,
)
from mario.view.debug_renderer import DebugRenderer

SCREEN_LEFT_X = 100
GOOMBA_X, GOOMBA_Y = 300, 120                 # in level pixels, clear of the ground and Mario
# An Observation window starting at level column 8 (screen x 28), with one solid
# cell and one enemy cell on its fourth row (screen row 5).
WINDOW_FIRST_COLUMN = 8
SOLID_CELL_AT, ENEMY_CELL_AT, EMPTY_CELL_AT = (3, 2), (3, 4), (3, 6)
STANDING_STILL = (0.0, 0.0, 1.0, 1.0)


@pytest.fixture(autouse=True, scope="module")
def fonts():
    pygame.font.init()
    yield
    pygame.font.quit()


def snapshot_with(enemies: tuple[EnemySnapshot, ...] = (), observation: ObservationSnapshot | None = None,
                  recent_events: tuple[GameEvent, ...] = ()) -> WorldSnapshot:
    """A screen with no tiles, Mario at its left, and what is given."""
    return WorldSnapshot(tick=0, screen_left_x_pixels=SCREEN_LEFT_X, tiles=VisibleTiles(0, ()),
                         mario=MarioSnapshot(SCREEN_LEFT_X, 194, 12, 14), enemies=enemies,
                         hud=HudSnapshot(0, 0, 400), observation=observation, recent_events=recent_events)


def drawn(snapshot: WorldSnapshot) -> pygame.Surface:
    screen = pygame.Surface((SCREEN_WIDTH_PIXELS, SCREEN_HEIGHT_PIXELS))
    DebugRenderer().draw(snapshot, screen)
    return screen


def drawn_with(goomba: EnemySnapshot) -> pygame.Surface:
    return drawn(snapshot_with(enemies=(goomba,)))


def colour_at(screen: pygame.Surface, level_x: int, y: int) -> tuple[int, int, int]:
    return tuple(screen.get_at((level_x - SCREEN_LEFT_X, y)))[:3]


def observation_with(state_numbers: tuple[float, ...] = STANDING_STILL) -> ObservationSnapshot:
    cells = [[0.0] * 13 for _ in range(12)]
    cells[SOLID_CELL_AT[0]][SOLID_CELL_AT[1]] = 1.0
    cells[ENEMY_CELL_AT[0]][ENEMY_CELL_AT[1]] = -1.0
    return ObservationSnapshot(WINDOW_FIRST_COLUMN, tuple(map(tuple, cells)), state_numbers)


def cell_centre_colour(screen: pygame.Surface, cell: tuple[int, int]) -> tuple[int, int, int]:
    row, column = cell
    return colour_at(screen, (WINDOW_FIRST_COLUMN + column) * 16 + 8, (2 + row) * 16 + 8)


def changed_rows(first: pygame.Surface, second: pygame.Surface) -> set[int]:
    return {y for x in range(SCREEN_WIDTH_PIXELS) for y in range(SCREEN_HEIGHT_PIXELS)
            if first.get_at((x, y)) != second.get_at((x, y))}


def test_a_goomba_is_drawn_as_its_hitbox_in_the_goomba_colour():
    screen = drawn_with(EnemySnapshot(EnemyKind.GOOMBA, GOOMBA_X, GOOMBA_Y, 16, 16, is_defeated=False))
    assert colour_at(screen, GOOMBA_X, GOOMBA_Y) == GOOMBA_COLOUR
    assert colour_at(screen, GOOMBA_X + 15, GOOMBA_Y + 15) == GOOMBA_COLOUR
    assert colour_at(screen, GOOMBA_X + 16, GOOMBA_Y) == SKY_COLOUR
    assert colour_at(screen, GOOMBA_X, GOOMBA_Y - 1) == SKY_COLOUR


def test_a_squashed_goomba_is_drawn_flattened_onto_its_feet():
    screen = drawn_with(EnemySnapshot(EnemyKind.GOOMBA, GOOMBA_X, GOOMBA_Y, 16, 16, is_defeated=True))
    assert colour_at(screen, GOOMBA_X, GOOMBA_Y) == SKY_COLOUR
    assert colour_at(screen, GOOMBA_X, GOOMBA_Y + 15) == GOOMBA_COLOUR


def test_the_observation_window_is_drawn_translucent_over_the_level_each_cell_tinted_by_its_value():
    screen = drawn(snapshot_with(observation=observation_with()))
    solid, enemy, empty = (cell_centre_colour(screen, cell) for cell in (SOLID_CELL_AT, ENEMY_CELL_AT, EMPTY_CELL_AT))
    assert len({solid, enemy, empty, SKY_COLOUR}) == 4
    assert solid != OBSERVATION_SOLID_TINT and enemy != OBSERVATION_ENEMY_TINT
    assert colour_at(screen, WINDOW_FIRST_COLUMN * 16 - 1, 5 * 16 + 8) == SKY_COLOUR      # left of the window
    assert colour_at(screen, WINDOW_FIRST_COLUMN * 16 + 8, 2 * 16 - 1) == SKY_COLOUR      # above it


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
