"""The HUD draws score, coins, world and time in the original's status-bar cells (#16)."""

import pygame
import pytest

from mario.constants.level import SCREEN_HEIGHT_PIXELS, SCREEN_WIDTH_PIXELS
from mario.constants.view import (
    HUD_CELL_PIXELS,
    HUD_COINS_CELL,
    HUD_COINS_DIGITS,
    HUD_SCORE_CELL,
    HUD_SCORE_CELLS_WIDE,
    HUD_TIME_CELL,
    HUD_TIME_DIGITS,
    SKY_COLOUR,
)
from mario.snapshots.world_snapshot import HudSnapshot
from mario.view.hud import Hud

HUD_ROWS = range(2, 4)


@pytest.fixture(scope="module")
def hud() -> Hud:
    pygame.font.init()
    yield Hud()
    pygame.font.quit()


def drawn(hud: Hud, numbers: HudSnapshot) -> pygame.Surface:
    screen = pygame.Surface((SCREEN_WIDTH_PIXELS, SCREEN_HEIGHT_PIXELS))
    screen.fill(SKY_COLOUR)
    hud.draw(numbers, screen)
    return screen


def changed_pixels(first: pygame.Surface, second: pygame.Surface) -> set[tuple[int, int]]:
    return {(x, y) for x in range(SCREEN_WIDTH_PIXELS) for y in range(SCREEN_HEIGHT_PIXELS)
            if first.get_at((x, y)) != second.get_at((x, y))}


def cell_pixels(first_cell: tuple[int, int], cells_wide: int) -> set[tuple[int, int]]:
    column, row = first_cell
    return {(x, y) for x in range(column * HUD_CELL_PIXELS, (column + cells_wide) * HUD_CELL_PIXELS)
            for y in range(row * HUD_CELL_PIXELS, (row + 1) * HUD_CELL_PIXELS)}


def test_the_hud_draws_only_in_the_status_bar_rows(hud):
    blank = pygame.Surface((SCREEN_WIDTH_PIXELS, SCREEN_HEIGHT_PIXELS))
    blank.fill(SKY_COLOUR)
    drawn_on = changed_pixels(blank, drawn(hud, HudSnapshot(0, 0, 400)))
    assert drawn_on
    assert {y // HUD_CELL_PIXELS for _, y in drawn_on} <= set(HUD_ROWS)


@pytest.mark.parametrize("changed_numbers, first_cell, cells_wide", [
    (HudSnapshot(1200, 0, 400), HUD_SCORE_CELL, HUD_SCORE_CELLS_WIDE),
    (HudSnapshot(0, 7, 400), HUD_COINS_CELL, HUD_COINS_DIGITS),
    (HudSnapshot(0, 0, 399), HUD_TIME_CELL, HUD_TIME_DIGITS),
])
def test_each_number_shows_in_its_own_cells(hud, changed_numbers, first_cell, cells_wide):
    difference = changed_pixels(drawn(hud, HudSnapshot(0, 0, 400)), drawn(hud, changed_numbers))
    assert difference
    assert difference <= cell_pixels(first_cell, cells_wide)
