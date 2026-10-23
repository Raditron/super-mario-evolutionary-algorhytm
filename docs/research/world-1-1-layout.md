# World 1-1 layout as a tile map

> Copied from branch `research/world-1-1-layout` (#3). Where this page recommends something, the spec in `docs/spec/game.md` has the final decision (e.g. fixed Goomba-pair positions, #8).

Research for issue #3: what World 1-1 of *Super Mario Bros.* (NES) looks like as a tile grid. The goal is a grid our pygame replica can load almost directly.

## Answer in one paragraph

World 1-1 is **224 × 15 tiles** of **16 × 16 px** (3584 × 240 px, 14 "pages" of 16 columns). The ground is the bottom two rows (13–14). There are **three pits**, at columns 69–70, 86–88 and 153–154. There are **6 pipes**, at columns 28 (2 tall), 38 (3), 46 (4), 57 (4, the warp pipe to the bonus room), 163 (2, where you come back out) and 179 (2). The staircases are at 134–143, 148–158 (with a pit in the middle) and 181–189 (8 tall). The **flagpole** is at column 198 and the **castle** at 202–206. There are **16 Goombas and 1 green Koopa Troopa**. Everything below was decoded from the game's own level data. It was then checked tile by tile against a full-level map image, and the two matched.

## Sources (by trust)

1. **The level data itself**: doppelganger's *Comprehensive Super Mario Bros. Disassembly* (`SMBDIS.ASM`). Mirrored as gist [1wErt3r/4048722](https://gist.github.com/1wErt3r/4048722); a browsable SourceGen port is at [6502disassembly.com/nes-smb](https://6502disassembly.com/nes-smb/SuperMarioBros.html). World 1-1 is labelled `;level 1-1` with:
   - `L_GroundArea6`, the area (terrain/object) data
   - `E_GroundArea6`, the enemy data

   I decoded those bytes using the disassembly's own parser routines (`AreaParserCore`, `DecodeAreaData`, `VerticalPipe`, `StaircaseObject`, `CastleObject`, `FlagpoleObject`, `Hole_Empty`, `QuestionBlockRow_High`, `ProcessEnemyData`, `HandleGroupEnemies`). **All positions in this document come from that decode** unless marked otherwise.
2. **Full-level map image**: Super Mario Wiki, [File:SMB NES World 1-1 Map.png](https://www.mariowiki.com/File:SMB_NES_World_1-1_Map.png), 3584 × 240 px. I sliced it into 16 × 16 tiles and compared every tile in columns 0–207 against the decoded grid. **Result:** every non-empty tile in my grid is non-sky in the image. Every non-sky tile in the image is one of three things:
   - something in my grid or scenery layer
   - an enemy, the flag, or the hidden block drawn on the map
   - one of the map's annotations (the "1-1" label, and arrows over the warp and exit pipes)

   The image is black from column 208 onwards (a legend panel), so it gives no evidence past column 207.
3. **Counts cross-check**: Super Mario Wiki, [World 1-1 (Super Mario Bros.)](https://www.mariowiki.com/World_1-1_(Super_Mario_Bros.)). It gives 16 Goombas, 1 Koopa Troopa, 3 power-ups in ? blocks, 1 Starman in a brick, 1 hidden 1-UP, 10 coins in ? blocks plus a ten-coin block, a 400-second timer, and a bonus room that exits at a later pipe. All of these agree with the decode.

## Coordinate convention

- **Tile size:** 16 × 16 px. These are the NES's "metatiles"; each is 2 × 2 hardware tiles of 8 × 8.
- **Origin:** top-left of the level. **Column `c`** runs 0–223, left to right. **Row `r`** runs 0–14, top to bottom. Tile `(c, r)` covers pixels `x = 16c … 16c+15`, `y = 16r … 16r+15`.
- **Screen:** 256 × 240 px, so 16 × 15 tiles. Rows 0–1 are where the HUD (score, coins, world, time) is drawn; no level tile is ever placed there.
- **Pages:** one page = 16 columns = 256 px, so column `c` is on page `c // 16`. The disassembly addresses everything as (page, column-in-page).
- **Converting from the disassembly:** its object data uses a 13-row "block buffer" whose row 0 = our row 2, so **our row = block-buffer row + 2**.

## Level size

- **Width: 224 columns (14 pages, 3584 px).** The Mario Wiki map is also 3584 px wide, but its art stops at column 207 (castle at 202–206). The NES has no scroll lock in 1-1, so the camera follows Mario until he walks into the castle door at about column 204. The last column that can come on screen is therefore around 213.

  The ground keeps going (the terrain setting never changes), so a 224-wide grid with ground to the end is safe. **Recommendation: stop the camera with its left edge at x = 3072 px (column 192)**, so the right edge is at column 208 and the flagpole and castle are fully in view. That is a design choice, not something the original enforces.
- **Height: 15 rows (240 px).** Of these, rows 2–14 are playfield and rows 0–1 are under the HUD.
- **Header facts** (header bytes `$50 $21`):
  - timer 400
  - terrain = "no ceiling, floor 2 rows" (rows 13–14)
  - background scenery = "mountains (hills) and bushes" plus clouds
- **Player start:** x = 40 px (`PlayerStarting_X_Pos`), standing on the ground (`PlayerStarting_Y_Pos` = `$b0`), i.e. around column 2.5.
- **Halfway checkpoint:** page 5 (= column 80), from `HalfwayPageNybbles`. If Mario dies after the screen's left edge has reached page 5, he restarts at page 5.

## Terrain

| Feature | Columns | Rows | Notes |
|---|---|---|---|
| Ground | 0–68, 71–85, 89–152, 155–223 | 13–14 | 2 rows thick everywhere |
| Pit 1 | 69–70 | — | 2 wide |
| Pit 2 | 86–88 | — | 3 wide (under the long upper brick row) |
| Pit 3 | 153–154 | — | 2 wide, between the two halves of staircase 2 |

## Blocks and their contents

`?` = question block. "Power-up" means a Super Mushroom, or a Fire Flower if Mario is already big. All blocks in the low row are at row 9, which is 4 tiles above the ground top. All blocks in the high row are at row 5.

| Column(s) | Row | Block | Contents |
|---|---|---|---|
| 16 | 9 | ? | coin |
| 20 | 9 | brick | — |
| 21 | 9 | ? | **power-up** |
| 22 | 9 | brick | — |
| 22 | 5 | ? | coin |
| 23 | 9 | ? | coin |
| 24 | 9 | brick | — |
| 64 | 8 | **hidden block** (invisible until hit from below) | **1-UP mushroom** |
| 77, 79 | 9 | brick | — |
| 78 | 9 | ? | **power-up** |
| 80–87 | 5 | brick ×8 | — (2 Goombas start on top) |
| 91–93 | 5 | brick ×3 | — |
| 94 | 5 | ? | coin |
| 94 | 9 | brick | **multi-coin** ("ten-coin block": gives coins until a timer runs out) |
| 100 | 9 | brick | — |
| 101 | 9 | brick | **Starman** |
| 106, 109, 112 | 9 | ? | coin each |
| 109 | 5 | ? | **power-up** |
| 118 | 9 | brick | — |
| 121–123 | 5 | brick ×3 | — |
| 128, 131 | 5 | brick | — |
| 129, 130 | 5 | ? | coin each |
| 129, 130 | 9 | brick | — |
| 168, 169, 171 | 9 | brick | — |
| 170 | 9 | ? | coin |

Totals: 13 ? blocks (10 coin, 3 power-up), 1 Starman brick, 1 multi-coin brick, 1 hidden 1-UP block, and 28 plain bricks.

The hidden 1-UP is only drawn when `Hidden1UpFlag` is set. A new game always sets it (`inc Hidden1UpFlag` at game start). The flag is cleared once the block has been rendered, so after a death the block does not come back in the original. For a training sandbox, always spawning it is the simpler choice.

## Pipes

A pipe is 2 columns wide. "Height" counts tiles above the ground, top cap included.

| Columns | Top row | Height | Enterable? |
|---|---|---|---|
| 28–29 | 11 | 2 | no |
| 38–39 | 10 | 3 | no |
| 46–47 | 9 | 4 | no |
| 57–58 | 9 | 4 | **yes**: press Down to go to the underground bonus room (area pointer `$c2`) |
| 163–164 | 11 | 2 | no, but Mario **comes out** of it when leaving the bonus room |
| 179–180 | 11 | 2 | no |

Details:

- **No Piranha Plants in 1-1.** `VerticalPipe` skips adding them: `ora WorldNumber ... ;if at world 1-1, do not add piranha plant ever`.
- **Bonus room return:** its enemy data holds a pointer back to 1-1, page 10 (`$1e,$a5,$0a`). Mario comes back at page 10 with x-in-page `$38` (56 px), i.e. x = 2616 px, which is centred on the pipe at 163–164.
- **Bonus room contents:** 19 coins (per Mario Wiki). Its layout is not covered here. **If the replica skips the bonus room, pipe 57 is just a solid pipe.**

## Staircases (hard blocks, solid)

Heights are in tiles above the ground; the top block is at row `13 - height`.

| Columns | Heights | Notes |
|---|---|---|
| 134–137 | 1, 2, 3, 4 | ascending |
| 140–143 | 4, 3, 2, 1 | descending (2-column gap at 138–139 at ground level) |
| 148–152 | 1, 2, 3, 4, 4 | ascending; column 152 is 4 tall |
| 153–154 | — | **pit** |
| 155–158 | 4, 3, 2, 1 | descending |
| 181–189 | 1, 2, 3, 4, 5, 6, 7, 8, 8 | final staircase; columns 188–189 are 8 tall (top at row 5) |

## Flagpole and castle

- **Flagpole, column 198:**
  - ball at row 2
  - shaft at rows 3–11
  - a solid hard block at row 12 as the base
  - the flag hangs on the left of the pole (x = 198·16 - 8 = 3160 px), starting at y = 48 (row 3)
- **Castle, columns 202–206, rows 8–12:** a small castle, 5 wide by 5 tall.
  - Castle tiles are **background**, not solid.
  - The door arch is at (204, 11) and the door at (204, 12).
  - `CastleObject` places **one invisible solid stopper block at (205, 12)**, just right of the door, so Mario stops "inside" the castle. Marked `W` in the grid.
  - The star flag that rises over the castle is spawned at column 204.

## Enemies

Enemy data (`E_GroundArea6`) is listed in column order. Every enemy starts on the ground (resting on row 13, so its sprite occupies row 12) unless noted.

| # | Enemy | Data column | Starting x (tiles) | Notes |
|---|---|---|---|---|
| 1 | Goomba | 22 | 22 | under the first ? cluster |
| 2 | Goomba | 40 | 40 | between pipes 2 and 3 |
| 3–4 | Goomba ×2 (group) | 54 | **≈51 and 52.5** | see *group spawns* |
| 5 | Goomba | 80 | 80 | **on top of the upper brick row** (stands on row 5, sprite at row 4) |
| 6 | Goomba | 82 | 82 | same, on the upper bricks |
| 7–8 | Goomba ×2 (group) | 100 | ≈97 and 98.5 | |
| 9 | **Koopa Troopa (green)** | 107 | 107 | the only Koopa |
| 10–11 | Goomba ×2 (group) | 117 | ≈114 and 115.5 | |
| 12–13 | Goomba ×2 (group) | 127 | ≈124 and 125.5 | |
| 14–15 | Goomba ×2 (group) | 131 | ≈128 and 129.5 | |
| 16–17 | Goomba ×2 (group) | 177 | ≈174 and 175.5 | |

Total: 16 Goombas and 1 Koopa, which matches Mario Wiki. None of these enemies use the "hard mode only" bit.

### When enemies activate

These rules come from `ProcessEnemyData` / `CheckRightBounds` / `HandleGroupEnemies`. Enemies **do not exist until the camera scrolls near them**. They are read from the list strictly in order.

- **Single enemies:** an enemy at pixel x = `16·col` is created when it lies between the screen's right edge and that edge + 48 px. Concretely, it spawns when `(ScreenRight + 48) & ~15 ≥ 16·col` and `16·col ≥ ScreenRight`. In other words, an enemy appears about **0–3 tiles beyond the right edge** of the screen, at its own column. Its starting y is `16·row + 8` px, which is 8 px above where it rests, so it drops onto the ground.
- **Group enemies** (IDs `$37`–`$3E`; 1-1 only uses `$37`, "2 Goombas on the ground") **ignore their own column**. When the trigger fires, which happens when the screen's right edge reaches about 3 tiles before the data column, the two Goombas are placed **at the screen's current right edge**, 24 px apart. That is why the table shows them about 3 tiles left of the data column.
  - The exact pixel depends on scroll speed; it can be a few pixels further right.
  - The Mario Wiki map draws the column-54 pair at about 51.4 and 52.9, the column-127 pair at 124 and 125.5, the column-131 pair at 128 and 129.5, and the column-177 pair at 174 and 175.5. These are consistent with the rule.
- **Enemies that are passed over are skipped for good.** The game has 5 enemy slots (a sixth is reserved for the flag). If the next enemy in the list is already left of the right edge when its turn comes (for example because the slots were full), it is never created.
- **Scrolling** (from `ScrollHandler`): the camera only moves right. It starts scrolling when Mario is more than 80 px from the left edge of the screen, and scrolls at Mario's full speed past 112 px.
- **Replica recommendation:** spawn each enemy when `camera_left + 256 + 48 ≥ spawn_x`, in list order. Put group Goombas at `camera_right_edge` and `+24 px`; or, to keep training deterministic, simply use fixed x values of `16·(col−3)` and `16·(col−1.5)`.

## Tile grid

### Layer 1: solid / interactive tiles (load this)

Legend, where every character is one 16 × 16 tile:

| Char | Meaning | Solid? |
|---|---|---|
| `.` | empty / sky | no |
| `X` | ground | yes |
| `#` | hard block (staircases, flagpole base) | yes |
| `B` | brick (plain) | yes, breakable by big Mario |
| `?` | ? block, coin | yes |
| `M` | ? block, power-up (mushroom / fire flower) | yes |
| `S` | brick containing a Starman | yes |
| `C` | brick with multiple coins | yes |
| `U` | hidden 1-UP block (invisible; solid only when hit from below) | special |
| `[` `]` | pipe top, left / right half | yes |
| `{` `}` | pipe body, left / right half | yes |
| `o` | flagpole ball | (part of the pole) |
| `\|` | flagpole shaft | touching it ends the level |
| `W` | invisible castle stopper | yes (behind the castle art) |

The three ruler lines give each column's hundreds, tens and ones digits. The first three characters of each grid line are the row number and a space; strip them to get 224 characters per row.

```
   0         0         0         0         0         0         0         0         0         0         1         1         1         1         1         1         1         1         1         1         2         2         2   
   0         1         2         3         4         5         6         7         8         9         0         1         2         3         4         5         6         7         8         9         0         1         2   
   01234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123
 0 ................................................................................................................................................................................................................................
 1 ................................................................................................................................................................................................................................
 2 ......................................................................................................................................................................................................o.........................
 3 ......................................................................................................................................................................................................|.........................
 4 ......................................................................................................................................................................................................|.........................
 5 ......................?.........................................................BBBBBBBB...BBB?..............M...........BBB....B??B........................................................##........|.........................
 6 ...........................................................................................................................................................................................###........|.........................
 7 ..........................................................................................................................................................................................####........|.........................
 8 ................................................................U........................................................................................................................#####........|.........................
 9 ................?...BMB?B.....................[].........[]..................BMB..............C.....BS....?..?..?.....B..........BB......#..#..........##..#............BB?B............######........|.........................
10 ......................................[]......{}.........{}.............................................................................##..##........###..##..........................#######........|.........................
11 ............................[]........{}......{}.........{}............................................................................###..###......####..###.....[]..............[].########........|.........................
12 ............................{}........{}......{}.........{}...........................................................................####..####....#####..####....{}..............{}#########........#......W..................
13 XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX..XXXXXXXXXXXXXXX...XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX..XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
14 XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX..XXXXXXXXXXXXXXX...XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX..XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### Layer 2: background scenery (decoration only, never solid)

These come from `BackSceneryData`, set 2 ("mountains and bushes"), which **repeats every 48 columns (3 pages)**; the castle comes from `CastleObject`. Draw this layer behind layer 1 (in the original, layer 1 objects overwrite scenery). Legend:

| Char | Meaning |
|---|---|
| `c` | cloud |
| `h` | hill |
| `b` | bush |
| `^` | castle battlement |
| `w` | castle window |
| `=` | castle brick |
| `(` | door arch |
| `D` | door |

```
   0         0         0         0         0         0         0         0         0         0         1         1         1         1         1         1         1         1         1         1         2         2         2   
   0         1         2         3         4         5         6         7         8         9         0         1         2         3         4         5         6         7         8         9         0         1         2   
   01234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123
 0 ................................................................................................................................................................................................................................
 1 ................................................................................................................................................................................................................................
 2 ...................ccc..............cccc...........................ccc..............cccc...........................ccc..............cccc...........................ccc..............cccc...........................ccc..........
 3 ........ccc........ccc.....ccccc....cccc................ccc........ccc.....ccccc....cccc................ccc........ccc.....ccccc....cccc................ccc........ccc.....ccccc....cccc................ccc........ccc.....ccccc
 4 ........ccc................ccccc........................ccc................ccccc........................ccc................ccccc........................ccc................ccccc........................ccc................ccccc
 5 ................................................................................................................................................................................................................................
 6 ................................................................................................................................................................................................................................
 7 ................................................................................................................................................................................................................................
 8 ...........................................................................................................................................................................................................^^^..................
 9 ...........................................................................................................................................................................................................w=w..................
10 ..h...............................................h...............................................h...............................................h...............................................h.......^^^^^.................
11 .hhh.............h...............................hhh.............h...............................hhh.............h...............................hhh.............h...............................hhh......==(==..h..............
12 hhhhh......bbbbbhhh....bbb...............bbbb...hhhhh......bbbbbhhh....bbb...............bbbb...hhhhh......bbbbbhhh....bbb...............bbbb...hhhhh......bbbbbhhh....bbb...............bbbb...hhhhh.....==D==bhhh....bbb......
13 ................................................................................................................................................................................................................................
14 ................................................................................................................................................................................................................................
```

### Entity list (not in the grid)

```
mario_start   x=40px  (col 2.5), on ground
goomba        col 22, 40, 80 (row 4, on bricks), 82 (row 4, on bricks)
goomba_pair   data col 54, 100, 117, 127, 131, 177  -> spawn at screen right edge, +24px apart
koopa_green   col 107
flag          x=3160px, y=48px (on pole at col 198)
warp_pipe     cols 57-58 -> bonus room; return at pipe cols 163-164 (page 10)
checkpoint    page 5 (col 80)
```

## Caveats and uncertainty

- **Decoding fidelity:** I wrote my own decoder (Python) that statically reimplements the disassembly's object routines. It does not emulate the column-by-column renderer.
  - Overlap order mattered in only two places: the ? blocks at (21, 9) and (129–130, 5) overwrite the bricks of a brick row. I traced the parser's slot order to confirm the ? blocks win, and the map image agrees.
  - Every terrain and block position was checked against the Mario Wiki map image (columns 0–207). **High confidence.**
- **Group Goomba x positions** depend on scroll speed at trigger time. The values given are ±~4 px. The data columns are exact.
- **Exact enemy y:** the game spawns enemies at `16·row + 8` px and gravity settles them. The "row 12 / row 4" in the table is where they end up resting, not a stored value.
- **Level width past column 207:** this is inferred from the scroll code (no scroll lock in 1-1), not from an image. The map image's art stops at 207. Treat columns 208–223 as "ground continues, nothing else", and stop the camera wherever is convenient.
- **Hidden block content:** the 1-UP is confirmed by the object type in the data (`$03` small object → `Hidden1UpBlock`). Its row 8 is one row higher than the usual ?-block row 9.
- **Not covered:** the bonus room's layout, enemy AI/speeds, and item behaviour. Each is a separate research question.

## Reproducing the decode

The bytes, verbatim from `SMBDIS.ASM`:

```
;level 1-1   L_GroundArea6 (area data; header $50,$21, then 2-byte objects, $fd = end)
$50,$21, $07,$81,$47,$24,$57,$00,$63,$01,$77,$01,$c9,$71,$68,$f2,$e7,$73,$97,$fb,$06,$83,
$5c,$01,$d7,$22,$e7,$00,$03,$a7,$6c,$02,$b3,$22,$e3,$01,$e7,$07,$47,$a0,$57,$06,$a7,$01,
$d3,$00,$d7,$01,$07,$81,$67,$20,$93,$22,$03,$a3,$1c,$61,$17,$21,$6f,$33,$c7,$63,$d8,$62,
$e9,$61,$fa,$60,$4f,$b3,$87,$63,$9c,$01,$b7,$63,$c8,$62,$d9,$61,$ea,$60,$39,$f1,$87,$21,
$a7,$01,$b7,$20,$39,$f1,$5f,$38,$6d,$c1,$af,$26, $fd

;level 1-1   E_GroundArea6 (enemy data; $ff = end)
$1e,$c2,$00, $6b,$06, $8b,$86, $63,$b7, $0f,$05, $03,$06, $23,$06, $4b,$b7, $bb,$00,
$5b,$b7, $fb,$37, $3b,$b7, $0f,$0b, $1b,$37, $ff
```

Format summary (area objects): byte 1 is `XXXXYYYY`, where X is the column within the page and Y is the block-buffer row (`$C`–`$F` are special rows). Byte 2 is `PTTTLLLL`, where P means "advance one page", T is the object type and L is the length or height.

- **Rows 0–11:**
  - T=2 is a brick row
  - T=6 is a hard-block column
  - T=7 is a pipe (height `L&7`, enterable if `L&8`)
  - T=0 is a single block whose kind is given by L: 0 ?power-up, 1 ?coin, 3 hidden 1-UP, 6 star brick, 7 multi-coin brick, …
- **Row `$C`:** T=0 is a hole, T=6 is a ? row at row 3.
- **Row `$D`:** a page skip or flagpole.
- **Row `$F`:** T=2 is a castle, T=3 is a staircase.

Enemy objects use the same `XXXXYYYY`. Byte 2 is `PHIIIIII` (P = page, H = hard-mode only, I = enemy ID: `$06` Goomba, `$00` green Koopa, `$37` pair of Goombas). Row `$E` is a 3-byte area pointer and row `$F` is a page skip.
