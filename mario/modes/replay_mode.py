"""py -m mario replay <run-folder> [--generation N] --best: best-agent replay (spec sections 2 and 11).

One Mario in the main process: the best agent's recorded attempt, rebuilt from
its Controller log by a ReplaySession, shown in the Viewer with both views (F1),
the HUD and the Debug view's overlay. Once the attempt (and, if it reached the
flag, the end of the level) is over, the last frame stays until the viewer quits.
It never imports the user's neuroevolution package, so it works while that is
empty or half-written.
"""

from pathlib import Path

from mario.level.static_level import StaticLevel
from mario.modes.replay_session import ReplaySession
from mario.recording.recorded_run import RecordedRun
from mario.view.viewer import Viewer
from mario.view.window import Window

REPLAYING_MESSAGE = ("Replaying generation {row.generation}, best agent {row.agent_index} (fitness {row.fitness}): "
                     "its attempt ended {row.end_reason} at furthest_x {row.furthest_x} "
                     "after {row.ticks_elapsed} ticks.")
CANT_REPLAY_MESSAGE = "Can't replay: {problem}."


class ReplayMode:
    def __init__(self, session: ReplaySession, viewer: Viewer):
        self._session = session
        self._viewer = viewer

    @classmethod
    def of_best_agent(cls, run_folder_path: Path, generation: int | None, sprites_folder: Path) -> "ReplayMode":
        """The best agent of the generation, by default the last one recorded. Exits
        with a message, before any window opens, if the run folder can't give it."""
        recorded_run = RecordedRun(run_folder_path)
        try:
            replayed_generation = recorded_run.last_generation() if generation is None else generation
            best_agent = recorded_run.best_agent(replayed_generation)
        except LookupError as problem:
            raise SystemExit(CANT_REPLAY_MESSAGE.format(problem=problem.args[0])) from None
        print(REPLAYING_MESSAGE.format(row=best_agent))
        session = ReplaySession(recorded_run.controller_log(replayed_generation, best_agent.agent_index),
                                StaticLevel.load_world_1_1())
        return cls(session, Viewer.with_both_views(Window(), sprites_folder))

    def run(self) -> None:
        try:
            while not self._viewer.handle_events():
                self._session.step()
                self._viewer.show(self._session.snapshot())
        finally:
            self._viewer.close()
