"""The flagpole: its touch, the flag, and the input-free slide and castle walk after it (#24).

Sourced from doppelganger's disassembly (docs/research/world-1-1-layout.md,
"Flagpole, castle walk and end-of-level points").
"""

from mario.constants.level import TILE_SIZE_PIXELS

# --- The touch (SideCheckLoop, HandleClimbing) ------------------------------------------

# Mario touches the pole with a side probe at his sprite y + 24 (on a climbable tile
# the upper probe is skipped for the lower one), at his box's left or right edge,
# and only where that probe is this many pixels or more into the pole's tile, up
# to the second value: the pole is thinner than its tile.
FLAGPOLE_TOUCH_PROBE_SPRITE_Y_PIXELS = 24
FLAGPOLE_TOUCH_MIN_X_IN_TILE_PIXELS = 6
FLAGPOLE_TOUCH_MAX_X_IN_TILE_PIXELS = 9

# --- The flag (FlagpoleObject) ---------------------------------------------------------------

# The flag hangs this far left of the pole's column, its top at this y.
FLAG_OFFSET_X_PIXELS = -8
FLAG_START_Y_PIXELS = 0x30
FLAG_SIZE_PIXELS = TILE_SIZE_PIXELS

# --- The slide (FlagpoleSlide, FlagpoleRoutine, ClimbingSub, PutPlayerOnVine) -----------------

# Mario holds the pole with his sprite this far from the pole's column, facing right.
FLAGPOLE_HOLD_SPRITE_OFFSET_X_PIXELS = -7
# Mario and the flag each slide down this many pixels a tick, plus the carry of an
# 8-bit fraction that gains this much a tick: 1 px on the first tick, then 2 px but
# one tick in 256.
FLAGPOLE_SLIDE_PIXELS_PER_TICK = 1
FLAGPOLE_SLIDE_FRACTION_PER_TICK = 0xFF
FLAGPOLE_SLIDE_FRACTION_BITS = 8
# Mario stops sliding once his sprite's top is this far down.
MARIO_SLIDE_STOP_SPRITE_Y_PIXELS = 0x9E
# The slide ends once the flag's top is this far down, or Mario's sprite's top this far.
FLAG_BOTTOM_Y_PIXELS = 0xAA
SLIDE_END_MARIO_SPRITE_Y_PIXELS = 0xA2

# --- Leaving the pole (PlayerEndLevel, ClimbingSub) ------------------------------------------

# Pressing right, he hops round to the other side of the pole and faces left, holds
# on for the climb-side timer, then moves right off it and lets go.
FLAGPOLE_HOP_PIXELS = 0x0E
FLAGPOLE_HOLD_AFTER_HOP_TICKS = 0x18
FLAGPOLE_LET_GO_PIXELS = 0x04

# --- The castle (RunStarFlagObj, AwardGameTimerPoints) ----------------------------------------

# Once the castle stopper stops him, the level timer counts down into the score this
# many units a tick.
TIME_UNITS_COUNTED_PER_TICK = 1
