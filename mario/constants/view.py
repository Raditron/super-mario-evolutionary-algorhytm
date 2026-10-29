"""The window, the renderers and the keyboard (#8)."""

WINDOW_TITLE = "Mario World 1-1"
WINDOW_SCALE = 3
FRAMES_PER_SECOND = 60

# --- Keyboard (play mode). Names as pygame.key.key_code() reads them. ----------------

KEYBOARD_BUTTON_KEYS = {
    "left": "left",
    "right": "right",
    "down": "down",
    "jump": "x",
    "run": "z",
}
QUIT_KEY = "escape"
VIEW_TOGGLE_KEY = "f1"                    # switches between the Sprite view and the Debug view

# --- Debug view colours (RGB) ------------------------------------------------------------

SKY_COLOUR = (92, 148, 252)
GROUND_COLOUR = (200, 76, 12)
HARD_BLOCK_COLOUR = (136, 20, 0)
BRICK_COLOUR = (228, 92, 16)
QUESTION_BLOCK_COLOUR = (252, 188, 60)
USED_BLOCK_COLOUR = (160, 108, 40)
HIDDEN_BLOCK_COLOUR = (188, 188, 252)
PIPE_COLOUR = (0, 168, 0)
FLAGPOLE_COLOUR = (240, 240, 240)
CASTLE_STOPPER_COLOUR = (60, 60, 60)
FLAG_COLOUR = (60, 188, 60)
MARIO_COLOUR = (216, 40, 0)                  # small or big
FIRE_MARIO_COLOUR = (252, 252, 252)
# A Starman's invincibility overrides his power state's colour, as the original's
# cycling star palette does (CyclePlayerPalette), small, big or fiery.
INVINCIBLE_MARIO_COLOUR = (184, 248, 24)
GOOMBA_COLOUR = (136, 76, 0)
KOOPA_COLOUR = (88, 216, 84)
KOOPA_SHELL_COLOUR = (16, 112, 72)           # still or moving
# A defeated enemy (a squashed Goomba, or one knocked out of the level) is drawn
# flattened to this height, standing on its feet.
DEFEATED_ENEMY_DRAWN_HEIGHT_PIXELS = 8
SUPER_MUSHROOM_COLOUR = (252, 116, 180)
ONE_UP_MUSHROOM_COLOUR = (0, 200, 120)
FIRE_FLOWER_COLOUR = (252, 160, 68)
STARMAN_COLOUR = (248, 184, 0)
FIREBALL_COLOUR = (252, 216, 0)
EXPLODING_FIREBALL_COLOUR = (252, 100, 0)

# --- Debug view: the followed agent's Observation and recent game events (#25) ---------------

# The Observation's 13 x 12 window is drawn over the level, each cell tinted by
# its value (RGB), at this opacity (0 transparent to 255 opaque), with this gap
# between cells so each one shows.
OBSERVATION_EMPTY_TINT = (0, 0, 0)
OBSERVATION_SOLID_TINT = (255, 255, 255)
OBSERVATION_ENEMY_TINT = (255, 0, 64)
OBSERVATION_TINT_OPACITY = 96
OBSERVATION_CELL_GAP_PIXELS = 1
# The four state numbers, as one line of text: a label for each, in the Observation's order.
OBSERVATION_STATE_LABELS = ("vx", "vy", "height", "ground")
OBSERVATION_STATE_DECIMALS = 2
OBSERVATION_STATE_TEXT_TOP_LEFT = (8, 228)
# Of the snapshot's recent game events, the newest few are listed.
DEBUG_GAME_EVENT_LINES = 4
DEBUG_GAME_EVENTS_TOP_LEFT = (8, 36)
DEBUG_TEXT_LINE_PIXELS = 9
DEBUG_TEXT_COLOUR = (252, 252, 252)
DEBUG_TEXT_BACKGROUND_COLOUR = (0, 0, 0)
DEBUG_FONT_SIZE = 14                      # pygame's default font, as the HUD uses

# --- HUD (TopStatusBarLine, StatusBarData, WriteBottomStatusLine) ----------------------------

# The original draws its status bar on the NES's 8 x 8 px text grid. Positions
# are (column, row) cells of that grid; each character fills one cell.
HUD_CELL_PIXELS = 8
HUD_TEXT_COLOUR = (252, 252, 252)
# The coin icon is this sprite, filling its cell; while it is missing, a rectangle
# in this colour at HUD_COIN_ICON_RECT_IN_CELL.
HUD_COIN_SPRITE_NAME = "coin"
HUD_COIN_ICON_COLOUR = (252, 152, 56)
HUD_FONT_SIZE = 14                        # pygame's default font, unsmoothed: digits about 8 px tall
HUD_LABELS = {(3, 2): "MARIO", (18, 2): "WORLD", (25, 2): "TIME"}
# The score shows at least 6 digits, right-aligned in 7 cells: the original
# prints 7 and blanks the first while it is 0.
HUD_SCORE_CELL = (2, 3)
HUD_SCORE_CELLS_WIDE = 7
HUD_SCORE_MIN_DIGITS = 6
HUD_COIN_ICON_CELL = (11, 3)
HUD_COIN_ICON_RECT_IN_CELL = (2, 1, 4, 6)  # x, y, width, height in px
HUD_COIN_CROSS_CELL = (12, 3)
HUD_COIN_CROSS = "x"
# While a generation is watched, the HUD adds this line about it (spec section 8).
GENERATION_LINE = "generation {generation} · alive {alive} / {population_size} · reached flag {reached_flag}"
HUD_COINS_CELL = (13, 3)
HUD_COINS_DIGITS = 2
HUD_WORLD_CELL = (19, 3)
HUD_TIME_CELL = (26, 3)
HUD_TIME_DIGITS = 3

# --- Sprite view (#32) -------------------------------------------------------------------------

# The sprites folder, from the repo root, and the one file type read from it.
# assets/sprites/README.md lists the file names and sizes.
SPRITES_FOLDER_PARTS = ("assets", "sprites")
SPRITE_FILE_EXTENSION = ".png"
# The original's sizes (width, height) in px. Tiles and scenery are one 16 x 16
# metatile each. The player object is 16 x 32, small Mario its lower 16 rows; an
# enemy object is 16 x 24, the Koopa all of it, the Goomba and the Koopa's shell
# its lower 16 rows and the defeated Goomba its lowest 8 (EnemyGraphicsTable); a power-up is two rows of two
# 8 x 8 tiles, 16 x 16 (PowerUpGfxTable, DrawPowerUp); a fireball is one 8 x 8
# sprite and its explosion four, 16 x 16 (DrawExplosion_Fireball); the flag is
# three 8 x 8 sprites in a 16 x 16 square from its corner (FlagpoleGfxHandler).
TILE_SPRITE_SIZE = (16, 16)
SMALL_MARIO_SPRITE_SIZE = (16, 16)
BIG_MARIO_SPRITE_SIZE = (16, 32)
# Big Mario's crouching frame is the player object's lower 24 rows (its top row
# of 8 x 8 tiles is blank in PlayerGraphicsTable).
BIG_MARIO_CROUCH_SPRITE_SIZE = (16, 24)
GOOMBA_SPRITE_SIZE = (16, 16)
DEFEATED_GOOMBA_SPRITE_SIZE = (16, 8)
KOOPA_SPRITE_SIZE = (16, 24)
KOOPA_SHELL_SPRITE_SIZE = (16, 16)
ITEM_SPRITE_SIZE = (16, 16)
FIREBALL_SPRITE_SIZE = (8, 8)
FIREBALL_EXPLOSION_SPRITE_SIZE = (16, 16)
FLAG_SPRITE_SIZE = (16, 16)
# The HUD's coin icon fills one 8 x 8 cell of the status bar's text grid.
HUD_COIN_SPRITE_SIZE = (HUD_CELL_PIXELS, HUD_CELL_PIXELS)
# Every sprite the Sprite view draws: its file name (without the extension) and size.
SPRITE_SIZES = {
    # tiles, by how they look: the bricks and ? blocks don't show what they hold
    "ground": TILE_SPRITE_SIZE,
    "hard_block": TILE_SPRITE_SIZE,
    "brick": TILE_SPRITE_SIZE,
    "question_block": TILE_SPRITE_SIZE,
    "used_block": TILE_SPRITE_SIZE,
    # a pipe by place: its rim's and body's left and right halves
    "pipe_rim_left": TILE_SPRITE_SIZE,
    "pipe_rim_right": TILE_SPRITE_SIZE,
    "pipe_body_left": TILE_SPRITE_SIZE,
    "pipe_body_right": TILE_SPRITE_SIZE,
    "flagpole": TILE_SPRITE_SIZE,
    # the flag on the flagpole
    "flag": FLAG_SPRITE_SIZE,
    # background scenery; a hill by place: its slopes, its peak and the fill between
    # a cloud by place: its top and bottom rows' left end, middle and right end
    "cloud_top_left": TILE_SPRITE_SIZE,
    "cloud_top_middle": TILE_SPRITE_SIZE,
    "cloud_top_right": TILE_SPRITE_SIZE,
    "cloud_bottom_left": TILE_SPRITE_SIZE,
    "cloud_bottom_middle": TILE_SPRITE_SIZE,
    "cloud_bottom_right": TILE_SPRITE_SIZE,
    "hill_left_slope": TILE_SPRITE_SIZE,
    "hill_right_slope": TILE_SPRITE_SIZE,
    "hill_peak": TILE_SPRITE_SIZE,
    "hill_fill": TILE_SPRITE_SIZE,
    # a bush by place: its left end, middle and right end, or a one-tile bush
    "bush_left_end": TILE_SPRITE_SIZE,
    "bush_middle": TILE_SPRITE_SIZE,
    "bush_right_end": TILE_SPRITE_SIZE,
    "bush_single": TILE_SPRITE_SIZE,
    "castle_battlement": TILE_SPRITE_SIZE,
    "castle_window": TILE_SPRITE_SIZE,
    "castle_brick": TILE_SPRITE_SIZE,
    "castle_door_arch": TILE_SPRITE_SIZE,
    "castle_door": TILE_SPRITE_SIZE,
    # the castle by place: its wall's and windows' left and right edges, its
    # battlements' corner merlons, and the wall top the tower rises from
    "castle_brick_left_edge": TILE_SPRITE_SIZE,
    "castle_brick_right_edge": TILE_SPRITE_SIZE,
    "castle_window_left_edge": TILE_SPRITE_SIZE,
    "castle_window_right_edge": TILE_SPRITE_SIZE,
    "castle_battlement_left_end": TILE_SPRITE_SIZE,
    "castle_battlement_right_end": TILE_SPRITE_SIZE,
    "castle_wall_top": TILE_SPRITE_SIZE,
    # Mario, by power state
    "mario_small": SMALL_MARIO_SPRITE_SIZE,
    "mario_big": BIG_MARIO_SPRITE_SIZE,
    "mario_fiery": BIG_MARIO_SPRITE_SIZE,
    # Mario invincible, by size: the star palette shows over fire Mario's colours too
    "mario_small_invincible": SMALL_MARIO_SPRITE_SIZE,
    "mario_big_invincible": BIG_MARIO_SPRITE_SIZE,
    # Mario's animation frames (#57), by standing sprite: three walking frames, the
    # skid and the jump, and for big Mario the crouch
    "mario_small_walk_1": SMALL_MARIO_SPRITE_SIZE,
    "mario_small_walk_2": SMALL_MARIO_SPRITE_SIZE,
    "mario_small_walk_3": SMALL_MARIO_SPRITE_SIZE,
    "mario_small_skid": SMALL_MARIO_SPRITE_SIZE,
    "mario_small_jump": SMALL_MARIO_SPRITE_SIZE,
    "mario_small_invincible_walk_1": SMALL_MARIO_SPRITE_SIZE,
    "mario_small_invincible_walk_2": SMALL_MARIO_SPRITE_SIZE,
    "mario_small_invincible_walk_3": SMALL_MARIO_SPRITE_SIZE,
    "mario_small_invincible_skid": SMALL_MARIO_SPRITE_SIZE,
    "mario_small_invincible_jump": SMALL_MARIO_SPRITE_SIZE,
    "mario_big_walk_1": BIG_MARIO_SPRITE_SIZE,
    "mario_big_walk_2": BIG_MARIO_SPRITE_SIZE,
    "mario_big_walk_3": BIG_MARIO_SPRITE_SIZE,
    "mario_big_skid": BIG_MARIO_SPRITE_SIZE,
    "mario_big_jump": BIG_MARIO_SPRITE_SIZE,
    "mario_big_crouch": BIG_MARIO_CROUCH_SPRITE_SIZE,
    "mario_fiery_walk_1": BIG_MARIO_SPRITE_SIZE,
    "mario_fiery_walk_2": BIG_MARIO_SPRITE_SIZE,
    "mario_fiery_walk_3": BIG_MARIO_SPRITE_SIZE,
    "mario_fiery_skid": BIG_MARIO_SPRITE_SIZE,
    "mario_fiery_jump": BIG_MARIO_SPRITE_SIZE,
    "mario_fiery_crouch": BIG_MARIO_CROUCH_SPRITE_SIZE,
    "mario_big_invincible_walk_1": BIG_MARIO_SPRITE_SIZE,
    "mario_big_invincible_walk_2": BIG_MARIO_SPRITE_SIZE,
    "mario_big_invincible_walk_3": BIG_MARIO_SPRITE_SIZE,
    "mario_big_invincible_skid": BIG_MARIO_SPRITE_SIZE,
    "mario_big_invincible_jump": BIG_MARIO_SPRITE_SIZE,
    "mario_big_invincible_crouch": BIG_MARIO_CROUCH_SPRITE_SIZE,
    # enemies
    "goomba": GOOMBA_SPRITE_SIZE,
    "goomba_defeated": DEFEATED_GOOMBA_SPRITE_SIZE,
    "koopa": KOOPA_SPRITE_SIZE,
    "koopa_shell": KOOPA_SHELL_SPRITE_SIZE,
    # a walking enemy's second walking frame (#57); its first is its own sprite
    "goomba_walk_2": GOOMBA_SPRITE_SIZE,
    "koopa_walk_2": KOOPA_SPRITE_SIZE,
    # items
    "super_mushroom": ITEM_SPRITE_SIZE,
    "one_up_mushroom": ITEM_SPRITE_SIZE,
    "fire_flower": ITEM_SPRITE_SIZE,
    "starman": ITEM_SPRITE_SIZE,
    # Mario's fireballs
    "fireball": FIREBALL_SPRITE_SIZE,
    "fireball_explosion": FIREBALL_EXPLOSION_SPRITE_SIZE,
    # the HUD's coin icon
    HUD_COIN_SPRITE_NAME: HUD_COIN_SPRITE_SIZE,
}
# Scenery has no hitbox; a missing scenery sprite is drawn in these colours (RGB).
CLOUD_COLOUR = (252, 252, 252)
HILL_COLOUR = (0, 120, 0)
BUSH_COLOUR = (128, 208, 16)
CASTLE_BRICK_COLOUR = (172, 80, 36)
CASTLE_OPENING_COLOUR = (0, 0, 0)        # its windows and door

# --- Watch-live: the other agents as ghosts, and the generation's line in the HUD (#29) ---------

# At most this many agents besides the followed one are drawn, the rightmost ones.
GHOST_DRAW_LIMIT = 100
# The Sprite view draws a ghost at this opacity (0 transparent to 255 opaque);
# the Debug view draws its hitbox's outline, this many pixels wide.
GHOST_OPACITY = 96
GHOST_OUTLINE_WIDTH_PIXELS = 1
# The HUD's GENERATION_LINE, under the level's ground line.
GENERATION_LINE_TOP_LEFT = (8, 216)
GENERATION_LINE_FONT_SIZE = 12            # pygame's default font: the longest line fits the screen
