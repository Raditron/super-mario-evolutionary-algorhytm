"""The shared memory watch-live's snapshots cross between processes in (spec section 11).

One slot per chunk, each guarded by its own lock. The worker playing a chunk
writes its latest ChunkSnapshot into the chunk's slot every tick, replacing the
last; the window reads every slot when it draws. A slot holds the length of the
pickled snapshot, then the snapshot.

The main process makes the channel; its writer, made of the memory's name and
the locks, goes to each worker process as it starts (under the spawn start
method, locks can be handed over only then) and is opened there.
"""

import multiprocessing
import pickle
from dataclasses import dataclass
from multiprocessing.shared_memory import SharedMemory
from multiprocessing.synchronize import Lock

from mario.constants.snapshots import SNAPSHOT_LENGTH_BYTE_ORDER, SNAPSHOT_LENGTH_BYTES, SNAPSHOT_SLOT_BYTES
from mario.constants.training import WORKER_START_METHOD
from mario.snapshots.live_snapshots import ChunkSnapshot


class SnapshotChannel:
    """The main process's side: it makes the memory, reads it, and frees it."""

    def __init__(self, slot_count: int):
        self._memory = SharedMemory(create=True, size=slot_count * SNAPSHOT_SLOT_BYTES)
        self._memory.buf[:] = bytes(len(self._memory.buf))  # every slot unwritten
        slot_locks = tuple(multiprocessing.get_context(WORKER_START_METHOD).Lock() for _ in range(slot_count))
        self.writer = SnapshotChannelWriter(self._memory.name, slot_locks)

    def read_all(self) -> list[ChunkSnapshot | None]:
        """The snapshot last written into each slot, None for a slot not yet written."""
        return [_read_slot(self._memory, slot, slot_lock) for slot, slot_lock in enumerate(self.writer.slot_locks)]

    def close(self) -> None:
        self._memory.close()
        self._memory.unlink()


@dataclass(frozen=True)
class SnapshotChannelWriter:
    """The workers' side, handed to each as it starts."""
    memory_name: str
    slot_locks: tuple[Lock, ...]

    def open(self) -> "OpenSnapshotChannelWriter":
        """Attach this process to the memory; done once per process."""
        return OpenSnapshotChannelWriter(SharedMemory(name=self.memory_name), self.slot_locks)


class OpenSnapshotChannelWriter:
    def __init__(self, memory: SharedMemory, slot_locks: tuple[Lock, ...]):
        self._memory = memory
        self._slot_locks = slot_locks

    def write(self, slot: int, snapshot: ChunkSnapshot) -> None:
        """Replace what the slot holds with this snapshot."""
        pickled = pickle.dumps(snapshot, protocol=pickle.HIGHEST_PROTOCOL)
        if SNAPSHOT_LENGTH_BYTES + len(pickled) > SNAPSHOT_SLOT_BYTES:
            raise ValueError(f"a chunk snapshot of {len(pickled)} bytes doesn't fit a slot of "
                             f"{SNAPSHOT_SLOT_BYTES}: play smaller chunks or make SNAPSHOT_SLOT_BYTES bigger")
        length_bytes, snapshot_start = _slot_layout(slot)
        with self._slot_locks[slot]:
            self._memory.buf[length_bytes] = len(pickled).to_bytes(SNAPSHOT_LENGTH_BYTES, SNAPSHOT_LENGTH_BYTE_ORDER)
            self._memory.buf[snapshot_start:snapshot_start + len(pickled)] = pickled


def _read_slot(memory: SharedMemory, slot: int, slot_lock: Lock) -> ChunkSnapshot | None:
    length_bytes, snapshot_start = _slot_layout(slot)
    with slot_lock:
        length = int.from_bytes(memory.buf[length_bytes], SNAPSHOT_LENGTH_BYTE_ORDER)
        pickled = bytes(memory.buf[snapshot_start:snapshot_start + length])
    return pickle.loads(pickled) if length else None


def _slot_layout(slot: int) -> tuple[slice, int]:
    """Where in the memory the slot keeps its snapshot's length, and where the snapshot starts."""
    slot_start = slot * SNAPSHOT_SLOT_BYTES
    return slice(slot_start, slot_start + SNAPSHOT_LENGTH_BYTES), slot_start + SNAPSHOT_LENGTH_BYTES
