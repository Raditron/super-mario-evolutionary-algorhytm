"""Lines of small text on a dark background, for the Debug view's readouts."""

import pygame

from mario.constants.view import (
    DEBUG_FONT_SIZE,
    DEBUG_TEXT_BACKGROUND_COLOUR,
    DEBUG_TEXT_COLOUR,
    DEBUG_TEXT_LINE_PIXELS,
)


class DebugText:
    def __init__(self):
        self._font = pygame.font.Font(None, DEBUG_FONT_SIZE)

    def draw_lines(self, lines: list[str], top_left: tuple[int, int], screen: pygame.Surface) -> None:
        """One line under the other, from the top-left corner down."""
        left_x, top_y = top_left
        for line_number, line in enumerate(lines):
            rendered = self._font.render(line, False, DEBUG_TEXT_COLOUR, DEBUG_TEXT_BACKGROUND_COLOUR)
            screen.blit(rendered, (left_x, top_y + line_number * DEBUG_TEXT_LINE_PIXELS),
                        pygame.Rect(0, 0, rendered.get_width(), DEBUG_TEXT_LINE_PIXELS))
