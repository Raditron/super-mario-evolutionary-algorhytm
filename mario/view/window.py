"""The window: the NES screen scaled up, drawn at 60 frames per second."""

import pygame

from mario.constants.level import SCREEN_HEIGHT_PIXELS, SCREEN_WIDTH_PIXELS
from mario.constants.view import FRAMES_PER_SECOND, QUIT_KEY, WINDOW_SCALE, WINDOW_TITLE


class Window:
    def __init__(self):
        pygame.init()
        self._display = pygame.display.set_mode(
            (SCREEN_WIDTH_PIXELS * WINDOW_SCALE, SCREEN_HEIGHT_PIXELS * WINDOW_SCALE))
        pygame.display.set_caption(WINDOW_TITLE)
        self.screen = pygame.Surface((SCREEN_WIDTH_PIXELS, SCREEN_HEIGHT_PIXELS))
        self._clock = pygame.time.Clock()
        self._quit_key = pygame.key.key_code(QUIT_KEY)

    def poll_quit_requested(self) -> bool:
        """Handle the window's events; True once it is closed or the quit key is pressed."""
        quit_requested = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_requested = True
            elif event.type == pygame.KEYDOWN and event.key == self._quit_key:
                quit_requested = True
        return quit_requested

    def present(self) -> None:
        """Show the NES screen, then wait for the next frame."""
        pygame.transform.scale(self.screen, self._display.get_size(), self._display)
        pygame.display.flip()
        self._clock.tick(FRAMES_PER_SECOND)

    def close(self) -> None:
        pygame.quit()
