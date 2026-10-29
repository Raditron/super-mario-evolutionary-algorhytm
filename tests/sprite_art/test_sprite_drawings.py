"""The drawings py -m sprite_art paints: each is a sprite the Sprite view knows, at
its size, and the PNG in assets/sprites/ is exactly what it paints."""

import pygame
import pytest

from mario.__main__ import SPRITES_FOLDER
from mario.constants.view import SPRITE_FILE_EXTENSION, SPRITE_SIZES
from sprite_art.drawings import ALL_DRAWINGS
from sprite_art.palettes.shared import SHARED_KEYS, WHITE
from sprite_art.sprite_drawing import SpriteDrawing

PIXEL_FORMAT = "RGBA"


def pixels(surface: pygame.Surface) -> bytes:
    return pygame.image.tobytes(surface, PIXEL_FORMAT)


@pytest.mark.parametrize("drawing", ALL_DRAWINGS, ids=lambda drawing: drawing.name)
def test_a_drawing_is_a_sprite_the_view_knows_at_its_size(drawing):
    assert drawing.size == SPRITE_SIZES[drawing.name]


def test_no_two_drawings_share_a_name():
    names = [drawing.name for drawing in ALL_DRAWINGS]
    assert len(names) == len(set(names))


@pytest.mark.parametrize("drawing", ALL_DRAWINGS, ids=lambda drawing: drawing.name)
def test_the_sprites_png_is_what_its_drawing_paints(drawing):
    """A drawing changed without running py -m sprite_art fails here."""
    sprite_file = SPRITES_FOLDER / f"{drawing.name}{SPRITE_FILE_EXTENSION}"
    assert pixels(pygame.image.load(str(sprite_file))) == pixels(drawing.painted())


def test_a_drawing_paints_one_pixel_per_key_with_transparent_dots():
    painted = SpriteDrawing("fireball", SHARED_KEYS, ("K.", ".W")).painted()
    assert painted.get_at((0, 0))[3] == 255
    assert painted.get_at((1, 0))[3] == 0
    assert tuple(painted.get_at((1, 1))) == WHITE


def test_a_drawing_with_rows_of_different_widths_is_refused():
    with pytest.raises(ValueError, match="wide"):
        SpriteDrawing("fireball", SHARED_KEYS, ("KK", "K"))


def test_a_drawing_with_a_key_not_in_the_palette_is_refused():
    with pytest.raises(ValueError, match="palette"):
        SpriteDrawing("fireball", SHARED_KEYS, ("K?",))
