"""py -m mario play: a human plays with the keyboard.

The PlaySession runs the lives, one Attempt each; this mode feeds it the
keyboard and draws it, with the HUD on top.
"""

from mario.controller.controller_source import ControllerSource
from mario.level.static_level import StaticLevel
from mario.modes.play_session import PlaySession
from mario.view.debug_renderer import DebugRenderer
from mario.view.hud import Hud
from mario.view.keyboard_controller_source import KeyboardControllerSource
from mario.view.window import Window


class PlayMode:
    def __init__(self, level: StaticLevel, window: Window, renderer: DebugRenderer, hud: Hud,
                 controller_source: ControllerSource):
        self._level = level
        self._window = window
        self._renderer = renderer
        self._hud = hud
        self._controller_source = controller_source

    @classmethod
    def with_keyboard(cls) -> "PlayMode":
        window = Window()
        return cls(StaticLevel.load_world_1_1(), window, DebugRenderer(), Hud(), KeyboardControllerSource())

    def run(self) -> None:
        session = PlaySession(self._level)
        try:
            while not self._window.poll_quit_requested():
                session.step(self._controller_source.next_buttons())
                snapshot = session.snapshot()
                self._renderer.draw(snapshot, self._window.screen)
                self._hud.draw(snapshot.hud, self._window.screen)
                self._window.present()
        finally:
            self._window.close()
