"""What each item is: what a block releases for Mario to collect."""

from enum import StrEnum


class ItemKind(StrEnum):
    SUPER_MUSHROOM = "super_mushroom"
    ONE_UP_MUSHROOM = "one_up_mushroom"
