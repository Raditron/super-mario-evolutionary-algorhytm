"""The HUD: score, coins, world and time, laid out as the original's status bar.

The original prints its status bar on the NES's 8 x 8 px text grid, one
character per cell; this draws each character's glyph sprite (assets/sprites/glyph_*.png)
filling its cell from the top-left corner, or, while that glyph is missing, the
character in pygame's default font, centred in its cell. While a
generation is watched (watch-live, all-ghost replay), a line about it is added
under the level's ground line, in a smaller font: it is longer than the screen
has cells. The coin before the coin count is the coin sprite (assets/sprites/coin.png),
the size of its cell, or, while that is missing, an orange rectangle in it.
"""

import pygame

from mario.constants.level import WORLD_NAME
from mario.constants.view import (
    GENERATION_LINE,
    GENERATION_LINE_FONT_SIZE,
    GENERATION_LINE_TOP_LEFT,
    HUD_CELL_PIXELS,
    HUD_COIN_CROSS,
    HUD_COIN_CROSS_CELL,
    HUD_COIN_ICON_CELL,
    HUD_COIN_ICON_COLOUR,
    HUD_COIN_ICON_RECT_IN_CELL,
    HUD_COIN_SPRITE_NAME,
    HUD_COINS_CELL,
    HUD_COINS_DIGITS,
    HUD_FONT_SIZE,
    HUD_GLYPH_SPRITE_NAMES,
    HUD_LABELS,
    HUD_SCORE_CELL,
    HUD_SCORE_CELLS_WIDE,
    HUD_SCORE_MIN_DIGITS,
    HUD_TEXT_COLOUR,
    HUD_TIME_CELL,
    HUD_TIME_DIGITS,
    HUD_WORLD_CELL,
)
from mario.snapshots.world_snapshot import GenerationProgress, HudSnapshot
from mario.view.sprite_library import SpriteLibrary

Cell = tuple[int, int]


def generation_line(progress: GenerationProgress) -> str:
    return GENERATION_LINE.format(generation=progress.generation, alive=progress.alive,
                                  population_size=progress.population_size, reached_flag=progress.reached_flag)


class Hud:
    def __init__(self, sprites: SpriteLibrary):
        self._coin_sprite = sprites.sprite(HUD_COIN_SPRITE_NAME)
        self._glyph_sprites = {character: sprites.sprite(name) for character, name in HUD_GLYPH_SPRITE_NAMES.items()}
        self._font = pygame.font.Font(None, HUD_FONT_SIZE)
        self._generation_line_font = pygame.font.Font(None, GENERATION_LINE_FONT_SIZE)
        self._font_glyphs: dict[str, pygame.Surface] = {}

    def draw(self, hud: HudSnapshot, screen: pygame.Surface) -> None:
        for cell, label in HUD_LABELS.items():
            self._draw_text(label, cell, screen)
        self._draw_text(f"{hud.score:0{HUD_SCORE_MIN_DIGITS}d}".rjust(HUD_SCORE_CELLS_WIDE),
                        HUD_SCORE_CELL, screen)
        self._draw_coin_icon(screen)
        self._draw_text(HUD_COIN_CROSS, HUD_COIN_CROSS_CELL, screen)
        self._draw_text(f"{hud.coins:0{HUD_COINS_DIGITS}d}", HUD_COINS_CELL, screen)
        self._draw_text(WORLD_NAME, HUD_WORLD_CELL, screen)
        self._draw_text(f"{hud.time_left:0{HUD_TIME_DIGITS}d}", HUD_TIME_CELL, screen)

    def draw_generation_progress(self, progress: GenerationProgress, screen: pygame.Surface) -> None:
        screen.blit(self._generation_line_font.render(generation_line(progress), False, HUD_TEXT_COLOUR),
                    GENERATION_LINE_TOP_LEFT)

    def _draw_text(self, text: str, first_cell: Cell, screen: pygame.Surface) -> None:
        first_column, row = first_cell
        for offset, character in enumerate(text):
            cell_rect = pygame.Rect((first_column + offset) * HUD_CELL_PIXELS, row * HUD_CELL_PIXELS,
                                    HUD_CELL_PIXELS, HUD_CELL_PIXELS)
            self._draw_character(character, cell_rect, screen)

    def _draw_character(self, character: str, cell_rect: pygame.Rect, screen: pygame.Surface) -> None:
        """Its glyph sprite from the cell's top-left corner, else the font's glyph centred in the cell."""
        glyph_sprite = self._glyph_sprites.get(character)
        if glyph_sprite is not None:
            screen.blit(glyph_sprite, cell_rect.topleft)
            return
        font_glyph = self._font_glyph(character)
        screen.blit(font_glyph, font_glyph.get_rect(center=cell_rect.center))

    def _font_glyph(self, character: str) -> pygame.Surface:
        if character not in self._font_glyphs:
            self._font_glyphs[character] = self._font.render(character, False, HUD_TEXT_COLOUR)
        return self._font_glyphs[character]

    def _draw_coin_icon(self, screen: pygame.Surface) -> None:
        """The coin sprite in its cell, else an orange rectangle in it while the sprite is missing."""
        column, row = HUD_COIN_ICON_CELL
        cell_left_x, cell_top_y = column * HUD_CELL_PIXELS, row * HUD_CELL_PIXELS
        if self._coin_sprite is not None:
            screen.blit(self._coin_sprite, (cell_left_x, cell_top_y))
            return
        x_in_cell, y_in_cell, width, height = HUD_COIN_ICON_RECT_IN_CELL
        screen.fill(HUD_COIN_ICON_COLOUR, pygame.Rect(cell_left_x + x_in_cell, cell_top_y + y_in_cell, width, height))
