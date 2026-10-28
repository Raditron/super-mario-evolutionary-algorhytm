"""The score, coins and lives (#16), as the original counts them."""

# GiveOneCoin: every coin is also worth 200 points.
COIN_POINTS = 200

# Stomps without landing in between climb the original's score table
# (HandleStompedShellE, FloateyNumTileData): 100, 200, 400, ... 8000. A stomp
# beyond the table is worth a 1-UP instead of points.
STOMP_CHAIN_POINTS = (100, 200, 400, 500, 800, 1000, 2000, 4000, 5000, 8000)

# An enemy defeated by bumping the block under it (GiveOEPoints).
BUMPED_ENEMY_POINTS = 100
# A Goomba defeated by a fireball (ShellOrBlockDefeat, GoombaPoints: floatey number
# $01). Most other enemies, a Koopa among them, give 200 (floatey number $02).
GOOMBA_FIREBALL_POINTS = 100

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

# --- Play mode only (PlaySession)---------------------------------------------------------

STARTING_LIVES = 3                                           # PrimaryGameSetup
COINS_PER_EXTRA_LIFE = 100                                   # GiveOneCoin; the coin count then restarts at 0
