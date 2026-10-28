"""What every mode that draws shares (spec section 8): the window, the two views and
the HUD. F1 toggles between the Sprite view and the Debug view, and Esc or closing
the window quits, in every mode. It reads only WorldSnapshots.
"""

from pathlib import Path
from typing import Protocol

import pygame

from mario.level.background_scenery import BackgroundScenery
from mario.snapshots.world_snapshot import WorldSnapshot
from mario.view.debug_renderer import DebugRenderer
from mario.view.hud import Hud
from mario.view.sprite_library import SpriteLibrary
from mario.view.sprite_renderer import SpriteRenderer
from mario.view.view_toggle import ViewToggle
from mario.view.window import WindowEvents


class ViewerWindow(Protocol):
    """The Window, as the viewer uses it."""
    screen: pygame.Surface

    def poll_events(self) -> WindowEvents: ...
    def present(self) -> None: ...
    def close(self) -> None: ...


class Viewer:
    def __init__(self, window: ViewerWindow, views: ViewToggle, hud: Hud):
        self._window = window
        self._views = views
        self._hud = hud

    @classmethod
    def with_both_views(cls, window: ViewerWindow, sprites_folder: Path) -> "Viewer":
        """The Sprite view first, reading its PNGs from sprites_folder (assets/sprites/), then the Debug view."""
        views = ViewToggle(SpriteRenderer(SpriteLibrary.load(sprites_folder), BackgroundScenery.load_world_1_1()),
                           DebugRenderer())
        return cls(window, views, Hud())

    def handle_events(self) -> bool:
        """Handle the window's events since the last frame: F1 toggles the view.
        Returns whether the viewer asked to quit."""
        window_events = self._window.poll_events()
        if window_events.view_toggle_pressed:
            self._views.toggle()
        return window_events.quit_requested

    def show(self, snapshot: WorldSnapshot) -> None:
        """Draw the snapshot in the view shown, with the HUD on top, then wait for the next frame."""
        self._views.draw(snapshot, self._window.screen)
        self._hud.draw(snapshot.hud, self._window.screen)
        self._window.present()

    def close(self) -> None:
        self._window.close()
