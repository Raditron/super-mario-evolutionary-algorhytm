"""py -m mario train --watch (#29, spec sections 2, 8 and 11): the run is shown live in the
shared Viewer, and closing its window stops the run cleanly, its folder keeping
only complete generations. Driven by the random-buttons double in place of the
user's package.
"""

import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import pygame
import pytest

import mario
from mario.modes.train_mode import TrainMode
from mario.recording.recorded_run import RecordedRun
from mario.view.window import WindowEvents
from tests.game.mario_with_a_frame_budget import FRAMES_SHOWN_PREFIX
from tests.game.random_buttons_algorithm import create_random_buttons_algorithm
from tests.game.scripted_window import CLOSED, NOTHING_PRESSED, ScriptedWindow
from tests.game.test_train_mode import RANDOM_BUTTONS_PACKAGE

REPO_ROOT = Path(mario.__file__).parent.parent
FRAME_BUDGET_SCRIPT = Path(__file__).parent / "mario_with_a_frame_budget.py"
THREE_GENERATION_CONFIG = """
[run]
name = "watched"
seed = 5
generations = 3
population_size = 6

[algorithm]
"""
STOPPED = "training stopped"
# Few enough frames to close the window early in the first generation.
FRAME_BUDGET = 20
# Closed at the start of a generation, the run stops well within this, though
# the generation's attempts would take longer: each lasts at least the stall
# limit's 3 seconds at the game's own speed.
SECONDS_TO_STOP = 2.0


@dataclass
class ClosesOnceGenerationOneIsRecorded(ScriptedWindow):
    """Shows frames until the run folder holds generation 1, then is closed: part-way into generation 2."""
    runs_root: Path | None = None
    closed_at: float | None = None

    def poll_events(self) -> WindowEvents:
        if self.closed_at is None and list(self.runs_root.glob("*/generations/0001/controller_logs.npz")):
            self.closed_at = time.perf_counter()
        return CLOSED if self.closed_at is not None else NOTHING_PRESSED


@pytest.fixture
def fonts():
    """The renderers need pygame's fonts, which the real Window initialises."""
    pygame.font.init()
    yield
    pygame.font.quit()


@pytest.fixture
def watched_train_mode(fonts, tmp_path, monkeypatch) -> tuple[TrainMode, ClosesOnceGenerationOneIsRecorded]:
    config_path = tmp_path / "config.toml"
    config_path.write_text(THREE_GENERATION_CONFIG)
    window = ClosesOnceGenerationOneIsRecorded([], runs_root=tmp_path / "runs")
    monkeypatch.setattr("mario.modes.train_mode._import_create_algorithm", lambda: create_random_buttons_algorithm)
    monkeypatch.setattr("mario.modes.watch_live.Window", lambda: window)
    return TrainMode(config_path, tmp_path / "runs", watch=True, sprites_folder=tmp_path), window


def test_closing_the_watch_window_stops_the_run_leaving_only_its_complete_generations(watched_train_mode, capsys):
    train_mode, window = watched_train_mode
    train_mode.run()
    assert time.perf_counter() - window.closed_at < SECONDS_TO_STOP  # the workers are stopped, not waited for
    [run_folder] = window.runs_root.iterdir()
    assert RecordedRun(run_folder).last_generation() == 1
    assert sorted(path.name for path in (run_folder / "generations").iterdir()) == ["0001"]
    assert STOPPED in capsys.readouterr().out
    assert window.frames_shown and window.is_closed


def train_watched_in(folder: Path, frame_budget: int) -> subprocess.CompletedProcess:
    """`py -m mario train config.toml --watch` in the folder, with the random-buttons double as the
    user's package and the window closed after the frame budget."""
    (folder / "config.toml").write_text(THREE_GENERATION_CONFIG)
    (folder / "neuroevolution").mkdir()
    (folder / "neuroevolution" / "__init__.py").write_text(RANDOM_BUTTONS_PACKAGE)
    return subprocess.run(
        [sys.executable, str(FRAME_BUDGET_SCRIPT), str(frame_budget), "train", "config.toml", "--watch"],
        cwd=folder, capture_output=True, text=True, timeout=180,
        env={**os.environ, "SDL_VIDEODRIVER": "dummy", "PYTHONPATH": os.pathsep.join([str(folder), str(REPO_ROOT)])})


def test_py_m_mario_train_watch_opens_the_window_and_stops_cleanly_when_it_is_closed(tmp_path):
    finished = train_watched_in(tmp_path, FRAME_BUDGET)
    assert finished.returncode == 0, finished.stderr
    assert "Traceback" not in finished.stderr
    assert f"{FRAMES_SHOWN_PREFIX}{FRAME_BUDGET}" in finished.stdout
    assert STOPPED in finished.stdout
    [run_folder] = (tmp_path / "runs").iterdir()
    with pytest.raises(LookupError, match="no generation recorded"):  # closed during the first generation
        RecordedRun(run_folder).last_generation()


def test_headless_train_opens_no_window(tmp_path):
    """Without --watch nothing is drawn: no frame is shown, and pygame isn't even loaded."""
    (tmp_path / "config.toml").write_text(THREE_GENERATION_CONFIG)
    (tmp_path / "neuroevolution").mkdir()
    (tmp_path / "neuroevolution" / "__init__.py").write_text(RANDOM_BUTTONS_PACKAGE)
    probe = ("import sys; from pathlib import Path; from mario.__main__ import main; "
             "main(runs_root=Path('runs')); print('pygame loaded:', 'pygame' in sys.modules)")
    finished = subprocess.run([sys.executable, "-c", probe, "train", "config.toml"], cwd=tmp_path,
                              capture_output=True, text=True, timeout=180,
                              env={**os.environ, "PYTHONPATH": os.pathsep.join([str(tmp_path), str(REPO_ROOT)])})
    assert finished.returncode == 0, finished.stderr
    assert "pygame loaded: False" in finished.stdout
