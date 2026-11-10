"""The picture a pipe tile is drawn with, chosen from its neighbouring tiles, so a
pipe two tiles wide draws as one wide pipe with a rim on its top row and not as
two thin tubes side by side.

An upright pipe's tile with no pipe tile above it is the rim, otherwise the body;
with no pipe tile on its left it is the left half, otherwise the right half. A
tile on the playfield's top row is the body: the pipe runs on above it, as the
bonus room's shaft does (RenderSidewaysPipe draws it from the block buffer's top,
with no rim).

The bonus room's exit pipe lies on its side, two tiles high, its mouth on the
left (ExitPipe): a sideways pipe's tile with no sideways pipe on its left is the
mouth, otherwise the body; with no sideways pipe above it, it is the top half,
otherwise the bottom half. Where it meets the upright shaft on its right, the
shaft's left half is the joint (SidePipeTopPart, SidePipeBottomPart: $1e over $21).
"""

from dataclasses import dataclass

from mario.constants.level import PLAYFIELD_TOP_ROW
from mario.level.tile_kind import TileKind
from mario.snapshots.world_snapshot import VisibleTiles

PIPE_RIM_LEFT_SPRITE_NAME = "pipe_rim_left"
PIPE_RIM_RIGHT_SPRITE_NAME = "pipe_rim_right"
PIPE_BODY_LEFT_SPRITE_NAME = "pipe_body_left"
PIPE_BODY_RIGHT_SPRITE_NAME = "pipe_body_right"
PIPE_JOINT_TOP_SPRITE_NAME = "pipe_joint_top"
PIPE_JOINT_BOTTOM_SPRITE_NAME = "pipe_joint_bottom"
SIDE_PIPE_MOUTH_TOP_SPRITE_NAME = "side_pipe_mouth_top"
SIDE_PIPE_MOUTH_BOTTOM_SPRITE_NAME = "side_pipe_mouth_bottom"
SIDE_PIPE_BODY_TOP_SPRITE_NAME = "side_pipe_body_top"
SIDE_PIPE_BODY_BOTTOM_SPRITE_NAME = "side_pipe_body_bottom"


@dataclass(frozen=True)
class PipeNeighbourhood:
    """Whether an upright pipe tile's neighbours are pipe tiles, and whether a
    sideways pipe joins it from its left (on its left, and above that). A
    neighbour outside the visible tiles is None: the snapshot holds only the
    columns on screen."""

    pipe_on_left: bool | None
    pipe_on_right: bool | None
    pipe_above: bool | None
    side_pipe_on_left: bool | None = False
    side_pipe_above_left: bool | None = False

    @classmethod
    def around(cls, tiles: VisibleTiles, column: int, row: int) -> "PipeNeighbourhood":
        runs_on_above_the_playfield = row == PLAYFIELD_TOP_ROW
        return cls(pipe_on_left=_is_kind(tiles, column - 1, row, TileKind.PIPE),
                   pipe_on_right=_is_kind(tiles, column + 1, row, TileKind.PIPE),
                   pipe_above=runs_on_above_the_playfield or _is_kind(tiles, column, row - 1, TileKind.PIPE),
                   side_pipe_on_left=_is_kind(tiles, column - 1, row, TileKind.SIDE_PIPE),
                   side_pipe_above_left=_is_kind(tiles, column - 1, row - 1, TileKind.SIDE_PIPE))

    @property
    def is_joint(self) -> bool:
        return self.side_pipe_on_left is True

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


@dataclass(frozen=True)
class SidePipeNeighbourhood:
    """Whether a sideways pipe tile has sideways pipe on its left and above it;
    None outside the visible tiles, where it counts as none."""

    side_pipe_on_left: bool | None
    side_pipe_above: bool | None

    @classmethod
    def around(cls, tiles: VisibleTiles, column: int, row: int) -> "SidePipeNeighbourhood":
        return cls(side_pipe_on_left=_is_kind(tiles, column - 1, row, TileKind.SIDE_PIPE),
                   side_pipe_above=_is_kind(tiles, column, row - 1, TileKind.SIDE_PIPE))

    @property
    def is_mouth(self) -> bool:
        return self.side_pipe_on_left is not True

    @property
    def is_top_half(self) -> bool:
        return self.side_pipe_above is not True


def pipe_sprite_name(neighbourhood: PipeNeighbourhood) -> str:
    """The name of the sprite the upright pipe tile is drawn with."""
    if neighbourhood.is_joint:
        joint_is_top = neighbourhood.side_pipe_above_left is not True
        return PIPE_JOINT_TOP_SPRITE_NAME if joint_is_top else PIPE_JOINT_BOTTOM_SPRITE_NAME
    if neighbourhood.is_rim:
        return PIPE_RIM_LEFT_SPRITE_NAME if neighbourhood.is_left_half else PIPE_RIM_RIGHT_SPRITE_NAME
    return PIPE_BODY_LEFT_SPRITE_NAME if neighbourhood.is_left_half else PIPE_BODY_RIGHT_SPRITE_NAME


def side_pipe_sprite_name(neighbourhood: SidePipeNeighbourhood) -> str:
    """The name of the sprite the sideways pipe tile is drawn with."""
    if neighbourhood.is_mouth:
        return SIDE_PIPE_MOUTH_TOP_SPRITE_NAME if neighbourhood.is_top_half else SIDE_PIPE_MOUTH_BOTTOM_SPRITE_NAME
    return SIDE_PIPE_BODY_TOP_SPRITE_NAME if neighbourhood.is_top_half else SIDE_PIPE_BODY_BOTTOM_SPRITE_NAME


def _is_kind(tiles: VisibleTiles, column: int, row: int, kind: TileKind) -> bool | None:
    """Whether the tile is of the kind, or None outside the visible tiles."""
    column_offset = column - tiles.first_column
    if not 0 <= row < len(tiles.rows) or not 0 <= column_offset < len(tiles.rows[row]):
        return None
    return tiles.rows[row][column_offset] is kind
