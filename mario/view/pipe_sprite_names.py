"""The picture a pipe tile is drawn with, chosen from its neighbouring tiles, so a
pipe two tiles wide draws as one wide pipe with a rim on its top row and not as
two thin tubes side by side.

A pipe tile with no pipe tile above it is the rim, otherwise the body; with no
pipe tile on its left it is the left half, otherwise the right half.
"""

from dataclasses import dataclass

from mario.level.tile_kind import TileKind
from mario.snapshots.world_snapshot import VisibleTiles

PIPE_RIM_LEFT_SPRITE_NAME = "pipe_rim_left"
PIPE_RIM_RIGHT_SPRITE_NAME = "pipe_rim_right"
PIPE_BODY_LEFT_SPRITE_NAME = "pipe_body_left"
PIPE_BODY_RIGHT_SPRITE_NAME = "pipe_body_right"


@dataclass(frozen=True)
class PipeNeighbourhood:
    """Whether a pipe tile's neighbours are pipe tiles. A neighbour outside the
    visible tiles is None: the snapshot holds only the columns on screen."""

    pipe_on_left: bool | None
    pipe_on_right: bool | None
    pipe_above: bool | None

    @classmethod
    def around(cls, tiles: VisibleTiles, column: int, row: int) -> "PipeNeighbourhood":
        return cls(pipe_on_left=_is_pipe(tiles, column - 1, row), pipe_on_right=_is_pipe(tiles, column + 1, row),
                   pipe_above=_is_pipe(tiles, column, row - 1))

    @property
    def is_left_half(self) -> bool:
        """No pipe on its left. A pipe is two tiles wide, so a tile whose left
        neighbour is off screen is the left half when pipe is on its right."""
        if self.pipe_on_left is None:
            return self.pipe_on_right is True
        return not self.pipe_on_left

    @property
    def is_rim(self) -> bool:
        return self.pipe_above is not True


def pipe_sprite_name(neighbourhood: PipeNeighbourhood) -> str:
    """The name of the sprite the pipe tile is drawn with."""
    if neighbourhood.is_rim:
        return PIPE_RIM_LEFT_SPRITE_NAME if neighbourhood.is_left_half else PIPE_RIM_RIGHT_SPRITE_NAME
    return PIPE_BODY_LEFT_SPRITE_NAME if neighbourhood.is_left_half else PIPE_BODY_RIGHT_SPRITE_NAME


def _is_pipe(tiles: VisibleTiles, column: int, row: int) -> bool | None:
    """Whether the tile is a pipe tile, or None outside the visible tiles."""
    column_offset = column - tiles.first_column
    if not 0 <= row < len(tiles.rows) or not 0 <= column_offset < len(tiles.rows[row]):
        return None
    return tiles.rows[row][column_offset] is TileKind.PIPE
