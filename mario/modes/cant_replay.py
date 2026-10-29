"""How both replays exit when the run folder can't give them what they replay (spec section 11):
with one line saying why, before any window opens or worker starts, and no traceback."""

from collections.abc import Iterator
from contextlib import contextmanager

CANT_REPLAY_MESSAGE = "Can't replay: {problem}."


@contextmanager
def exits_if_cant_replay() -> Iterator[None]:
    """A LookupError raised inside, by RecordedRun, exits with CANT_REPLAY_MESSAGE."""
    try:
        yield
    except LookupError as problem:
        raise SystemExit(CANT_REPLAY_MESSAGE.format(problem=problem.args[0])) from None
