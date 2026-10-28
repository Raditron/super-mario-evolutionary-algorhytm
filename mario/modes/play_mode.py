"""py -m mario play: a human plays with the keyboard.

The PlaySession runs the lives, one Attempt each; this mode feeds it the
keyboard and draws it in the view shown, the Sprite view until F1 switches to
the Debug view, with the HUD on top.
"""

from pathlib import Path

from mario.controller.controller_source import ControllerSource
from mario.level.background_scenery import BackgroundScenery
from mario.level.static_level import StaticLevel
from mario.modes.play_session import PlaySession
from mario.view.debug_renderer import DebugRenderer
from mario.view.hud import Hud
from mario.view.keyboard_controller_source import KeyboardControllerSource
from mario.view.sprite_library import SpriteLibrary
from mario.view.sprite_renderer import SpriteRenderer
from mario.view.view_toggle import ViewToggle
from mario.view.window import Window


class PlayMode:
    def __init__(self, level: StaticLevel, window: Window, views: ViewToggle, hud: Hud,
                 controller_source: ControllerSource):
        self._level = level
        self._window = window
        self._views = views
        self._hud = hud
        self._controller_source = controller_source

    @classmethod
    def with_keyboard(cls, sprites_folder: Path) -> "PlayMode":
        """sprites_folder: where the Sprite view finds its PNGs (assets/sprites/)."""
        window = Window()
        views = ViewToggle(SpriteRenderer(SpriteLibrary.load(sprites_folder), BackgroundScenery.load_world_1_1()),
                           DebugRenderer())
        return cls(StaticLevel.load_world_1_1(), window, views, Hud(), KeyboardControllerSource())

    def run(self) -> None:
        session = PlaySession(self._level)
        try:
            while True:
                window_events = self._window.poll_events()
                if window_events.quit_requested:
                    break
                if window_events.view_toggle_pressed:
                    self._views.toggle()
                session.step(self._controller_source.next_buttons())
                snapshot = session.snapshot()
                self._views.draw(snapshot, self._window.screen)
                self._hud.draw(snapshot.hud, self._window.screen)
                self._window.present()
        finally:
            self._window.close()
