# Super Mario Bros. (NES, NTSC) movement and physics constants

> Copied from branch `research/smb-physics-constants` (#2). The engine stores positions in 1/4096 px on both axes (#4, #8), not the mixed units suggested in section 6; every value here converts exactly.

Research for issue #2. The goal is a pygame replica of World 1-1 that runs at a fixed 60 ticks/s.
Every value below is **per NES frame**. One engine tick equals one NES frame.

## Sources

| Key | Source | Trust |
|---|---|---|
| **[D]** | doppelganger, *SMBDIS.ASM – A Comprehensive Super Mario Bros. Disassembly*, <https://gist.github.com/1wErt3r/4048722>. Line numbers below refer to that file (16,351 lines). | **Primary.** The data tables are ROM bytes. The labels and comments are doppelganger's interpretation. |
| **[S]** | slither (silverslither), *SMBpedia – Movement*, last updated 2025-02-08, <https://simplistic6502.github.io/smb1_tll/smbpedia_movement.html> | High. Written from [D] (it uses [D]'s variable names) and used by speedrunners and TASers. |
| **[J]** | Jdaster64, *A Complete Guide to SMB's Physics Engine* (image), archived at <https://web.archive.org/web/20130807122227/http://i276.photobucket.com/albums/kk21/jdaster64/smb_playerphysics.png> | Medium. The community's classic reference. Its own disclaimer says it is "not 100% accurate … from a coding perspective". |
| **[T]** | TASVideos, *Game Resources: NES Super Mario Bros.*, <https://tasvideos.org/GameResources/NES/SuperMarioBros> | High, but it covers only a few facts. |
| **[N]** | NESdev Wiki, *Cycle reference chart* (<https://www.nesdev.org/wiki/Cycle_reference_chart>), and NESdev BBS on NTSC frame rate | High. The wiki returned 403 to direct fetch, so this figure came through search excerpts. |

When sources disagree, **[D] wins**, because it is the game's own code and data. [S] agrees with [D] on every value checked here. The places where [J] differs are listed in [Disagreements](#disagreements-between-sources).

## Frame rate

- An NTSC NES renders 29,780.5 CPU cycles per frame at 1.789773 MHz, which is **≈ 60.0988 frames/s** [N].
- SMB runs its whole game loop once per frame (NMI), so all constants here are per frame [D].
- A 60 ticks/s engine that uses these per-frame constants unchanged plays about 0.16 % slower in wall-clock time than real hardware. That is negligible. Keep the constants per tick and do not rescale them.
- PAL values differ and are out of scope.

## Units

SMB uses different fixed-point formats on the two axes [D][S].

| Quantity | Storage | 1 unit equals |
|---|---|---|
| X speed (`Player_X_Speed`, `$57`) | signed byte | **1/16 px/frame**. [T] calls this "16 subpixels make up 1 pixel". |
| X sub-speed (`Player_X_MoveForce`, `$0705`) | unsigned byte, used only to accumulate acceleration | 1/256 of an X-speed unit = **1/4096 px/frame** |
| X position fraction (`SprObject_X_MoveForce`, `$0400`) | high nibble used | 1/16 px |
| Y speed (`Player_Y_Speed`) | signed byte | **1 px/frame** |
| Y sub-speed (`Player_Y_MoveForce`, `$0433`) | unsigned byte | **1/256 px/frame** |
| Y position fraction (`Player_YMF_Dummy`, `$0416`) | byte | 1/256 px |
| Gravity (`VerticalForce` / `VerticalForceDown`) | byte added to Y sub-speed each frame | **1/256 px/frame²** |
| X acceleration (`FrictionAdderLow/High`) | 9-bit value added to X sub-speed each frame | **1/4096 px/frame²** |

**How motion is integrated.** In `MoveObjectHorizontally` (l. 7541), position advances by `speed/16` px each frame. The 4-bit fraction is kept in `$0400`. The X sub-speed does **not** move Mario. It only carries into the speed byte [S]. In `ImposeGravity` (l. 7704), Y position advances by `speed + subspeed/256`. *After* that, gravity is added to the speed. The order each frame is therefore position first, then velocity.

[J] writes values as five hex digits, block.pixel.sub.subsub.subsubsub, each digit 1/16 of the one before it. A [J] value `0xABCDE` therefore means `0xABCDE / 4096` px. For example, [J] `0x00098` equals [D] acceleration `$98`, and [J] `0x04000` equals [D] Y speed `4`.

Physics are identical for small and big Mario. The physics routines never read `PlayerSize` except to pick the jump sound [D l. 6134-6138].

---

## 1. Horizontal movement on the ground

### Top speeds (`MaxLeftXSpdData`/`MaxRightXSpdData`, [D] l. 6026-6031)

| Condition | Raw | px/frame | Source |
|---|---|---|---|
| Walking (B not held, `RunningTimer` = 0) | 24 (`$18`) | **1.5** | [D], [S] |
| Running (B held, or `RunningTimer` > 0) | 40 (`$28`) | **2.5** | [D], [S] |
| Water level, on the ground | 16 (`$10`) | 1.0 | [D], [S] |
| Pipe-entrance cutscene (`GameEngineSubroutine` = 7) | 12 (`$0C`) | 0.75 | [D], [S] |

- **`RunningTimer`** is set to 10 frames on each frame where Mario is on the ground, holds B, and holds the direction he is moving. It is a frame timer that counts down every frame [D `SetRTmr` l. 6168, `DecTimers` l. 789-799][S]. If B is released while running, Mario keeps the 2.5 cap for 10 frames. After that the cap drops to 1.5 and the speed is **clamped instantly** to 24 [D `ImposeFriction` l. 6227][J].
- **Hard cap and soft cap.** The clamp only runs in the direction Mario is accelerating. If no direction is held, the speed decays by friction and is never clamped, so a speed above the current cap bleeds off gradually [S].

### Acceleration and deceleration (`FrictionData`, [D] l. 6033; selected in `X_Physics` l. 6139)

The base value is chosen from `FrictionData = [$E4, $98, $D0]`. It is **doubled** whenever `PlayerFacingDir ≠ Player_MovingDir` [D l. 6180-6187][S]. On the ground, the facing direction follows the d-pad and the moving direction follows the sign of the speed. So pressing against the current motion (a skid) doubles the value.

| Situation (ground) | Raw (1/4096 px/f²) | px/frame² | Source |
|---|---|---|---|
| Walk acceleration (holding forward, no B) | `$98` = 152 | **0.037109** | [D], [S], [J] |
| Run acceleration (holding forward + B, or `RunningTimer` > 0) | `$E4` = 228 | **0.055664** | [D], [S], [J] |
| Release deceleration (no direction held), normally | `$98` = 152 | **0.037109** | [D] (see disagreement 3) |
| Release deceleration when the `RunningSpeed` flag is set (speed reached ≥ 28, i.e. ≥ 1.75 px/f) or speed ≥ 33 | `$D0` = 208 | **0.050781** | [D] l. 6159-6166, [S], [J] |
| Skid (holding opposite direction) from walk speed | `$98`×2 = 304 | **0.074219** | [D] |
| Skid with `RunningSpeed` set | `$D0`×2 = 416 | **0.101563** | [D], [J] (`0x001A0`) |
| First frame of acceleration from standstill, when the facing direction differs from the stored moving direction | `$98`×2 = 304 | 0.074219 | [D]; this is [J]'s "minimum walk velocity 0x00130" |

- **`RunningSpeed` flag** (`GetPlayerAnimSpeed`, [D] l. 6195-6211). It is set when |speed| ≥ 28. It is cleared only on a frame where Mario holds his moving direction with |speed| < 28 [S].
- **Skid turnaround** ([D] `ChkSkid`/`ProcSkid` l. 6204-6220). While Mario holds the opposite direction, or any button other than A and the travel direction, and |speed| < **11** (`$0B`, 0.6875 px/f), the game zeroes the speed and sub-speed and flips the moving direction to the facing direction [D][S]. Mario then accelerates the new way from zero.
- **Release friction stops at zero.** Friction is applied toward zero by the sign of the speed. If the speed is 0 and no button is held, nothing changes [D `ImposeFriction` l. 6227-6234][S].

### Derived figures (computed from [D] values)

- 0 to walk cap: about 40 frames (24 × 256 / 152).
- 0 to run cap: about 45 frames.
- Run cap to stop with no input: about 49 frames.

---

## 2. Horizontal movement in the air

All values from [D] `X_Physics` (l. 6139-6191) and `JumpSwimSub` (l. 5922-5957), confirmed by [S] and [J].

- **No direction held means no change.** `ImposeFriction` is called in the air only when a direction is held, so momentum is preserved [D `LRAir` l. 5947-5949][J].
- **B does nothing in the air** [D][J].
- **Facing direction is frozen in the air**, because it is updated only on the ground or when swimming. Pressing backward is therefore *not* doubled, unless Mario was already facing against his motion at takeoff (for example, jumping mid-skid) [D].

| Current |X speed| | Cap | Acceleration (forward or backward) |
|---|---|---|---|
| ≥ 25 (≥ 1.5625 px/f) | 40 (2.5 px/f) | `$E4` (0.055664) |
| < 25, `RunningSpeed` set | 24 (1.5 px/f) | `$D0` (0.050781) |
| < 25, `RunningSpeed` clear | 24 (1.5 px/f) | `$98` (0.037109) |

---

## 3. Jumping and gravity

### Jump initiation (`ProcJumping`, [D] l. 6074-6131; tables l. 6014-6024)

A jump starts only on the frame A goes from released to pressed while Mario is on the ground [D `CheckForJumping` l. 6064-6072]. The |X speed| *at takeoff* picks a row. The thresholds are `[9, 16, 25, 28]`, but rows 0/1 and rows 3/4 hold identical data, so there are three effective bands [D][S]:

| Takeoff |X speed| | Initial Y speed | Gravity while rising **and A held** (`JumpMForceData`) | Gravity otherwise (`FallMForceData`) | Source |
|---|---|---|---|---|---|
| < 16 (< 1.0 px/f) | **−4.0 px/f** (`$FC`, sub-speed 0) | `$20` = **0.125 px/f²** | `$70` = **0.4375 px/f²** | [D], [S], [J] |
| 16 – 24 (1.0 – 1.5 px/f) | **−4.0 px/f** | `$1E` = **0.1171875** | `$60` = **0.375** | [D], [S], [J] |
| ≥ 25 (≥ 1.5625 px/f) | **−5.0 px/f** (`$FB`) | `$28` = **0.15625** | `$90` = **0.5625** | [D], [S]; [J] gives a different threshold (disagreement 2) |

Because the walk cap is 24, a walking jump never reaches the third band. Only a run does.

### How holding A changes the arc (`JumpSwimSub`, [D] l. 5922-5934)

- Each frame in the air, if Y speed < 0 **and** A is held this frame and was held last frame, the gentle rising gravity (`VerticalForce`) stays in effect.
- Otherwise `VerticalForce` is overwritten with the falling gravity (`VerticalForceDown`). This happens when Mario starts falling (Y speed ≥ 0) or when A is released.
- Once switched, the rising gravity does **not** come back until the next jump. Pressing A again mid-air has no effect [D][S][J].
- On the very first frame (before the "held last frame" condition can be true), the routine keeps the rising gravity while Mario has risen less than `DiffToHaltJump` = 1 px [D l. 5928-5932, l. 6108-6109][S].
- So releasing A early cuts the jump. Holding A gives a long jump up to the apex.

### Simulated jump heights (from [D] constants)

These come from a per-frame simulation of `ImposeGravity` using [D]'s constants. Use them as reference values for tests. They are accurate to about ±1 px, because the real game also truncates position and collides with tiles.

| Band | A held to apex: height / frames to apex | A tapped for 1 frame: height / frames |
|---|---|---|
| < 1.0 px/f | ≈ 66 px (≈ 4.1 tiles) / 32 f | ≈ 23 px / 10 f |
| 1.0 – 1.5 px/f | ≈ 70 px / 35 f | ≈ 26 px / 12 f |
| ≥ 1.5625 px/f | ≈ 82.5 px (≈ 5.2 tiles) / 32 f | ≈ 28 px / 10 f |

### Other gravity values

| Situation | Value | Source |
|---|---|---|
| Walking off a ledge | Uses whatever `VerticalForceDown` holds, i.e. the falling gravity of the *last* jump (`FallingSub`) | [D] l. 5915-5918, [J] |
| `VerticalForceDown` at area/level entry, before any jump | `$28` = **0.15625 px/f²**. Walking off a ledge before ever jumping in an area gives a slow fall. | [D] l. 2836-2837, [S], [J] ("level entry 0x00280") |
| Death | Y speed −4, gravity `$28`, X speed 0 | [D] `KillPlayer` l. 11427-11435, l. 5952-5956, [S] |
| Landing | Y speed and sub-speed reset to 0 | [S] |
| Head hits a hard block or a used block | Y speed set to +1 px/f, sub-speed kept | [S] |
| Head hits a brick: does not break / breaks | Y speed 0 / −2 | [S] |

### Terminal fall speed (`MovePlayerVertically` → `ImposeGravity`, [D] l. 7586-7596, l. 7728-7735)

- The cap is **4 px/frame** (Mario's maximum vertical speed `$04`) [D][S][J].
- Quirk: the clamp fires only when speed ≥ 4 **and** sub-speed ≥ `$80`. Speed can therefore sit between 4.0 and about 4.5 for a frame before it snaps back to exactly 4.0 [D][S]. [J] describes the same thing as "caps at 0x04800, wrapping back to 0x04000".
- For a replica, `vy = min(vy, 4.0)` is close enough. To be exact, reproduce the two-condition check.

---

## 4. Stomp bounce (`EnemyStomped`, [D] l. 11439-11513)

| Enemy stomped | Mario's new Y speed | Source |
|---|---|---|
| Goomba, Koopa Troopa (turned into a shell), Paratroopa (demoted to Troopa) | **−4.0 px/f** (`SBnce`, `$FC`) | [D] l. 11511, [S] |
| Cheep Cheep, Bullet Bill, Hammer Bro, Lakitu, Blooper | −3.0 px/f (`$FD`) | [D] l. 11477, [S] |
| Spiny | Stomp hurts Mario | [D] l. 11441-11443 |

- **Gravity is not reset on a stomp** [D][S]. The Y sub-speed is not changed either [S].
- Mario stomps while falling, so `VerticalForce` already holds the falling gravity. Holding A therefore does **not** make the bounce higher [D].
- Using the 1-1 typical fall gravity `$70`, the bounce rises about 20 px over about 10 frames. With `$90` it rises about 16 px.
- The player–enemy collision check runs **only on every other frame** (`FrameCounter` bit 0) [D `PlayerEnemyCollision` l. 11293-11296][T].

---

## 5. Enemy and item speeds

Enemy X speeds use the same 1/16 px/frame unit and the same `MoveObjectHorizontally` routine [D l. 7530-7534].

| Object | Value | px/frame | Source |
|---|---|---|---|
| Goomba walk | `$F8` = −8 (starts moving left) | **0.5** | [D] `NormalXSpdData` l. 8163, `InitGoomba` l. 8138 |
| Green/Red Koopa Troopa walk (objects `$00-$03`) | −8 | **0.5** | [D] l. 8072-8075, l. 8166-8180 |
| Same, when the hard-mode flag `PrimaryHardMode` is set (not set in first-quest 1-1) | `$F4` = −12 | 0.75 | [D] l. 8163-8172 (`GetESpd`) |
| Kicked Koopa shell | `$30` / `$D0` = ±48, away from Mario | **3.0** | [D] `KickedShellXSpdData` l. 11287, l. 11360-11364 |
| Kicked shell while airborne | speed reduced by 24 toward zero (`XSpeedAdderData`) | ≈ 1.5 | [D] l. 9207, `SlowM`/`AddHS` l. 9324-9332. Moderate confidence: read from code, not checked elsewhere. |
| Koopa re-emerging from shell | ±8 (hard mode ±12) | 0.5 | [D] `RevivedXSpeed` l. 9210 |
| Shell revival delay | `EnemyIntervalTimer` = `$10` interval ticks (1 tick = 21 frames) → ≈ 336 frames ≈ 5.6 s (hard mode `$0B`) | – | [D] `RevivalRateData` l. 11496, `DecTimers` l. 789-799 |
| Stomped Goomba removal | removed when its interval timer goes from `$10` to `$0E` → ≈ 22–42 frames | – | [D] `ChkKillGoomba` l. 9360-9367 |
| Demoted Paratroopa | ±8 | 0.5 | [D] `DemotedKoopaXSpdData` l. 11290 |
| Enemy knocked from below a bumped block | Y −3 px/f, X ±1 px/f (`$10`/`$F0`), away from Mario | 1.0 | [D] l. 12466-12492 |
| **Mushroom (and 1-up)**: emerging | rises 1 px every 4 frames for 16 px (≈ 64 frames), drawn behind the block | – | [D] `GrowThePowerUp` l. 7181-7196 |
| **Mushroom**: moving | `$10` = +16, always starts moving **right**, reverses at walls | **1.0** | [D] l. 7188-7196 |
| Starman | X +1.0 px/f; vertical gravity `$1C`/256, max 3 px/f; re-bounces with Y −3 px/f on landing | 1.0 | [D] `MoveJumpingEnemy`/`EnemyJump`, `MoveJ_EnemyVertically` l. 7642-7645, l. 9371 |
| Enemy and mushroom falling (off a ledge, or a defeated enemy) | gravity `$3D` = **0.238 px/f²**, terminal **3 px/f** (same ≥ `$80` quirk) | – | [D] `MoveD_EnemyVertically` l. 7599-7604 → `SetHiMax` l. 7644-7645 |

---

## 6. Suggested representation for the pygame engine

This is a recommendation, not a sourced fact.

- **X:** store `speed` as an int in 1/16 px/frame units, `subspeed` as an int 0–255, and position as an int in 1/16 px.
  Each tick:
  1. `subspeed += accel` (accel in 1/4096 px/f²).
  2. Carry into `speed`.
  3. Clamp.
  4. `pos += speed`.
- **Y:** store velocity as a signed int in 1/256 px/frame and position as an int in 1/256 px.
  Each tick:
  1. `pos += vel`.
  2. `vel += gravity` (in 1/256 px/f²).
  3. Cap at 4 × 256.
- Integer fixed-point reproduces [D]'s behaviour exactly and is deterministic. Determinism matters for neuroevolution, so that the same genome gets the same fitness.
- **Per-frame order** in [D] `PlayerMovementSubs` (l. 5874):
  1. Jump check and physics-table selection.
  2. Horizontal friction/acceleration.
  3. Horizontal move.
  4. Vertical move.
  5. Collisions follow later in the frame.

---

## Disagreements between sources

1. **Top speeds are off by one in [J].** [J] lists max walk 0x01900, max run 0x02900, underwater 0x01100 and entry 0x00D00. [D]'s tables say 24/40/16/12 (`$18/$28/$10/$0C`), and [S] agrees (±24, ±40, ±16, 12). [J] seems to state these limits as exclusive bounds. **Use [D]: 1.5 / 2.5 / 1.0 / 0.75 px/f.**
2. **Fast-jump threshold.** [J] says the −5 px/f jump needs takeoff speed ≥ 0x02500 (≈ 2.31 px/f). [D] compares `Player_XSpeedAbsolute` against `#$19` (25 = 1.5625 px/f) [D l. 6095-6106]. [S] gives the same `[9, 16, 25, 28]` thresholds. [J]'s other two bands match [D] exactly. **Use [D]: ≥ 25.**
3. **Release deceleration.** [J] gives a single value, 0x000D0. [D]/[S] use `$D0` only while `RunningSpeed` is set (or |speed| ≥ 33), and otherwise `$98`. **Use [D].**
4. **Skid turnaround speed.** [J] gives 0x00900 (0.5625 px/f). [D] uses |speed| < `$0B` = 11 (0.6875 px/f) [D `ProcSkid` l. 6213-6215], and [S] agrees ("less than 11"). **Use [D]: 11.**
5. **"Minimum walk velocity 0x00130"** in [J] is not a constant in [D]. It is the doubled first-frame acceleration (2 × `$98`) that happens when the facing and moving directions differ.
6. **Unit naming.** [T] and [S] call 1/16 px a "subpixel". [J] calls 1/16 px an "s.-pixel" and goes down to 1/4096 px. Some forum posts use "subpixel" for 1/256 px. The table in [Units](#units) defines every unit used here.

## Added during the build (#15)

These facts were sourced from [D] while building the play-mode tracer bullet. Line numbers refer to the same file.

| Fact | Value | Source |
|---|---|---|
| Player start position | sprite x = `$28` (40 px). Sprite y = `$B0` (176 px) for 1-1's entrance setting (header `$50`, bits 5–3 = 2). The player object is 16 × 32 px, so small Mario's feet rest at y + 32 = 208, the ground top. | [D] `PlayerStarting_X_Pos` l. 2815, `PlayerStarting_Y_Pos` l. 2822 |
| Small Mario's background probes | head at sprite (8, 18); feet at (3, 32) and (12, 32); sides at (2, 24) and (13, 24). The replica uses one box from them: **12 × 14 px at sprite offset (2, 18)**. | [D] `BlockBufferAdderData` l. 13027 (offset `$0E` for small Mario), `BlockBuffer_X_Adder` l. 13030, `BlockBuffer_Y_Adder` l. 13036 |
| Per-frame order | timers count down first (in the NMI), then: jump check and X physics → ground, jump or fall movement → moving direction from the sign of the speed → scroll → background collision → pit check. Only the jump and fall states move Mario vertically. | [D] `DecTimers` l. 789, `PlayerCtrlRoutine` l. 5558-5612, `OnGroundStateSub` l. 5903 |
| Walking off a ledge | at the start of background collision, the on-ground state becomes falling. It returns to on-ground only if the feet probes find ground. | [D] `SetFallS` l. 11917, `LandPlyr` l. 12015 |
| Down held on the ground with a direction | left/right are ignored that frame (for small Mario too). | [D] l. 5580-5590 |
| Skid turnaround condition | runs on the ground when any button other than A is held and the held direction is not the moving direction. Below speed 11 it zeroes the speed and its fraction and sets the moving direction to the facing direction. | [D] `ChkSkid`/`ProcSkid` l. 6204-6220 |
| Head bump | Y speed byte set to 1; the fraction is kept. | [D] `NYSpd` l. 11972 |
| Landing | Y snapped to the tile top; Y speed and fraction set to 0. | [D] `LandPlyr` l. 12015-12026 |
| Wall bump | when moving into the wall: X speed byte set to 0, fraction kept, and `SideCollisionTimer` = 16 frames, which blocks scrolling. | [D] `ImpedePlayerMove` l. 12318-12349 |
| Scroll amount | only if the sprite's screen x *on the previous frame* was ≥ 80 px and Mario moved right this frame. Below 112 px the screen scrolls by (pixels moved − 1), but at least 1. From 112 px it scrolls by the pixels moved. The previous-frame position is stored by the player renderer, after the scroll. | [D] `ScrollHandler`/`ChkNearMid` l. 5378-5405, `RenderPlayerSub` l. 14565 |
| Screen edges | a sprite at or left of the screen's left edge is put on it. A sprite less than 16 px from the right edge (x > left + 239) is put at left + 239. Either way the X speed byte is zeroed unless Mario holds the direction away from that edge. | [D] `KeepOnscr` l. 5438-5452, `X_SubtracterData` l. 5454, `GetXOffscreenBits` l. 14909, `DividePDiff` l. 14978 |
| Pit death | once the sprite's top reaches y = 256 (`Player_Y_HighPos` = 2). | [D] `PlayerHole` l. 5624-5627 |

**Replica simplifications**:
- The replica uses one box and axis-separated push-out, as the spec decided, instead of the probes.
- The scroll uses Mario's net pixel movement after the wall push-out, so the 16-frame `SideCollisionTimer` isn't needed.

## Added during the build (#17)

These facts were sourced from [D] while building the Goombas. Line numbers refer to the same file.

| Fact | Value | Source |
|---|---|---|
| Goomba start | Speed `$F8` (−0.5 px/f), moving left, vertical speed 0. | [D] `InitGoomba` l. 8138-8140, `InitNormalEnemy` l. 8166-8174, `SetBBox`/`InitVStf` l. 8224-8230 |
| Goomba walking and falling | In its normal state a Goomba only moves sideways. With no ground under it, it falls with enemy gravity and keeps moving sideways at the same speed. | [D] `MoveNormalEnemy` l. 9293-9330 |
| Goomba tile probes | Foot probe at sprite (8, 24). Side probes at sprite (0, 20) and (16, 20). Only the side it is moving towards is checked, and a solid tile there turns it around. | [D] `ChkUnderEnemy` l. 12707-12710, `DoEnemySideCheck` l. 12592-12608, `BlockBuffer_X_Adder` l. 13030, `BlockBuffer_Y_Adder` l. 13036 |
| Enemy landing | Y speed and its fraction set to 0, and y snapped to `(y & $F0) + 8`. | [D] `EnemyLanding` l. 12646-12652 |
| Enemy bounding boxes | The Goomba's box for touching Mario is control `$09` = sprite (3, 14) to (13, 20), and small Mario's is `$01` = (3, 20) to (13, 32), edges inclusive. | [D] `SmallBBox` l. 8209, `ChkMoveDir` l. 5591-5598, `BoundBoxCtrlData` l. 12766-12778, `PlayerCollisionCore` l. 12931-12988 |
| Stomp or injury | Mario moving down (Y speed byte positive and not 0) touching a Goomba stomps it, wherever his feet are. Moving up, or with Y speed byte 0, he is hurt. The position test (Mario's y + 12 above the enemy's y) applies only to enemies from `$07` (Blooper) on, none of which are in 1-1. | [D] `ChkForPlayerInjury` l. 11376-11389 |
| Same-frame stomps | `StompTimer` goes up by 1 with each stomp. While it is not 0, any touch counts as a stomp. It is a frame timer (`$0791`, inside the frame timers `$0780`-`$0794`), so it is back at 0 by the next check. | [D] `ChkETmrs` l. 11388-11389, `HandleStompedShellE` l. 11507, `Timers` l. 81-99, `DecTimers` l. 789-799 |
| Stomped Goomba | State `$04`. Mario's Y speed byte set to −4 (`SBnce`). The Goomba no longer moves or hurts Mario, and is erased when its interval timer goes from `$10` to `$0E`. | [D] `HandleStompedShellE` l. 11499-11513, `ReviveStunned`/`ChkKillGoomba` l. 9338-9367, `HandlePECollisions` l. 11351-11357 |
| Interval timers | They count down once every 21 frames (`IntervalTimerControl` reloads `$14`). That control is not cleared at area start, so the first count after a stomp comes 1-21 frames later. | [D] `DecTimers` l. 789-799, `InitializeArea` l. 2660-2667 |

**Replica choices**:
- **Goomba hitbox:** one 16 × 16 box at sprite offset (0, 8), from its probes, used for tiles and for Mario. This matches how #15 took Mario's box from his probes. The original's smaller bounding boxes (row above) are not used.
- **Stomp rule:** as in the original, moving down at 1 px/f or more (`STOMP_MIN_FALL_SPEED`), wherever the feet are. The spec (§4) also asked for "feet above the enemy's centre". With the every-other-tick check, Mario falls up to about 9 px between checks, more than half of a 16 px Goomba, so that clause skipped the stomp. In a sweep of walking and running jumps onto a ground Goomba, 224 of 386 fall-ons killed Mario with the clause, and none without it.
- **Squash time:** always the longest, 2 × 21 = 42 ticks, so it stays deterministic.

## Added during the build (#18)

These facts were sourced from [D] while building the blocks. Line numbers refer to the same file.

| Fact | Value | Source |
|---|---|---|
| Which block the head hits | One head probe, at sprite (8, 18) for small Mario: the block over his centre. The block object is placed at `(Player_X + 8) & $F0`. | [D] `HeadChk` l. 11946-11965, `InitBlock_XY_Pos` l. 7290-7303 |
| Head hits a block it can bump | `BumpBlock` sets the Y speed byte to 0; the fraction is kept. A hard or used block sets it to 1 instead (`NYSpd`). | [D] `BumpBlock` l. 7307-7314, `SolidOrClimb`/`NYSpd` l. 11967-11973 |
| Bump lockout | `BlockBounceTimer` = `$10` frames after a bump. While it runs, a head hit bumps nothing and sets the Y speed byte to 1. | [D] `PlayerHeadCollision` l. 7263-7264, `HeadChk` l. 11962-11963 |
| Bouncing block | Starts at Y speed −2 (`$FE`), gravity `$50`, max fall speed 8 (`MaxSpdBlockData`). It ends when the low nybble of its y is below 5 again, which is back in place: about 8 px up and down in 13 frames. While it bounces, its tile is the blank metatile `$23`. | [D] `BumpBlock` l. 7315-7316, `BouncingBlockHandler` l. 7481-7494, `ImposeGravityBlock` l. 7660-7666, `MaxSpdBlockData` l. 7653-7654, `PlayerHeadCollision` l. 7260-7262 |
| What a hit does | Small Mario: a plain brick only bumps. A coin `?` block gives a coin (`CoinBlock` → `GiveOneCoin`: 1 coin, 200 points) and becomes the used block `$C4`, as do the power-up `?` block, the Starman brick and the hidden 1-UP block (their items come from `SetupPowerUp`). | [D] `PlayerHeadCollision` l. 7219-7258, `BumpBlock` l. 7317-7335, `CoinBlock`/`JCoinC` l. 6963-6998, `GiveOneCoin`/`CoinPoints` l. 7084-7102 |
| Hidden 1-UP block | Not solid for Mario's feet and sides (`ChkInvisibleMTiles`), nor for enemies (`ChkForNonSolids`); only the head probe finds it. | [D] `ContChk` l. 12005-12006, `CheckSideMTiles` l. 12063-12065, `ChkInvisibleMTiles` l. 12238-12242, `ChkForNonSolids` l. 12712-12722 |
| Enemy on a bouncing block | An enemy whose foot probe finds `$23` under it: a Goomba is defeated (`KillEnemyAboveBlock` → `ShellOrBlockDefeat`), 100 points. Both routines set the same floatey number, so it is 100 once, not twice. A Koopa is only stunned. The tile is then set to blank `$00` so it doesn't trigger again. | [D] `HandleEToBGCollision` l. 12436-12453, `ShellOrBlockDefeat` l. 11172-11199, `SetupFloateyNumber` l. 11533-11540 |
| Defeated by a bump | Raised 2 px, X speed ±1 px/f (`$10`/`$F0`) away from Mario, Y speed −4 (`$FC`, overriding the stun's −3). It then falls with enemy gravity `$3D` up to 3 px/f, through all tiles. | [D] `ChkToStunEnemies` l. 12455-12492, `KillEnemyAboveBlock` l. 12686-12690, `MoveDefeatedEnemy` l. 9356-9358, `MoveD_EnemyVertically` l. 7599-7607 |

**Replica choices**:
- **Hidden block from below:** it stops a box that enters its row from below, and only then. Mario can't be inside it from the side and then reveal it by rising.
- **Bounce end:** the block is back when its offset is no longer above its place. With the bounce's 8 px rise, that is the original's "low nybble below 5" test.
- **One enemy per bump:** the original's `$00` write is not copied. Every enemy standing on a bouncing block is defeated. In 1-1, two Goombas are never over the same block: the pair stands 24 px apart.
- **Who is left of whom:** the direction away from Mario compares the enemy's x with the left edge of Mario's hitbox, not his sprite x, which is 2 px further left.

## Added during the build (#19)

These facts were sourced from [D] while building the mushroom, big Mario, brick breaking, damage and the 1-UP. Line numbers refer to the same file.

| Fact | Value | Source |
|---|---|---|
| Big Mario's background probes | Big Mario uses adder set `$00`: head at sprite (8, 4), feet at (3, 32) and (12, 32), sides at (2, 8), (2, 24), (13, 8) and (13, 24). Crouching (and small) uses set `$0E`, small Mario's. The replica's boxes: **big 12 × 28 at sprite offset (2, 4)**; crouching, small Mario's 12 × 14 at (2, 18). | [D] `ChkCollSize` l. 11929-11940, `BlockBufferAdderData` l. 13027, `BlockBuffer_X_Adder` l. 13030, `BlockBuffer_Y_Adder` l. 13036 |
| Crouching | Each frame, big Mario on the ground has `CrouchingFlag` set from the down button. In the air the flag keeps its value; small Mario's is always 0. | [D] `PlayerMovementSubs` l. 5874-5882 |
| What big Mario's head does | The block object gets the breakable state `$12` when big. A block holding something (`BrickQBlockMetatiles`: ? blocks and the bricks with coins, a Starman, a vine or a 1-UP) is set back to the unbreakable `$11` and bumped as for small Mario. A plain brick is broken. Crouching changes only the block object's y. | [D] `PlayerHeadCollision`/`DBlockSte` l. 7219-7277, `BrickQBlockMetatiles` l. 7361-7366, `BlockBumpedChk` l. 7368-7374 |
| Breaking a brick | `BrickShatter`: Mario's Y speed byte set to −2 (`$FE`), so he keeps rising; 50 points (`DigitModifier+5` = 5). The bounce lockout `BlockBounceTimer` = `$10` is set as for a bump. The block buffer gets the blank metatile `$00` later in the same frame, after the enemies have run. | [D] `BrickShatter` l. 7379-7391, `PlayerHeadCollision` l. 7263-7264, `BlockObjMT_Updater` l. 7502-7523, `GameEngine` l. 5310-5323 |
| Enemy on a breaking brick | During that frame the brick's tile is the blank-but-solid `$23`, so an enemy standing on it is defeated as on a bouncing block. | [D] `PlayerHeadCollision` l. 7261-7262, `HandleEToBGCollision` l. 12436-12453, `GameEngine` l. 5310-5323 |
| What a power-up block releases | `MushFlowerBlock` (type 0) and `ExtraLifeMushBlock` (type 3). Type 0 becomes the fire flower when `PlayerStatus` is not small. | [D] `BumpBlock` jump table l. 7326-7334, `MushFlowerBlock` l. 7338, `ExtraLifeMushBlock` l. 7346-7349, `SetupPowerUp` l. 7144-7149 |
| One power-up at a time | It always takes enemy slot 5, so a new one replaces the old. | [D] `SetupPowerUp` l. 7125-7128 |
| Power-up start | x = the block's x; sprite y = the block's y − 8, so its 16 × 16 box (enemy probes) starts exactly over the block. | [D] `SetupPowerUp` l. 7129-7137 |
| Rising out of the block | Every 4th frame (`FrameCounter & 3` = 0) it rises 1 px and its state goes up by 1, from 1. On the 17th step (state was `$11`) it gets X speed `$10` (1 px/f) to the right instead, and moves from the next frame. Mario can touch it once the state is ≥ 6 (5 px risen). It is drawn behind the background until then. | [D] `GrowThePowerUp` l. 7181-7199 |
| Mushroom movement | Both mushrooms move as an enemy does (`MoveNormalEnemy`, `EnemyToBGCollisionDet`): turn at walls, fall with enemy gravity. Nothing moves while `TimerControl` is set. | [D] `PowerUpObjHandler` l. 7159-7179 |
| Power-up removal | As every enemy object: once more than 72 px past either screen edge. | [D] `OffscreenBoundsCheck` l. 11006-11050 |
| Collecting | Through `PlayerEnemyCollision`: every other frame, only while the player control routine runs (`GameEngineSubroutine` = 8). Slot 5 is checked after the enemies. A mushroom or fire flower gives 1000 points (floatey number `$06`); the 1-UP gives a life instead (`$0B`). Small Mario becomes super (routine `$09`); super becomes fiery. | [D] `PlayerEnemyCollision` l. 11293-11314, `CheckForPUpCollision` l. 11316-11320, `HandlePowerUpCollision` l. 11237-11252, `Shroom_Flower_PUp`/`UpToSuper` l. 11254-11280, `FloateyNumTileData` l. 1262-1274 |
| The freeze | `SetPRout` sets `TimerControl` = `$FF`. Each frame the NMI counts it down and runs no frame or interval timers while it isn't 0, and enemies and power-ups don't move. It also sets `Player_State`: 0 (on the ground) for a power-up, 1 (jumping) for an injury. The jump button is still saved every frame. | [D] `SetPRout`/`SetKRout` l. 11415-11422, `UpToFiery` l. 11277-11280, `NMI` l. 785-800, `GameEngine` l. 5357 |
| Growing | `PlayerChangeSize`: the size flips at `TimerControl` = `$F8` (7 frames in) and play resumes at `$C4` (59 frames). | [D] `PlayerChangeSize` l. 5732-5740, `InitChangeSize` l. 5753-5761, `DonePlayerTask` l. 5772-5777 |
| Shrinking | `PlayerInjuryBlink`: frozen until `$F0`, where the size flips (the `ExitBlink` branch falls through to `InitChangeSize`), then movement stays off while the change-size flag is set, and play resumes at `$C8` (55 frames). | [D] `PlayerInjuryBlink` l. 5744-5751, `PlayerMovementSubs` l. 5884-5885 |
| Size-change animation | From the flip, the frame steps every 4th frame, 10 frames. Growing shows `ChangeSizeOffsetAdder` 0, 1, 0, 1, 0, 1, 2, 0, 1, 2 (small, intermediate, big). The intermediate grow frame is 24 px tall: its top row of tiles is blank. Shrinking alternates the small and big swimming frames (`$02`, `$00` × 5). | [D] `HandleChangeSize` l. 14693-14726, `ChangeSizeOffsetAdder` l. 14689-14691, `PlayerGraphicsTable` l. 14429 |
| Damage | Big Mario touched by an enemy (not a stomp) becomes small and `InjuryTimer` = 8. It is an interval timer (`$079E`), so it counts every 21 frames, and not during the freeze. While it runs a touch hurts nothing, but a stomp still counts (it is checked first). Small Mario dies. | [D] `ChkForPlayerInjury` l. 11376-11391, `InjurePlayer`/`ForceInjury` l. 11401-11415, `InjuryTimer` l. 99 |
| Blinking | While `InjuryTimer` runs, Mario isn't drawn on odd frames. | [D] `PlayerGfxHandler` l. 14435-14440 |

**Replica choices**:
- **Timing phase:** the rise steps and the injury timer depend on the original's free-running frame and interval clocks. As with `STOMPED_GOOMBA_TICKS`, the replica always takes the longest: the mushroom's first rise comes 4 ticks after release (the release tick counts as its first), and invulnerability lasts 8 × 21 = 168 ticks after the freeze, 223 ticks from the hit.
- **The 17th step:** the original's last rise puts the mushroom 1 px above the block, and landing snaps it back. The replica rises 16 px and sets off at the same moment.
- **Shrinking:** the original runs the player routine with movement off from `$F0` to `$C8`. The replica freezes Mario for all 55 ticks, which looks the same.
- **The freeze stops everything**, the level timer and bouncing blocks included. The ticks still count, and so does the stall rule.
- **Big Mario and a mushroom:** in the original he would become fiery. Until the fire flower (#20), the power-up block gives big Mario a mushroom too, and collecting it scores 1000 points and changes nothing else.
- **Intermediate grow frame:** nothing collides while it shows, so it is only drawn, as a 12 × 21 box from sprite y + 11, midway between the small and big boxes.
- **Not reproduced:** an enemy that hurts Mario while walking away from him turns around (`ChkEnemyFaceRight`); the per-enemy collision bit, which stops one continuous touch from hurting twice; a bumped block knocking a mushroom; the brick chunks (drawing only).

## Not covered or uncertain

- **Swimming** (rows 5–6 of the jump tables), **springboards** (Y −12 if A held, −7 otherwise [S]), **vines** and **whirlpools**. None of these appear in 1-1.
- The **airborne kicked-shell slowdown** and **Goomba removal timing** come from reading [D] only.
- **Collision resolution** (wall push-out, ceiling bonk geometry). [S] points to Dan Salvato's *SMB1 Tile Collision Flowchart* for this. It probably needs its own ticket.
