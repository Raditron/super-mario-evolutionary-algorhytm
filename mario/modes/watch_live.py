"""Watch-live's window (spec sections 8 and 11): while the workers play a generation,
the main process shows it in the shared Viewer, at 60 frames per second.

Every frame it handles the window's events (F1 switches the view; closing the
window or Esc stops training), then draws what the followed-agent camera makes
of the snapshots the workers last published. Until the generation's first
snapshot arrives, the last frame stays.

The window opens only when the first generation starts to play, so a run that
fails to start never flashes one. It reads only snapshots, so all-ghost replay
(#30) drives it the same way, its workers replaying Controller logs; a replay
keeps showing its generation once played, until the viewer quits, as
best-agent replay holds its last frame.
"""

from collections.abc import Callable
from pathlib import Path

from mario.snapshots.snapshot_channel import SnapshotChannel
from mario.training.play_watcher import PlayWatcher, ViewerClosed
from mario.view.followed_agent_camera import FollowedAgentCamera
from mario.view.viewer import Viewer
from mario.view.window import Window


class WatchLive(PlayWatcher):
    def __init__(self, open_viewer: Callable[[], Viewer], keeps_showing_once_played: bool = False):
        """open_viewer: makes the Viewer, window and all, when the first generation starts.
        keeps_showing_once_played: a played generation stays shown until the viewer
        quits (a replay's), rather than training going on to the next."""
        self._open_viewer = open_viewer
        self._keeps_showing_once_played = keeps_showing_once_played
        self._viewer: Viewer | None = None

    @classmethod
    def in_a_window(cls, sprites_folder: Path, keeps_showing_once_played: bool = False) -> "WatchLive":
        """sprites_folder: where the Sprite view finds its PNGs (assets/sprites/)."""
        return cls(lambda: Viewer.with_both_views(Window(), sprites_folder), keeps_showing_once_played)

    def watch_until_played(self, generation: int, population_size: int, channel: SnapshotChannel,
                           is_played: Callable[[], bool]) -> None:
        if self._viewer is None:
            self._viewer = self._open_viewer()
        camera = FollowedAgentCamera()
        while not is_played():
            self._show_a_frame(camera, generation, population_size, channel)
        while self._keeps_showing_once_played:  # left only by ViewerClosed
            self._show_a_frame(camera, generation, population_size, channel)

    def _show_a_frame(self, camera: FollowedAgentCamera, generation: int, population_size: int,
                      channel: SnapshotChannel) -> None:
        """Raises ViewerClosed if the viewer has quit."""
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
