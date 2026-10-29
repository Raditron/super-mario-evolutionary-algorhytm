"""The HUD draws score, coins, world and time in the original's status-bar cells (#16),
the coin's icon from the coin sprite, else as an orange rectangle (#60), and every
character from its own 8 x 8 glyph sprite, else in pygame's default font (#59)."""

import pygame
import pytest

from mario.__main__ import SPRITES_FOLDER
from mario.constants.level import SCREEN_HEIGHT_PIXELS, SCREEN_WIDTH_PIXELS, WORLD_NAME
from mario.constants.view import (
    HUD_CELL_PIXELS,
    HUD_COIN_CROSS,
    HUD_COIN_ICON_CELL,
    HUD_COIN_ICON_COLOUR,
    HUD_COIN_ICON_RECT_IN_CELL,
    HUD_COIN_SPRITE_NAME,
    HUD_COINS_CELL,
    HUD_COINS_DIGITS,
    HUD_GLYPH_SPRITE_NAMES,
    HUD_LABELS,
    HUD_SCORE_CELL,
    HUD_SCORE_CELLS_WIDE,
    HUD_TEXT_COLOUR,
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


# --- The HUD's glyphs (#59) ------------------------------------------------------------------

# The status bar's two rows for HudSnapshot(1200, 7, 399), one character per cell from
# column 0, as the original lays them out: the score blanks its first digit while it is 0,
# the coin icon (a space here) stands before the cross, and the world is 1-1.
STATUS_BAR_ROWS = {
    2: "   MARIO          WORLD  TIME",
    3: "   001200   x07    1-1    399",
}
STATUS_BAR_NUMBERS = HudSnapshot(1200, 7, 399)


def glyph_colour(glyph_index: int) -> tuple[int, int, int]:
    """A colour of its own for each glyph, none of them the sky's or the HUD text's."""
    return 10 + glyph_index * 8, 40, 90


GLYPH_COLOURS = {character: glyph_colour(index) for index, character in enumerate(HUD_GLYPH_SPRITE_NAMES)}


def glyph_sprites(missing: str = "") -> SpriteLibrary:
    """Every glyph as a solid square of its own colour, but the characters in missing."""
    sprites = {}
    for character, name in HUD_GLYPH_SPRITE_NAMES.items():
        if character not in missing:
            glyph = pygame.Surface(SPRITE_SIZES[name], pygame.SRCALPHA)
            glyph.fill((*GLYPH_COLOURS[character], 255))
            sprites[name] = glyph
    return SpriteLibrary(sprites)


def status_bar_characters() -> list[tuple[str, tuple[int, int]]]:
    return [(character, (column, row)) for row, line in STATUS_BAR_ROWS.items()
            for column, character in enumerate(line) if character != " "]


@pytest.mark.parametrize("character, cell", status_bar_characters(),
                         ids=lambda value: str(value))
def test_each_hud_character_fills_its_cell_with_its_own_glyph(fonts, character, cell):
    screen = drawn(Hud(glyph_sprites()), STATUS_BAR_NUMBERS)
    assert colours_at(screen, cell_pixels(cell, 1)) == {GLYPH_COLOURS[character]}


MARIO_M_CELL = (3, 2)
MARIO_A_CELL = (4, 2)


def test_a_character_whose_glyph_is_missing_is_printed_in_the_font_in_its_cell(fonts):
    screen = drawn(Hud(glyph_sprites(missing="M")), STATUS_BAR_NUMBERS)
    colours_in_cell = colours_at(screen, cell_pixels(MARIO_M_CELL, 1))
    assert colours_in_cell == {SKY_COLOUR, HUD_TEXT_COLOUR}
    assert colours_at(screen, cell_pixels(MARIO_A_CELL, 1)) == {GLYPH_COLOURS["A"]}


def test_the_font_prints_the_same_character_its_glyph_would_stand_for(fonts):
    """The fallback prints the missing character itself: an M looks unlike an A."""
    m_in_the_font = drawn(Hud(glyph_sprites(missing="MA")), STATUS_BAR_NUMBERS)
    m_cell, a_cell = cell_pixels(MARIO_M_CELL, 1), cell_pixels(MARIO_A_CELL, 1)
    m_shape = {(x - MARIO_M_CELL[0] * HUD_CELL_PIXELS, y) for x, y in m_cell
               if tuple(m_in_the_font.get_at((x, y)))[:3] == HUD_TEXT_COLOUR}
    a_shape = {(x - MARIO_A_CELL[0] * HUD_CELL_PIXELS, y) for x, y in a_cell
               if tuple(m_in_the_font.get_at((x, y)))[:3] == HUD_TEXT_COLOUR}
    assert m_shape and a_shape and m_shape != a_shape


def test_every_character_the_hud_prints_has_a_glyph():
    printed = "".join(HUD_LABELS.values()) + WORLD_NAME + HUD_COIN_CROSS + "0123456789"
    assert set(printed) <= HUD_GLYPH_SPRITE_NAMES.keys()


def test_the_repos_sprites_folder_has_every_glyph():
    sprites = SpriteLibrary.load(SPRITES_FOLDER)
    assert [name for name in HUD_GLYPH_SPRITE_NAMES.values() if sprites.sprite(name) is None] == []
