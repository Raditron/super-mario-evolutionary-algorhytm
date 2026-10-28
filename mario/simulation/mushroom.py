"""The mushrooms, the Super Mushroom and the 1-UP mushroom: items that walk.

Once out of its block, a mushroom sets off right at 1 px/f and walks as an
enemy does: it turns at walls and falls off ledges (MoveNormalEnemy).
"""

from mario.constants.physics import BUMPED_ENEMY_SPEED_Y, MUSHROOM_SPEED
from mario.simulation.attempt_result import GameEventKind
from mario.simulation.attempt_tiles import AttemptTiles
from mario.simulation.item import Item
from mario.simulation.item_kind import ItemKind
from mario.simulation.walking_body import WalkingBody


class Mushroom(Item, WalkingBody):
    def step(self, tiles: AttemptTiles) -> None:
        if not self.is_emerging:
            self.walk(tiles)
            return
        super().step(tiles)
        if not self.is_emerging:
            self._set_off()

    def hop_away_from(self, mario_x: int) -> None:
        """The block under it was bumped from below: it jumps away from Mario as an
        enemy object does. With nothing under it now, it starts to fall the tick after."""
        self.jump_away_from(mario_x, BUMPED_ENEMY_SPEED_Y)
        self.is_falling = False

    def _set_off(self) -> None:
        self.is_falling = False
        self.velocity_x = MUSHROOM_SPEED


class SuperMushroom(Mushroom):
    kind = ItemKind.SUPER_MUSHROOM
    collected_event_kind = GameEventKind.COLLECTED_MUSHROOM


class OneUpMushroom(Mushroom):
    kind = ItemKind.ONE_UP_MUSHROOM
    collected_event_kind = GameEventKind.COLLECTED_ONE_UP
