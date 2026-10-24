"""The level, the screen and scrolling (#3, #8)."""

from mario.constants.physics import SUBPIXEL_BITS

LEVEL_FILE_NAME = "world_1_1.toml"
LEVEL_WIDTH_TILES = 224
LEVEL_HEIGHT_TILES = 15

TILE_SIZE_PIXELS = 16
TILE_PIXEL_BITS = 4                                          # 16 px = 1 << 4
SUBPIXEL_TO_TILE_SHIFT = SUBPIXEL_BITS + TILE_PIXEL_BITS
TILE_SIZE_SUBPIXELS = 1 << SUBPIXEL_TO_TILE_SHIFT

# --- The NES screen ----------------------------------------------------------------

SCREEN_WIDTH_PIXELS = 256
SCREEN_HEIGHT_PIXELS = 240

# --- Scroll (ScrollHandler) ----------------------------------------------------------

# The screen starts to follow Mario once his sprite is this far from its left
# edge, and follows at his full speed from the second distance on.
SCROLL_START_SCREEN_X_PIXELS = 80
SCROLL_FULL_SPEED_SCREEN_X_PIXELS = 112
# Between the two, the screen scrolls this much less than Mario moved, but at least the minimum.
SLOW_SCROLL_LAG_PIXELS = 1
SLOW_SCROLL_MIN_PIXELS = 1
# The scroll stops with the screen's left edge at this column, so the flagpole
# and the castle stay in view (#3, #8).
SCROLL_STOP_COLUMN = 192
SCROLL_STOP_LEFT_X_PIXELS = SCROLL_STOP_COLUMN * TILE_SIZE_PIXELS
# Mario's sprite is held between the screen's left edge and this far from its
# right edge (KeepOnscr, X_SubtracterData).
SCREEN_RIGHT_EDGE_MARGIN_PIXELS = 16

# --- Mario's start and size (PlayerStarting_X_Pos / _Y_Pos, BlockBuffer adders) -------

# The original's player object is a 16 x 32 sprite; small Mario's body is its lower part.
MARIO_START_SPRITE_X_PIXELS = 0x28
MARIO_START_SPRITE_Y_PIXELS = 0xB0
# Small Mario's hitbox: from his side probes (sprite x + 2 and + 13), his head
# probe (sprite y + 18) and his feet, which rest at sprite y + 32.
SMALL_MARIO_HITBOX_OFFSET_X_PIXELS = 2
SMALL_MARIO_HITBOX_OFFSET_Y_PIXELS = 18
SMALL_MARIO_HITBOX_WIDTH_PIXELS = 12
SMALL_MARIO_HITBOX_HEIGHT_PIXELS = 14

# Mario has fallen into a pit once his sprite's top is this far down (Player_Y_HighPos = 2).
PIT_DEATH_SPRITE_Y_PIXELS = 256

# --- The level timer (header timer setting, RunGameTimer) ------------------------------

LEVEL_TIMER_START_UNITS = 400
LEVEL_TIMER_TICKS_PER_UNIT = 24                              # GameTimerCtrlTimer reload, $18

# --- The checkpoint (HalfwayPageNybbles) ---------------------------------------------------

# A human player who dies once the screen's left edge has reached this column
# starts the next life with the screen's left edge there.
CHECKPOINT_COLUMN = 80                                       # page 5
CHECKPOINT_LEFT_X_PIXELS = CHECKPOINT_COLUMN * TILE_SIZE_PIXELS

WORLD_NAME = "1-1"

# --- Enemy spawn positions (#3, #8) -------------------------------------------------------

# A Goomba pair sits at 16 * (data column - 3) and 16 * (data column - 1.5) px.
GOOMBA_PAIR_FIRST_OFFSET_PIXELS = -3 * TILE_SIZE_PIXELS
GOOMBA_PAIR_SECOND_OFFSET_PIXELS = -3 * TILE_SIZE_PIXELS // 2

# --- Enemy activation and removal (CheckRightBounds, OffscreenBoundsCheck, EnemyGfxHandler) ---

# An enemy activates once its x (a Goomba pair: its data column) is at most this
# far past the screen's right edge. One already left of the right edge when its
# turn comes in the list is skipped for good.
ENEMY_ACTIVATION_RANGE_PIXELS = 48
# An enemy is removed once its x is more than this far left of the screen's left edge.
ENEMY_REMOVAL_RANGE_PIXELS = 72
# An enemy that falls into a pit is removed once its sprite's top is this far down
# (Enemy_Y_HighPos = 2).
ENEMY_FELL_OUT_SPRITE_Y_PIXELS = 256
# An enemy spawns this far above the tile it rests on and drops onto it: the
# original sets its sprite y to 16 * row, and it lands at 16 * row + 8.
ENEMY_SPAWN_DROP_PIXELS = 8

# --- Goomba size (BlockBuffer_X_Adder / _Y_Adder for enemies) -------------------------------

# The original's enemy sprite is 16 x 24 px with the Goomba in its lower 16 rows.
# Its side probes (sprite x + 0 and + 16) and foot probe (sprite y + 24) give one
# 16 x 16 box at sprite offset (0, 8).
GOOMBA_HITBOX_WIDTH_PIXELS = 16
GOOMBA_HITBOX_HEIGHT_PIXELS = 16
GOOMBA_HITBOX_OFFSET_Y_PIXELS = 8
