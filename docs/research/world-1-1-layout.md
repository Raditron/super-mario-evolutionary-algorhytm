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

**The multi-coin brick's timer** (added in #18): its first hit sets `BrickCoinTimer` to `$0B` interval ticks of 21 frames, so 211–231 frames depending on the interval clock. Every hit gives a coin and leaves the brick in place while the timer runs. The first hit after it has run out gives one more coin and turns the brick into a used block. The timer and its flag (`BrickCoinTimerFlag`) are one for the whole level. The replica always takes the longest, 231 ticks, as for the squashed Goomba. Source: [doppelganger's disassembly](https://gist.github.com/1wErt3r/4048722), `PlayerHeadCollision` l. 7240-7258 (`StartBTmr`/`ContBTmr`), `DecTimers` l. 789-799.

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

## Timer, score, lives, checkpoint and HUD

Added for #16, sourced from `SMBDIS.ASM` (gist 1wErt3r/4048722, 16,351 lines); `l.` is its line number.

| Fact | Value | Source |
|---|---|---|
| Timer start | The header's timer setting picks `GameTimerData` = `$04`, and the last digit is set to 1, so the display starts at **401**. The frame timers are cleared at area start, so the first decrement (to 400) happens on the timer's first frame. | `Entrance_GameTimerSetup` l. 2867–2872, `ClrTimersLoop` l. 2665 |
| Timer speed | Each time `GameTimerCtrlTimer` reaches 0, one is taken off the display and it is reloaded with **`$18` = 24 frames**. It is a frame timer, so it counts down every frame. | `ResGTCtrl` l. 6461–6462, `Timers` l. 81–89, `DecTimers` l. 789–799 |
| Time up | When a decrement is due and the display already reads 000, `TimeUpOn` kills Mario. The timer doesn't run during the entrance or death routines, or while Mario is below the screen. | `RunGameTimer` l. 6436–6472 |
| Timer per life | Every new life reloads the timer from the header. | `ContinueGame` l. 2990–2994 |
| Coins | Each coin adds 1 to the coin count. At 100 the count goes back to 0 and Mario gains a life. Every coin is also worth **200 points**. | `GiveOneCoin` l. 7084–7102 |
| Score | Six BCD digits plus a fixed trailing "0" on screen, so all points are multiples of 10. The highest digit is drawn blank while it is 0, so a new game shows `000000`. | `TopStatusBarLine` l. 1641, `UpdateNumber` l. 7113–7119 |
| Score table | The awards, in order: 100, 200, 400, 500, 800, 1000, 2000, 4000, 5000, 8000, then 1-UP. Which event gives which is up to each slice. | `FloateyNumTileData` l. 1262–1274, `ScoreUpdateData` l. 1278–1281 |
| Lives | `NumberofLives` starts at 2, the lives left after the current one, so **3 lives**. Each death takes one. Game over comes when it would go below 0. | `PrimaryGameSetup` l. 2721–2722, `PlayerLoseLife` l. 2906–2917 |
| Checkpoint | 1-1's halfway page is the high nybble of `$56`, so **page 5**. At each death it is kept only if the screen's left edge (`ScreenLeft_PageLoc`) is at page 5 or beyond, otherwise it becomes 0. | `HalfwayPageNybbles` l. 2896–2897, `PlayerLoseLife` l. 2919–2940 |
| Restart position | The next life starts with the screen's left edge at that page. Mario is placed on the same page at `PlayerStarting_X_Pos` = `$28`, so from the checkpoint he starts at x = 5 × 256 + 40 = **1320 px**, at the usual height. | `InitializeArea` l. 2668–2672, `Entrance_GameTimerSetup` l. 2834–2835, l. 2856–2857 |

**The replica's timer (spec §5):** 400 units shown at spawn, one taken off every 24 ticks, and the attempt ends when it reaches 0, at tick 9,600. The original reaches 000 at the same point, then kills Mario one 24-frame period later. The spec's 9,600 is kept.

**HUD layout.** The status bar sits on the NES's 8 × 8 px text grid, rows 2–3 (y = 16–31). Columns below are 8 px cells. They are read from the name-table addresses (`$20RC`: row = `RC` ÷ 32, column = `RC` mod 32).

| Row | Column | Shows | Source |
|---|---|---|---|
| 2 | 3 | `MARIO` | `TopStatusBarLine` l. 1638 (`$2043`) |
| 2 | 18 | `WORLD`, then at 25 `TIME` | l. 1639–1640 (`$2052`) |
| 3 | 2–8 | score: 6 digits and the fixed trailing 0, the first blanked while 0 | `StatusBarData` l. 2521 (`$2062`), l. 1641 (`$2068`) |
| 3 | 11, 12 | coin icon, then `x` | l. 1641 |
| 3 | 13–14 | coins, 2 digits | `StatusBarData` l. 2523 (`$206d`) |
| 3 | 19–21 | `1-1` | `WriteBottomStatusLine` l. 1499–1517 (`$2073`) |
| 3 | 26–28 | time, 3 digits | `StatusBarData` l. 2525 (`$207a`) |

The original shows the lives only on the screen between lives, not in the HUD.

## Enemy activation, removal and stomp points

Added for #17, sourced from `SMBDIS.ASM` (gist 1wErt3r/4048722); `l.` is its line number.

| Fact | Value | Source |
|---|---|---|
| Activation range | The next enemy in the list is created once `(ScreenRight + 48) & $F0 ≥` its column's x. For an x on the 16 px grid, that means x ≤ screen right edge + 48. | `CheckRightBounds` l. 7906-7912, `CheckRightExtBounds` l. 7958-7963 |
| Passed-over enemies | An enemy whose column is already left of the screen's right edge when its turn comes is skipped for good. A life started at the checkpoint therefore skips the two Goombas on the upper bricks (columns 80 and 82). | `PositionEnemyObj` l. 7942-7956, `CheckThreeBytes` l. 8041-8053 |
| Spawn height | Sprite y = 16 × the data's row nybble, then the enemy lands 8 px lower (see `EnemyLanding` in the physics research). | `CheckRightExtBounds` l. 7966-7971 |
| Removal | An enemy is erased once its x is more than 72 px left of the screen's left edge, or more than 72 px right of its right edge. | `OffscreenBoundsCheck` l. 11006-11050 |
| Falling into a pit | An enemy is erased once its sprite's top reaches y = 256 (`Enemy_Y_HighPos` = 2). | `EnemyGfxHandler` l. 14055-14058 |
| Stomp chain | Each stomp adds 1 to `StompChainCounter`. Its points are the score table at `StompChainCounter + StompTimer`: 100, 200, 400, 500, 800, 1000, 2000, 4000, 5000, 8000, then a 1-UP. Two stomps in the same frame therefore give 100, then 400. | `HandleStompedShellE` l. 11499-11507, `FloateyNumbersRoutine` l. 1283-1312 |
| Chain reset | `StompChainCounter` goes back to 0 each frame Mario stands on the ground. | `LandPlyr` l. 12015-12023 |
| When points count | The floatey number's points are added 5 frames after the stomp, when its timer goes from `$30` to `$2B`. | `SetupFloateyNumber` l. 11533-11536, `FloateyNumbersRoutine` l. 1295-1312 |

**Replica choices**:
- **Activation x:** a Goomba pair activates when its data column comes into range, so both appear together at the screen's right edge, as in the original. A single enemy uses its own x.
- **Removal:** only the left side is used, as the spec (§4) asks. The original's right-side erase isn't modelled.
- **Points:** they are scored on the stomp's own tick, not 5 ticks later. A stomp beyond 8000 scores nothing. Its 1-UP waits for the 1-UP slice (#19).

## Flagpole, castle walk and end-of-level points

Added for #24, sourced from `SMBDIS.ASM` (gist 1wErt3r/4048722); `l.` is its line number.

| Fact | Value | Source |
|---|---|---|
| The touch | Mario's side probes run each frame after he moves. On a climbable tile (the pole's ball `$24` or shaft `$25`) the upper probe is skipped for the lower one, at sprite y + 24, on his left (sprite x + 2) or right (sprite x + 13) side. It touches the pole only where it is 6 to 9 px into the pole's tile: the pole is thinner than its tile. Moving right, he touches it with his sprite at x 3161–3164. | `SideCheckLoop`/`BHalf` l. 12034-12061, `CheckSideMTiles` l. 12063-12068, `HandleClimbing`/`ChkForFlagpole` l. 12153-12165, `BlockBuffer_X_Adder`/`_Y_Adder` l. 13030-13040 |
| What the touch does | It sets `ScrollLock` (the screen stops), stores Mario's sprite y and its band for the points, and starts the slide (game routine 4). He is put on the pole with his sprite 7 px left of its column, facing right, with no speed. | `FlagpoleCollision` l. 12167-12194, `PutPlayerOnVine`/`SetVXPl` l. 12206-12227, `ClimbXPosAdder` l. 12144 |
| Height points | His sprite's y at the touch is checked against `FlagpoleYPosData` from the bottom: y ≥ `$90` (144) scores **100**, ≥ `$68` (104) **400**, ≥ `$50` (80) **800**, ≥ `$22` (34) **2000**, above that **5000** (the table's first entry, `$18`, is never compared). The points are `FlagpoleScoreMods` at the digit `FlagpoleScoreDigits` gives (3 = thousands, 4 = hundreds). They are added when the slide ends. | `FlagpoleYPosData` l. 12150-12151, `ChkFlagpoleYPosLoop`/`MtchF` l. 12187-12192, `FlagpoleScoreMods`/`FlagpoleScoreDigits` l. 6573-6577, `GiveFPScr` l. 6611-6617 |
| The timer stops | `RunGameTimer` runs only in game routines 8 and up, so it stops on the touch's frame: the touch comes in the player routine, before the timer runs that frame. | `RunGameTimer` l. 6436-6441, `GameEngine` l. 5311-5334 |
| The flag | `FlagpoleObject` puts the flag 8 px left of the pole's column, its top at y = `$30` (48). | `FlagpoleObject` l. 3966-3990 |
| The slide | Each frame Mario, pressing down (`AutoControlPlayer` with `$04`), moves down 1 px plus the carry of a fraction that gains `$FF`, until his sprite's y is `$9E` (158) or more. Then the flag moves the same way, from the touch's own frame on. The slide ends (and the height points are added) once the flag's y is `$AA` (170) or more, or Mario's `$A2` (162). | `FlagpoleSlide`/`SlidePlayer` l. 5810-5822, `ClimbingSub` l. 5966-5976, `Climb_Y_SpeedData`/`Climb_Y_MForceData` l. 6036-6040, `ProcClimb` l. 6054-6058, `FlagpoleRoutine` l. 6579-6617 |
| Leaving the pole | `PlayerEndLevel` presses right (`$01`) from then on. Still climbing, the first press moves him `$0E` (14) px right, round the pole, facing left, and sets the climb-side timer to `$18` (24 frames). When it has run out, the next press moves him `$04` px right; his probe is then out of the pole's thin part, so he is no longer climbing: he falls, then walks right. (The timer has run out by the end of the slide: it is cleared on every frame no left or right is held.) | `PlayerEndLevel` l. 5831-5836, `ClimbingSub`/`CSetFDir`/`InitCSTimer` l. 5976-6009, `ClimbAdderLow` l. 5961-5964 |
| The screen | The scroll lock is cleared once Mario's sprite y reaches `$AE` (174), off the pole, so the screen follows him again into the castle. | `PlayerEndLevel` l. 5836-5842, `ScrollHandler` l. 5383-5384 |
| The castle | The invisible stopper at (205, 12) stops his right side (`ImpedePlayerMove` clears collision bit 0). That starts the star flag's tasks: on the same frame, the fireworks count is chosen from the timer's last digit; from the next frame, the timer counts down **1 unit a frame**, each worth **50 points**; then the star flag rises over the castle, fireworks go off, and once the music ends the next area loads. | `ChkStop`/`InCastle`/`RdyNextA` l. 5843-5852, `ImpedePlayerMove`/`ExIPM` l. 12318-12351, `RunStarFlagObj` l. 10452-10485, `GameTimerFireworks` l. 10466-10482, `AwardGameTimerPoints`/`EndAreaPoints` l. 10487-10516 |

**The camera stop at column 192, checked against the original** (spec §4). The original has no scroll stop, but the touch locks its scroll (above). Before the touch, its screen follows Mario's rule (scrolling from 80 px, full speed from 112 px), and he touches the pole with his sprite at x 3161–3164. So its left edge is then at most 3164 − 80 = 3084 px (column 192.75):
- **Running**, as the test pilot does, the left edge is about 3050 px (column 190.6) at the touch. That is short of the replica's stop, which then changes nothing.
- **Walking slowly**, the original's screen can be up to 12 px further right than the replica's.
- **During the castle walk**, the original scrolls again and ends around column 195–196, its right edge near column 212. The replica stays at column 192 (right edge at column 208). Both show the flagpole and the whole castle (202–206).

The caveat below ("no scroll lock in 1-1") is wrong about the flagpole: the lock exists, from the touch until Mario is off the pole.

**Replica choices** (spec §5):
- **The points are scored at the touch**, both the height points and the remaining-time points, and the attempt ends there. In play mode the HUD shows them as the original does: the height points once the flag is down, the time points one unit a tick in the castle.
- **The sequence after the touch** (play and replay only) is the slide, leaving the pole, the walk to the stopper and the count. The star flag, the fireworks and the wait for the music are not built: play mode starts a new game when the count is done.
- Both sliding fractions start at 0. Enemies, items and fireballs stand still after the touch.
- The replica's boxes stop Mario with his box's right edge on the stopper (sprite x 3266); the original's probe stops him 1 px further right.

## Caveats and uncertainty

- **Decoding fidelity:** I wrote my own decoder (Python) that statically reimplements the disassembly's object routines. It does not emulate the column-by-column renderer.
  - Overlap order mattered in only two places: the ? blocks at (21, 9) and (129–130, 5) overwrite the bricks of a brick row. I traced the parser's slot order to confirm the ? blocks win, and the map image agrees.
  - Every terrain and block position was checked against the Mario Wiki map image (columns 0–207). **High confidence.**
- **Group Goomba x positions** depend on scroll speed at trigger time. The values given are ±~4 px. The data columns are exact.
- **Exact enemy y:** the game spawns enemies at `16·row + 8` px and gravity settles them. The "row 12 / row 4" in the table is where they end up resting, not a stored value.
- **Level width past column 207:** this is inferred from the scroll code (no scroll lock in 1-1, but for the flagpole's: see above), not from an image. The map image's art stops at 207. Treat columns 208–223 as "ground continues, nothing else", and stop the camera wherever is convenient.
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
