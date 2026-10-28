"""What the things moving in one Attempt see of it: its tiles, and where the screen is."""

from mario.simulation.attempt_tiles import AttemptTiles
from mario.simulation.scroll import Scroll


class Playfield:
    def __init__(self, tiles: AttemptTiles, scroll: Scroll):
        self.tiles = tiles
        self._scroll = scroll

    @property
    def screen_left_x_pixels(self) -> int:
        return self._scroll.left_x_pixels
