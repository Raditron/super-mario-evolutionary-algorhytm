"""The settings of one run, read from the [run] table of config.toml (spec section 10)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RunSettings:
    name: str
    seed: int
    generations: int
    population_size: int
