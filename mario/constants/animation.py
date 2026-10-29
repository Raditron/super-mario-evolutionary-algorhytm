"""Which animation frame Mario and the enemies show (#57): the original's
ProcessPlayerAction, AnimationControl, GetPlayerAnimSpeed and CheckForSecondFrame
(docs/research/smb-physics-constants.md)."""

from mario.constants.physics import NES_X_SPEED_UNIT

# --- Mario ---------------------------------------------------------------------------------

# His walk is three walking frames in a loop, numbered 1 to 3 as their sprites are
# (PlayerAnimCtrl 0 to 2).
FIRST_WALK_FRAME = 1
WALK_FRAME_COUNT = 3
# Each walking frame shows for this many ticks (PlayerAnimTmrData), chosen on the
# ground from his speed (Player_XSpeedAbsolute): at or above RUN_ANIMATION_SPEED,
# at or above WALK_ANIMATION_SPEED, or slower. In the air the last choice is kept.
RUN_ANIMATION_SPEED = 28 * NES_X_SPEED_UNIT
WALK_ANIMATION_SPEED = 14 * NES_X_SPEED_UNIT
RUN_TICKS_PER_WALK_FRAME = 2
WALK_TICKS_PER_WALK_FRAME = 4
SLOW_TICKS_PER_WALK_FRAME = 7
# On the ground he shows his skid frame at or above this speed while he faces
# against the way he moves.
SKID_FRAME_MIN_SPEED = 9 * NES_X_SPEED_UNIT

# --- Enemies -------------------------------------------------------------------------------

# A walking enemy shows its second walking frame on ticks whose number has this
# bit clear, 8 of every 16 (FrameCounter & EnemyAnimTimingBMask), and its first
# on the others.
ENEMY_FIRST_WALK_FRAME = 1
ENEMY_SECOND_WALK_FRAME = 2
ENEMY_WALK_FRAME_TICK_BIT = 0x08
