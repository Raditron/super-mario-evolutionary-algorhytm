"""py -m mario play: a human plays with the keyboard.

Each life is its own Attempt in a freshly loaded level; when one ends, the
next starts. Lives, score and the checkpoint arrive with PlaySession.
"""

from mario.controller.controller_source import ControllerSource
from mario.level.static_level import StaticLevel
from mario.simulation.attempt import Attempt
from mario.snapshots.world_snapshot import WorldSnapshot
from mario.view.debug_renderer import DebugRenderer
from mario.view.keyboard_controller_source import KeyboardControllerSource
from mario.view.window import Window


class PlayMode:
    def __init__(self, level: StaticLevel, window: Window, renderer: DebugRenderer,
                 controller_source: ControllerSource):
        self._level = level
        self._window = window
        self._renderer = renderer
        self._controller_source = controller_source

    @classmethod
    def with_keyboard(cls) -> "PlayMode":
        window = Window()
        return cls(StaticLevel.load_world_1_1(), window, DebugRenderer(), KeyboardControllerSource())

    def run(self) -> None:
        attempt = Attempt(self._level)
        try:
            while not self._window.poll_quit_requested():
                attempt.step(self._controller_source.next_buttons())
                if attempt.is_over:
                    attempt = Attempt(self._level)
                self._renderer.draw(WorldSnapshot.of(attempt), self._window.screen)
                self._window.present()
        finally:
            self._window.close()
