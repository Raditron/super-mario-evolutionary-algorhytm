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
- **Bonus room contents:** 19 coins (per Mario Wiki). Its layout, decoded for #23, is in [The bonus room](#the-bonus-room) below.

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

## The bonus room

Added for #23, decoded from `SMBDIS.ASM` (gist 1wErt3r/4048722) by the same method as 1-1 above; `l.` is its line number.

### Where it is

- **1-1 points to it.** The first entry of 1-1's enemy data, `$1e,$c2,$00` (`E_GroundArea6` l. 4612), is in the special row `$E`: an area pointer, read by `ParseRow0e` (l. 8021-8037). Its second byte, `$c2`, becomes `AreaPointer`; its third byte holds the world (its top 3 bits, 0 = world 1, so 1-1 uses it) and the entrance page (its low 5 bits: page 0).
- **`$c2` is the underground bonus area.** `GetAreaDataAddrs` (l. 4377-4400) takes the area type from bits 6-5 (`$c2` → 2, underground) and the offset from the low 5 bits (2). `EnemyAddrHOffsets` (l. 4484-4485) gives `$1c` + 2 = entry 30, `E_UndergroundArea3`; `AreaDataHOffsets` (l. 4503-4504) gives `$19` + 2 = entry 27, `L_UndergroundArea3`. The comment at l. 4476-4477 agrees: "underground bonus area - c2".
- **The area is shared.** `L_UndergroundArea3` is "underground bonus rooms area used in many levels" (l. 5226-5241): each world's pipe enters it at its own page. 1-1 enters at page 0, so **1-1's room is page 0 of that area**, its first 16 columns.
- **The way back.** The first entry of the room's enemy data, `$1e,$a5,$0a` (`E_UndergroundArea3` l. 4745), sits at column 1 of page 0. It is read as the room loads: world 1 (`$0a` >> 5 = 0), so it is used, with `AreaPointer` = `$a5` (type 1, offset 5: `E_GroundArea6` and `L_GroundArea6`, which is 1-1) and entrance page `$0a` = **page 10**. Its other area pointers name other worlds and are skipped.

### Its bytes and their decode

```
;underground bonus rooms area   L_UndergroundArea3 (l. 5227), page 0 only
$48,$01,                                   header
$0e,$01, $00,$5a, $3e,$06, $45,$46, $47,$46, $53,$44, $ae,$01, $df,$4a,
$4d,$c7, ...                               page 1 begins: not 1-1's room
```

| Bytes | Column | What (routine) | Result |
|---|---|---|---|
| `$48,$01` | header | bits 5-3 of `$48`: player entrance control 1; bits 7-6: timer setting 1; `$01`: terrain 1, no background scenery (header parse l. 4401-4455) | Mario starts at sprite y `$20` (below) |
| `$0e,$01` | 0 | row `$E`: `AlterAreaAttributes` (l. 3536-3551), terrain 1 | no ceiling, floor 2 |
| `$00,$5a` | 0 | row 0, type 5: `ColumnOfBricks` (l. 4079-4082), height `$a` + 1 = 11 | bricks, rows 2-12 |
| `$3e,$06` | 3 | `AlterAreaAttributes`, terrain 6 | ceiling 1, floor 5 |
| `$45,$46` | 4 | row 5, type 4: `RowOfCoins` (l. 4017-4020), length 6 + 1 = 7 | coins at row 7, columns 4-10 |
| `$47,$46` | 4 | row 7, `RowOfCoins`, 7 long | coins at row 9, columns 4-10 |
| `$53,$44` | 5 | row 3, `RowOfCoins`, 5 long | coins at row 5, columns 5-9 |
| `$ae,$01` | 10 | `AlterAreaAttributes`, terrain 1 | no ceiling, floor 2 |
| `$df,$4a` | 13 | row `$F`, type 4: `ExitPipe` (l. 3810-3835), height `$a` | the exit pipe, columns 13-16 |
| `$4d,$c7` | page 1, column 4 | row `$D` with d6 set, object 7: `ScrollLockObject` (l. 3581-3585) | the screen locks |

Rows are block-buffer rows; **our row = block-buffer row + 2**, as for 1-1. How each object draws:

- **Terrain** (`RenderSceneryTerrain` l. 3159-3271, `TerrainRenderBits` l. 3136-3152). The two bytes are bit masks over block-buffer rows 0-7 and 8-12. Terrain 1 (`%00000000, %00011000`) fills rows 11-12; terrain 6 (`%00000001, %00011111`) fills row 0 and rows 8-12. The underground terrain metatile is `$52`, a brick (`TerrainMetatiles` l. 3133-3134), switched to `$54`, ground, from block-buffer row 11 down (`EndUChk` l. 3255-3260). So the floor is 2 rows of ground everywhere; terrain 6 adds a brick ceiling (our row 2) and 3 rows of bricks on the floor (our rows 10-12).
- **A terrain change applies from the next column.** `AreaParserCore` renders a column's terrain first and only then runs that column's objects (`RendBBuf: jsr ProcessAreaData`, l. 3271), so `AlterAreaAttributes` at column 3 changes columns 4 onward, and the one at column 10 columns 11 onward. The ceiling and the brick block are therefore columns 4-10, under the two rows of 7 coins.
- **The exit pipe** (`ExitPipe`, `RenderSidewaysPipe`, `SidePipeShaftData` / `SidePipeTopPart` / `SidePipeBottomPart` l. 3800-3835) is 4 columns, drawn from its fixed length 3 down to 0, so the tables read backwards: column 13 is the mouth (`$1c` over `$1f`), column 14 the sideways pipe's body (`$1d`, `$20`), and columns 15-16 the vertical pipe, its shaft from block-buffer row 0 to row `$a` - 2 = 8, the sideways part joining it at rows 9-10. In our rows: the sideways pipe is at rows 11-12, the vertical pipe at rows 2-12.
- **Coins** are metatile `$c2` underground (`CoinMetatileData` l. 4014-4015).
- **The screen never scrolls.** The renderer draws 24 columns ahead as an area starts (`ColumnSets` = `$0b`, "1 1/2 screens", l. 2692), so the scroll lock at page 1, column 4 (column 20) is set before Mario appears.

### The grid (16 × 15, one screen)

Legend as for layer 1, plus:

| Char | Meaning | Solid? |
|---|---|---|
| `$` | coin | no: touching it collects it |
| `<` | the sideways exit pipe's mouth | yes |
| `-` | the sideways exit pipe's body | yes |

Column 16, the vertical pipe's right half, is off the screen and outside this grid; outside the grid counts as solid at the sides, as for 1-1.

```
   0         1     
   0123456789012345
 0 ................
 1 ................
 2 B...BBBBBBB....{
 3 B..............{
 4 B..............{
 5 B....$$$$$.....{
 6 B..............{
 7 B...$$$$$$$....{
 8 B..............{
 9 B...$$$$$$$....{
10 B...BBBBBBB....{
11 B...BBBBBBB..<-{
12 B...BBBBBBB..<-{
13 XXXXXXXXXXXXXXXX
14 XXXXXXXXXXXXXXXX
```

**19 coins** (7 + 7 + 5), which matches Mario Wiki. The bricks are underground bricks (`$52`, the underground entry of `BrickMetatiles` l. 4057-4058), so big Mario can break them.

### Going in, and coming out

| Fact | Value | Source |
|---|---|---|
| Entering | On a frame Mario lands or stands (`LandPlyr`), holding down, with his left foot probe (sprite x + 3) on the warp pipe's top-left metatile (`$10`) and his right one (sprite x + 12) on its top-right one (`$11`), he enters: only a pipe drawn with those metatiles (a "pipe that leads somewhere", `VerticalPipeData`) can be entered. In 1-1 that is pipe 57 alone. So his sprite x must be 916-924. Down with left or right held is not down: on the ground, the directions are all cleared. | `HandlePipeEntry` l. 12270-12289, `LandPlyr` l. 12015-12019, `BlockBuffer_X_Adder` l. 13030 (feet: `$03`, `$0c`), `VerticalPipeData` l. 3837-3841, `PlayerCtrlRoutine` l. 5581-5590 |
| Sinking | `ChangeAreaTimer` = `$30`: for **48 frames** Mario moves down **1 px a frame**, behind the pipe (`Player_SprAttrib` bit 5), with no control; then the area changes. | `HandlePipeEntry`, `VerticalPipeEntry` l. 5683-5694, `ChgAreaPipe` l. 5708-5715 |
| Arriving | A vertical pipe's entry mode is 1, so Mario's sprite starts at x = `PlayerStarting_X_Pos`[1] = `$18` (24) and y = `PlayerStarting_Y_Pos`[header's entrance control 1] = `$20` (32), facing right. While his sprite y is under `$30` (48) he moves with no buttons pressed (falling); on the frame it is `$30` or more, control returns, from the next frame. | `Entrance_GameTimerSetup` l. 2833-2862, `PlayerStarting_X_Pos` / `_Y_Pos` l. 2815-2824, `PlayerEntrance` l. 5494-5503, `PlayerRdy` l. 5542-5548 |
| A new area | Each area starts with memory cleared: every enemy, item and fireball is gone, and Mario's speeds, crouch and jump state with them (`InitializeMemory` up to `$074b`); his power state is kept. The frame timers are cleared too (`ClrTimersLoop`, `$0780-$07a1`), so a Starman's invincibility (`StarInvincibleTimer`) and the while after being hurt (`InjuryTimer`) end, and the game timer's frame timer restarts, so the level timer takes a unit off on its first frame. Falling uses `$28` (`VerticalForceDown`) until the first jump. | `InitializeArea` l. 2660-2666, `InitializeMemory` l. 2770-2785, `Entrance_GameTimerSetup` l. 2836-2837, `RunGameTimer` l. 6436-6462 |
| Collecting a coin | A coin metatile (`$c2`) under any of Mario's probes (head, feet or sides) is erased and gives 1 coin (and its 200 points). | `CheckForCoinMTiles` l. 12371-12379, `HandleCoinMetatile` l. 12122-12125, `GiveOneCoin` l. 7084-7102 |
| Leaving | Mario on the ground (`Player_State` 0), facing right, whose side probe meets the mouth's bottom metatile (`$1f`) starts the exit. `ChangeAreaTimer` is set from `AreaChangeTimerData`: `$a0` (**160 frames**) on page 0, as here. | `ChkPBtm` / `PipeDwnS` / `SetCATmr` l. 12076-12109, `AreaChangeTimerData` l. 12119-12120 |
| Walking in | For those 160 frames, with no control and tile collision off, Mario is set an x speed of `$08` (0.5 px a frame) and right is pressed for him, until his sprite x is a multiple of 16; then he stands. He is drawn behind the pipe. Then the area changes. | `SideExitPipeEntry` / `ChgAreaPipe` l. 5705-5715, `EnterSidePipe` l. 5717-5728, `PlayerBGCollision` l. 11902-11909 (no tile collision in game routines 0-3) |
| Coming out | A side pipe's entry mode is 2: the screen's left edge is at the entrance page, page 10 (2560 px), and Mario's sprite at x = 2560 + `PlayerStarting_X_Pos`[2] = `$38`, so **2616**, and y = `$f0` (240), below the screen, behind pipe 163. Each frame he rises 1 px, with no control, until his sprite y is under `$91`: at y = `$90` (144), after **96 frames**, he stands on the pipe's top (row 11) and control returns, from the next frame. | `InitializeArea` l. 2667-2672, `Entrance_GameTimerSetup` l. 2851-2858, `AltYPosOffset` l. 2819-2820, `EntrMode2` l. 5516-5521 |
| The level timer | It counts only in game routine 8 and up, so it stops while Mario sinks (routine 3), walks into the exit pipe (2) and arrives (7). | `RunGameTimer` l. 6436-6441, `GameRoutines` l. 5474-5486 |
| Enemies meanwhile | Enemies, items and fireballs go on moving while Mario is in a transition, but none touches him: the enemy check runs only in routine 8. | `PlayerEnemyCollision` l. 11301-11303 |

### How it looks

| Fact | Value | Source |
|---|---|---|
| Background | Black: the room's header (`$48,$01`) sets no background colour (its low 3 bits are 0, under 4), so the colour is the area type's, underground (2): `BackgroundColors`[2] = `$0f`, black. 1-1 (ground) is `$22`, its sky blue. | `BackgroundColors` l. 1426-1428, `SetBGColor` l. 1461-1464, header parse l. 4404-4408 |
| No scenery | The header's second byte, `$01`, has its background scenery bits (5-4) at 0: none. | header parse l. 4425-4436 |
| The exit pipe's pieces | Read backwards from its length 3 (`ExitPipe`, `RenderSidewaysPipe`): column 13 the mouth, `$1c` over `$1f`; column 14 the sideways body, `$1d` over `$20`; column 15 the shaft's left half (`$14`) from the block buffer's top, row 0, with the joint, `$1e` over `$21`, where the sideways pipe meets it; column 16 the shaft's right half (`$15`), off the room's screen. The shaft has no rim: it is the same `$14`/`$15` as an upright pipe's body (`VerticalPipeData`). | `SidePipeShaftData` / `SidePipeTopPart` / `SidePipeBottomPart` l. 3800-3808, `RenderSidewaysPipe` l. 3815-3834, `VerticalPipeData` l. 3837-3841 |
| Behind the pipes | Mario is drawn behind the background (`Player_SprAttrib` bit 5) while he sinks into the warp pipe and walks into the exit pipe, while he drops into the room (`PlayerBGPriorityData`[1] = `$20`, the room's entrance control being 1) and while he rises out of pipe 163. The bit is cleared once he is in play again (game routine 8) and his sprite is below y = `$40`. | `HandlePipeEntry` l. 12287, `PipeDwnS` l. 12086-12091, `PlayerBGPriorityData` l. 2826-2827, `Entrance_GameTimerSetup` l. 2860-2861, `PlayerCtrlRoutine` l. 5612-5623 |

**Replica choices** (spec §4, §5):
- **The room is its own 16 × 15 grid**, kept with 1-1's data, and a fixed screen. Mario's x there is in the room's own pixels.
- **The black screens are skipped.** The original blanks the screen for some frames while it loads the next area; the replica changes area at once, at the end of the sinking or the walk into the exit pipe. Every frame that shows something is kept: the 48-tick sinking, the drop into the room, the 160-tick walk into the exit pipe and the 96-tick rise out of pipe 163.
- **Entering** needs, as in the original, Mario on the ground, holding down with neither left nor right, his foot probes at sprite x + 3 and + 12 over the warp pipe's two columns, and his feet on its top.
- **Leaving** is his box against the mouth's lower tile, (13, 12), on the ground, facing right: the replica's boxes stop him with his box's right edge on the mouth (sprite x 194).
- **The walk into the exit pipe** keeps 0.5 px a tick: the original's friction can carry the speed's fraction into a ninth 1/16 px now and then, which isn't modelled.
- **Coins** are collected by Mario's box touching their tile, as the replica's boxes stand for the original's probes elsewhere.
- **The views** (spec §8) draw the room on black, with no scenery. The exit pipe's tiles are their own kind, `SIDE_PIPE`, solid as a pipe's, so the Sprite view can draw its mouth and body, which have the same neighbours as an upright pipe's rim and body. A pipe tile on the playfield's top row, row 2, is drawn as the body, so the shaft has no rim. While a pipe transition moves Mario (the drop into the room too) he is drawn behind the tiles. The original clears that once his sprite is below y = `$40` after control returns, which is always so in the room and on pipe 163's top; the replica clears it as control returns.
- **A change of area** starts Mario afresh where he arrives, keeping his power state and nothing else (no speed, no invincibility, no invulnerability), clears enemies, items and fireballs, and restarts the level timer's unit. Enemies already passed over in 1-1 stay skipped on the way back; those due at page 10 activate as the screen arrives there.

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
- **Not covered:** enemy AI/speeds and item behaviour. Each is a separate research question. (The bonus room's layout was added for #23.)

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
