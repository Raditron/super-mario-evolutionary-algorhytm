"""The worker processes that play a generation's agents (spec section 9, #4).

A persistent spawn-context pool, created once per run. Each worker loads its
own World 1-1 and builds its own algorithm once, through the same
create_algorithm the main process uses. Each generation, the genomes are split
into contiguous chunks, each worker plays its chunks in lock-step with a brain
built from their genomes, and the PlayedAttempts come back in agent order.
"""

import multiprocessing
import os
from collections.abc import Callable, Iterator
from contextlib import contextmanager

import numpy as np

from mario.constants.training import (
    BLAS_THREAD_COUNT_VARIABLES,
    BLAS_THREADS_PER_WORKER,
    CHUNKS_PER_WORKER,
    TRAINING_WORKER_COUNT,
)
from mario.level.static_level import StaticLevel
from mario.training.chunk_player import ChunkPlayer, PlayedAttempt
from mario.training.neuroevolution_algorithm import NeuroevolutionAlgorithm

# How every process builds the user's algorithm: create_algorithm(settings).
AlgorithmFactory = Callable[[dict], NeuroevolutionAlgorithm]

# Workers are started fresh rather than forked, the same on every platform.
WORKER_START_METHOD = "spawn"


class AgentWorkerPool:
    def __init__(self, create_algorithm: AlgorithmFactory, algorithm_settings: dict,
                 worker_count: int = TRAINING_WORKER_COUNT):
        """create_algorithm must be importable by name (a module-level function), since
        each worker process imports it to build its own algorithm."""
        self._chunk_count = worker_count * CHUNKS_PER_WORKER
        with _blas_pinned_in_new_processes():
            self._pool = multiprocessing.get_context(WORKER_START_METHOD).Pool(
                worker_count, initializer=_start_worker, initargs=(create_algorithm, algorithm_settings))

    def __enter__(self) -> "AgentWorkerPool":
        return self

    def __exit__(self, exception_type, exception, traceback) -> None:
        if exception_type is None:
            self._pool.close()
        else:
            self._pool.terminate()
        self._pool.join()

    def play(self, genomes: list[np.ndarray]) -> list[PlayedAttempt]:
        """One training attempt per genome; the results line up with the genomes."""
        chunks = [[genomes[agent] for agent in agents]
                  for agents in np.array_split(np.arange(len(genomes)), self._chunk_count) if len(agents)]
        played_chunks = self._pool.map(_play_chunk, chunks, chunksize=1)
        return [played_attempt for played_chunk in played_chunks for played_attempt in played_chunk]


@contextmanager
def _blas_pinned_in_new_processes() -> Iterator[None]:
    """Processes started inside this block inherit the BLAS thread limit; this one is left as it was."""
    saved_values = {name: os.environ.get(name) for name in BLAS_THREAD_COUNT_VARIABLES}
    os.environ.update({name: str(BLAS_THREADS_PER_WORKER) for name in BLAS_THREAD_COUNT_VARIABLES})
    try:
        yield
    finally:
        for name, saved_value in saved_values.items():
            if saved_value is None:
                del os.environ[name]
            else:
                os.environ[name] = saved_value


class _Worker:
    """What one worker process keeps for the whole run: its algorithm and its level."""

    def __init__(self, algorithm: NeuroevolutionAlgorithm):
        self._algorithm = algorithm
        self._chunk_player = ChunkPlayer(StaticLevel.load_world_1_1())

    def play(self, genomes: list[np.ndarray]) -> list[PlayedAttempt]:
        return self._chunk_player.play(self._algorithm.build_brain(genomes), len(genomes))


# The worker of this process, set once when the pool starts it.
_this_process_worker: _Worker | None = None


def _start_worker(create_algorithm: AlgorithmFactory, algorithm_settings: dict) -> None:
    global _this_process_worker
    _this_process_worker = _Worker(create_algorithm(algorithm_settings))


def _play_chunk(genomes: list[np.ndarray]) -> list[PlayedAttempt]:
    return _this_process_worker.play(genomes)
