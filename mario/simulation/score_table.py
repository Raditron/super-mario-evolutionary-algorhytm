"""The original's score table (FloateyNumTileData): the stomp chain, a shell's
kick and a moving shell's defeats each score one of its steps."""

from mario.constants.scoring import SCORE_TABLE_POINTS


def score_table_points(step: int) -> int | None:
    """The score table's points at this step, from 1; None beyond it (a 1-UP in the original)."""
    return SCORE_TABLE_POINTS[step - 1] if step <= len(SCORE_TABLE_POINTS) else None
