"""One sprite, drawn as rows of palette keys, one key per pixel."""

from dataclasses import dataclass

import pygame

from sprite_art.palettes.shared import Colour


@dataclass(frozen=True)
class SpriteDrawing:
    """name is the sprite's file name without its extension, as SPRITE_SIZES names it;
    palette maps each key its rows use to a colour."""

    name: str
    palette: dict[str, Colour]
    rows: tuple[str, ...]

    def __post_init__(self):
        if len({len(row) for row in self.rows}) != 1:
            raise ValueError(f"{self.name}: every row must be as wide as the first")
        unknown_keys = set("".join(self.rows)) - self.palette.keys()
        if unknown_keys:
            raise ValueError(f"{self.name}: keys not in the palette: {sorted(unknown_keys)}")

    @property
    def size(self) -> tuple[int, int]:
        """(width, height) in px."""
        return len(self.rows[0]), len(self.rows)

    def painted(self) -> pygame.Surface:
        """The sprite as a surface with transparency, one pixel per key."""
        surface = pygame.Surface(self.size, pygame.SRCALPHA)
        for row_index, row in enumerate(self.rows):
            for column_index, key in enumerate(row):
                surface.set_at((column_index, row_index), self.palette[key])
        return surface
