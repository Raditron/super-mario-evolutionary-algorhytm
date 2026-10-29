"""The HUD draws score, coins, world and time in the original's status-bar cells (#16),
the coin's icon from the coin sprite, else as an orange rectangle (#60)."""

import pygame
import pytest

from mario.constants.level import SCREEN_HEIGHT_PIXELS, SCREEN_WIDTH_PIXELS
from mario.constants.view import (
    HUD_CELL_PIXELS,
    HUD_COIN_ICON_CELL,
    HUD_COIN_ICON_COLOUR,
    HUD_COIN_ICON_RECT_IN_CELL,
    HUD_COIN_SPRITE_NAME,
    HUD_COINS_CELL,
    HUD_COINS_DIGITS,
    HUD_SCORE_CELL,
    HUD_SCORE_CELLS_WIDE,
    HUD_TIME_CELL,
    HUD_TIME_DIGITS,
    SKY_COLOUR,
    SPRITE_SIZES,
)
from mario.level.static_level import StaticLevel
from mario.simulation.attempt import Attempt
from mario.snapshots.world_snapshot import HudSnapshot, WorldSnapshot
from mario.view.hud import Hud
from mario.view.sprite_library import SpriteLibrary
from mario.view.viewer import Viewer
from tests.game.scripted_window import NOTHING_PRESSED, ScriptedWindow

HUD_ROWS = range(2, 4)
COIN_SPRITE_COLOUR = (10, 200, 30)


@pytest.fixture(scope="module")
def fonts():
    pygame.font.init()
    yield
    pygame.font.quit()


@pytest.fixture(scope="module")
def hud(fonts) -> Hud:
    return Hud(SpriteLibrary({}))


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


def colours_at(screen: pygame.Surface, pixels: set[tuple[int, int]]) -> set[tuple[int, int, int]]:
    return {tuple(screen.get_at(pixel))[:3] for pixel in pixels}


def test_the_coin_cell_shows_the_coin_sprite(fonts):
    coin_sprite = pygame.Surface(SPRITE_SIZES[HUD_COIN_SPRITE_NAME], pygame.SRCALPHA)
    coin_sprite.fill((*COIN_SPRITE_COLOUR, 255))
    screen = drawn(Hud(SpriteLibrary({HUD_COIN_SPRITE_NAME: coin_sprite})), HudSnapshot(0, 0, 400))
    assert colours_at(screen, cell_pixels(HUD_COIN_ICON_CELL, 1)) == {COIN_SPRITE_COLOUR}


def test_the_viewers_hud_shows_the_coin_png_from_the_sprites_folder(fonts, tmp_path):
    coin_png = pygame.Surface(SPRITE_SIZES[HUD_COIN_SPRITE_NAME], pygame.SRCALPHA)
    coin_png.fill((*COIN_SPRITE_COLOUR, 255))
    pygame.image.save(coin_png, str(tmp_path / f"{HUD_COIN_SPRITE_NAME}.png"))
    window = ScriptedWindow([NOTHING_PRESSED])
    Viewer.with_both_views(window, tmp_path).show(WorldSnapshot.of(Attempt(StaticLevel(["." * 20] * 15))))
    [frame] = window.frames_shown
    assert colours_at(frame, cell_pixels(HUD_COIN_ICON_CELL, 1)) == {COIN_SPRITE_COLOUR}


def test_without_the_coin_sprite_the_coin_cell_shows_an_orange_rectangle(hud):
    column, row = HUD_COIN_ICON_CELL
    x_in_cell, y_in_cell, width, height = HUD_COIN_ICON_RECT_IN_CELL
    rectangle = {(column * HUD_CELL_PIXELS + x_in_cell + x, row * HUD_CELL_PIXELS + y_in_cell + y)
                 for x in range(width) for y in range(height)}
    screen = drawn(hud, HudSnapshot(0, 0, 400))
    assert colours_at(screen, rectangle) == {HUD_COIN_ICON_COLOUR}
    assert colours_at(screen, cell_pixels(HUD_COIN_ICON_CELL, 1) - rectangle) == {SKY_COLOUR}
