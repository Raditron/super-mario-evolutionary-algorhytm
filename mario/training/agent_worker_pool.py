"""The worker processes that play a generation's agents (spec section 9, #4).

A persistent spawn-context pool, created once per run. Each worker loads its
own World 1-1 and builds its own algorithm once, through the same
create_algorithm the main process uses. Each generation, the genomes are split
into contiguous chunks, each worker plays its chunks in lock-step with a brain
built from their genomes, and the PlayedAttempts come back in agent order.

A worker whose algorithm fails to build doesn't raise while starting (the pool
would only start it again, forever); it reports why back to the main process,
and the pool, once every worker has reported, stops them all and raises
WorkerStartError before anything is played.

Given a PlayWatcher, the generations are watched (spec section 11): every chunk
plays at once, each in a process of its own, at the game's own speed, writing
its snapshots into a SnapshotChannel with one slot per chunk, while the main
process hands itself to the watcher until the generation has been played. The
chunks are the very ones a headless run plays, so every brain gets the same
rows and the results are the same. Unwatched, nothing is written or paced.
"""

import multiprocessing
import os
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from multiprocessing.queues import SimpleQueue

import numpy as np

from mario.constants.training import (
    BLAS_THREAD_COUNT_VARIABLES,
    BLAS_THREADS_PER_WORKER,
    CHUNKS_PER_WORKER,
    TRAINING_WORKER_COUNT,
    WORKER_START_METHOD,
)
from mario.level.static_level import StaticLevel
from mario.simulation.observation_builder import ObservationBuilder
from mario.snapshots.live_chunk_publisher import LiveChunkPublisher
from mario.snapshots.snapshot_channel import OpenSnapshotChannelWriter, SnapshotChannel, SnapshotChannelWriter
from mario.training.algorithm_factory import AlgorithmFactory
from mario.training.chunk_player import ChunkPlayer, PlayedAttempt
from mario.training.neuroevolution_algorithm import NeuroevolutionAlgorithm
from mario.training.play_watcher import PlayWatcher


class WorkerStartError(RuntimeError):
    """A worker process couldn't build the algorithm; the message says why."""


@dataclass(frozen=True)
class ChunkToPlay:
    """One chunk of a generation, as sent to a worker: its genomes, in agent order."""
    generation: int
    chunk_index: int                                  # also its slot in the snapshot channel
    first_agent: int                                  # the generation's index of its first agent
    genomes: list[np.ndarray]


class AgentWorkerPool:
    def __init__(self, algorithm_factory: AlgorithmFactory, worker_count: int = TRAINING_WORKER_COUNT,
                 play_watcher: PlayWatcher | None = None):
        """Starts the workers and waits until each has built its algorithm. Watched,
        it starts one per chunk instead: worker_count x CHUNKS_PER_WORKER.

        Raises WorkerStartError, with every worker stopped, if any couldn't."""
        self._chunk_count = worker_count * CHUNKS_PER_WORKER
        self._play_watcher = play_watcher
        self._snapshot_channel = SnapshotChannel(self._chunk_count) if play_watcher is not None else None
        channel_writer = self._snapshot_channel.writer if self._snapshot_channel is not None else None
        process_count = self._chunk_count if play_watcher is not None else worker_count
        context = multiprocessing.get_context(WORKER_START_METHOD)
        start_reports = context.SimpleQueue()
        with _blas_pinned_in_new_processes():
            self._pool = context.Pool(process_count, initializer=_start_worker,
                                      initargs=(algorithm_factory, start_reports, channel_writer))
        start_failures = [start_failure for start_failure in (start_reports.get() for _ in range(process_count))
                          if start_failure]
        if start_failures:
            self._pool.terminate()
            self._pool.join()
            self._close_snapshot_channel()
            raise WorkerStartError(start_failures[0])

    def __enter__(self) -> "AgentWorkerPool":
        return self

    def __exit__(self, exception_type, exception, traceback) -> None:
        if exception_type is None:
            self._pool.close()
        else:
            self._pool.terminate()
        self._pool.join()
        self._close_snapshot_channel()

    def play(self, genomes: list[np.ndarray], generation: int) -> list[PlayedAttempt]:
        """One training attempt per genome; the results line up with the genomes.

        Watched, it returns once the watcher has shown the whole generation, and
        raises ViewerClosed, returning nothing, if the window is closed first."""
        agent_chunks = [agents for agents in np.array_split(np.arange(len(genomes)), self._chunk_count) if len(agents)]
        chunks = [ChunkToPlay(generation, chunk_index, int(agents[0]), [genomes[agent] for agent in agents])
                  for chunk_index, agents in enumerate(agent_chunks)]
        if self._play_watcher is None:
            played_chunks = self._pool.map(_play_chunk, chunks, chunksize=1)
        else:
            chunks_being_played = self._pool.map_async(_play_chunk, chunks, chunksize=1)
            self._play_watcher.watch_until_played(generation, len(genomes), self._snapshot_channel,
                                                  chunks_being_played.ready)
            played_chunks = chunks_being_played.get()
        return [played_attempt for played_chunk in played_chunks for played_attempt in played_chunk]

    def _close_snapshot_channel(self) -> None:
        if self._snapshot_channel is not None:
            self._snapshot_channel.close()
            self._snapshot_channel = None


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
    """What one worker process keeps for the whole run: its algorithm and its level,
    and, watched, its way into the snapshot channel."""

    def __init__(self, algorithm: NeuroevolutionAlgorithm, channel_writer: OpenSnapshotChannelWriter | None):
        level = StaticLevel.load_world_1_1()
        self._algorithm = algorithm
        self._chunk_player = ChunkPlayer(level)
        self._observation_builder = ObservationBuilder(level)
        self._channel_writer = channel_writer

    def play(self, chunk: ChunkToPlay) -> list[PlayedAttempt]:
        publisher = None
        if self._channel_writer is not None:
            publisher = LiveChunkPublisher(self._channel_writer, chunk.chunk_index, chunk.generation,
                                           chunk.first_agent, self._observation_builder)
        return self._chunk_player.play(self._algorithm.build_brain(chunk.genomes), len(chunk.genomes), publisher)


# The worker of this process, set once when the pool starts it.
_this_process_worker: _Worker | None = None


def _start_worker(algorithm_factory: AlgorithmFactory, start_reports: SimpleQueue,
                  channel_writer: SnapshotChannelWriter | None) -> None:
    """Builds this process's worker, then reports to the main process: why it couldn't, or "" if it could.

    channel_writer: watched, the snapshot channel's writer, which this process opens once."""
    global _this_process_worker
    try:
        algorithm = algorithm_factory.create()
    except Exception as problem:  # the user's code, half-written
        start_reports.put(f"create_algorithm(settings) failed in a worker process "
                          f"({type(problem).__name__}: {problem})")
        return
    _this_process_worker = _Worker(algorithm, channel_writer.open() if channel_writer is not None else None)
    start_reports.put("")


def _play_chunk(chunk: ChunkToPlay) -> list[PlayedAttempt]:
    return _this_process_worker.play(chunk)
