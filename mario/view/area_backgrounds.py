"""Each area's background colour, behind everything both views draw: the level's
sky, and the bonus room's black, as the original's underground areas are
(BackgroundColors by area type, the room's header setting no colour of its own)."""

from mario.constants.view import SKY_COLOUR, UNDERGROUND_COLOUR
from mario.snapshots.world_snapshot import Area

AREA_BACKGROUND_COLOURS = {
    Area.LEVEL: SKY_COLOUR,
    Area.BONUS_ROOM: UNDERGROUND_COLOUR,
}
