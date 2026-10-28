"""F1 switches between the Sprite view and the Debug view; play starts in the
Sprite view (spec sections 6 and 8)."""

from dataclasses import dataclass, field

import pygame
import pytest

from mario.constants.level import SCREEN_HEIGHT_PIXELS, SCREEN_WIDTH_PIXELS, TILE_SIZE_PIXELS
from mario.constants.view import CLOUD_COLOUR
from mario.level.background_scenery import BackgroundScenery
from mario.modes.play_mode import PlayMode
from mario.view.debug_renderer import DebugRenderer
from mario.view.hud import Hud
from mario.view.sprite_library import SpriteLibrary
from mario.view.sprite_renderer import SpriteRenderer
from mario.view.view_toggle import ViewToggle
from mario.view.window import Window, WindowEvents
from tests.game.helpers import HOLD_NOTHING

# The middle of a cloud's tile on the opening screen (layer 2 of the grid).
CLOUD_PIXEL = (8 * TILE_SIZE_PIXELS + TILE_SIZE_PIXELS // 2, 3 * TILE_SIZE_PIXELS + TILE_SIZE_PIXELS // 2)
NOTHING_PRESSED = WindowEvents(quit_requested=False, view_toggle_pressed=False)
F1_PRESSED = WindowEvents(quit_requested=False, view_toggle_pressed=True)
CLOSED = WindowEvents(quit_requested=True, view_toggle_pressed=False)


@dataclass
class ScriptedWindow:
    """Hands play mode the given window events, one frame each, then closes; keeps every frame shown."""
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


class HeldNothing:
    def next_buttons(self) -> int:
        return HOLD_NOTHING


@pytest.fixture
def fonts():
    pygame.font.init()
    yield
    pygame.font.quit()


def played(events_by_frame: list[WindowEvents], world_1_1, tmp_path) -> ScriptedWindow:
    """Play mode with an empty sprites folder, driven by the window events."""
    window = ScriptedWindow(events_by_frame)
    views = ViewToggle(SpriteRenderer(SpriteLibrary.load(tmp_path), BackgroundScenery.load_world_1_1()),
                       DebugRenderer())
    PlayMode(world_1_1, window, views, Hud(), HeldNothing()).run()
    return window


def shows_the_sprite_view(frame: pygame.Surface) -> bool:
    """Only the Sprite view draws the scenery."""
    return tuple(frame.get_at(CLOUD_PIXEL))[:3] == CLOUD_COLOUR


def test_play_starts_in_the_sprite_view_and_f1_switches_to_the_debug_view_and_back(fonts, world_1_1, tmp_path):
    window = played([NOTHING_PRESSED, F1_PRESSED, NOTHING_PRESSED, F1_PRESSED], world_1_1, tmp_path)
    assert [shows_the_sprite_view(frame) for frame in window.frames_shown] == [True, False, False, True]
    assert window.is_closed


@pytest.fixture
def window(monkeypatch):
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    window = Window()
    yield window
    window.close()


def test_the_window_reports_f1_as_a_view_toggle_and_escape_as_quitting(window):
    assert window.poll_events() == NOTHING_PRESSED
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F1))
    assert window.poll_events() == F1_PRESSED
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    assert window.poll_events().quit_requested
