"""Watch-live's main-process side, as the worker pool sees it (spec section 11).

While the workers play a watched generation, writing their snapshots into the
channel, the pool hands the main process to its PlayWatcher, which shows them
until the generation has been played. The window that does it lives outside
training (modes/ and view/), so training never loads pygame.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable

from mario.snapshots.snapshot_channel import SnapshotChannel


class ViewerClosed(Exception):
    """The person watching closed the window: training stops at once, and the
    generation being played is never recorded, so the run folder keeps only
    complete generations."""


class PlayWatcher(ABC):
    @abstractmethod
    def watch_until_played(self, generation: int, population_size: int, channel: SnapshotChannel,
                           is_played: Callable[[], bool]) -> None:
        """Show the generation from the channel's snapshots until is_played() is true.

        Raises ViewerClosed if the window is closed first."""
