"""config.toml: the settings of one run (spec section 10).

[run] holds the game's per-run settings; [algorithm] belongs to the user and is
handed to create_algorithm as a plain dict, unread by the game.
"""

import tomllib
from dataclasses import Field, dataclass, field, fields
from pathlib import Path

RUN_TABLE = "run"
ALGORITHM_TABLE = "algorithm"
# A RunSettings field with this metadata must be at least 1.
POSITIVE = "positive"


@dataclass(frozen=True)
class RunSettings:
    """The [run] table: one key per field, named and typed as the field."""
    name: str
    seed: int
    generations: int = field(metadata={POSITIVE: True})
    population_size: int = field(metadata={POSITIVE: True})


@dataclass(frozen=True)
class RunConfig:
    run: RunSettings
    algorithm_settings: dict

    @classmethod
    def load(cls, config_path: Path) -> "RunConfig":
        try:
            return cls._from_tables(tomllib.loads(config_path.read_text()))
        except ValueError as problem:
            raise ValueError(f"{config_path}: {problem}") from problem

    @classmethod
    def _from_tables(cls, tables: dict) -> "RunConfig":
        for table in (RUN_TABLE, ALGORITHM_TABLE):
            if not isinstance(tables.get(table), dict):
                raise ValueError(f"needs a [{table}] table")
        run_table = tables[RUN_TABLE]
        run_settings = RunSettings(**{setting.name: _checked(run_table.get(setting.name), setting)
                                      for setting in fields(RunSettings)})
        return cls(run_settings, tables[ALGORITHM_TABLE])


def _checked(value: object, setting: Field) -> object:
    """The [run] value for this setting, refused unless it has the setting's type."""
    if setting.type is str and not isinstance(value, str):
        raise ValueError(f"[{RUN_TABLE}] {setting.name} must be text")
    positive = setting.metadata.get(POSITIVE, False)
    if setting.type is int and (type(value) is not int or (positive and value < 1)):
        raise ValueError(f"[{RUN_TABLE}] {setting.name} must be a {'positive ' if positive else ''}whole number")
    return value
