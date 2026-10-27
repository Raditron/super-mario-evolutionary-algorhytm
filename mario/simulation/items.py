"""One Attempt's items: the power-up a block has released.

There is at most one, as in the original's single power-up slot (SetupPowerUp
uses enemy slot 5): a new one replaces the old. It is removed by the bounds
that remove an enemy, on either side of the screen, or once it falls into a pit
(OffscreenBoundsCheck).
"""

from mario.constants.level import (
    ENEMY_FELL_OUT_SPRITE_Y_PIXELS,
    ENEMY_REMOVAL_RANGE_PIXELS,
    SCREEN_RIGHT_EDGE_OFFSET_PIXELS,
)
from mario.simulation.attempt_tiles import AttemptTiles
from mario.simulation.hitbox import Hitbox
from mario.simulation.mushroom import ItemKind, Mushroom


class Items:
    def __init__(self):
        self.power_up: Mushroom | None = None

    @property
    def active(self) -> list[Mushroom]:
        return [] if self.power_up is None else [self.power_up]

    def release(self, kind: ItemKind, block_column: int, block_row: int) -> None:
        self.power_up = Mushroom(kind, block_column, block_row)

    def step(self, tiles: AttemptTiles, screen_left_x_pixels: int) -> None:
        if self.power_up is None:
            return
        self.power_up.step(tiles)
        if _is_out_of_play(self.power_up, screen_left_x_pixels):
            self.power_up = None

    def take_touched(self, mario_hitbox: Hitbox) -> Mushroom | None:
        """The power-up Mario is touching, which he collects: it leaves play."""
        power_up = self.power_up
        if power_up is None or not power_up.is_touchable or not power_up.hitbox().overlaps(mario_hitbox):
            return None
        self.power_up = None
        return power_up


def _is_out_of_play(power_up: Mushroom, screen_left_x_pixels: int) -> bool:
    x_pixels = power_up.hitbox().x_pixels
    return (x_pixels < screen_left_x_pixels - ENEMY_REMOVAL_RANGE_PIXELS
            or x_pixels >= screen_left_x_pixels + SCREEN_RIGHT_EDGE_OFFSET_PIXELS + ENEMY_REMOVAL_RANGE_PIXELS
            or power_up.sprite_top_has_reached(ENEMY_FELL_OUT_SPRITE_Y_PIXELS))
