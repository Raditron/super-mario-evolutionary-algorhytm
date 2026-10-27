"""Where everything about one run is recorded (spec section 10): the run folder's layout."""

from datetime import datetime
from pathlib import Path

from mario.constants.recording import (
    BEST_GENOME_FILE_NAME,
    CONFIG_COPY_FILE_NAME,
    CONTROLLER_LOGS_FILE_NAME,
    GENERATION_FOLDER_DIGITS,
    GENERATION_TIMES_FILE_NAME,
    GENERATIONS_FOLDER_NAME,
    RESULTS_FILE_NAME,
    RUN_FOLDER_NAME_FORMAT,
    RUN_FOLDER_TIMESTAMP_FORMAT,
)


class RunFolder:
    """The paths of one run folder's files; it reads and writes none of them."""

    def __init__(self, path: Path):
        self.path = path

    @classmethod
    def for_new_run(cls, runs_root: Path, run_name: str, started_at: datetime) -> "RunFolder":
        """runs_root/YYYY-MM-DD_HH-MM_<run-name>, not yet made."""
        folder_name = RUN_FOLDER_NAME_FORMAT.format(
            started_at=started_at.strftime(RUN_FOLDER_TIMESTAMP_FORMAT), run_name=run_name)
        return cls(runs_root / folder_name)

    @property
    def config_copy_path(self) -> Path:
        return self.path / CONFIG_COPY_FILE_NAME

    @property
    def results_path(self) -> Path:
        return self.path / RESULTS_FILE_NAME

    @property
    def generation_times_path(self) -> Path:
        return self.path / GENERATION_TIMES_FILE_NAME

    def generation_path(self, generation: int) -> Path:
        return self.path / GENERATIONS_FOLDER_NAME / f"{generation:0{GENERATION_FOLDER_DIGITS}d}"

    def controller_logs_path(self, generation: int) -> Path:
        return self.generation_path(generation) / CONTROLLER_LOGS_FILE_NAME

    def best_genome_path(self, generation: int) -> Path:
        return self.generation_path(generation) / BEST_GENOME_FILE_NAME
