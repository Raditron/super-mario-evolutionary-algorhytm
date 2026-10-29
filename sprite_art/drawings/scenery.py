"""The background scenery: one picture per tile, repeated across every tile of a kind,
so each tiles seamlessly with itself."""

from sprite_art.palettes.scenery import SCENERY_PALETTE
from sprite_art.sprite_drawing import SpriteDrawing

CLOUD = SpriteDrawing("cloud", SCENERY_PALETTE, (
    "...WWWWWWWWWW...",
    ".WWWWWWWWWWWWWW.",
    ".WWWWWWWWWWWWWW.",
    "WWWWWWWWWWWWWWWW",
    "WWWWWWWWWWWWWWWW",
    "WWWWWWWWWWWWWWWW",
    "WWWWWWWWWWWWWWWW",
    "WWWWWWWWWWWWWWWW",
    "WWWWWWWWWWWWWWWs",
    "WWWWWWWWWWWWWWWs",
    "WWWWWWWWWWWWWWss",
    "WWWWWWWWWWWWWWss",
    "sWWWWWWWWWWWWsss",
    ".sWWWWWWWWWWsss.",
    ".sssssssssssssS.",
    "...SSSSSSSSSS...",
))

HILL = SpriteDrawing("hill", SCENERY_PALETTE, (
    "GGGGGGGGGGGGGGGG",
    "GGGLGGGGGGGGGGGG",
    "GGLgLGGGGGGGGgGG",
    "GGGGGGGGGGGGGGGG",
    "GGGGGGGGGLGGGGGG",
    "GgGGGGGGLgLGGGGG",
    "GGGGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGGLG",
    "GGGGLGGGGGGGGLgL",
    "GGGLgLGGGgGGGGGG",
    "GGGGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGGGG",
    "GGGGGGGGGGLGGGGG",
    "GGgGGGGGGLgLGGGG",
    "GGGGGGGGGGGGGGGG",
    "GGGGGGGGGGGGGGgG",
))

BUSH = SpriteDrawing("bush", SCENERY_PALETTE, (
    "................",
    "..JJJJJ.........",
    ".JJBBBBB........",
    "JJBBBBBbb..JJJ..",
    "JBBBBBBBb.JJBBB.",
    "JBBBBBBBbJJBBBBb",
    "BBBBBBBbbJBBBBJJ",
    "JJBBBBJJJJJBBbBB",
    "BBBbbJBBBBBBbBBB",
    "BBBbbBBBBBBbbBBB",
    "BBBbJBBBBBBbbBBB",
    "bBbJJJBBBBBbJJJb",
    "bbJJBBBBBJJJBBBb",
    "bbJBBBBbbJBBBbbb",
    "bbBBBBBbbBBBBbbb",
    "bbbBBbbbbbBBbbbb",
))

CASTLE_BRICK = SpriteDrawing("castle_brick", SCENERY_PALETTE, (
    "VVVVVVVVVVVVVVVc",
    "VCCCCCCCCCCCCCvc",
    "VCCCCvCCCCCCCCvc",
    "VCCCCCCCCCCCCCvc",
    "VCCCCCCCCCCvCCvc",
    "VCCCCCCCCCCCCCvc",
    "Vvvvvvvvvvvvvvvc",
    "cccccccccccccccc",
    "VVVVVVVcVVVVVVVV",
    "CCCCCCvcVCCCCCCC",
    "CCCCCCvcVCCCCCCC",
    "CCvCCCvcVCCCCCCC",
    "CCCCCCvcVCCCCvCC",
    "CCCCCCvcVCCCCCCC",
    "vvvvvvvcVvvvvvvv",
    "cccccccccccccccc",
))

CASTLE_BATTLEMENT = SpriteDrawing("castle_battlement", SCENERY_PALETTE, (
    "....VVVVVVVV....",
    "....VCCCCCCv....",
    "....VCCCCCCv....",
    "....VCCCvCCv....",
    "....VCCCCCCv....",
    "VVVcVCCCCCCvcVVV",
    "vvvcvvvvvvvvcvvv",
    "cccccccccccccccc",
) + CASTLE_BRICK.rows[8:])

CASTLE_WINDOW = SpriteDrawing("castle_window", SCENERY_PALETTE, (
    "VVVVVVVVVVVVVVVc",
    "VCCCCCccccCCCCvc",
    "VCCCCcOOOOcCCCvc",
    "VCCCcOOOOOOcCCvc",
    "VCCCcOOOOOocCCvc",
    "VCCCcOOOOOocCCvc",
    "VvvvcOOOOOocvvvc",
    "cccccOOOOOoccccc",
    "VVVVcOOOOOocVVVV",
    "CCCCcOOOOOocCCCC",
    "CCCCcOOOOOocCCCC",
    "CCvCcOOOOOocCCCC",
    "CCCCcoooooocCCCC",
    "CCCVVVVVVVVVVCCC",
    "vvvccccccccccvvv",
    "cccccccccccccccc",
))

CASTLE_DOOR_ARCH = SpriteDrawing("castle_door_arch", SCENERY_PALETTE, (
    "VVVVVccccccVVVVc",
    "VCCccVVVVVVccCvc",
    "VCcVVVccccVVVcvc",
    "VcVVccOOOOccVVcc",
    "cVVcOOOOOOOOcVVc",
    "VVcNnNNnnNNnNcVv",
    "VcNNnNNnnNNnNNcv",
    "VcNNnNNnnNNnNNcv",
    "VcNNnNNnnNNnNNcv",
    "VcIIIIInnIIIIIcv",
    "VcNNnNNnnNNnNNcv",
    "VcNNnNNnnNNnNNcv",
    "VcNNnNNnnNNnNNcv",
    "VcNNnNNnnNNnNNcv",
    "VcNNnNNnnNNnNNcv",
    "VcNNnNNnnNNnNNcv",
))

CASTLE_DOOR = SpriteDrawing("castle_door", SCENERY_PALETTE, (
    "VcNNnNNnnNNnNNcv",
    "VcNNnNNnnNNnNNcv",
    "VcIIIIInnIIIIIcv",
    "VcNNnNNnnNNnNNcv",
    "VcNNnNNnnNNnNNcv",
    "VcNNnNNnnNNnNNcv",
    "VcNNnNNnnNNnNNcv",
    "VcNNnNInnINnNNcv",
    "VcNNnNNnnNNnNNcv",
    "VcNNnNNnnNNnNNcv",
    "VcNNnNNnnNNnNNcv",
    "VcNNnNNnnNNnNNcv",
    "VcIIIIInnIIIIIcv",
    "VcNNnNNnnNNnNNcv",
    "VcNNnNNnnNNnNNcv",
    "VcNNnNNnnNNnNNcv",
))

SCENERY_DRAWINGS = (CLOUD, HILL, BUSH, CASTLE_BATTLEMENT, CASTLE_WINDOW, CASTLE_BRICK, CASTLE_DOOR_ARCH,
                    CASTLE_DOOR)
