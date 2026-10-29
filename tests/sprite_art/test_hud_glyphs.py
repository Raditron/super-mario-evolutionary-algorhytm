"""The HUD's font (#59): one 8 x 8 glyph per character the HUD prints, in the HUD's white,
every glyph but the dash (the letters, the digits and the coin count's cross) from the cap
height down to the same baseline, the dash centred on the middle line between them, and every
glyph leaving its cell's last row and column clear, so the characters stand apart when printed
side by side."""

import pytest

from mario.constants.view import HUD_GLYPH_SPRITE_NAMES, HUD_TEXT_COLOUR, HUD_WORLD_DASH
from sprite_art.drawings import ALL_DRAWINGS
from sprite_art.drawings.hud import HUD_GLYPH_DRAWINGS
from sprite_art.palettes.shared import SHARED_KEYS, TRANSPARENT

[TRANSPARENT_KEY] = [key for key, colour in SHARED_KEYS.items() if colour == TRANSPARENT]
CAP_HEIGHT_ROW = 0
BASELINE_ROW = 6
MIDDLE_LINE_ROW = 3


def glyph_drawing(character: str):
    [drawing] = [drawing for drawing in HUD_GLYPH_DRAWINGS if drawing.name == HUD_GLYPH_SPRITE_NAMES[character]]
    return drawing


def inked_rows(drawing) -> list[int]:
    return [row_index for row_index, row in enumerate(drawing.rows) if row.strip(TRANSPARENT_KEY)]


def test_every_glyph_the_hud_knows_is_drawn():
    drawn_names = {drawing.name for drawing in ALL_DRAWINGS}
    assert set(HUD_GLYPH_SPRITE_NAMES.values()) <= drawn_names


@pytest.mark.parametrize("drawing", HUD_GLYPH_DRAWINGS, ids=lambda drawing: drawing.name)
def test_a_glyph_is_inked_in_the_huds_white(drawing):
    ink = {drawing.palette[key] for row in drawing.rows for key in row if key != TRANSPARENT_KEY}
    assert ink == {(*HUD_TEXT_COLOUR, 255)}


@pytest.mark.parametrize("drawing", HUD_GLYPH_DRAWINGS, ids=lambda drawing: drawing.name)
def test_a_glyph_leaves_its_last_row_and_column_clear(drawing):
    assert set(drawing.rows[-1]) == {TRANSPARENT_KEY}
    assert {row[-1] for row in drawing.rows} == {TRANSPARENT_KEY}


@pytest.mark.parametrize("character", [character for character in HUD_GLYPH_SPRITE_NAMES
                                       if character != HUD_WORLD_DASH])
def test_every_glyph_but_the_dash_spans_the_cap_height_to_the_baseline(character):
    rows = inked_rows(glyph_drawing(character))
    assert (rows[0], rows[-1]) == (CAP_HEIGHT_ROW, BASELINE_ROW)


def test_the_dash_is_centred_on_the_middle_line():
    rows = inked_rows(glyph_drawing(HUD_WORLD_DASH))
    assert rows[0] + rows[-1] == 2 * MIDDLE_LINE_ROW
