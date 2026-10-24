"""A box in whole level pixels, for checks between Mario and enemies."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Hitbox:
    """Top-left corner at (x, y); right and bottom are one past the last pixel."""
    x: int
    y: int
    width: int
    height: int

    @property
    def right(self) -> int:
        return self.x + self.width

    @property
    def bottom(self) -> int:
        return self.y + self.height

    def overlaps(self, other: "Hitbox") -> bool:
        return (self.x < other.right and other.x < self.right
                and self.y < other.bottom and other.y < self.bottom)
