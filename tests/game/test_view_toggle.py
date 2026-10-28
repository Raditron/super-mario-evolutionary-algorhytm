"""F1 switches between the Sprite view and the Debug view; play starts in the
Sprite view (spec sections 6 and 8)."""

import pygame
import pytest

from mario.modes.play_mode import PlayMode
from mario.view.viewer import Viewer
from mario.view.window import Window, WindowEvents
from tests.game.helpers import HOLD_NOTHING
from tests.game.scripted_window import F1_PRESSED, NOTHING_PRESSED, ScriptedWindow, shows_the_sprite_view


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
    PlayMode(world_1_1, Viewer.with_both_views(window, tmp_path), HeldNothing()).run()
    return window


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
