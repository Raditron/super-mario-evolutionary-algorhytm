"""The background scenery: one picture per tile, repeated across every tile of a kind,
so each tiles seamlessly with itself; a hill's tiles by their place in the hill, the
slopes open to the sky on their outer side, and a cloud's by its place in the cloud,
its puffs and rounded ends open to the sky, and a bush's by its place in the bush,
its rounded ends open to the sky, and the castle's wall, windows and battlements by
their place in the castle, its edges a clean outline; all lit from the top-left."""

from sprite_art.palettes.scenery import SCENERY_PALETTE
from sprite_art.sprite_drawing import SpriteDrawing

CLOUD_TOP_LEFT = SpriteDrawing("cloud_top_left", SCENERY_PALETTE, (
    "................",
    "................",
    "................",
    ".......WWWs.....",
    ".....WWWWWWWs...",
    "....WWWWWWWWWs..",
    "....WWWWWWWWWs..",
    "...WWWWWWWWWWWs.",
    "...WWWWWWWWWWWWW",
    "...WWWWWWWWWWWWW",
    "...WWWWWWWWWWWWW",
    "..WWWWWWWWWWWWWW",
    "..WWWWWWWWWWWWWW",
    ".WWWWWWWWWWWWWWW",
    ".WWWWWWWWWWWWWWW",
    "WWWWWWWWWWWWWWWW",
))

CLOUD_TOP_MIDDLE = SpriteDrawing("cloud_top_middle", SCENERY_PALETTE, (
    "................",
    "................",
    ".....WWWWs......",
    "...WWWWWWWWs....",
    "..WWWWWWWWWWs...",
    "..WWWWWWWWWWs...",
    ".WWWWWWWWWWWWs..",
    ".WWWWWWWWWWWWs..",
    "WWWWWWWWWWWWWWWW",
    "WWWWWWWWWWWWWWWW",
    "WWWWWWWWWWWWWWWW",
    "WWWWWWWWWWWWWWWW",
    "WWWWWWWWWWWWWWWW",
    "WWWWWWWWWWWWWWWW",
    "WWWWWWWWWWWWWWWW",
    "WWWWWWWWWWWWWWWW",
))

CLOUD_TOP_RIGHT = SpriteDrawing("cloud_top_right", SCENERY_PALETTE, (
    "................",
    "................",
    "................",
    "................",
    ".....WWWs.......",
    "...WWWWWWWs.....",
    "..WWWWWWWWWs....",
    "..WWWWWWWWWs....",
    "WWWWWWWWWWWWs...",
    "WWWWWWWWWWWWs...",
    "WWWWWWWWWWWWs...",
    "WWWWWWWWWWWWWs..",
    "WWWWWWWWWWWWWs..",
    "WWWWWWWWWWWWWWs.",
    "WWWWWWWWWWWWWWs.",
    "WWWWWWWWWWWWWWWs",
))

CLOUD_BOTTOM_LEFT = SpriteDrawing("cloud_bottom_left", SCENERY_PALETTE, (
    "WWWWWWWWWWWWWWWW",
    "WWWWWWWWWWWWWWWW",
    "WWWWWWWWWWWWWWWW",
    "SWWWWWWWWWWWWWWW",
    "SWWWWWWWWWWWWWWW",
    ".SWWWWWWWWWWWWWW",
    ".SsWWWWWWWWWWWWW",
    "..SssWWWWWWWWWWW",
    "..SSSssWWWWWWWWW",
    "...SSSSsssssssss",
    ".....SSSSSSSSSSS",
    ".......SSSSSSSSS",
    "................",
    "................",
    "................",
    "................",
))

CLOUD_BOTTOM_MIDDLE = SpriteDrawing("cloud_bottom_middle", SCENERY_PALETTE, (
    "WWWWWWWWWWWWWWWW",
    "WWWWWWWWWWWWWWWW",
    "WWWWWWWWWWWWWWWW",
    "WWWWWWWWWWWWWWWW",
    "WWWWWWWWWWWWWWWW",
    "WWWWWWWWWWWWWWWW",
    "WWWWWWWWWWWWWWWW",
    "WWWWWWWWWWWWWWWW",
    "WWWWWWWWWWWWWWWW",
    "ssssssssssssssss",
    "SSSSSSSSSSSSSSSS",
    "SSSSSSSSSSSSSSSS",
    "................",
    "................",
    "................",
    "................",
))

CLOUD_BOTTOM_RIGHT = SpriteDrawing("cloud_bottom_right", SCENERY_PALETTE, (
    "WWWWWWWWWWWWWWWs",
    "WWWWWWWWWWWWWWWs",
    "WWWWWWWWWWWWWWWs",
    "WWWWWWWWWWWWWWWS",
    "WWWWWWWWWWWWWWsS",
    "WWWWWWWWWWWWWWS.",
    "WWWWWWWWWWWWWsS.",
    "WWWWWWWWWWWssS..",
    "WWWWWWWWWssSSS..",
    "sssssssssSSSS...",
    "SSSSSSSSSSS.....",
    "SSSSSSSSS.......",
    "................",
    "................",
    "................",
    "................",
))

HILL_LEFT_SLOPE = SpriteDrawing("hill_left_slope", SCENERY_PALETTE, (
    "...............L",
    "..............LL",
    ".............LLG",
    "............LLGG",
    "...........LLGGG",
    "..........LLGGGG",
    ".........LLGGGLG",
    "........LLGGGLgL",
    ".......LLGGGGGGG",
    "......LLGGGGGGGG",
    ".....LLGGGGGGgGG",
    "....LLGGGGGGGGGG",
    "...LLGGGGLGGGGGG",
    "..LLGGGGLgLGGGGG",
    ".LLGGGGGGGGGGGGG",
    "LLGGGGGgGGGGGGGG",
))

HILL_RIGHT_SLOPE = SpriteDrawing("hill_right_slope", SCENERY_PALETTE, (
    "g...............",
    "gg..............",
    "Ggg.............",
    "GGgg............",
    "GLGgg...........",
    "LgLGgg..........",
    "GGGGGgg.........",
    "GGGGGGgg........",
    "GGGgGGGgg.......",
    "GGGGGGGGgg......",
    "GGGGGLGGGgg.....",
    "GGGGLgLGGGgg....",
    "GGGGGGGGGGGgg...",
    "GgGGGGGGGGGGgg..",
    "GGGGGGGGGGgGGgg.",
    "GGGGGGGGGGGGGGgg",
))

HILL_PEAK = SpriteDrawing("hill_peak", SCENERY_PALETTE, (
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "......LLLg......",
    "....LLLGGGgg....",
    "...LLGGGGGGGg...",
    "...LGGGGGGGGg...",
    "..LLGGGGGGGGgg..",
    "..LGGGGLGGGGGg..",
    ".LLGGGLgLGGGGgg.",
    ".LGGGGGGGGGGGGg.",
    "LLGGGGGGGGGGGGgg",
))

HILL_FILL = SpriteDrawing("hill_fill", SCENERY_PALETTE, (
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

BUSH_LEFT_END = SpriteDrawing("bush_left_end", SCENERY_PALETTE, (
    "................",
    "................",
    "................",
    "...............J",
    "....JJJJB.JJJ.JJ",
    "...JJJJBJJJJBBJJ",
    "..JJJBBJJJJBBJJJ",
    ".JJJBBBJJBBBBJJB",
    ".JJBBBJJJBBBBJJB",
    ".JJBBBJJBBBBBJBB",
    ".JBBBBJBBBBJBBBB",
    ".BBBJBBBBBBBbBBB",
    ".bBBBbBBBBBBBBBB",
    ".bbBbbbbBbbbbbbB",
    ".bbbbbbbbbbbbbbb",
    "...bbbbbbbbbbbbb",
))

BUSH_MIDDLE = SpriteDrawing("bush_middle", SCENERY_PALETTE, (
    "................",
    "................",
    ".JJJJ...........",
    "JJJJBBB........J",
    "JJJBBBBB..JJJ.JJ",
    "JBBBBBBBJJJJBBJJ",
    "BBBBBBBJJJJBBJJJ",
    "BBBBBBBJJBBBBJJB",
    "BBBBBBJJJBBBBJJB",
    "BBJBBBJJBBBBBJBB",
    "BBBbBBJBBBBJBBBB",
    "BBBBBBbBBBBBbBBB",
    "BBBBBbbBBBBBBBBB",
    "bbbbbbbbBbbbbbbB",
    "bbbbbbbbbbbbbbbb",
    "bbbbbbbbbbbbbbbb",
))

BUSH_RIGHT_END = SpriteDrawing("bush_right_end", SCENERY_PALETTE, (
    "................",
    "................",
    ".JJJJ...........",
    "JJJJBBB.........",
    "JJJBBBBBJJJJB...",
    "JBBBBBBJJJJBBB..",
    "BBBBBBJJJBBBBBB.",
    "BBBBBJJJBBBBBBbb",
    "BBBBBJJBBBBBBBbb",
    "BBJBBJJBBBJBBBbb",
    "BBBbBJBBBBBbBBbb",
    "BBBBBBBBBBBBBBbb",
    "BBBBBbBBBBBBBbb.",
    "bbbbbbbBbbbbbbb.",
    "bbbbbbbbbbbbbbb.",
    "bbbbbbbbbbbbb...",
))

BUSH_SINGLE = SpriteDrawing("bush_single", SCENERY_PALETTE, (
    "................",
    "................",
    "................",
    "................",
    "...JJJJBBJJ.....",
    "..JJJJBBBBJBB...",
    ".JJJBBBBBBbBBB..",
    ".JJBBBBBBbbBBBb.",
    ".JJBBBBBBBbBJBb.",
    ".JBBJBBBBBbBBbb.",
    ".BBBBbBBBbbBBBb.",
    ".BBBBBBBBbbBBbb.",
    ".bBBbBBbbbBBBbb.",
    ".bbbbbbbbBBbbbb.",
    ".bbbbbbbbbbbbbb.",
    "...bbbbbbbbbb...",
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

# The castle's edges: its left side lit along its whole height, its right side a
# shaded line of mortar, so every course of bricks ends on the same clean outline.
CASTLE_BRICK_LEFT_EDGE = SpriteDrawing("castle_brick_left_edge", SCENERY_PALETTE, (
    "VVVVVVVVVVVVVVVc",
    "VCCCCCCCCCCCCCvc",
    "VCCCCvCCCCCCCCvc",
    "VCCCCCCCCCCCCCvc",
    "VCCCCCCCCCCvCCvc",
    "VCCCCCCCCCCCCCvc",
    "Vvvvvvvvvvvvvvvc",
    "Vccccccccccccccc",
    "VVVVVVVcVVVVVVVV",
    "VCCCCCvcVCCCCCCC",
    "VCCCCCvcVCCCCCCC",
    "VCvCCCvcVCCCCCCC",
    "VCCCCCvcVCCCCvCC",
    "VCCCCCvcVCCCCCCC",
    "VvvvvvvcVvvvvvvv",
    "Vccccccccccccccc",
))

CASTLE_BRICK_RIGHT_EDGE = SpriteDrawing("castle_brick_right_edge", SCENERY_PALETTE, (
    CASTLE_BRICK.rows[:8] + (
        "VVVVVVVcVVVVVVVc",
        "CCCCCCvcVCCCCCvc",
        "CCCCCCvcVCCCCCvc",
        "CCvCCCvcVCCCCCvc",
        "CCCCCCvcVCCvCCvc",
        "CCCCCCvcVCCCCCvc",
        "vvvvvvvcVvvvvvvc",
        "cccccccccccccccc",
    )
))

CASTLE_WINDOW_LEFT_EDGE = SpriteDrawing("castle_window_left_edge", SCENERY_PALETTE, (
    "VVVVVVVVVVVVVVVc",
    "VCCCCCccccCCCCvc",
    "VCCCCcOOOOcCCCvc",
    "VCCCcOOOOOOcCCvc",
    "VCCCcOOOOOocCCvc",
    "VCCCcOOOOOocCCvc",
    "VvvvcOOOOOocvvvc",
    "VccccOOOOOoccccc",
    "VVVVcOOOOOocVVVV",
    "VCCCcOOOOOocCCCC",
    "VCCCcOOOOOocCCCC",
    "VCvCcOOOOOocCCCC",
    "VCCCcoooooocCCCC",
    "VCCVVVVVVVVVVCCC",
    "Vvvccccccccccvvv",
    "Vccccccccccccccc",
))

CASTLE_WINDOW_RIGHT_EDGE = SpriteDrawing("castle_window_right_edge", SCENERY_PALETTE, (
    CASTLE_WINDOW.rows[:8] + (
        "VVVVcOOOOOocVVVc",
        "CCCCcOOOOOocCCvc",
        "CCCCcOOOOOocCCvc",
        "CCvCcOOOOOocCCvc",
        "CCCCcoooooocCCvc",
        "CCCVVVVVVVVVVCvc",
        "vvvccccccccccvvc",
        "cccccccccccccccc",
    )
))

# A battlement's ends: a corner merlon, wider than the others, flush with the edge.
CASTLE_BATTLEMENT_LEFT_END = SpriteDrawing("castle_battlement_left_end", SCENERY_PALETTE, (
    "VVVVVVVVVVVV....",
    "VCCCCCCCCCCv....",
    "VCCCvCCCCCCv....",
    "VCCCCCCCCCCv....",
    "VCCCCCCCvCCv....",
    "VCCCCCCCCCCvcVVV",
    "Vvvvvvvvvvvvcvvv",
    "Vccccccccccccccc",
) + CASTLE_BRICK_LEFT_EDGE.rows[8:])

CASTLE_BATTLEMENT_RIGHT_END = SpriteDrawing("castle_battlement_right_end", SCENERY_PALETTE, (
    "....VVVVVVVVVVVc",
    "....VCCCCCCCCCvc",
    "....VCCCCvCCCCvc",
    "....VCCCCCCCCCvc",
    "....VCCCCCCvCCvc",
    "VVVcVCCCCCCCCCvc",
    "vvvcvvvvvvvvvvvc",
    "cccccccccccccccc",
) + CASTLE_BRICK_RIGHT_EDGE.rows[8:])

# Under the tower: no merlons and no sky, a course of stone the tower stands on,
# then the walkway's ledge running on at the battlement's height.
CASTLE_WALL_TOP = SpriteDrawing("castle_wall_top", SCENERY_PALETTE, (
    "VVVVVVVVVVVVVVVc",
    "VCCCCvCCCCCCCCvc",
    "VCCCCCCCCCCvCCvc",
    "Vvvvvvvvvvvvvvvc",
    "cccccccccccccccc",
    "VVVVVVVVVVVVVVVV",
    "vvvvvvvvvvvvvvvv",
    "cccccccccccccccc",
) + CASTLE_BRICK.rows[8:])

SCENERY_DRAWINGS = (CLOUD_TOP_LEFT, CLOUD_TOP_MIDDLE, CLOUD_TOP_RIGHT, CLOUD_BOTTOM_LEFT, CLOUD_BOTTOM_MIDDLE,
                    CLOUD_BOTTOM_RIGHT, HILL_LEFT_SLOPE, HILL_RIGHT_SLOPE, HILL_PEAK, HILL_FILL, BUSH_LEFT_END, BUSH_MIDDLE, BUSH_RIGHT_END, BUSH_SINGLE, CASTLE_BATTLEMENT, CASTLE_WINDOW, CASTLE_BRICK, CASTLE_DOOR_ARCH,
                    CASTLE_DOOR, CASTLE_BRICK_LEFT_EDGE, CASTLE_BRICK_RIGHT_EDGE, CASTLE_WINDOW_LEFT_EDGE,
                    CASTLE_WINDOW_RIGHT_EDGE, CASTLE_BATTLEMENT_LEFT_END, CASTLE_BATTLEMENT_RIGHT_END, CASTLE_WALL_TOP)
