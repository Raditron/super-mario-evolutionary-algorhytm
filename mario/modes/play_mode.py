"""py -m mario play: a human plays with the keyboard.

The PlaySession runs the lives, one Attempt each; this mode feeds it the
keyboard and shows it in the Viewer, the Sprite view until F1 switches to the
Debug view, with the HUD on top.
"""

from pathlib import Path

from mario.controller.controller_source import ControllerSource
from mario.level.static_level import StaticLevel
from mario.modes.play_session import PlaySession
from mario.view.keyboard_controller_source import KeyboardControllerSource
from mario.view.viewer import Viewer
from mario.view.window import Window


class PlayMode:
    def __init__(self, level: StaticLevel, viewer: Viewer, controller_source: ControllerSource):
        self._level = level
        self._viewer = viewer
        self._controller_source = controller_source

    @classmethod
    def with_keyboard(cls, sprites_folder: Path) -> "PlayMode":
        """sprites_folder: where the Sprite view finds its PNGs (assets/sprites/)."""
        viewer = Viewer.with_both_views(Window(), sprites_folder)
        return cls(StaticLevel.load_world_1_1(), viewer, KeyboardControllerSource())

    def run(self) -> None:
        session = PlaySession(self._level)
        try:
            while not self._viewer.handle_events():
                session.step(self._controller_source.next_buttons())
                self._viewer.show(session.snapshot())
        finally:
            self._viewer.close()
