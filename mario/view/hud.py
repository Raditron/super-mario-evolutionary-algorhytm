"""The HUD: score, coins, world and time, laid out as the original's status bar.

The original prints its status bar on the NES's 8 x 8 px text grid, one
character per cell; this draws each character centred in its cell. While a
generation is watched (watch-live, all-ghost replay), a line about it is added
under the level's ground line, in a smaller font: it is longer than the screen
has cells.
"""

import pygame

from mario.constants.level import WORLD_NAME
from mario.constants.view import (
    GENERATION_LINE_FONT_SIZE,
    GENERATION_LINE_TOP_LEFT,
    HUD_CELL_PIXELS,
    HUD_COIN_CROSS,
    HUD_COIN_CROSS_CELL,
    HUD_COIN_ICON_CELL,
    HUD_COIN_ICON_COLOUR,
    HUD_COIN_ICON_RECT_IN_CELL,
    HUD_COINS_CELL,
    HUD_COINS_DIGITS,
    HUD_FONT_SIZE,
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

Cell = tuple[int, int]
GENERATION_LINE = "generation {generation} · alive {alive} / {population_size} · reached flag {reached_flag}"


def generation_line(progress: GenerationProgress) -> str:
    return GENERATION_LINE.format(generation=progress.generation, alive=progress.alive,
                                  population_size=progress.population_size, reached_flag=progress.reached_flag)


class Hud:
    def __init__(self):
        self._font = pygame.font.Font(None, HUD_FONT_SIZE)
        self._generation_line_font = pygame.font.Font(None, GENERATION_LINE_FONT_SIZE)
        self._glyphs: dict[str, pygame.Surface] = {}

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
            glyph = self._glyph(character)
            cell_rect = pygame.Rect((first_column + offset) * HUD_CELL_PIXELS, row * HUD_CELL_PIXELS,
                                    HUD_CELL_PIXELS, HUD_CELL_PIXELS)
            screen.blit(glyph, glyph.get_rect(center=cell_rect.center))

    def _glyph(self, character: str) -> pygame.Surface:
        if character not in self._glyphs:
            self._glyphs[character] = self._font.render(character, False, HUD_TEXT_COLOUR)
        return self._glyphs[character]

    @staticmethod
    def _draw_coin_icon(screen: pygame.Surface) -> None:
        column, row = HUD_COIN_ICON_CELL
        x_in_cell, y_in_cell, width, height = HUD_COIN_ICON_RECT_IN_CELL
        screen.fill(HUD_COIN_ICON_COLOUR, pygame.Rect(column * HUD_CELL_PIXELS + x_in_cell,
                                                      row * HUD_CELL_PIXELS + y_in_cell, width, height))
