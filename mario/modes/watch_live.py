"""Watch-live's window (spec sections 8 and 11): while the workers play a generation,
the main process shows it in the shared Viewer, at 60 frames per second.

Every frame it handles the window's events (F1 switches the view; closing the
window or Esc stops training), then draws what the followed-agent camera makes
of the snapshots the workers last published. Until the generation's first
snapshot arrives, the last frame stays.

The window opens only when the first generation starts to play, so a run that
fails to start never flashes one. It reads only snapshots, so all-ghost replay
(#30) can drive it the same way, its workers replaying Controller logs.
"""

from collections.abc import Callable
from pathlib import Path

from mario.snapshots.snapshot_channel import SnapshotChannel
from mario.training.play_watcher import PlayWatcher, ViewerClosed
from mario.view.followed_agent_camera import FollowedAgentCamera
from mario.view.viewer import Viewer
from mario.view.window import Window


class WatchLive(PlayWatcher):
    def __init__(self, open_viewer: Callable[[], Viewer]):
        """open_viewer: makes the Viewer, window and all, when the first generation starts."""
        self._open_viewer = open_viewer
        self._viewer: Viewer | None = None

    @classmethod
    def in_a_window(cls, sprites_folder: Path) -> "WatchLive":
        """sprites_folder: where the Sprite view finds its PNGs (assets/sprites/)."""
        return cls(lambda: Viewer.with_both_views(Window(), sprites_folder))

    def watch_until_played(self, generation: int, population_size: int, channel: SnapshotChannel,
                           is_played: Callable[[], bool]) -> None:
        if self._viewer is None:
            self._viewer = self._open_viewer()
        camera = FollowedAgentCamera()
        while not is_played():
            if self._viewer.handle_events():
                raise ViewerClosed
            snapshot = camera.snapshot(generation, population_size, channel.read_all())
            if snapshot is None:
                self._viewer.show_again()
            else:
                self._viewer.show(snapshot)

    def close(self) -> None:
        if self._viewer is not None:
            self._viewer.close()
