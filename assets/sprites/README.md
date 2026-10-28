# Sprites

The Sprite view (`F1` toggles it with the Debug view) draws every thing from a PNG in this folder. **A PNG that isn't here is drawn as a box of the sprite's size in that thing's hitbox colour**, so the view works with this folder empty, and adding a texture never touches the code: save the PNG under its name below and start the game again.

## The rules

- **File names:** one PNG per sprite, named after what it shows, in lower-case `snake_case`, plus `_<state>` for another look of the same thing (`goomba_defeated.png`). Exactly the names below are read. Any other file in this folder is ignored.
- **Sizes:** the original's, in NES pixels, on the 16 px grid. A PNG of another size is scaled to the size below, so draw it at that size.
- **Transparency:** transparent pixels show what is behind (the sky, the scenery, the tiles).
- **Placement:** a sprite stands on the bottom of its thing's box, centred across it. Mario's 16 px wide sprite overhangs his 12 px box by 2 px on each side. A fireball's explosion is centred on the fireball.
- **One picture per sprite:** no animation frames and no facing yet. Those, and the full sprite list, are for the texture-pass ticket (spec section 12).

## The sprites

### Tiles (16 × 16, one per tile)

Tiles are named by how they look: a brick or ? block doesn't show what it holds. The hidden 1-UP block isn't drawn until it is hit (it then shows as a used block), and neither is the invisible castle stopper.

| File | Size (px) | Drawn for |
|---|---|---|
| `ground.png` | 16 × 16 | ground |
| `hard_block.png` | 16 × 16 | the staircases' blocks and the flagpole's base |
| `brick.png` | 16 × 16 | every brick: plain, multi-coin and Starman |
| `question_block.png` | 16 × 16 | every ? block: coin and power-up |
| `used_block.png` | 16 × 16 | a block that has been emptied |
| `pipe.png` | 16 × 16 | every tile of a pipe |
| `flagpole.png` | 16 × 16 | the flagpole's ball and shaft |

### Background scenery (16 × 16, one per tile, behind the tiles)

Layer 2 of the grid in `docs/research/world-1-1-layout.md`. A cloud, hill or bush is several tiles, each drawn with the same picture.

| File | Size (px) | Drawn for |
|---|---|---|
| `cloud.png` | 16 × 16 | a cloud's tile |
| `hill.png` | 16 × 16 | a hill's tile |
| `bush.png` | 16 × 16 | a bush's tile |
| `castle_battlement.png` | 16 × 16 | the castle's battlements |
| `castle_window.png` | 16 × 16 | the castle's windows |
| `castle_brick.png` | 16 × 16 | the castle's wall |
| `castle_door_arch.png` | 16 × 16 | the arch over the castle's door |
| `castle_door.png` | 16 × 16 | the castle's door |

### Mario, by power state

| File | Size (px) | Drawn for |
|---|---|---|
| `mario_small.png` | 16 × 16 | small Mario |
| `mario_big.png` | 16 × 32 | big Mario |
| `mario_fiery.png` | 16 × 32 | fire Mario |

### Enemies

| File | Size (px) | Drawn for |
|---|---|---|
| `goomba.png` | 16 × 16 | a Goomba |
| `goomba_defeated.png` | 16 × 8 | a squashed Goomba |

### Items

| File | Size (px) | Drawn for |
|---|---|---|
| `super_mushroom.png` | 16 × 16 | the Super Mushroom |
| `one_up_mushroom.png` | 16 × 16 | the 1-UP mushroom |
| `fire_flower.png` | 16 × 16 | the fire flower |

### Mario's fireballs

| File | Size (px) | Drawn for |
|---|---|---|
| `fireball.png` | 8 × 8 | a flying fireball |
| `fireball_explosion.png` | 16 × 16 | a fireball exploding |

The sizes and names are `SPRITE_SIZES` in `mario/constants/view.py`; a test checks this page lists every one.
