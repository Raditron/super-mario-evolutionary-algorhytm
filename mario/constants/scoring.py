"""The score, coins and lives (#16), as the original counts them."""

# GiveOneCoin: every coin is also worth 200 points.
COIN_POINTS = 200

# The original's score table (FloateyNumTileData): 100, 200, 400, ... 8000. Stomps
# without landing in between climb it (HandleStompedShellE), and kicks and a moving
# shell's defeats score from it too. A step beyond the table is worth a 1-UP instead.
SCORE_TABLE_POINTS = (100, 200, 400, 500, 800, 1000, 2000, 4000, 5000, 8000)

# Kicking a still shell scores the score table's step this far past the stomp
# chain (HandlePECollisions: floatey number StompChainCounter + 3), so 400 once
# Mario has landed; but while the shell's interval timer is at 0, 1 or 2, just
# before it wakes, it scores these instead (KickedShellPtsData).
KICKED_SHELL_STEPS_PAST_STOMP_CHAIN = 3
KICKED_SHELL_POINTS_BY_INTERVAL_TICKS_LEFT = (8000, 1000, 500)

# Each enemy a moving shell defeats scores the score table's step this far past
# the shell's own chain, which counts its defeats for as long as it is a shell and
# is never reset (ShellCollisions: floatey number ShellChainCounter + 4): 500, 800, ...
SHELL_DEFEAT_STEPS_PAST_SHELL_CHAIN = 4

# An enemy defeated by bumping the block under it (GiveOEPoints).
BUMPED_ENEMY_POINTS = 100
# A Goomba defeated by a fireball (ShellOrBlockDefeat, GoombaPoints: floatey number
# $01); a Koopa, walking or in its shell, like most other enemies (floatey number $02).
GOOMBA_FIREBALL_POINTS = 100
KOOPA_FIREBALL_POINTS = 200

# An item collected (HandlePowerUpCollision: floatey number $06). The 1-UP
# mushroom gives a life instead (floatey number $0B).
ITEM_POINTS = 1000
# A brick big Mario breaks (BrickShatter: DigitModifier+5 = 5, the tens digit).
BROKEN_BRICK_POINTS = 50

# Touching the flagpole scores by the height of the touch (FlagpoleYPosData,
# FlagpoleScoreMods, FlagpoleScoreDigits): Mario's sprite's top at or below each y
# scores its points, checked from the lowest band up; above them all, the top prize.
FLAGPOLE_POINTS_BY_LOWEST_SPRITE_Y_PIXELS = ((0x90, 100), (0x68, 400), (0x50, 800), (0x22, 2000))
FLAGPOLE_TOP_POINTS = 5000
# Then every unit left on the level timer is worth 50 points (AwardGameTimerPoints).
POINTS_PER_TIME_UNIT_LEFT = 50

# --- Play mode only (PlaySession) ---------------------------------------------------------

STARTING_LIVES = 3                                           # PrimaryGameSetup
COINS_PER_EXTRA_LIFE = 100                                   # GiveOneCoin; the coin count then restarts at 0
