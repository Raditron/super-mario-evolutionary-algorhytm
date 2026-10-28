"""The run folder (#7, #27, spec section 10): its name, its files and their formats."""

# Run folders are made inside this folder, at the repo root (git-ignored).
RUNS_FOLDER_NAME = "runs"
# A run folder is named after when the run started and the run's name: YYYY-MM-DD_HH-MM_<run-name>.
RUN_FOLDER_TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M"
RUN_FOLDER_NAME_FORMAT = "{started_at}_{run_name}"

# The copy of the config the run started with.
CONFIG_COPY_FILE_NAME = "config.toml"

# One row per agent per generation, after a header row naming these columns.
RESULTS_FILE_NAME = "results.csv"
RESULTS_COLUMNS = ("generation", "agent", "fitness", "end_reason", "furthest_x", "ticks_elapsed",
                   "final_score", "coins_collected")

# One row per generation, after a header row naming these columns: its wall-clock seconds.
GENERATION_TIMES_FILE_NAME = "generation_times.csv"
GENERATION_TIMES_COLUMNS = ("generation", "seconds")

# One folder per generation, numbered with this many digits: generations/0001/, generations/0002/ ...
GENERATIONS_FOLDER_NAME = "generations"
GENERATION_FOLDER_DIGITS = 4

# Every agent's Controller log, one uint8 array per agent, compressed, keyed by the agent's index.
CONTROLLER_LOGS_FILE_NAME = "controller_logs.npz"
CONTROLLER_LOG_KEY_FORMAT = "{agent}"

# The genome of the generation's best agent only.
BEST_GENOME_FILE_NAME = "best_genome.npy"
