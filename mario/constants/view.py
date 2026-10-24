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

# --- Debug view colours (RGB) ------------------------------------------------------------

SKY_COLOUR = (92, 148, 252)
GROUND_COLOUR = (200, 76, 12)
HARD_BLOCK_COLOUR = (136, 20, 0)
BRICK_COLOUR = (228, 92, 16)
QUESTION_BLOCK_COLOUR = (252, 188, 60)
HIDDEN_BLOCK_COLOUR = (188, 188, 252)
PIPE_COLOUR = (0, 168, 0)
FLAGPOLE_COLOUR = (240, 240, 240)
CASTLE_STOPPER_COLOUR = (60, 60, 60)
MARIO_COLOUR = (216, 40, 0)
GOOMBA_COLOUR = (136, 76, 0)
# A squashed Goomba is drawn flattened to this height, standing on its feet.
SQUASHED_GOOMBA_DRAWN_HEIGHT_PIXELS = 8

# --- HUD (TopStatusBarLine, StatusBarData, WriteBottomStatusLine) ----------------------------

# The original draws its status bar on the NES's 8 x 8 px text grid. Positions
# are (column, row) cells of that grid; each character fills one cell.
HUD_CELL_PIXELS = 8
HUD_TEXT_COLOUR = (252, 252, 252)
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
HUD_COINS_CELL = (13, 3)
HUD_COINS_DIGITS = 2
HUD_WORLD_CELL = (19, 3)
HUD_TIME_CELL = (26, 3)
HUD_TIME_DIGITS = 3
