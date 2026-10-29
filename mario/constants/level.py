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
# Big Mario's probes are the same but for his head, at sprite y + 4
# (BlockBufferAdderData offset $00): a 12 x 28 box at sprite offset (2, 4). Big
# Mario crouching uses small Mario's probes (offset $0E), so his box is small Mario's.
BIG_MARIO_HITBOX_OFFSET_Y_PIXELS = 4
BIG_MARIO_HITBOX_HEIGHT_PIXELS = 28
# The intermediate frame of the grow animation is a 24 px tall sprite (its top row
# of tiles is blank, PlayerGraphicsTable). Nothing collides while it shows, so it
# is only drawn: as a box midway between the small and big ones.
INTERMEDIATE_MARIO_HITBOX_OFFSET_Y_PIXELS = 11
INTERMEDIATE_MARIO_HITBOX_HEIGHT_PIXELS = 21
# His box's edges keep him out of solid tiles, but growing or standing up can put
# it inside one. Then the original's own probes act (PlayerBGCollision): his head
# probe, over his centre at his box's top, hits a tile it is at least this far
# into (HeadChk: low nybble >= 4), and his side probes, at his box's left and
# right edges, at these sprite y's, push him out (BlockBuffer_Y_Adder: big
# Mario's at + 8 and + 24, small or crouching Mario's both at + 24).
HEAD_PROBE_MIN_DEPTH_PIXELS = 4
BIG_MARIO_SIDE_PROBE_SPRITE_Y_PIXELS = (8, 24)
SMALL_MARIO_SIDE_PROBE_SPRITE_Y_PIXELS = (24,)

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
# A fireball skips an enemy that is off the screen (EnemyOffscrBitsMasked, its
# offscreen bits masked by GetEnemyBoundBox): one whose x is this far or further
# left of the screen's left edge, or this far or further right of it, past its
# right edge.
ENEMY_OFF_SCREEN_LEFT_PIXELS = 8
ENEMY_OFF_SCREEN_RIGHT_X_PIXELS = SCREEN_WIDTH_PIXELS

# --- Goomba and Koopa size (BlockBuffer_X_Adder / _Y_Adder for enemies) ---------------------

# The original's enemy sprite is 16 x 24 px with the Goomba in its lower 16 rows.
# Its side probes (sprite x + 0 and + 16) and foot probe (sprite y + 24) give one
# 16 x 16 box at sprite offset (0, 8).
GOOMBA_HITBOX_WIDTH_PIXELS = 16
GOOMBA_HITBOX_HEIGHT_PIXELS = 16
GOOMBA_HITBOX_OFFSET_Y_PIXELS = 8
# The green Koopa is the same enemy object, drawn 8 px taller (EnemyGraphicsTable).
# Its probes are every enemy's, whatever its kind (BlockBufferChk_Enemy: ChkUnderEnemy
# at (8, 24), DoEnemySideCheck at (0, 20) and (16, 20)), so the same box; its shell,
# which nothing re-probes or resizes, keeps it.
KOOPA_HITBOX_WIDTH_PIXELS = GOOMBA_HITBOX_WIDTH_PIXELS
KOOPA_HITBOX_HEIGHT_PIXELS = GOOMBA_HITBOX_HEIGHT_PIXELS
KOOPA_HITBOX_OFFSET_Y_PIXELS = GOOMBA_HITBOX_OFFSET_Y_PIXELS

# --- Fireball size, tile probe and removal (FireballObjCore, BlockBufferChk_FBall,
# BoundBoxCtrlData, GetFireballOffscreenBits) -------------------------------------------------

# A fireball is an 8 x 8 box (bounding box control $07). It starts at Mario's
# sprite x + 4 and his sprite y.
FIREBALL_SIZE_PIXELS = 8
FIREBALL_START_OFFSET_X_PIXELS = 4
# Its one tile probe is just under its middle (block buffer adder $1A: (4, 8)). On
# a bounce its y is snapped down to a multiple of this (and #$F8).
FIREBALL_PROBE_X_PIXELS = 4
FIREBALL_PROBE_Y_PIXELS = 8
FIREBALL_BOUNCE_SNAP_PIXELS = 8
# It is removed once its x is at or left of the screen's left edge, at or past
# this far right of it, or once its y is at or below this (its offscreen bits).
FIREBALL_REMOVAL_SCREEN_RIGHT_X_PIXELS = 248
FIREBALL_FELL_OUT_Y_PIXELS = 240

# --- Item size and removal (SetupPowerUp, EnemyToBGCollisionDet, OffscreenBoundsCheck) ----

# The original's power-up (every item) is an enemy object (slot 5) and collides with
# tiles through the same probes, so its box is a Goomba's: 16 x 16 at sprite offset (0, 8).
# It appears with that box exactly over the block that released it.
ITEM_HITBOX_WIDTH_PIXELS = 16
ITEM_HITBOX_HEIGHT_PIXELS = 16
ITEM_HITBOX_OFFSET_Y_PIXELS = 8
# The same bounds remove it as an enemy, on both sides: once its x is more than
# ENEMY_REMOVAL_RANGE_PIXELS left of the screen's left edge, or that far right of
# the screen's right edge (ScreenRight_X_Pos, the screen's last pixel column).
SCREEN_RIGHT_EDGE_OFFSET_PIXELS = SCREEN_WIDTH_PIXELS - 1

# --- The Starman's tile probes (EnemyJump, ChkUnderEnemy, DoEnemySideCheck) and an
# enemy's landing (EnemyLanding) ------------------------------------------------------------

# No tile stops the Starman's box: only its probes act (EnemyJump), every enemy's.
# Its foot probe is at sprite (8, 24), just under its box (ChkUnderEnemy); its side
# probe, on the side it moves to only, at sprite (0, 20) moving left and (16, 20)
# moving right (DoEnemySideCheck). It has no head probe.
STARMAN_FOOT_PROBE_X_PIXELS = 8
STARMAN_FOOT_PROBE_Y_PIXELS = 24
STARMAN_LEFT_PROBE_X_PIXELS = 0
STARMAN_RIGHT_PROBE_X_PIXELS = 16
STARMAN_SIDE_PROBE_Y_PIXELS = 20
# Landing, an enemy's sprite y is snapped to (y & $F0) + 8 (EnemyLanding, which
# EnemyJump runs once the Starman's foot probe finds a tile): this far into the
# 16 px tile row its sprite's top is in, which stands its box on the tile under it.
ENEMY_LANDING_SPRITE_Y_IN_ROW_PIXELS = 8
