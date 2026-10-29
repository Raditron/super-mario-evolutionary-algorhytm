"""The enemies: a purple slime that is stomped flat, and a goblin footsoldier under
an iron pot-helmet that he hides inside when stomped."""

from sprite_art.palettes.enemies import ENEMY_PALETTE
from sprite_art.sprite_drawing import SpriteDrawing

GOOMBA = SpriteDrawing("goomba", ENEMY_PALETTE, (
    "................",
    "................",
    "................",
    ".....KKKKKK.....",
    "...KKLLSSSSKK...",
    "..KLLWSSSSSSsK..",
    ".KLLWSSSSSSSSsK.",
    ".KLSKKSSSSKKSsK.",
    "KLSSSSKSSKSSSSsK",
    "KSSSWKSSSSKWSSsK",
    "KSSSWKSSSSKWSSsK",
    "KSSSSSSSSSSSSSsK",
    "KSSSSKKKKKKSSSsK",
    "KsSSKSKSSKSKSssK",
    "KssssssssssssssK",
    ".KKKKKKKKKKKKKK.",
))

GOOMBA_DEFEATED = SpriteDrawing("goomba_defeated", ENEMY_PALETTE, (
    "................",
    "....KKKKKKKK....",
    "..KKLWLSSSSSKK..",
    ".KLLKSKSSKSKSSK.",
    "KLSSSKSSSSKSSSsK",
    "KSSSKSKSSKSKSSsK",
    "KsSSSSSSSSSSSssK",
    ".KKKKKKKKKKKKKK.",
))

KOOPA = SpriteDrawing("koopa", ENEMY_PALETTE, (
    ".......KK.......",
    "......KHmK......",
    "....KKKMmKKK....",
    "...KHHHMMMMmK...",
    "..KHWMMMMMMMmK..",
    "..KHMMMMMMMMmK..",
    "..KHMMMMMMMMmK..",
    "..KMMMMMMMMmmK..",
    "KKKRHRRRRRRHrKKK",
    "KHHHMMMMMMMMMmmK",
    "KmmmmmmmmmmmmmmK",
    "KKKKKKKKKKKKKKKK",
    "KGGKggggggggKGGK",
    ".KKKGYKGGKYGKKK.",
    "...KGGGggGGGK...",
    "...KGGWKKWGGK...",
    "....KKGGGGKK....",
    "...KKRRRRRRrKK..",
    "..KGKRRRRRRrKGK.",
    "...KKRRRRrrrKK..",
    "....KKKKKKKK....",
    "....KgK..KgK....",
    "..KmmmK..KmmmK..",
    "..KKKKK..KKKKK..",
))

KOOPA_SHELL = SpriteDrawing("koopa_shell", ENEMY_PALETTE, (
    "................",
    "................",
    ".......KK.......",
    "......KHmK......",
    "....KKKMmKKK....",
    "...KHHHMMMMmK...",
    "..KHWMMMMMMMmK..",
    "..KHMMMMMMMMmK..",
    "..KHMMMMMMMMmK..",
    "..KMMMMMMMMmmK..",
    "KKKRHRRRRRRHrKKK",
    "KHHHMMMMMMMMMmmK",
    "KmmmmmmmmmmmmmmK",
    "KKKKKKKKKKKKKKKK",
    ".KKKYYKKKKYYKKK.",
    "..KKKKKKKKKKKK..",
))

ENEMY_DRAWINGS: tuple[SpriteDrawing, ...] = (GOOMBA, GOOMBA_DEFEATED, KOOPA, KOOPA_SHELL)
