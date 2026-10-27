"""The fire flower: an item that, once out of its block, stays where it is.

The original runs neither movement nor a background check for it
(PowerUpObjHandler skips both for power-up type 1), so nothing moves it, not
even a bumped block under it.
"""

from mario.simulation.attempt_result import GameEventKind
from mario.simulation.item import Item
from mario.simulation.item_kind import ItemKind


class FireFlower(Item):
    kind = ItemKind.FIRE_FLOWER
    collected_event_kind = GameEventKind.COLLECTED_FIRE_FLOWER
