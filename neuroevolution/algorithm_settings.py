from dataclasses import dataclass
from typing import Any, get_type_hints

MINIMUM_RATE = 0.0
MAXIMUM_RATE = 1.0
MINIMUM_SIZE = 1
MINIMUM_ELITE_COUNT = 0

RATE_SETTINGS = ("mutation_rate", "crossover_rate")
SIZE_SETTINGS = ("hidden_layer_size", "tournament_size")


@dataclass(frozen=True)
class AlgorithmSettings:
    hidden_layer_size: int
    button_press_threshold: float
    coin_reward: float
    flag_reward: float
    time_reward: float
    tournament_size: int
    mutation_rate: float
    mutation_strength: float
    crossover_rate: float
    elite_count: int

    @classmethod
    def from_dict(cls, raw_values: dict[str, object]) -> "AlgorithmSettings":
        """The settings from the [algorithm] table, refused unless every key is present and valid."""
        setting_types = get_type_hints(cls)

        missing = setting_types.keys() - raw_values.keys()
        if missing:
            raise ValueError(
                f"Missing algorithm settings: {', '.join(sorted(missing))}"
            )

        unknown = raw_values.keys() - setting_types.keys()
        if unknown:
            raise ValueError(
                f"Unknown algorithm settings: {', '.join(sorted(unknown))}"
            )

        return cls(
            **{
                name: _checked_type(name, value, setting_types[name])
                for name, value in raw_values.items()
            }
        )

    def __post_init__(self) -> None:
        for name in RATE_SETTINGS:
            if not MINIMUM_RATE <= getattr(self, name) <= MAXIMUM_RATE:
                raise ValueError(
                    f"Algorithm setting '{name}' must be between {MINIMUM_RATE} and {MAXIMUM_RATE}"
                )
        for name in SIZE_SETTINGS:
            if getattr(self, name) < MINIMUM_SIZE:
                raise ValueError(
                    f"Algorithm setting '{name}' must be at least {MINIMUM_SIZE}"
                )
        if self.mutation_strength <= 0:
            raise ValueError(
                "Algorithm setting 'mutation_strength' must be greater than 0"
            )
        if self.elite_count < MINIMUM_ELITE_COUNT:
            raise ValueError(
                f"Algorithm setting 'elite_count' must be at least {MINIMUM_ELITE_COUNT}"
            )


def _checked_type(name: str, value: object, expected_type: type) -> Any:
    """The value, refused unless it has the setting's type. A whole number is accepted for a float (TOML reads 100 as an int)."""
    if expected_type is float and isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    if type(value) is not expected_type:
        raise ValueError(
            f"Algorithm setting '{name}' must be {expected_type.__name__}, got {type(value).__name__}"
        )
    return value
