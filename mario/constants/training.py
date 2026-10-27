"""Training (#5, #7, #26)."""

# A training attempt stalls after this many ticks without a new furthest-right
# position in the area Mario is in.
STALL_LIMIT_TICKS = 180

# py -m mario train reads the run's settings from this file at the repo root by default.
DEFAULT_CONFIG_FILE_NAME = "config.toml"

# --- The worker pool (#4, spec section 9) --------------------------------------------------

# Worker processes playing agents, created once per run.
TRAINING_WORKER_COUNT = 8
# Workers are started fresh rather than forked, the same on every platform.
WORKER_START_METHOD = "spawn"
# Each generation's population is split into this many chunks per worker, so a
# worker that finishes a chunk of short attempts early picks up another.
CHUNKS_PER_WORKER = 2
# Each worker's numpy runs its linear algebra on this many threads, set through
# these environment variables, so the workers don't fight over the cores.
BLAS_THREADS_PER_WORKER = 1
BLAS_THREAD_COUNT_VARIABLES = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")

# --- The line printed per generation ---------------------------------------------------------

PRINTED_FITNESS_DECIMALS = 2
PRINTED_SECONDS_DECIMALS = 2
