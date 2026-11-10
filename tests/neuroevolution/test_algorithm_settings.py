"""Milestone 0: AlgorithmSettings reads the [algorithm] table, and create_algorithm builds from it."""

import tomllib
from pathlib import Path

import pytest

from mario.training.neuroevolution_algorithm import NeuroevolutionAlgorithm
from neuroevolution import create_algorithm
from neuroevolution.algorithm_settings import AlgorithmSettings

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config.toml"

VALID_RAW_VALUES = {
    "hidden_layer_size": 24,
    "button_press_threshold": 0.0,
    "coin_reward": 100,
    "flag_reward": 20000,
    "time_reward": 1.0416666666666667,
    "tournament_size": 3,
    "mutation_rate": 0.05,
    "mutation_strength": 0.05,
    "crossover_rate": 0.7,
    "elite_count": 10,
}


def with_change(**changes: object) -> dict[str, object]:
    return {**VALID_RAW_VALUES, **changes}


def without(name: str) -> dict[str, object]:
    return {key: value for key, value in VALID_RAW_VALUES.items() if key != name}


def test_a_full_table_builds_the_settings():
    settings = AlgorithmSettings.from_dict(VALID_RAW_VALUES)

    assert settings.hidden_layer_size == 24
    assert settings.mutation_rate == 0.05
    assert settings.elite_count == 10


def test_a_whole_number_is_accepted_for_a_float_setting():
    settings = AlgorithmSettings.from_dict(VALID_RAW_VALUES)

    assert settings.coin_reward == 100.0
    assert isinstance(settings.coin_reward, float)


def test_the_real_config_table_builds_the_settings():
    table = tomllib.loads(CONFIG_PATH.read_text())["algorithm"]

    AlgorithmSettings.from_dict(table)


@pytest.mark.parametrize("name", sorted(VALID_RAW_VALUES))
def test_a_missing_key_is_refused(name):
    with pytest.raises(ValueError, match=name):
        AlgorithmSettings.from_dict(without(name))


def test_an_unknown_key_is_refused():
    with pytest.raises(ValueError, match="mutaton_rate"):
        AlgorithmSettings.from_dict(with_change(mutaton_rate=0.1))


@pytest.mark.parametrize("name, value", [
    ("hidden_layer_size", 24.0),
    ("tournament_size", "3"),
    ("elite_count", True),
    ("mutation_rate", "0.05"),
    ("coin_reward", True),
])
def test_a_wrong_type_is_refused(name, value):
    with pytest.raises(ValueError, match=name):
        AlgorithmSettings.from_dict(with_change(**{name: value}))


@pytest.mark.parametrize("name, value", [
    ("mutation_rate", 1.5),
    ("mutation_rate", -0.1),
    ("crossover_rate", 1.5),
    ("crossover_rate", -0.1),
    ("hidden_layer_size", 0),
    ("tournament_size", 0),
    ("mutation_strength", 0.0),
    ("elite_count", -1),
])
def test_a_value_out_of_range_is_refused(name, value):
    with pytest.raises(ValueError, match=name):
        AlgorithmSettings.from_dict(with_change(**{name: value}))


@pytest.mark.parametrize("name, value", [
    ("mutation_rate", 0.0),
    ("mutation_rate", 1.0),
    ("crossover_rate", 0.0),
    ("crossover_rate", 1.0),
    ("hidden_layer_size", 1),
    ("elite_count", 0),
])
def test_a_value_on_the_edge_of_its_range_is_accepted(name, value):
    AlgorithmSettings.from_dict(with_change(**{name: value}))


def test_the_settings_cannot_be_changed_once_built():
    settings = AlgorithmSettings.from_dict(VALID_RAW_VALUES)

    with pytest.raises(AttributeError):
        settings.mutation_rate = 0.5  # type: ignore[misc]


def test_create_algorithm_builds_a_neuroevolution_algorithm_from_a_table():
    assert isinstance(create_algorithm(dict(VALID_RAW_VALUES)), NeuroevolutionAlgorithm)


def test_create_algorithm_refuses_a_table_with_a_missing_key():
    with pytest.raises(ValueError, match="elite_count"):
        create_algorithm(without("elite_count"))
