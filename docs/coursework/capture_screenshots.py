"""The report's screenshots, drawn off-screen by the game's own Viewer from a recorded run:
the best agent's replay in both views at one tick, and all-ghost replays of two generations.
Nothing in the game changes; this only stands in for the window.

py docs/coursework/capture_screenshots.py   (from the repo root, with the run in runs/)
"""

import os
import sys
import time

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")  # no window opens

from report_constants import (
    BEST_AGENT_GENERATION, BEST_AGENT_SHOT_TICK, FIGURES_FOLDER, GHOST_SHOTS, REPO_ROOT, SCREENSHOT_RUN,
    SCREENSHOT_SCALE,
)

sys.path.insert(0, str(REPO_ROOT))

import pygame  # noqa: E402

from mario.constants.level import SCREEN_HEIGHT_PIXELS, SCREEN_WIDTH_PIXELS  # noqa: E402
from mario.constants.view import SPRITES_FOLDER_PARTS  # noqa: E402
from mario.level.background_scenery import BackgroundScenery  # noqa: E402
from mario.level.static_level import StaticLevel  # noqa: E402
from mario.modes.all_ghost_replay_mode import AllGhostReplayMode  # noqa: E402
from mario.modes.replay_session import ReplaySession  # noqa: E402
from mario.modes.watch_live import WatchLive  # noqa: E402
from mario.recording.recorded_run import RecordedRun  # noqa: E402
from mario.view.debug_renderer import DebugRenderer  # noqa: E402
from mario.view.hud import Hud  # noqa: E402
from mario.view.sprite_library import SpriteLibrary  # noqa: E402
from mario.view.sprite_renderer import SpriteRenderer  # noqa: E402
from mario.view.view_toggle import ViewToggle  # noqa: E402
from mario.view.viewer import Viewer  # noqa: E402
from mario.view.window import WindowEvents  # noqa: E402

SPRITES_FOLDER = REPO_ROOT.joinpath(*SPRITES_FOLDER_PARTS)


class OffscreenWindow:
    """The Viewer's window, drawing to a surface only. It asks to quit once wants_to_quit says so,
    and hands every presented frame to on_present."""

    def __init__(self, wants_to_quit=lambda: False, on_present=lambda screen: None):
        pygame.init()
        pygame.display.set_mode((1, 1))
        self.screen = pygame.Surface((SCREEN_WIDTH_PIXELS, SCREEN_HEIGHT_PIXELS))
        self._wants_to_quit = wants_to_quit
        self._on_present = on_present

    def poll_events(self) -> WindowEvents:
        pygame.event.pump()
        return WindowEvents(quit_requested=self._wants_to_quit(), view_toggle_pressed=False)

    def present(self) -> None:
        self._on_present(self.screen)

    def close(self) -> None:
        pygame.quit()


def save_screen(screen: pygame.Surface, file_name: str) -> None:
    scaled = pygame.transform.scale(screen, (screen.get_width() * SCREENSHOT_SCALE,
                                             screen.get_height() * SCREENSHOT_SCALE))
    FIGURES_FOLDER.mkdir(exist_ok=True)
    pygame.image.save(scaled, str(FIGURES_FOLDER / file_name))


def viewer_with_views(window) -> tuple[Viewer, ViewToggle]:
    """The Viewer as Viewer.with_both_views builds it, with its ViewToggle kept so a shot can switch views."""
    sprites = SpriteLibrary.load(SPRITES_FOLDER)
    views = ViewToggle(SpriteRenderer(sprites, BackgroundScenery.load_world_1_1()), DebugRenderer())
    return Viewer(window, views, Hud(sprites)), views


def best_agent_in_both_views() -> None:
    recorded_run = RecordedRun(SCREENSHOT_RUN)
    best_agent = recorded_run.best_agent(BEST_AGENT_GENERATION)
    session = ReplaySession(recorded_run.controller_log(BEST_AGENT_GENERATION, best_agent.agent_index),
                            StaticLevel.load_world_1_1())
    window = OffscreenWindow()
    viewer, views = viewer_with_views(window)
    for _ in range(BEST_AGENT_SHOT_TICK):
        session.step()
    snapshot = session.snapshot()
    viewer.show(snapshot)
    save_screen(window.screen, "screenshot_sprite_view.png")
    views.toggle()
    viewer.show(snapshot)
    save_screen(window.screen, "screenshot_debug_view.png")
    viewer.close()


def all_ghosts(generation: int, seconds_in: float) -> None:
    """The generation's all-ghost replay, played through the real worker pool, shot seconds_in after it starts."""
    controller_logs = RecordedRun(SCREENSHOT_RUN).controller_logs(generation)
    shot = {"started_at": None, "taken": False}

    def on_present(screen: pygame.Surface) -> None:
        now = time.monotonic()
        if shot["started_at"] is None:
            shot["started_at"] = now
        if not shot["taken"] and now - shot["started_at"] >= seconds_in:
            save_screen(screen, f"screenshot_ghosts_generation_{generation}.png")
            shot["taken"] = True

    def open_viewer() -> Viewer:
        return viewer_with_views(OffscreenWindow(lambda: shot["taken"], on_present))[0]

    AllGhostReplayMode(generation, controller_logs, WatchLive(open_viewer, keeps_showing_once_played=True)).run()


if __name__ == "__main__":
    best_agent_in_both_views()
    for ghost_generation, ghost_seconds in GHOST_SHOTS:
        all_ghosts(ghost_generation, ghost_seconds)
