# Sprites

The Sprite view (`F1` toggles it with the Debug view) draws every thing from a PNG in this folder. **A PNG that isn't here is drawn as a box of the sprite's size in that thing's hitbox colour**, so the view works with this folder empty, and adding a texture never touches the code: save the PNG under its name below and start the game again.

The PNGs here are painted from text drawings in `sprite_art/drawings/`, one palette per group in `sprite_art/palettes/`: change a drawing, then run `py -m sprite_art` to repaint them all. A test fails while a PNG differs from its drawing.

## The rules

- **File names:** one PNG per sprite, named after what it shows, in lower-case `snake_case`, plus `_<state>` for another look of the same thing (`goomba_defeated.png`). Exactly the names below are read. Any other file in this folder is ignored.
- **Sizes:** the original's, in NES pixels, on the 16 px grid. A PNG of another size is scaled to the size below, so draw it at that size.
- **Transparency:** transparent pixels show what is behind (the sky, the scenery, the tiles).
- **Placement:** a sprite stands on the bottom of its thing's box, centred across it. Mario's 16 px wide sprite overhangs his 12 px box by 2 px on each side. A fireball's explosion is centred on the fireball.
- **Facing right:** draw Mario and the enemies facing right. The Sprite view mirrors the picture, in the same place, for Mario, a ghost or an enemy facing left; an enemy faces the way it walks. A Koopa's shell is never mirrored, so draw it to look the same either way.
- **Animation frames:** a frame is its thing's standing sprite's name plus `_<frame>`, after any state already in the name: `_walk_1` to `_walk_3`, `_skid`, `_jump` and `_crouch` for Mario (`mario_big_walk_1.png`, `mario_small_invincible_jump.png`), and `_walk_2` for an enemy's second walking frame (`goomba_walk_2.png`), its first being its own sprite. The game picks the frame (the snapshot carries Mario's pose and walking frame, and an enemy's walking frame); the Sprite view keeps no clock of its own. **A frame that isn't here is drawn as the standing sprite**, and that as the box in the thing's colour while it is missing too.

## The sprites

### Tiles (16 × 16, one per tile)

Tiles are named by how they look: a brick or ? block doesn't show what it holds. The hidden 1-UP block isn't drawn until it is hit (it then shows as a used block), and neither is the invisible castle stopper. A pipe is two tiles wide, and its tile is drawn by its place in the pipe, which its neighbouring tiles give: with no pipe above it, it is the rim, otherwise the body; with no pipe on its left, it is the left half, otherwise the right half. The rim is a lip the pipe's full width over the body, which is set in 2 px on each side (transparent there), so the two halves read as one wide pipe with a lip on top. A tile at the screen's left edge, whose left neighbour is off screen, is the left half when pipe is on its right.

| File | Size (px) | Drawn for |
|---|---|---|
| `ground.png` | 16 × 16 | ground |
| `hard_block.png` | 16 × 16 | the staircases' blocks and the flagpole's base |
| `brick.png` | 16 × 16 | every brick: plain, multi-coin and Starman |
| `question_block.png` | 16 × 16 | every ? block: coin and power-up |
| `used_block.png` | 16 × 16 | a block that has been emptied |
| `pipe_rim_left.png` | 16 × 16 | a pipe's tile with no pipe above it or on its left |
| `pipe_rim_right.png` | 16 × 16 | a pipe's tile with no pipe above it and pipe on its left |
| `pipe_body_left.png` | 16 × 16 | a pipe's tile with pipe above it and none on its left |
| `pipe_body_right.png` | 16 × 16 | a pipe's tile with pipe above it and on its left |
| `flagpole.png` | 16 × 16 | the flagpole's ball and shaft |

### The flag

| File | Size (px) | Drawn for |
|---|---|---|
| `flag.png` | 16 × 16 | the flag on the left of the flagpole, from its top-left corner, sliding down with Mario at the end of the level |

### Background scenery (16 × 16, one per tile, behind the tiles)

Layer 2 of the grid in `docs/research/world-1-1-layout.md`. A hill's tile is drawn by its place in the hill, which its scenery neighbours give: with no hill on either side it is the peak, with none on its left the left slope, with none on its right the right slope, and otherwise fill. A slope's outer side is transparent, so the sky shows through and the hill's outline reads as a smooth slope. A cloud's tile is drawn by its place in the cloud the same way: with cloud above it, it is the bottom row, otherwise the top row; with no cloud on its left the left end, with none on its right the right end, and otherwise the middle. The top row carries the puffs and the bottom row the flat underside, each end rounded and open to the sky, so a cloud of any width reads as one solid shape. A bush is one tile tall, and its tile is drawn by its place in the bush: with no bush on its left it is the left end, with none on its right the right end, and otherwise the middle; a one-tile bush, with none on either side (World 1-1 has one, against the castle), has a picture of its own, rounded on both sides. Each end is rounded and open to the sky, and the middle tiles seamlessly with itself and the ends. The castle's wall, windows and battlements are drawn by their place in the castle too, any castle tile counting as castle: a tile with no castle on its left is the castle's left edge, lit along its whole height, and one with none on its right its right edge, a shaded line of mortar, so the castle has a clean outline on both sides. A battlement's ends are corner merlons, flush with the edge, and a battlement with castle above it (the front wall's, under the tower) is the solid wall top the tower rises from, with no merlons and no sky.

| File | Size (px) | Drawn for |
|---|---|---|
| `cloud_top_left.png` | 16 × 16 | a cloud's top-row tile with no cloud on its left |
| `cloud_top_middle.png` | 16 × 16 | a cloud's top-row tile with cloud on both sides |
| `cloud_top_right.png` | 16 × 16 | a cloud's top-row tile with no cloud on its right |
| `cloud_bottom_left.png` | 16 × 16 | a cloud's bottom-row tile (cloud above it) with no cloud on its left |
| `cloud_bottom_middle.png` | 16 × 16 | a cloud's bottom-row tile with cloud on both sides |
| `cloud_bottom_right.png` | 16 × 16 | a cloud's bottom-row tile with no cloud on its right |
| `hill_left_slope.png` | 16 × 16 | a hill's tile with no hill on its left |
| `hill_right_slope.png` | 16 × 16 | a hill's tile with no hill on its right |
| `hill_peak.png` | 16 × 16 | a hill's tile with no hill on either side: its top |
| `hill_fill.png` | 16 × 16 | a hill's tile with hill on both sides |
| `bush_left_end.png` | 16 × 16 | a bush's tile with no bush on its left |
| `bush_middle.png` | 16 × 16 | a bush's tile with bush on both sides |
| `bush_right_end.png` | 16 × 16 | a bush's tile with no bush on its right |
| `bush_single.png` | 16 × 16 | a one-tile bush: no bush on either side |
| `castle_battlement.png` | 16 × 16 | the castle's battlements |
| `castle_window.png` | 16 × 16 | the castle's windows |
| `castle_brick.png` | 16 × 16 | the castle's wall |
| `castle_door_arch.png` | 16 × 16 | the arch over the castle's door |
| `castle_door.png` | 16 × 16 | the castle's door |
| `castle_brick_left_edge.png` | 16 × 16 | a castle wall tile with no castle on its left |
| `castle_brick_right_edge.png` | 16 × 16 | a castle wall tile with no castle on its right |
| `castle_window_left_edge.png` | 16 × 16 | a castle window with no castle on its left: the tower's left side |
| `castle_window_right_edge.png` | 16 × 16 | a castle window with no castle on its right: the tower's right side |
| `castle_battlement_left_end.png` | 16 × 16 | a battlement tile with no castle on its left: its corner merlon |
| `castle_battlement_right_end.png` | 16 × 16 | a battlement tile with no castle on its right: its corner merlon |
| `castle_wall_top.png` | 16 × 16 | a battlement tile with castle above it: the wall top the tower rises from |

### Mario, by power state, and invincible

| File | Size (px) | Drawn for |
|---|---|---|
| `mario_small.png` | 16 × 16 | small Mario |
| `mario_big.png` | 16 × 32 | big Mario |
| `mario_fiery.png` | 16 × 32 | fire Mario |
| `mario_small_invincible.png` | 16 × 16 | small Mario while a Starman makes him invincible |
| `mario_big_invincible.png` | 16 × 32 | big or fire Mario while a Starman makes him invincible (the star's colours show over fire Mario's) |

### Mario's animation frames

Each of the five Mario sprites above has these frames, painted from one set of rows per size in its own palette; only big Mario has a crouch. He shows the standing sprite while he stands still (and while his power state changes). Walking or running, the three walking frames take turns, 1, 2, 3, 1 …, each for 7, 4 or 2 ticks as his speed on the ground grows; falling off a ledge, he keeps the one he had. The walk is half a stride, and his arms swing as well as his legs: frame 1 is the stride, front arm swung forward and back arm trailing; frame 2 the back leg passing, front hand still forward; frame 3 the front foot reaching forward, arms at rest as when standing. On the ground, fast enough and facing against the way he moves, he skids; in the air he shows the jump frame; big Mario holding down shows the crouch.

| File | Size (px) | Drawn for |
|---|---|---|
| `mario_small_walk_1.png` | 16 × 16 | small Mario walking: his first walking frame |
| `mario_small_walk_2.png` | 16 × 16 | small Mario walking: his second walking frame |
| `mario_small_walk_3.png` | 16 × 16 | small Mario walking: his third walking frame |
| `mario_small_skid.png` | 16 × 16 | small Mario skidding |
| `mario_small_jump.png` | 16 × 16 | small Mario in the air |
| `mario_small_invincible_walk_1.png` | 16 × 16 | the same, invincible |
| `mario_small_invincible_walk_2.png` | 16 × 16 | the same, invincible |
| `mario_small_invincible_walk_3.png` | 16 × 16 | the same, invincible |
| `mario_small_invincible_skid.png` | 16 × 16 | the same, invincible |
| `mario_small_invincible_jump.png` | 16 × 16 | the same, invincible |
| `mario_big_walk_1.png` | 16 × 32 | big Mario walking: his first walking frame |
| `mario_big_walk_2.png` | 16 × 32 | big Mario walking: his second walking frame |
| `mario_big_walk_3.png` | 16 × 32 | big Mario walking: his third walking frame |
| `mario_big_skid.png` | 16 × 32 | big Mario skidding |
| `mario_big_jump.png` | 16 × 32 | big Mario in the air |
| `mario_big_crouch.png` | 16 × 24 | big Mario crouching |
| `mario_fiery_walk_1.png` | 16 × 32 | the same, fire Mario |
| `mario_fiery_walk_2.png` | 16 × 32 | the same, fire Mario |
| `mario_fiery_walk_3.png` | 16 × 32 | the same, fire Mario |
| `mario_fiery_skid.png` | 16 × 32 | the same, fire Mario |
| `mario_fiery_jump.png` | 16 × 32 | the same, fire Mario |
| `mario_fiery_crouch.png` | 16 × 24 | the same, fire Mario |
| `mario_big_invincible_walk_1.png` | 16 × 32 | the same, big or fire Mario invincible |
| `mario_big_invincible_walk_2.png` | 16 × 32 | the same, big or fire Mario invincible |
| `mario_big_invincible_walk_3.png` | 16 × 32 | the same, big or fire Mario invincible |
| `mario_big_invincible_skid.png` | 16 × 32 | the same, big or fire Mario invincible |
| `mario_big_invincible_jump.png` | 16 × 32 | the same, big or fire Mario invincible |
| `mario_big_invincible_crouch.png` | 16 × 24 | the same, big or fire Mario invincible |

### Enemies

| File | Size (px) | Drawn for |
|---|---|---|
| `goomba.png` | 16 × 16 | a Goomba |
| `goomba_defeated.png` | 16 × 8 | a squashed Goomba |
| `koopa.png` | 16 × 24 | the green Koopa Troopa, walking |
| `koopa_shell.png` | 16 × 16 | its shell: still, kicked, or flipped as it falls out of the level |
| `goomba_walk_2.png` | 16 × 16 | a walking Goomba's second walking frame, shown on 8 ticks of every 16 |
| `koopa_walk_2.png` | 16 × 24 | a walking Koopa's second walking frame, shown on 8 ticks of every 16 |

### Items

| File | Size (px) | Drawn for |
|---|---|---|
| `super_mushroom.png` | 16 × 16 | the Super Mushroom |
| `one_up_mushroom.png` | 16 × 16 | the 1-UP mushroom |
| `fire_flower.png` | 16 × 16 | the fire flower |
| `starman.png` | 16 × 16 | the Starman |

### Mario's fireballs

| File | Size (px) | Drawn for |
|---|---|---|
| `fireball.png` | 8 × 8 | a flying fireball |
| `fireball_explosion.png` | 16 × 16 | a fireball exploding |

### The HUD

The coin before the HUD's coin count is drawn in its 8 × 8 cell of the status bar's text grid, from the cell's top-left corner, over whichever view is shown. The level has no free-standing coins, so this is the only place it is drawn. While it is missing, the HUD draws an orange rectangle in its cell instead.

| File | Size (px) | Drawn for |
|---|---|---|
| `coin.png` | 8 × 8 | the coin icon before the HUD's coin count |

The sizes and names are `SPRITE_SIZES` in `mario/constants/view.py`; a test checks this page lists every one.
