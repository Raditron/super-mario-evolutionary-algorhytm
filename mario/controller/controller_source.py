"""Where a mode's Controller buttons come from: the keyboard, a brain or a Controller log."""

from abc import ABC, abstractmethod


class ControllerSource(ABC):
    @abstractmethod
    def next_buttons(self) -> int:
        """The Controller bitmask for the next tick."""
