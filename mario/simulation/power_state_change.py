"""Mario's power state, and one change of it: growing, shrinking or catching fire
(the original's SetPRout and the player routines it starts: PlayerChangeSize,
PlayerInjuryBlink, PlayerFireFlower).

The whole game stands still while a change runs. Growing and shrinking change
his size part-way in, and his power state with it (SizeChange); catching fire
leaves his size alone.
"""

from enum import StrEnum

from mario.constants.size_change import CATCH_FIRE_TICKS, GROW_TICKS, SHRINK_TICKS
from mario.simulation.size_change import MarioBody, SizeChange


class PowerState(StrEnum):
    """The original's PlayerStatus."""
    SMALL = "small"
    BIG = "big"
    FIERY = "fiery"


class PowerStateChange:
    def __init__(self, ticks: int, power_state_after: PowerState, size_change: SizeChange | None = None):
        self._ticks = ticks
        self.power_state_after = power_state_after
        self._size_change = size_change
        self._ticks_elapsed = 0

    @classmethod
    def growing(cls) -> "PowerStateChange":
        return cls(GROW_TICKS, PowerState.BIG, SizeChange.growing())

    @classmethod
    def shrinking(cls) -> "PowerStateChange":
        return cls(SHRINK_TICKS, PowerState.SMALL, SizeChange.shrinking())

    @classmethod
    def catching_fire(cls) -> "PowerStateChange":
        """He is fiery from the touch on (UpToFiery); only the freeze is left."""
        return cls(CATCH_FIRE_TICKS, PowerState.FIERY)

    @property
    def is_over(self) -> bool:
        return self._ticks_elapsed >= self._ticks

    @property
    def has_reached_power_state_after(self) -> bool:
        """Whether he has his new power state: with a size change, from its flip on (PlayerSize)."""
        return self._size_change is None or self._size_change.has_flipped

    @property
    def shown_body(self) -> MarioBody | None:
        """The body the size change shows now; None if his size doesn't change."""
        return None if self._size_change is None else self._size_change.shown_body

    def step(self) -> None:
        self._ticks_elapsed += 1
        if self._size_change is not None:
            self._size_change.step()
