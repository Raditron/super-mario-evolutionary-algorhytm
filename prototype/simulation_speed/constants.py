"""Every tunable number of the simulation-speed prototype (issue #4).

PROTOTYPE, throwaway. Sections: fixed-point units, physics (from issue #2),
level (from issue #3), Controller, attempt limits, placeholder brain, benchmark.

All positions and speeds are integers in sub-pixels so that stepping is
bit-exact on every machine and in every process (see the write-up).
"""

# --- Fixed-point units --------------------------------------------------------

SUBPIXEL_BITS = 12
SUBPIXELS_PER_PIXEL = 1 << SUBPIXEL_BITS          # 4096 sub-pixels = 1 px
TILE_SIZE_PIXELS = 16
TILE_PIXEL_BITS = 4                               # 16 px = 1 << 4
SUBPIXEL_TO_TILE_SHIFT = SUBPIXEL_BITS + TILE_PIXEL_BITS
TILE_SIZE_SUBPIXELS = TILE_SIZE_PIXELS * SUBPIXELS_PER_PIXEL

# NES storage units (issue #2): x speed in 1/16 px/frame, x acceleration in
# 1/4096 px/frame^2, y speed in 1 px/frame, gravity in 1/256 px/frame^2.
NES_X_SPEED_UNIT = SUBPIXELS_PER_PIXEL // 16
NES_X_ACCELERATION_UNIT = SUBPIXELS_PER_PIXEL // 4096
NES_Y_SPEED_UNIT = SUBPIXELS_PER_PIXEL
NES_GRAVITY_UNIT = SUBPIXELS_PER_PIXEL // 256

# --- Mario physics (per tick, 60 ticks per second) ----------------------------

TICKS_PER_SECOND = 60

MAX_WALK_SPEED = 24 * NES_X_SPEED_UNIT                 # 1.5 px/f
MAX_RUN_SPEED = 40 * NES_X_SPEED_UNIT                  # 2.5 px/f
WALK_ACCELERATION = 0x98 * NES_X_ACCELERATION_UNIT
RUN_ACCELERATION = 0xE4 * NES_X_ACCELERATION_UNIT
RELEASE_FRICTION = 0x98 * NES_X_ACCELERATION_UNIT
RELEASE_FRICTION_AFTER_RUN_SPEED = 0xD0 * NES_X_ACCELERATION_UNIT
SKID_DECELERATION_WALK = 0x130 * NES_X_ACCELERATION_UNIT
SKID_DECELERATION_RUN = 0x1A0 * NES_X_ACCELERATION_UNIT
SKID_TURNAROUND_SPEED = 11 * NES_X_SPEED_UNIT
AIR_FAST_CAP_TAKEOFF_SPEED = 25 * NES_X_SPEED_UNIT     # |vx| >= 1.5625 keeps the 2.5 cap

SLOW_JUMP_TAKEOFF_SPEED_LIMIT = 16 * NES_X_SPEED_UNIT  # |vx| < 1.0
MEDIUM_JUMP_TAKEOFF_SPEED_LIMIT = 25 * NES_X_SPEED_UNIT
SLOW_JUMP_VELOCITY = -4 * NES_Y_SPEED_UNIT
FAST_JUMP_VELOCITY = -5 * NES_Y_SPEED_UNIT
SLOW_JUMP_GRAVITY_HELD = 0x20 * NES_GRAVITY_UNIT
SLOW_JUMP_GRAVITY_FALLING = 0x70 * NES_GRAVITY_UNIT
MEDIUM_JUMP_GRAVITY_HELD = 0x1E * NES_GRAVITY_UNIT
MEDIUM_JUMP_GRAVITY_FALLING = 0x60 * NES_GRAVITY_UNIT
FAST_JUMP_GRAVITY_HELD = 0x28 * NES_GRAVITY_UNIT
FAST_JUMP_GRAVITY_FALLING = 0x90 * NES_GRAVITY_UNIT
INITIAL_FALLING_GRAVITY = 0x28 * NES_GRAVITY_UNIT     # before any jump in the area
TERMINAL_FALL_SPEED = 4 * NES_Y_SPEED_UNIT
STOMP_BOUNCE_VELOCITY = -4 * NES_Y_SPEED_UNIT

MARIO_WIDTH_PIXELS = 12
MARIO_HEIGHT_PIXELS = 16
MARIO_START_X_PIXELS = 40
MARIO_START_ROW = 12                                  # standing on the ground top (row 13)

# --- Goomba physics -------------------------------------------------------------

GOOMBA_WALK_SPEED = 8 * NES_X_SPEED_UNIT              # 0.5 px/f
ENEMY_GRAVITY = 0x3D * NES_GRAVITY_UNIT
ENEMY_TERMINAL_FALL_SPEED = 3 * NES_Y_SPEED_UNIT
GOOMBA_SIZE_PIXELS = 16
ENEMY_ACTIVATION_DISTANCE_PIXELS = 48                 # spawn this far past the screen's right edge
ENEMY_DESPAWN_DISTANCE_PIXELS = 128                   # forget enemies this far left of the camera
STOMP_MAX_PENETRATION_PIXELS = 8                      # a falling Mario this deep into a Goomba's top stomps it

# --- Camera (per agent; only used for enemy activation in headless mode) --------

SCREEN_WIDTH_PIXELS = 256
CAMERA_FOLLOW_OFFSET_PIXELS = 112                     # camera keeps Mario this far from its left edge

# --- Level (issue #3) -----------------------------------------------------------

LEVEL_FILE_NAME = "level_1_1.txt"
LEVEL_WIDTH_TILES = 224
LEVEL_HEIGHT_TILES = 15
SOLID_TILE_CHARACTERS = frozenset("X#B?MSC[]{}W")     # 'U' (hidden 1-UP) treated as empty here
FLAGPOLE_COLUMN = 198
GOOMBA_PAIR_SPACING_PIXELS = 24                       # second Goomba of a pair 24 px right
GOOMBA_PAIR_OFFSET_TILES = 3                          # pairs appear ~3 tiles left of their data column
GROUND_ENEMY_ROW = 12
BRICK_TOP_ENEMY_ROW = 4
SINGLE_GOOMBAS = ((22, GROUND_ENEMY_ROW), (40, GROUND_ENEMY_ROW),
                  (80, BRICK_TOP_ENEMY_ROW), (82, BRICK_TOP_ENEMY_ROW))
GOOMBA_PAIR_DATA_COLUMNS = (54, 100, 117, 127, 131, 177)

# --- Controller -----------------------------------------------------------------

BUTTON_LEFT = 1
BUTTON_RIGHT = 2
BUTTON_JUMP = 4
BUTTON_RUN = 8
CONTROLLER_BUTTON_ORDER = (BUTTON_LEFT, BUTTON_RIGHT, BUTTON_JUMP, BUTTON_RUN)

# --- Attempt limits -------------------------------------------------------------

LEVEL_TIMER_TICKS = 400 * 24                          # 400 timer units x 24 frames = 9600 ticks
NO_PROGRESS_LIMIT_TICKS = 3 * TICKS_PER_SECOND        # end the attempt if max x stalls this long

# --- Placeholder brain (NOT the user's ANN: a per-tick cost stand-in only) -------

OBSERVATION_COLUMNS_BEHIND = 3
OBSERVATION_COLUMNS_AHEAD = 8
OBSERVATION_FIRST_ROW = 2                             # rows 0-1 sit under the HUD
OBSERVATION_COLUMNS = OBSERVATION_COLUMNS_BEHIND + 1 + OBSERVATION_COLUMNS_AHEAD
OBSERVATION_ROWS = LEVEL_HEIGHT_TILES - OBSERVATION_FIRST_ROW
OBSERVATION_SIZE = OBSERVATION_COLUMNS * OBSERVATION_ROWS      # 12 x 13 = 156 inputs
OBSERVATION_SOLID = 1.0
OBSERVATION_ENEMY = -1.0
PLACEHOLDER_HIDDEN_SIZE = 24
PLACEHOLDER_OUTPUT_SIZE = len(CONTROLLER_BUTTON_ORDER)
PLACEHOLDER_WEIGHT_SCALE = 0.5
PLACEHOLDER_RIGHT_BIAS = 1.5                          # nudges random agents rightwards so they meet terrain and Goombas
PLACEHOLDER_PRESS_THRESHOLD = 0.0

# --- Benchmark ------------------------------------------------------------------

POPULATION_SIZE = 1000
GENERATIONS_IN_RUN = 100
WORKER_PROCESSES = 8
ALTERNATIVE_WORKER_COUNTS = (4,)                      # the laptop has 4 physical cores / 8 threads
CHUNKS_PER_WORKER = 2                                 # smaller chunks balance uneven attempt lengths
BENCHMARK_SEED = 20261021
TIMED_GENERATIONS_SINGLE_PROCESS = 1                  # single-process generations are slow; time one
TIMED_GENERATIONS_PARALLEL = 3                        # median of this many generations is reported
SINGLE_AGENT_BENCHMARK_TICKS = 20_000
PESSIMISTIC_TICKS_PER_ATTEMPT = 2400                  # every agent walks to the flag (~3200 px at 1.5 px/f)
DECISION_INTERVALS_TICKS = (1, 4)
SCRIPTED_PILOT_LOOK_AHEAD_TILES = 3                  # reaches column ~170 in ~1500 ticks                     # how often the brain is asked for new Controller buttons
