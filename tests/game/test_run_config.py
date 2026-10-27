"""config.toml: the [run] settings, and the [algorithm] table handed to the user as it is (#26, spec section 10)."""

from pathlib import Path

import pytest

import mario
from mario.training.run_config import RunConfig, RunSettings

REPO_ROOT_CONFIG = Path(mario.__file__).parent.parent / "config.toml"

A_CONFIG = """
[run]
name = "long-jumps"
seed = 7
generations = 50
population_size = 300

[algorithm]
hidden_layer_size = 24
mutation = { rate = 0.05 }
"""


def write_config(tmp_path: Path, text: str) -> Path:
    config_path = tmp_path / "config.toml"
    config_path.write_text(text)
    return config_path


def test_the_run_table_becomes_the_run_settings_and_the_algorithm_table_a_plain_dict(tmp_path):
    config = RunConfig.load(write_config(tmp_path, A_CONFIG))
    assert config.run == RunSettings(name="long-jumps", seed=7, generations=50, population_size=300)
    assert config.algorithm_settings == {"hidden_layer_size": 24, "mutation": {"rate": 0.05}}


def test_the_repo_root_config_has_the_four_run_settings_and_an_empty_algorithm_table():
    config = RunConfig.load(REPO_ROOT_CONFIG)
    assert config.run.population_size > 0 and config.run.generations > 0
    assert config.algorithm_settings == {}


@pytest.mark.parametrize("run_table, named_setting", [
    ('name = "a"\ngenerations = 5\npopulation_size = 10', "seed"),                     # missing
    ('name = "a"\nseed = "seven"\ngenerations = 5\npopulation_size = 10', "seed"),     # not a whole number
    ('name = "a"\nseed = 7\ngenerations = 0\npopulation_size = 10', "generations"),    # not positive
    ('name = 3\nseed = 7\ngenerations = 5\npopulation_size = 10', "name"),             # not text
])
def test_a_broken_run_table_is_refused_naming_the_setting(tmp_path, run_table, named_setting):
    with pytest.raises(ValueError, match=named_setting):
        RunConfig.load(write_config(tmp_path, f"[run]\n{run_table}\n\n[algorithm]\n"))


def test_a_config_without_an_algorithm_table_is_refused(tmp_path):
    with pytest.raises(ValueError, match=r"\[algorithm\]"):
        RunConfig.load(write_config(tmp_path, '[run]\nname = "a"\nseed = 7\ngenerations = 5\npopulation_size = 10\n'))
