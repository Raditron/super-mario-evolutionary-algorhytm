"""The window: the NES screen scaled up, drawn at 60 frames per second."""

from dataclasses import dataclass

import pygame

from mario.constants.level import SCREEN_HEIGHT_PIXELS, SCREEN_WIDTH_PIXELS
from mario.constants.view import FRAMES_PER_SECOND, QUIT_KEY, VIEW_TOGGLE_KEY, WINDOW_SCALE, WINDOW_TITLE


@dataclass(frozen=True)
class WindowEvents:
    """What happened to the window since it was last asked."""
    quit_requested: bool       # it was closed, or the quit key pressed
    view_toggle_pressed: bool


class Window:
    def __init__(self):
        pygame.init()
        self._display = pygame.display.set_mode(
            (SCREEN_WIDTH_PIXELS * WINDOW_SCALE, SCREEN_HEIGHT_PIXELS * WINDOW_SCALE))
        pygame.display.set_caption(WINDOW_TITLE)
        self.screen = pygame.Surface((SCREEN_WIDTH_PIXELS, SCREEN_HEIGHT_PIXELS))
        self._clock = pygame.time.Clock()
        self._quit_key = pygame.key.key_code(QUIT_KEY)
        self._view_toggle_key = pygame.key.key_code(VIEW_TOGGLE_KEY)

    def poll_events(self) -> WindowEvents:
        """Handle the window's events."""
        quit_requested = view_toggle_pressed = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_requested = True
            elif event.type == pygame.KEYDOWN and event.key == self._quit_key:
                quit_requested = True
            elif event.type == pygame.KEYDOWN and event.key == self._view_toggle_key:
                view_toggle_pressed = True
        return WindowEvents(quit_requested, view_toggle_pressed)

    def present(self) -> None:
        """Show the NES screen, then wait for the next frame."""
        pygame.transform.scale(self.screen, self._display.get_size(), self._display)
        pygame.display.flip()
        self._clock.tick(FRAMES_PER_SECOND)

    def close(self) -> None:
        pygame.quit()
