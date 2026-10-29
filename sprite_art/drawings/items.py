"""The items that come out of blocks, as knight-world pickups: a health potion makes the hero
big, a heart crystal is an extra life, a torch grants fire and a holy shield makes him invincible."""

from sprite_art.palettes.items import ITEM_PALETTE
from sprite_art.sprite_drawing import SpriteDrawing

HEALTH_POTION = SpriteDrawing("super_mushroom", ITEM_PALETTE, (
    "................",
    "......KKKK......",
    ".....KCCCcK.....",
    ".....KCCccK.....",
    "......KKKK......",
    "......KgGK......",
    ".....KKgGKK.....",
    "....KgGGGGGK....",
    "...KsRRRRRRRK...",
    "..KsWRRRRRRRrK..",
    "..KsRRRRRRRRrK..",
    "..KRRRRRRRRRrK..",
    "..KRRRRRRRRrrK..",
    "...KrRRRRRrrK...",
    "....KrrrrrrK....",
    ".....KKKKKK.....",
))

HEART_CRYSTAL = SpriteDrawing("one_up_mushroom", ITEM_PALETTE, (
    "..............L.",
    ".W...........LWL",
    "..............L.",
    "..KKKK....KKKK..",
    ".KLLHHK..KMMMMK.",
    "KLWLHHHKKMMMMMhK",
    "KLLHHHHHMMMMMMhK",
    "KLHHHHHHMMMMMMhK",
    "KHHHHHHHMMMMMhhK",
    ".KHHHHHHMMMMMhK.",
    "..KHHHHHMMMMhK..",
    "...KHHHHMMMhK...",
    "....KHHHMMhK....",
    ".....KHHMhK.....",
    "......KHhK......",
    ".......KK.......",
))

TORCH = SpriteDrawing("fire_flower", ITEM_PALETTE, (
    "......q.........",
    ".....qOq..q.....",
    ".....qOOqqOq....",
    "....qOOFOOOq....",
    "...qOOFFFOOOq...",
    "...qOFFWFFOOq...",
    "...qOFWWWFFOq...",
    "...qOFWWWFOOq...",
    "..KUIIIIIIIIiK..",
    "...KUIIIIIIiK...",
    "....KiIIIIiK....",
    ".....KNNNnK.....",
    ".....KiiiiK.....",
    ".....KNNNnK.....",
    ".....KNNNnK.....",
    ".....KKKKKK.....",
))

HOLY_SHIELD = SpriteDrawing("starman", ITEM_PALETTE, (
    ".Z............Z.",
    "..KKKKKKKKKKKK..",
    "..KZZZZZZZZZYK..",
    "..KZBBBZYBBbYK..",
    "..KZBBBZYBBbYK..",
    "..KZBZZZZZZbYK..",
    "..KZBYYYYYYbYK..",
    "Z.KZBBBZYBBbYK.Z",
    "..KZBBBZYBBbYK..",
    "..KZBBBZYBBbyK..",
    "...KZBBZYBbyK...",
    "...KZBBZYBbyK...",
    "....KZBZYbyK....",
    ".....KZZYyK.....",
    "......KyyK......",
    ".......KK.......",
))

ITEM_DRAWINGS = (HEALTH_POTION, HEART_CRYSTAL, TORCH, HOLY_SHIELD)
