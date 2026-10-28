"""A stand-in for the Window, shared by the tests of the modes that draw."""

from dataclasses import dataclass, field

import pygame

from mario.constants.level import SCREEN_HEIGHT_PIXELS, SCREEN_WIDTH_PIXELS, TILE_SIZE_PIXELS
from mario.constants.view import CLOUD_COLOUR
from mario.view.window import WindowEvents

NOTHING_PRESSED = WindowEvents(quit_requested=False, view_toggle_pressed=False)
F1_PRESSED = WindowEvents(quit_requested=False, view_toggle_pressed=True)
CLOSED = WindowEvents(quit_requested=True, view_toggle_pressed=False)
# The middle of a cloud's tile on the opening screen (layer 2 of the grid).
CLOUD_PIXEL = (8 * TILE_SIZE_PIXELS + TILE_SIZE_PIXELS // 2, 3 * TILE_SIZE_PIXELS + TILE_SIZE_PIXELS // 2)


@dataclass
class ScriptedWindow:
    """Hands a mode the given window events, one frame each, then closes; keeps every frame shown."""
    events_by_frame: list[WindowEvents]
    screen: pygame.Surface = field(default_factory=lambda: pygame.Surface((SCREEN_WIDTH_PIXELS,
                                                                           SCREEN_HEIGHT_PIXELS)))
    frames_shown: list[pygame.Surface] = field(default_factory=list)
    is_closed: bool = False

    def poll_events(self) -> WindowEvents:
        return self.events_by_frame.pop(0) if self.events_by_frame else CLOSED

    def present(self) -> None:
        self.frames_shown.append(self.screen.copy())

    def close(self) -> None:
        self.is_closed = True


def shows_the_sprite_view(frame: pygame.Surface) -> bool:
    """Only the Sprite view draws the scenery, so a cloud on the opening screen tells the views apart."""
    return tuple(frame.get_at(CLOUD_PIXEL))[:3] == CLOUD_COLOUR
