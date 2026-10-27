"""Movement and physics constants of the original game (#2), per tick.

One tick is one NES frame; the game runs at 60 ticks per second.
Every position and speed is an integer in 1/4096 px on both axes, so each value
from docs/research/smb-physics-constants.md converts exactly: the original's
X speed unit (1/16 px/f) is 256 sub-pixels, its X acceleration unit
(1/4096 px/f^2) is 1, its Y speed unit (1 px/f) is 4096 and its Y sub-speed and
gravity unit (1/256 px/f, 1/256 px/f^2) is 16.
"""

TICKS_PER_SECOND = 60

# --- Fixed-point units -----------------------------------------------------------

SUBPIXEL_BITS = 12
SUBPIXELS_PER_PIXEL = 1 << SUBPIXEL_BITS
NES_X_SPEED_UNIT = SUBPIXELS_PER_PIXEL // 16
NES_X_ACCELERATION_UNIT = SUBPIXELS_PER_PIXEL // 4096
NES_Y_SPEED_UNIT = SUBPIXELS_PER_PIXEL
NES_Y_SUBSPEED_UNIT = SUBPIXELS_PER_PIXEL // 256
NES_GRAVITY_UNIT = NES_Y_SUBSPEED_UNIT
SUBPIXEL_FRACTION_MASK = SUBPIXELS_PER_PIXEL - 1             # the part of a position below 1 px

# The original keeps a whole speed byte and a fractional "move force" byte.
# Only the whole part moves an object; the fraction only carries into it.
X_SUBSPEED_MASK = NES_X_SPEED_UNIT - 1
Y_SUBSPEED_MASK = NES_Y_SPEED_UNIT - 1

# --- Mario on the ground (MaxLeftXSpdData / MaxRightXSpdData / FrictionData) -----

WALK_SPEED_CAP = 24 * NES_X_SPEED_UNIT                       # 1.5 px/f
RUN_SPEED_CAP = 40 * NES_X_SPEED_UNIT                        # 2.5 px/f
WATER_GROUND_SPEED_CAP = 16 * NES_X_SPEED_UNIT               # 1.0 px/f, not in 1-1
PIPE_INTRO_SPEED_CAP = 12 * NES_X_SPEED_UNIT                 # 0.75 px/f, not in 1-1

RUN_ACCELERATION = 0xE4 * NES_X_ACCELERATION_UNIT            # FrictionData[0]
WALK_ACCELERATION = 0x98 * NES_X_ACCELERATION_UNIT           # FrictionData[1]
FAST_DECELERATION = 0xD0 * NES_X_ACCELERATION_UNIT           # FrictionData[2]
# Acceleration doubles while Mario faces against his motion (a skid).
SKID_ACCELERATION_MULTIPLIER = 2

RUNNING_TIMER_TICKS = 10                  # run cap kept this long after B is released
RUNNING_SPEED_FLAG_SPEED = 28 * NES_X_SPEED_UNIT             # sets RunningSpeed
FAST_DECELERATION_SPEED = 33 * NES_X_SPEED_UNIT              # FrictionData[2] at or above this
SKID_TURNAROUND_SPEED = 11 * NES_X_SPEED_UNIT                # below this a skid turns Mario around

# --- Mario in the air --------------------------------------------------------------

AIR_RUN_CAP_SPEED = 25 * NES_X_SPEED_UNIT                    # at or above this, the 2.5 px/f cap

# --- Jumping (ProcJumping: JumpMForceData / FallMForceData / PlayerYSpdData) --------

# Takeoff speed bands: below each threshold uses that band's row.
SLOW_JUMP_SPEED_LIMIT = 16 * NES_X_SPEED_UNIT                # rows 0-1: below 1.0 px/f
MEDIUM_JUMP_SPEED_LIMIT = 25 * NES_X_SPEED_UNIT              # row 2: below 1.5625 px/f

SLOW_JUMP_SPEED = -4 * NES_Y_SPEED_UNIT
SLOW_JUMP_RISING_GRAVITY = 0x20 * NES_GRAVITY_UNIT
SLOW_JUMP_FALLING_GRAVITY = 0x70 * NES_GRAVITY_UNIT
MEDIUM_JUMP_SPEED = -4 * NES_Y_SPEED_UNIT
MEDIUM_JUMP_RISING_GRAVITY = 0x1E * NES_GRAVITY_UNIT
MEDIUM_JUMP_FALLING_GRAVITY = 0x60 * NES_GRAVITY_UNIT
FAST_JUMP_SPEED = -5 * NES_Y_SPEED_UNIT
FAST_JUMP_RISING_GRAVITY = 0x28 * NES_GRAVITY_UNIT
FAST_JUMP_FALLING_GRAVITY = 0x90 * NES_GRAVITY_UNIT

# Falling gravity at area entry, before any jump: walking off a ledge reuses it.
AREA_ENTRY_FALLING_GRAVITY = 0x28 * NES_GRAVITY_UNIT
# The rising gravity is kept on the first tick of a jump, until Mario has risen this far.
JUMP_HALT_RISE_PIXELS = 1                                    # DiffToHaltJump

# --- Falling (ImposeGravity) ----------------------------------------------------------

MARIO_TERMINAL_FALL_SPEED = 4 * NES_Y_SPEED_UNIT
# The fall speed is clamped only when its fraction is at least half a pixel,
# so a fall can overshoot the cap for a tick (≈ 4.5 px/f).
FALL_CAP_FRACTION_THRESHOLD = 0x80 * NES_Y_SUBSPEED_UNIT
HEAD_BUMP_SPEED = 1 * NES_Y_SPEED_UNIT                       # after hitting a hard or used block from below
BLOCK_BUMP_SPEED = 0 * NES_Y_SPEED_UNIT                      # after bumping a block (BumpBlock)

DEATH_JUMP_SPEED = -4 * NES_Y_SPEED_UNIT
DEATH_GRAVITY = 0x28 * NES_GRAVITY_UNIT

# --- Stomps (EnemyStomped) -----------------------------------------------------------------

STOMP_BOUNCE_SPEED = -4 * NES_Y_SPEED_UNIT                   # Goomba, Koopa
# Touching a Goomba or Koopa while moving down at least this fast is a stomp,
# wherever Mario's feet are (ChkForPlayerInjury: Player_Y_Speed positive, not 0).
STOMP_MIN_FALL_SPEED = 1 * NES_Y_SPEED_UNIT

# --- Enemies and items (section 5 of the research) ------------------------------------

GOOMBA_WALK_SPEED = 8 * NES_X_SPEED_UNIT                     # 0.5 px/f, starts moving left
KOOPA_WALK_SPEED = 8 * NES_X_SPEED_UNIT                      # 0.5 px/f
KICKED_SHELL_SPEED = 48 * NES_X_SPEED_UNIT                   # 3.0 px/f, away from Mario
AIRBORNE_SHELL_SLOWDOWN = 24 * NES_X_SPEED_UNIT              # taken off a shell's speed in the air
REVIVED_KOOPA_SPEED = 8 * NES_X_SPEED_UNIT
SHELL_REVIVAL_INTERVAL_TICKS = 0x10                          # interval ticks before a Koopa wakes
INTERVAL_TIMER_TICKS = 21                                    # ticks per interval tick
BUMPED_ENEMY_SPEED_X = 16 * NES_X_SPEED_UNIT                 # knocked from below a block
BUMPED_ENEMY_SPEED_Y = -3 * NES_Y_SPEED_UNIT
BUMPED_ENEMY_LIFT_PIXELS = 2                                 # ChkToStunEnemies raises it this much
# An enemy defeated by a bumped block (a Goomba; a Koopa is only stunned) jumps
# faster (KillEnemyAboveBlock), then falls through everything (MoveDefeatedEnemy).
BUMP_DEFEAT_SPEED_Y = -4 * NES_Y_SPEED_UNIT
MUSHROOM_SPEED = 16 * NES_X_SPEED_UNIT                       # 1.0 px/f, starts moving right
POWER_UP_EMERGE_PIXELS = 16                                  # rises out of its block this far
POWER_UP_EMERGE_TICKS_PER_PIXEL = 4
STARMAN_SPEED = 16 * NES_X_SPEED_UNIT
STARMAN_GRAVITY = 0x1C * NES_GRAVITY_UNIT
STARMAN_BOUNCE_SPEED = -3 * NES_Y_SPEED_UNIT
STARMAN_TERMINAL_FALL_SPEED = 3 * NES_Y_SPEED_UNIT
ENEMY_GRAVITY = 0x3D * NES_GRAVITY_UNIT                      # also mushrooms and defeated enemies
ENEMY_TERMINAL_FALL_SPEED = 3 * NES_Y_SPEED_UNIT

# A stomped Goomba lies squashed until its interval timer goes from $10 to $0E
# (ChkKillGoomba): 2 interval ticks. The original's interval clock is not reset
# at area start, so this is 22-42 ticks there; the replica always takes the longest.
STOMPED_GOOMBA_INTERVAL_TICKS = 2
STOMPED_GOOMBA_TICKS = STOMPED_GOOMBA_INTERVAL_TICKS * INTERVAL_TIMER_TICKS

# --- Blocks (PlayerHeadCollision, BumpBlock) ------------------------------------------------

# After a bump, Mario's head bumps no block for this long (BlockBounceTimer): it
# stops him as a hard block would.
BLOCK_BOUNCE_LOCKOUT_TICKS = 0x10
# A bumped block jumps up and falls back into place (BumpBlock, ImposeGravityBlock):
# about 8 px up and down in 13 ticks.
BLOCK_BOUNCE_SPEED = -2 * NES_Y_SPEED_UNIT
BLOCK_BOUNCE_GRAVITY = 0x50 * NES_GRAVITY_UNIT
BLOCK_BOUNCE_TERMINAL_FALL_SPEED = 8 * NES_Y_SPEED_UNIT      # MaxSpdBlockData

# The multi-coin brick gives a coin per hit until BrickCoinTimer, started at its
# first hit, runs out; the hit after that gives one more coin and uses it up. Like
# STOMPED_GOOMBA_TICKS, the replica always takes the longest the interval clock allows.
MULTI_COIN_BRICK_INTERVAL_TICKS = 0x0B
MULTI_COIN_BRICK_TICKS = MULTI_COIN_BRICK_INTERVAL_TICKS * INTERVAL_TIMER_TICKS

# --- The Mario-enemy check (PlayerEnemyCollision) ----------------------------------------

# The check runs only on every other tick (FrameCounter bit 0 clear): on ticks
# whose number is a multiple of this.
ENEMY_CHECK_TICK_INTERVAL = 2
