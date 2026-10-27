"""py -m mario train: the one place the user's package is imported (#26, spec sections 2 and 9).

Each test runs the command in a fresh folder holding its own stand-in
`neuroevolution` package, which shadows any real one at the repo root, and has
it make its run folders in runs/ of that folder instead of the repo root's.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

import mario

REPO_ROOT = Path(mario.__file__).parent.parent
SMALL_RUN_CONFIG = """
[run]
name = "smoke"
seed = 3
generations = 2
population_size = 4

[algorithm]
"""
RANDOM_BUTTONS_PACKAGE = ("from tests.game.random_buttons_algorithm import "
                          "create_random_buttons_algorithm as create_algorithm\n")
FAILS_ONLY_IN_A_WORKER_PACKAGE = """
import multiprocessing
from tests.game.random_buttons_algorithm import create_random_buttons_algorithm

def create_algorithm(settings):
    if multiprocessing.parent_process() is not None:
        raise RuntimeError("broken in a worker process")
    return create_random_buttons_algorithm(settings)
"""
NOT_READY = "isn't ready"
# `py -m mario`, but with the run folders made in runs/ of the folder it runs in.
MARIO_WITH_RUNS_HERE = "from pathlib import Path; from mario.__main__ import main; main(runs_root=Path('runs'))"


def train_in(folder: Path, neuroevolution_init: str | None) -> subprocess.CompletedProcess:
    """Run `py -m mario train config.toml` in the folder, with the given neuroevolution/__init__.py."""
    (folder / "config.toml").write_text(SMALL_RUN_CONFIG)
    if neuroevolution_init is not None:
        (folder / "neuroevolution").mkdir()
        (folder / "neuroevolution" / "__init__.py").write_text(neuroevolution_init)
    environment = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}
    return subprocess.run([sys.executable, "-c", MARIO_WITH_RUNS_HERE, "train", "config.toml"], cwd=folder,
                          env=environment, capture_output=True, text=True, timeout=120)


@pytest.mark.parametrize("neuroevolution_init", [
    "raise ImportError('half-written')\n",                       # fails on import
    "def build_something_else(): pass\n",                        # no create_algorithm
    "def create_algorithm(settings):\n    raise NotImplementedError\n",
    "def create_algorithm(settings):\n    return object()\n",    # not a NeuroevolutionAlgorithm
    FAILS_ONLY_IN_A_WORKER_PACKAGE,
], ids=["fails-on-import", "no-create-algorithm", "create-algorithm-raises", "wrong-type",
        "create-algorithm-raises-only-in-a-worker"])
def test_train_exits_with_a_clear_message_when_the_users_package_isnt_working(tmp_path, neuroevolution_init):
    finished = train_in(tmp_path, neuroevolution_init)
    assert finished.returncode != 0
    assert "neuroevolution" in finished.stderr and NOT_READY in finished.stderr
    assert "Traceback" not in finished.stderr


def test_train_runs_every_generation_and_prints_one_line_each(tmp_path):
    finished = train_in(tmp_path, RANDOM_BUTTONS_PACKAGE)
    assert finished.returncode == 0, finished.stderr
    lines = finished.stdout.splitlines()
    assert [line.split(" · ")[0] for line in lines] == ["generation 1", "generation 2"]
    assert all("best fitness" in line and "mean fitness" in line and line.endswith(" s") for line in lines)


def test_train_records_the_run_in_its_own_folder_under_runs(tmp_path):
    finished = train_in(tmp_path, RANDOM_BUTTONS_PACKAGE)
    assert finished.returncode == 0, finished.stderr
    [run_folder] = (tmp_path / "runs").iterdir()
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}_smoke", run_folder.name)
    assert (run_folder / "config.toml").read_text() == SMALL_RUN_CONFIG
    assert sorted(path.name for path in (run_folder / "generations").iterdir()) == ["0001", "0002"]


@pytest.mark.parametrize("neuroevolution_init", [
    "raise ImportError('half-written')\n",
    FAILS_ONLY_IN_A_WORKER_PACKAGE,
], ids=["fails-on-import", "create-algorithm-raises-only-in-a-worker"])
def test_train_makes_no_run_folder_when_the_users_package_isnt_working(tmp_path, neuroevolution_init):
    finished = train_in(tmp_path, neuroevolution_init)
    assert NOT_READY in finished.stderr
    assert not (tmp_path / "runs").exists()


def test_run_folders_are_made_in_runs_at_the_repo_root_whatever_folder_train_is_run_from():
    from mario.__main__ import RUNS_ROOT
    assert RUNS_ROOT == REPO_ROOT / "runs"
    assert "runs/" in (REPO_ROOT / ".gitignore").read_text().splitlines()
