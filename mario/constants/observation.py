"""The Observation (#6, #25): what an agent perceives each tick (spec section 7).

The user's algorithm depends on this layout, so it never changes once built:
156 grid cells, row by row from the top, each row left to right, then 4 state numbers.
"""

from mario.constants.level import TILE_SIZE_SUBPIXELS
from mario.constants.physics import MARIO_TERMINAL_FALL_SPEED, RUN_SPEED_CAP

# --- The grid: a 13 x 12 window of tiles around Mario -----------------------------------

# The window's columns: this many behind the tile column holding Mario's centre x,
# his own column, and this many ahead.
OBSERVATION_COLUMNS_BEHIND = 3
OBSERVATION_COLUMNS_AHEAD = 9
# The window's rows: from this screen row down to this one, both included.
OBSERVATION_TOP_ROW = 2
OBSERVATION_BOTTOM_ROW = 13

OBSERVATION_COLUMNS = OBSERVATION_COLUMNS_BEHIND + 1 + OBSERVATION_COLUMNS_AHEAD
OBSERVATION_ROWS = OBSERVATION_BOTTOM_ROW - OBSERVATION_TOP_ROW + 1
OBSERVATION_GRID_CELLS = OBSERVATION_ROWS * OBSERVATION_COLUMNS

# What a cell holds. A solid tile, and every cell outside the area, is solid; an
# enemy marks the cell holding its hitbox centre and wins over a solid tile there.
EMPTY_CELL = 0
SOLID_CELL = 1
ENEMY_CELL = -1

# --- Mario's state: four numbers after the grid ------------------------------------------

OBSERVATION_STATE_NUMBERS = 4
OBSERVATION_LENGTH = OBSERVATION_GRID_CELLS + OBSERVATION_STATE_NUMBERS

# Each state number is a quantity of the game (in sub-pixels) divided by its divisor:
# 1. horizontal speed (the whole part that moves him), ÷ the run cap (2.5 px/f)
OBSERVATION_X_SPEED_DIVISOR = RUN_SPEED_CAP
# 2. vertical speed, positive when falling, ÷ the terminal fall (4 px/f)
OBSERVATION_Y_SPEED_DIVISOR = MARIO_TERMINAL_FALL_SPEED
# 3. height: his feet below the band's top edge, ÷ the distance from that edge to the
#    ground's top (row 13), so 0 at the top and 1 standing on the ground
OBSERVATION_BAND_TOP_Y = OBSERVATION_TOP_ROW * TILE_SIZE_SUBPIXELS
OBSERVATION_HEIGHT_DIVISOR = OBSERVATION_BOTTOM_ROW * TILE_SIZE_SUBPIXELS - OBSERVATION_BAND_TOP_Y
# 4. on the ground: 0 or 1, kept as it is
OBSERVATION_ON_GROUND_DIVISOR = 1
OBSERVATION_STATE_DIVISORS = (OBSERVATION_X_SPEED_DIVISOR, OBSERVATION_Y_SPEED_DIVISOR,
                              OBSERVATION_HEIGHT_DIVISOR, OBSERVATION_ON_GROUND_DIVISOR)
