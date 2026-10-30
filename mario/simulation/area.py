"""Where in the game Mario is: the level, or the bonus room its warp pipe leads to."""

from enum import StrEnum


class Area(StrEnum):
    LEVEL = "level"
    BONUS_ROOM = "bonus_room"
