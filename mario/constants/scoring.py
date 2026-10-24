"""The score, coins and lives (#16), as the original counts them."""

# GiveOneCoin: every coin is also worth 200 points.
COIN_POINTS = 200

# --- Play mode only (PlaySession) ---------------------------------------------------------

STARTING_LIVES = 3                                           # PrimaryGameSetup
COINS_PER_EXTRA_LIFE = 100                                   # GiveOneCoin; the coin count then restarts at 0
