"""py -m mario replay <run-folder> [--generation N], without --best: all-ghost replay
(spec sections 2, 8 and 11).

Every agent of the generation is replayed from its Controller log through
watch-live's own pipeline: the worker pool plays the chunks in lock-step at the
game's own speed, the buttons coming from ControllerLogChunkControllerSourceFactory,
and WatchLive shows the snapshots they publish in the shared Viewer, with the
followed agent, the ghosts and the HUD's generation line. Once the generation has
played out, it stays shown until the viewer quits (Esc or closing the window);
quitting earlier stops the workers at once. No algorithm is built and no genome
is run, so it never imports the user's neuroevolution package.
"""

from pathlib import Path

import numpy as np

from mario.modes.cant_replay import exits_if_cant_replay
from mario.modes.watch_live import WatchLive
from mario.recording.recorded_run import RecordedRun
from mario.training.agent_worker_pool import AgentWorkerPool
from mario.training.controller_log_chunk_controller_source import ControllerLogChunkControllerSourceFactory
from mario.training.play_watcher import ViewerClosed

REPLAYING_ALL_MESSAGE = "Replaying generation {generation}: all {agent_count} agents, as ghosts."


class AllGhostReplayMode:
    def __init__(self, generation: int, controller_logs: list[np.ndarray], watch_live: WatchLive):
        """controller_logs: every agent's Controller log, in agent order. watch_live:
        keeps showing the generation once played, until the viewer quits."""
        self._generation = generation
        self._controller_logs = controller_logs
        self._watch_live = watch_live

    @classmethod
    def of_generation(cls, run_folder_path: Path, generation: int | None, sprites_folder: Path) -> "AllGhostReplayMode":
        """Every agent of the generation, by default the last one recorded. Exits with
        a message, before any worker starts or window opens, if the run folder can't give them."""
        recorded_run = RecordedRun(run_folder_path)
        with exits_if_cant_replay():
            replayed_generation = recorded_run.generation_or_last(generation)
            controller_logs = recorded_run.controller_logs(replayed_generation)
        print(REPLAYING_ALL_MESSAGE.format(generation=replayed_generation, agent_count=len(controller_logs)),
              flush=True)
        return cls(replayed_generation, controller_logs,
                   WatchLive.in_a_window(sprites_folder, keeps_showing_once_played=True))

    def run(self) -> None:
        try:
            with AgentWorkerPool(ControllerLogChunkControllerSourceFactory(),
                                 play_watcher=self._watch_live) as worker_pool:
                worker_pool.play(self._controller_logs, self._generation)
        except ViewerClosed:  # the only way a replay's watcher is left; the workers are stopped, not waited for
            pass
        finally:
            self._watch_live.close()
