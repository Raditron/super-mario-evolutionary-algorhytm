"""A box in whole level pixels, for checks between Mario and enemies."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Hitbox:
    """Top-left corner at (x_pixels, y_pixels); the right and bottom edges are one past the last pixel."""
    x_pixels: int
    y_pixels: int
    width_pixels: int
    height_pixels: int

    @property
    def right_x_pixels(self) -> int:
        return self.x_pixels + self.width_pixels

    @property
    def bottom_y_pixels(self) -> int:
        return self.y_pixels + self.height_pixels

    def overlaps(self, other: "Hitbox") -> bool:
        return (self.x_pixels < other.right_x_pixels and other.x_pixels < self.right_x_pixels
                and self.y_pixels < other.bottom_y_pixels and other.y_pixels < self.bottom_y_pixels)
