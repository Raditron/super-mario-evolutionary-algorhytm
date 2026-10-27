"""config.toml: the settings of one run (spec section 10).

[run] holds the game's per-run settings; [algorithm] belongs to the user and is
handed to create_algorithm as a plain dict, unread by the game.
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path

RUN_TABLE = "run"
ALGORITHM_TABLE = "algorithm"


@dataclass(frozen=True)
class RunSettings:
    name: str
    seed: int
    generations: int
    population_size: int


@dataclass(frozen=True)
class RunConfig:
    run: RunSettings
    algorithm_settings: dict

    @classmethod
    def load(cls, config_path: Path) -> "RunConfig":
        tables = tomllib.loads(config_path.read_text())
        for table in (RUN_TABLE, ALGORITHM_TABLE):
            if not isinstance(tables.get(table), dict):
                raise ValueError(f"{config_path}: needs a [{table}] table")
        return cls(_run_settings(tables[RUN_TABLE], config_path), tables[ALGORITHM_TABLE])


def _run_settings(run_table: dict, config_path: Path) -> RunSettings:
    name = run_table.get("name")
    if not isinstance(name, str):
        raise ValueError(f"{config_path}: [run] name must be text")
    return RunSettings(name=name, seed=_whole_number(run_table, "seed", config_path),
                       generations=_whole_number(run_table, "generations", config_path, positive=True),
                       population_size=_whole_number(run_table, "population_size", config_path, positive=True))


def _whole_number(run_table: dict, setting: str, config_path: Path, positive: bool = False) -> int:
    value = run_table.get(setting)
    if type(value) is not int or (positive and value < 1):
        raise ValueError(f"{config_path}: [run] {setting} must be a {'positive ' if positive else ''}whole number")
    return value
