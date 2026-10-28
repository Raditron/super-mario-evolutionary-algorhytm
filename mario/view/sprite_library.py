"""The sprites found in assets/sprites/, each at the original's size.

Every file the Sprite view knows (SPRITE_SIZES) is looked for once, at start-up;
one that isn't there is simply missing, and the Sprite view draws that thing in
its hitbox colour. A PNG of any size is scaled to its sprite's size.
"""

from pathlib import Path

import pygame

from mario.constants.view import SPRITE_FILE_EXTENSION, SPRITE_SIZES


class SpriteLibrary:
    def __init__(self, sprites_by_name: dict[str, pygame.Surface]):
        self._sprites_by_name = sprites_by_name

    @classmethod
    def load(cls, sprites_folder: Path) -> "SpriteLibrary":
        sprites_by_name = {}
        for name, size in SPRITE_SIZES.items():
            sprite_file = sprites_folder / f"{name}{SPRITE_FILE_EXTENSION}"
            if sprite_file.is_file():
                sprites_by_name[name] = pygame.transform.scale(_load_image(sprite_file), size)
        return cls(sprites_by_name)

    def sprite(self, name: str) -> pygame.Surface | None:
        """The sprite of that name, or None while its file is missing."""
        return self._sprites_by_name.get(name)


def _load_image(image_file: Path) -> pygame.Surface:
    """With its transparency; in the window's pixel format once there is a window, for fast drawing."""
    image = pygame.image.load(str(image_file))
    return image.convert_alpha() if pygame.display.get_surface() is not None else image
