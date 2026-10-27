"""The followed agent's Observation in the Debug view: its 13 x 12 window drawn
translucent over the level, each cell tinted by its value, and its four state
numbers as one line of text."""

import pygame

from mario.constants.level import TILE_SIZE_PIXELS
from mario.constants.observation import EMPTY_CELL, ENEMY_CELL, OBSERVATION_TOP_ROW, SOLID_CELL
from mario.constants.view import (
    OBSERVATION_CELL_GAP_PIXELS,
    OBSERVATION_EMPTY_TINT,
    OBSERVATION_ENEMY_TINT,
    OBSERVATION_SOLID_TINT,
    OBSERVATION_STATE_DECIMALS,
    OBSERVATION_STATE_LABELS,
    OBSERVATION_STATE_TEXT_TOP_LEFT,
    OBSERVATION_TINT_OPACITY,
)
from mario.snapshots.world_snapshot import ObservationSnapshot
from mario.view.debug_text import DebugText

TINT_BY_CELL_VALUE = {
    EMPTY_CELL: (*OBSERVATION_EMPTY_TINT, OBSERVATION_TINT_OPACITY),
    SOLID_CELL: (*OBSERVATION_SOLID_TINT, OBSERVATION_TINT_OPACITY),
    ENEMY_CELL: (*OBSERVATION_ENEMY_TINT, OBSERVATION_TINT_OPACITY),
}
CELL_TINT_SIZE_PIXELS = TILE_SIZE_PIXELS - OBSERVATION_CELL_GAP_PIXELS


class ObservationOverlay:
    def __init__(self, debug_text: DebugText):
        self._debug_text = debug_text

    def draw(self, observation: ObservationSnapshot, screen_left_x_pixels: int, screen: pygame.Surface) -> None:
        self._draw_cells(observation, screen_left_x_pixels, screen)
        state_line = "  ".join(f"{label} {number:+.{OBSERVATION_STATE_DECIMALS}f}"
                               for label, number in zip(OBSERVATION_STATE_LABELS, observation.state_numbers))
        self._debug_text.draw_lines([state_line], OBSERVATION_STATE_TEXT_TOP_LEFT, screen)

    @staticmethod
    def _draw_cells(observation: ObservationSnapshot, screen_left_x_pixels: int, screen: pygame.Surface) -> None:
        rows, columns = len(observation.cells), len(observation.cells[0])
        tints = pygame.Surface((columns * TILE_SIZE_PIXELS, rows * TILE_SIZE_PIXELS), pygame.SRCALPHA)
        for row, row_values in enumerate(observation.cells):
            for column, value in enumerate(row_values):
                tints.fill(TINT_BY_CELL_VALUE[value], pygame.Rect(column * TILE_SIZE_PIXELS, row * TILE_SIZE_PIXELS,
                                                                  CELL_TINT_SIZE_PIXELS, CELL_TINT_SIZE_PIXELS))
        screen.blit(tints, (observation.first_column * TILE_SIZE_PIXELS - screen_left_x_pixels,
                            OBSERVATION_TOP_ROW * TILE_SIZE_PIXELS))
