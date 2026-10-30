"""The warp pipe, the bonus room and the pipe transitions between them (#23).

Sourced from doppelganger's disassembly (docs/research/world-1-1-layout.md,
"The bonus room"). Positions are of the original's 16 x 32 player sprite.
"""

from mario.constants.level import SCREEN_WIDTH_PIXELS, TILE_SIZE_PIXELS
from mario.constants.physics import NES_X_SPEED_UNIT, SUBPIXELS_PER_PIXEL

# --- Entering (HandlePipeEntry, BlockBuffer_X_Adder) -----------------------------------------

# Down enters the warp pipe while both of Mario's foot probes, at these sprite x's,
# are on its top: the left one over its left column, the right one over its right.
LEFT_FOOT_PROBE_SPRITE_X_PIXELS = 0x03
RIGHT_FOOT_PROBE_SPRITE_X_PIXELS = 0x0C
# The width of a pipe: two columns.
PIPE_WIDTH_TILES = 2

# --- Sinking into the warp pipe (VerticalPipeEntry, ChangeAreaTimer = $30) --------------------

SINKING_TICKS = 0x30
SINKING_SUBPIXELS_PER_TICK = 1 * SUBPIXELS_PER_PIXEL

# --- Arriving in the bonus room (Entrance_GameTimerSetup, PlayerEntrance) -----------------------

# A vertical pipe's entry puts Mario's sprite here (PlayerStarting_X_Pos[1], and
# PlayerStarting_Y_Pos at the room header's entrance control, 1).
BONUS_ROOM_START_SPRITE_X_PIXELS = 0x18
BONUS_ROOM_START_SPRITE_Y_PIXELS = 0x20
# He falls with no button pressed until his sprite's top is this far down; control
# returns the tick after.
BONUS_ROOM_CONTROL_SPRITE_Y_PIXELS = 0x30

# --- Walking into the exit pipe (SideExitPipeEntry, EnterSidePipe, AreaChangeTimerData) -------

# The area changes this many ticks after Mario touches the mouth (the timer's value
# on page 0, where the room is).
EXIT_PIPE_WALK_TICKS = 0xA0
# He moves right at this speed, through the pipe's tiles, until his sprite's x is
# a multiple of this; then he stands.
EXIT_PIPE_WALK_SPEED = 0x08 * NES_X_SPEED_UNIT
EXIT_PIPE_WALK_STOP_SPRITE_X_MULTIPLE_PIXELS = TILE_SIZE_PIXELS

# --- Coming out of pipe 163 (InitializeArea, Entrance_GameTimerSetup, EntrMode2) ------------------

# The screen's left edge is at the return page; a page is a screen wide.
PAGE_WIDTH_PIXELS = SCREEN_WIDTH_PIXELS
# Mario's sprite starts this far into that page (PlayerStarting_X_Pos[2]), and
# this far down, below the screen (PlayerStarting_Y_Pos[8]).
RETURN_SPRITE_X_IN_PAGE_PIXELS = 0x38
RETURN_START_SPRITE_Y_PIXELS = 0xF0
# He rises this much a tick until his sprite's top is this far down, standing on the
# pipe's top; control returns the tick after.
RISING_SUBPIXELS_PER_TICK = 1 * SUBPIXELS_PER_PIXEL
RETURN_CONTROL_SPRITE_Y_PIXELS = 0x90
