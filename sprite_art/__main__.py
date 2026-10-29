"""py -m sprite_art: paints every drawing into assets/sprites/, overwriting the PNGs there."""

import pygame

from mario.__main__ import SPRITES_FOLDER
from mario.constants.view import SPRITE_FILE_EXTENSION
from sprite_art.drawings import ALL_DRAWINGS


def main() -> None:
    for drawing in ALL_DRAWINGS:
        sprite_file = SPRITES_FOLDER / f"{drawing.name}{SPRITE_FILE_EXTENSION}"
        pygame.image.save(drawing.painted(), str(sprite_file))
        print(f"painted {sprite_file.name}")


if __name__ == "__main__":
    main()
