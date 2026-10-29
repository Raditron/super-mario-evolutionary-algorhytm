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
| Inside a solid tile | Growing, or standing up from a crouch, can put big Mario's taller body inside a tile; nothing checks for it then. Each frame, after he moves, `PlayerBGCollision` runs his probes: rising, a head probe at least 4 px into a solid tile (low nybble ≥ 4) hits it, as any head hit: a hard or used block sets his Y speed to 1 (`NYSpd`), a brick or ? block is bumped or broken (`PlayerHeadCollision`). Then the side probes, left pair first: one in a solid tile pushes him 1 px a frame to the other side and sets his X speed byte to 0 (`ImpedePlayerMove`), unless he is moving away (left side: X speed ≥ 1; right side: X speed < 0). Once the left side has found a tile, the right side is not checked that frame. Walls stop him the same way in the original. | [D] `PlayerCtrlRoutine` l. 5590-5610, `PlayerBGCollision` l. 11902-11927, `ChkCollSize`/`HeadChk` l. 11929-11966, `SolidOrClimb`/`NYSpd` l. 11967-11973, `DoPlayerSideCheck`/`SideCheckLoop` l. 12027-12061, `CheckSideMTiles`/`StopPlayerMove` l. 12063-12117, `ImpedePlayerMove` l. 12318-12351 |
| Crouching | Each frame, big Mario on the ground has `CrouchingFlag` set from the down button. In the air the flag keeps its value; small Mario's is always 0. | [D] `PlayerMovementSubs` l. 5874-5882 |
| What big Mario's head does | The block object gets the breakable state `$12` when big. A block holding something (`BrickQBlockMetatiles`: ? blocks and the bricks with coins, a Starman, a vine or a 1-UP) is set back to the unbreakable `$11` and bumped as for small Mario. A plain brick is broken. Crouching changes only the block object's y. | [D] `PlayerHeadCollision`/`DBlockSte` l. 7219-7277, `BrickQBlockMetatiles` l. 7361-7366, `BlockBumpedChk` l. 7368-7374 |
| Breaking a brick | `BrickShatter`: Mario's Y speed byte set to −2 (`$FE`), so he keeps rising; 50 points (`DigitModifier+5` = 5). The bounce lockout `BlockBounceTimer` = `$10` is set as for a bump. The block buffer gets the blank metatile `$00` later in the same frame, after the enemies have run. | [D] `BrickShatter` l. 7379-7391, `PlayerHeadCollision` l. 7263-7264, `BlockObjMT_Updater` l. 7502-7523, `GameEngine` l. 5310-5323 |
| Enemy on a breaking brick | During that frame the brick's tile is the blank-but-solid `$23`, so an enemy standing on it is defeated as on a bouncing block. | [D] `PlayerHeadCollision` l. 7261-7262, `HandleEToBGCollision` l. 12436-12453, `GameEngine` l. 5310-5323 |
| What a power-up block releases | `MushFlowerBlock` (type 0) and `ExtraLifeMushBlock` (type 3). Type 0 becomes the fire flower when `PlayerStatus` is not small. | [D] `BumpBlock` jump table l. 7326-7334, `MushFlowerBlock` l. 7338, `ExtraLifeMushBlock` l. 7346-7349, `SetupPowerUp` l. 7144-7149 |
| One power-up at a time | It always takes enemy slot 5, so a new one replaces the old. | [D] `SetupPowerUp` l. 7125-7128 |
| Power-up start | x = the block's x; sprite y = the block's y − 8, so its 16 × 16 box (enemy probes) starts exactly over the block. | [D] `SetupPowerUp` l. 7129-7137 |
| Rising out of the block | Every 4th frame (`FrameCounter & 3` = 0) it rises 1 px and its state goes up by 1, from 1. On the 17th step (state was `$11`) it gets X speed `$10` (1 px/f) to the right instead, and moves from the next frame. Mario can touch it once the state is ≥ 6 (5 px risen). It is drawn behind the background until then. | [D] `GrowThePowerUp` l. 7181-7199 |
| Mushroom movement | Both mushrooms move as an enemy does (`MoveNormalEnemy`, `EnemyToBGCollisionDet`): turn at walls, fall with enemy gravity. Nothing moves while `TimerControl` is set. | [D] `PowerUpObjHandler` l. 7159-7179 |
| Mushroom on a bumped block | Its background check looks under it as for a Goomba (`CInvu`: the power-up object `$2E` is let through). On the bouncing block's `$23` tile, an object `$15` or higher skips the Goomba's defeat and points and goes straight to `SetStun`: it is lifted 2 px, gets Y speed `$FD` (−3 px/f) and walks at 1 px/f (`EnemyBGCXSpdData` `$10`/`$F0`) to the right if its x is at or right of Mario's (`PlayerEnemyDiff`), to the left otherwise. Its state keeps d7, so it still moves as a walking mushroom: with nothing under it any more, the next frame's check sets d6 (`ChkForRedKoopa`) and it falls from the frame after, with enemy gravity, until it lands and walks on. In 1-1, the (21,9) mushroom walks over the bricks at 22–24. | [D] `EnemyToBGCollisionDet`/`CInvu` l. 12401-12427, `HandleEToBGCollision` l. 12436-12446, `ChkToStunEnemies`/`SetStun` l. 12455-12493, `EnemyBGCXSpdData` l. 12398-12399, `PlayerEnemyDiff` l. 12635-12642, `ChkForRedKoopa`/`SetD6Ste` l. 12572-12586, `MoveNormalEnemy` l. 9293-9320, `PowerUpObjHandler`/`ShroomM` l. 7177-7179 |
| Power-up removal | As every enemy object: once more than 72 px past either screen edge. | [D] `OffscreenBoundsCheck` l. 11006-11050 |
| Collecting | Through `PlayerEnemyCollision`: every other frame, only while the player control routine runs (`GameEngineSubroutine` = 8). Slot 5 is checked after the enemies. A mushroom or fire flower gives 1000 points (floatey number `$06`); the 1-UP gives a life instead (`$0B`). Small Mario becomes super (routine `$09`); super becomes fiery. | [D] `PlayerEnemyCollision` l. 11293-11314, `CheckForPUpCollision` l. 11316-11320, `HandlePowerUpCollision` l. 11237-11252, `Shroom_Flower_PUp`/`UpToSuper` l. 11254-11280, `FloateyNumTileData` l. 1262-1274 |
| The freeze | `SetPRout` sets `TimerControl` = `$FF`. Each frame the NMI counts it down and runs no frame or interval timers while it isn't 0, and enemies and power-ups don't move. It also sets `Player_State`: 0 (on the ground) for a power-up, 1 (jumping) for an injury. `SaveAB` still copies the A and B buttons into `PreviousA_B_Buttons` every frame, but only the player control routine reads them from the Controller, so growing (and catching fire) they stay as they were at the touch (corrected in #20, see "Buttons during a freeze" below). | [D] `SetPRout`/`SetKRout` l. 11415-11422, `UpToFiery` l. 11277-11280, `NMI` l. 785-800, `GameEngine` l. 5357 |
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
- **Big Mario and a mushroom:** as in the original, he becomes fiery (built in #20, see below).
- **Intermediate grow frame:** nothing collides while it shows, so it is only drawn, as a 12 × 21 box from sprite y + 11, midway between the small and big boxes.
- **Inside a solid tile:** the replica's box edges stop Mario at walls, so its probes find nothing in normal play. They act only once his box is inside a solid tile, and while it is, his box's edges don't stop him sideways, so that, as in the original, the probes alone get him out. The side probes are at his box's left and right edges, at sprite y + 8 and + 24 (small or crouching: + 24).
- **Bumped mushroom:** as for a bumped enemy (#18), "away from Mario" compares its x with the left edge of Mario's hitbox, and the `$00` write that stops a second object from seeing the same bump is not copied.
- **Power state:** the original changes `PlayerStatus` at the touch and `PlayerSize` at the flip. The replica has one power state, which changes at the flip with his box, so the snapshot never says big with small Mario's box (or small with big Mario's).
- **Not reproduced:** an enemy that hurts Mario while walking away from him turns around (`ChkEnemyFaceRight`); the per-enemy collision bit, which stops one continuous touch from hurting twice; the brick chunks (drawing only).

## Added during the build (#20)

These facts were sourced from [D] while building the fire flower and fireballs. Line numbers refer to the same file.

### The fire flower and fire Mario

| Fact | Value | Source |
|---|---|---|
| Fire flower out of its block | It rises out of its block as the mushroom does (`GrowThePowerUp`). After that, `PowerUpObjHandler` runs neither movement nor a background check for power-up type 1: it stays where it is, and a bump can't reach it. | [D] `PowerUpObjHandler` l. 7159-7179 |
| Collecting it | 1000 points (floatey number `$06`), as for the mushroom. `Shroom_Flower_PUp` doesn't look at which of the two Mario touched: small, he becomes super (and grows, as for a mushroom); super, he becomes fiery; fiery, nothing changes but the points. So big Mario touching a Super Mushroom becomes fiery too. | [D] `HandlePowerUpCollision` l. 11237-11252, `Shroom_Flower_PUp` l. 11254-11265 |
| Catching fire | `PlayerStatus` = 2 (fiery) at the touch, then `UpToFiery` → `SetPRout`: routine `$0C` (`PlayerFireFlower`), `Player_State` = 0 (on the ground), `TimerControl` = `$FF`. Play resumes at `$C0` (`DonePlayerTask`): **63 frames**. His size doesn't change. | [D] `Shroom_Flower_PUp`/`UpToFiery` l. 11254-11280, `SetPRout` l. 11416-11422, `PlayerFireFlower`/`ResetPalFireFlower` l. 5779-5797, `DonePlayerTask` l. 5772-5777 |
| Fire Mario hurt | `ForceInjury` stores 0 in `PlayerStatus` whatever it was (A still holds `InjuryTimer`, which is 0), so fire Mario becomes small, exactly as big Mario does. His colours change at once (`GetPlayerColors`); his size flips later, as big Mario's does. | [D] `InjurePlayer`/`ForceInjury` l. 11401-11415 |
| During the freeze | The freeze stops the enemies and timers, but not the fireballs: `GameEngine` runs `ProcFireball_Bubble` every frame, and neither it, `FireballObjCore`, `ImposeGravity`, `MoveObjectHorizontally` nor `FireballEnemyCollision` looks at `TimerControl`. So his fireballs fly, explode and hit the (standing) enemies while he catches fire. | [D] `GameEngine` l. 5311-5312, `ProcFireball_Bubble`/`ProcFireballs` l. 6273-6309, `FireballObjCore`/`RunFB` l. 6327-6378, `FireballEnemyCollision` l. 11060-11118, `RunNormalEnemies` l. 9067-9080 |
| Buttons during a freeze | Only `PlayerCtrlRoutine` reads the A and B buttons from the Controller into `A_B_Buttons`. `GameRoutines` runs `PlayerChangeSize` (growing) or `PlayerFireFlower` (catching fire) instead, neither of which calls it, so `A_B_Buttons` keeps the touch frame's buttons, and `SaveAB` copies that into `PreviousA_B_Buttons` every frame. The shot check still runs during the freeze, but never sees a fresh B press; once play resumes, a press is fresh against the buttons held at the touch. `PlayerInjuryBlink` (shrinking) runs `PlayerCtrlRoutine` from `$F0` on, so there the buttons are read. | [D] `PlayerCtrlRoutine`/`SaveJoyp` l. 5558-5574, `GameRoutines` l. 5474-5490, `PlayerChangeSize` l. 5732-5740, `PlayerInjuryBlink` l. 5744-5751, `PlayerFireFlower` l. 5779-5785, `SaveAB` l. 5356-5357 |

**Replica choices**:
- **Power state at catching fire:** the replica's power state changes at the touch, as `PlayerStatus` does; there is no box change to wait for.
- **Fire Mario hurt:** his power state is big from the touch (his fire gone, as his colours are) and small from the flip, so the snapshot never says fiery once he is hurt, nor small with big Mario's box.
- **The freeze stops everything but the fireballs**, as in the original. Growing and catching fire, Mario keeps the buttons of the touch tick; shrinking, he reads them every tick (the original from `$F0` on, which leaves the same buttons when play resumes).

### Fireballs

| Fact | Value | Source |
|---|---|---|
| When fire Mario shoots | Only while fiery (`PlayerStatus` = 2), on a fresh B (run) press: B held this frame and not the last (`PreviousA_B_Buttons`, saved at the end of every frame). Not while crouching, climbing, or with `Player_Y_HighPos` ≠ 1 (his sprite's top above the screen, or below it). | [D] `ProcFireball_Bubble` l. 6273-6303, `SaveAB` l. 5356-5357 |
| **The limit: 2** | Two fireball objects (`FireballObjCore` runs for x = 0 and 1). A shot takes slot `FireballCounter & 1`, and only if that slot's state is 0 (an exploding fireball still holds it); each shot adds 1 to `FireballCounter`. So at most 2 are in flight, and while one slot is busy a press shoots nothing if the counter points at it. | [D] `ProcFireball_Bubble` l. 6282-6286, l. 6303, `ProcFireballs` l. 6305-6309 |
| Start | x = Mario's sprite x + 4, y = his sprite y (the top of his 16 × 32 sprite). X speed `$40` / `$C0` (**±4 px/f**) by `PlayerFacingDir`, Y speed **+4 px/f** (down). Bounding box control `$07`: **8 × 8** at sprite (0, 0). It moves on the frame it is shot (state 2 falls through into `RunFB`). | [D] `FireballObjCore` l. 6327-6354, `FireballXSpdData` l. 6324-6325, `BoundBoxCtrlData` l. 12766-12778 |
| Flight | `ImposeGravity` with downward force **`$50`** and maximum **3 px/f** (the same ≥ `$80` clamp, so the 4 px/f start lasts 2 frames), then `MoveObjectHorizontally`: vertical first. | [D] `RunFB` l. 6355-6365, `ImposeGravity` l. 7704-7735, `MoveObjectHorizontally` l. 7541-7576 |
| Order in the frame | `ProcFireball_Bubble` is the first thing `GameEngine` does: after the player routine (and the scroll), before the enemies move. | [D] `GameCoreRoutine` l. 5301-5309, `GameEngine` l. 5311-5312 |
| Tile probe and bounce | One probe, block buffer adder `$1A`: sprite (4, 8), just under its middle. Nothing there (or a non-solid metatile: coins, the hidden blocks, `ChkForNonSolids`): the bouncing flag is cleared. Something solid: if it is moving up (Y speed negative) or the bouncing flag is set, it explodes (state `$80`); otherwise it bounces: Y speed **`$FD` (−3 px/f)**, the fraction kept, bouncing flag set, and its y snapped down to a multiple of 8 (`and #$F8`), which rests its box on a tile top. Skipped while its y < `$18` (the status bar). | [D] `FireballBGCollision` l. 12726-12757, `BlockBufferChk_FBall` l. 13015-13025, `BlockBuffer_X_Adder`/`_Y_Adder` l. 13030-13040 (entry `$1A`: 4, 8), `ChkForNonSolids` l. 12712-12722 |
| **Walls** | From the rule above: flying into a wall while rising, it explodes at once; while falling it "bounces" in the wall first, and the next frame, still in the wall with the flag set, it explodes. | [D] `FireballBGCollision` l. 12726-12757 |
| Leaving the screen | Its offscreen bits, masked with `%11001100`, erase it at once: once its x is at or left of `ScreenLeft_X_Pos`, at `ScreenLeft_X_Pos` + **248** or more, or its y is **240** or more (or 8 px or more above the screen's top). This happens after the tile probe, so it also erases one that has just been set to explode. | [D] `RunFB`/`EraseFB` l. 6366-6378, `GetFireballOffscreenBits` l. 14826-14830, `GetXOffscreenBits` l. 14909-14936, `XOffscreenBitsData` l. 14902-14904, `GetYOffscreenBits` l. 14949-14976, `YOffscreenBitsData` l. 14938-14940, `DividePDiff` l. 14978-14990 |
| Explosion | From state `$80`, `DrawExplosion_Fireball` adds 1 each frame and frees the slot once (state ÷ 2) & 7 reaches 3: drawn for 6 frames, freed on the **7th**, after that frame's shot check. It doesn't move or hit anything meanwhile. | [D] `FireballObjCore` l. 6327-6331, `FireballExplosion` l. 6380-6382, `DrawExplosion_Fireball` l. 14258-14265, `KillFireBall` l. 14302-14305 |
| Hitting enemies | Every other frame (`FrameCounter` bit 0 clear, as `PlayerEnemyCollision`), and not while exploding. It loops over the enemy slots **from 4 down to 0** (slot 5, the power-up, is never checked); it skips a defeated enemy (state d5), a stomped Goomba (state ≥ 2), objects `$24`-`$2A` (platforms and the like) and an enemy off the screen (below). On a hit the fireball explodes (state `$80`) and `HandleEnemyFBallCol` runs; the loop goes on, so one fireball can defeat two enemies at once. | [D] `FireballEnemyCollision` l. 11060-11118 (`ldx #$04` l. 11074, `dex`/`bpl` l. 11112-11114, `EnemyOffscrBitsMasked` l. 11095-11096) |
| Enemy off the screen | `EnemyOffscrBitsMasked` is the enemy's offscreen bits masked by `GetEnemyBoundBox`: with `$48` if its x is right of `ScreenLeft_X_Pos`, `$44` if at or left of it. Worked through `GetXOffscreenBits` and `GetYOffscreenBits`, a bit is left set (and a fireball skips the enemy) once its **x is 8 px or more left of the screen's left edge**, its **x is 256 px or more right of it** (past the right edge), or its sprite's top is at 240 or more, or 16 px or more above the screen. A new enemy counts as off the screen until its routine first runs. The bits and the box are worked out in the enemy's routine before it moves, with that frame's screen, and a fireball uses them on the next frame. | [D] `GetEnemyBoundBox`/`GetMaskedOffScrBits`/`CMBits` l. 12797-12823, `GetEnemyOffscreenBits`/`GetOffScreenBitsSet`/`RunOffscrBitsSubs` l. 14854-14893, `XOffscreenBitsData`/`GetXOffscreenBits` l. 14902-14936, `YOffscreenBitsData`/`GetYOffscreenBits` l. 14938-14976, `DividePDiff` l. 14978-14990, `CheckpointEnemyID` l. 8055-8064, `RunNormalEnemies` l. 9067-9080 |
| Enemy slots | Each frame `GameEngine` runs slots 0 to 5 in turn; an empty slot loads the next enemy of the level's list, so a new enemy takes the lowest free slot. | [D] `GameEngine`/`ProcELoop` l. 5313-5319, `EnemiesAndLoopsCore` l. 7763-7775 |
| What a hit does | `HandleEnemyFBallCol` → `ShellOrBlockDefeat` for a Goomba, a Koopa (walking or in its shell) and every other enemy below `$15` but the Buzzy Beetle: `ChkToStunEnemies`/`SetStun` lifts it 2 px and gives it Y speed `$FD` (−3 px/f) and X speed ±1 px/f (`$10`/`$F0`) away from Mario; then state d5 is set, so it falls through everything (`MoveDefeatedEnemy`). **Points: a Goomba 100** (floatey number `$01`), a Hammer Bro 1000, every other enemy (the Koopa among them) **200** (`$02`). | [D] `HandleEnemyFBallCol`/`ChkBuzzyBeetle` l. 11123-11139, `ChkOtherEnemies`/`ShellOrBlockDefeat` l. 11164-11199, `ChkToStunEnemies`/`SetStun` l. 12455-12493, `MoveDefeatedEnemy` l. 9356-9358, `FloateyNumTileData` l. 1262-1274 |
| Fire Mario hurt | `ProcFireball_Bubble` skips `ProcFireballs` unless `PlayerStatus` is fiery, so once he is hurt his fireballs neither move nor are drawn. Nothing clears `Fireball_State`: they stay in their slots (which stay taken), and fly on from where they stopped once he is fiery again, already during the freeze of catching fire. | [D] `ProcFireball_Bubble` l. 6273-6276, `ProcFireballs` l. 6305-6309 |

**Replica choices**:
- **Tile collision:** the fireball uses the original's single probe (its box's edges don't stop it), since its bounce and its explosion at walls are defined by that probe. Against enemies it uses its 8 × 8 box and the enemy's 16 × 16 replica hitbox, as Mario does.
- **Starting fractions:** the original never sets a fireball's Y speed fraction or y fraction, so they are left over from the slot's last fireball. The replica starts both at 0.
- **Enemy order:** the replica's enemies aren't kept in slots (it has no 5-enemy limit, and a new enemy goes last rather than into the lowest free slot), so a fireball checks them newest first. That is the original's 4-to-0 order as long as no slot has been freed and taken again. The order only changes the order of the game events: each enemy hit scores its own points whatever the order.
- **Enemy off the screen:** the replica works it out from the enemy's position and the screen as they are, as its Mario-enemy check does, rather than from before the enemy's last move. Only the horizontal bounds are checked: a fireball is gone before it can touch an enemy whose sprite's top is at 240 (its box starts 8 px lower), and no enemy gets above the screen in 1-1.
- **Explosion drawing:** the snapshot shows the fireball as exploding from the tick it explodes; the original draws it as a fireball once more on that frame.
- **Not reproduced:** the fireball's removal above the screen's top and its status-bar skip (a fireball rises at most about 16 px after a bounce, so neither happens in 1-1); climbing (no vine in 1-1); the shooting animation (drawing only).

## Added during the build (#32)

These facts were sourced from [D] while building the Sprite view, for the sizes its sprites are drawn at. Line numbers refer to the same file.

| Fact | Value | Source |
|---|---|---|
| Mario's sprites | The player object is 16 × 32 px, 4 rows of two 8 × 8 tiles. Every big-Mario frame fills all of it but crouching, whose top row is blank (16 × 24). Every small-Mario frame leaves the top 2 rows blank (`$fc`): small Mario is **16 × 16**, the object's lower half. The intermediate grow frame leaves the top row blank. | [D] `PlayerGraphicsTable` l. 14399-14429 |
| Enemy sprites | An enemy object is 16 × 24 px, 3 rows of two tiles. The Goomba leaves its top row blank: **16 × 16**, as its box. The defeated (squashed) Goomba leaves its top 2 rows blank: **16 × 8**, standing on the same feet. | [D] `EnemyGraphicsTable` l. 13551-13575 (`;goomba`, `;defeated goomba`) |
| Item sprites | Every power-up (Super Mushroom, fire flower, Starman, 1-UP Mushroom) is drawn as two rows of two 8 × 8 tiles (`PowerUpGfxTable`: top left, right, bottom left, right): **16 × 16**, from 8 px below the power-up object's position. | [D] `PowerUpGfxTable` l. 13474-13479, `DrawPowerUp`/`PUpDrawLoop` l. 13484-13511 |
| Fireball explosion | Four 8 × 8 sprites, from 4 px up and left of the fireball's position to 12 px down and right: **16 × 16, centred on the 8 × 8 fireball**. A flying fireball is one 8 × 8 sprite at its position. | [D] `DrawFireball` l. 14229-14234, `DrawExplosion_Fireball`/`DrawExplosion_Fireworks` l. 14258-14300 |
| The flag | Three 8 × 8 sprites: two side by side at the flag's position (triangle, skull), the third 8 px below the right one (triangle). Its place is **16 × 16 from the flag's position**, the same square as its box in the game. | [D] `FlagpoleGfxHandler` l. 13259-13286 |

**Replica choices**:
- **One picture per sprite:** the Sprite view draws each thing with one picture (small, big or fire Mario; a Goomba; a squashed Goomba). Crouching, the grow frames and walking frames are drawing only, and wait for the texture pass (spec section 12). Facing came with #56 (see below).

## Added during the build (#22)

These facts were sourced from [D] while building the green Koopa and its shell. Line numbers refer to the same file. The walking, kicked and revived speeds, the airborne slowdown and the revival delay are in section 5.

| Fact | Value | Source |
|---|---|---|
| Stomping a Koopa | `EnemyStomped` sends a Koopa (`$00`, below `$09`) to `HandleStompedShellE`: state `$04` (a still shell), the stomp chain's points as for a Goomba, `EnemyIntervalTimer` = `$10`, Mario's Y speed −4. Its X speed is left as it was, but state `$04` makes `MoveNormalEnemy` run only `ReviveStunned`: **a still shell doesn't move at all, not even to fall**. | [D] `EnemyStomped`/`ChkForDemoteKoopa` l. 11439-11483, `HandleStompedShellE` l. 11496-11513, `MoveNormalEnemy` l. 9293-9310 |
| Touching a still shell | In `HandlePECollisions`, an enemy whose state is `$02` or more without d7 (a shell, still or flipped and hopping) is **kicked by any touch, from above too**, with no bounce: d7 is set (a moving shell), X speed `$30` / `$D0` (±3 px/f) **away from Mario** (`EnemyFacePlayer`: rightwards if its x is at or right of his). It scores floatey number `StompChainCounter + 3` (400 after a landing), the chain not climbing, unless its `EnemyIntervalTimer` is below 3: then `KickedShellPtsData` `$0A`, `$06`, `$04` (8000, 1000, 500) for 0, 1, 2. | [D] `KickedShellPtsData`/`HandlePECollisions` l. 11325-11374, `EnemyFacePlayer` l. 11524-11531 |
| A moving shell and Mario | With d7 set it goes through `ChkForPlayerInjury` as a walking enemy does: a stomp (`HandleStompedShellE`) **stops it**, state `$04` again, with the stomp chain's points and the revival timer set afresh to `$10`; any other touch hurts Mario. | [D] `HandlePECollisions` l. 11353-11355, `ChkForPlayerInjury` l. 11376-11391, `HandleStompedShellE` l. 11499-11513 |
| A touch counts once | `HandlePECollisions` leaves at once if the enemy's collision bit d0 is set, and sets it otherwise; `PlayerEnemyCollision` clears it only on a check that finds them apart. So **an enemy is acted on once per touch**: a shell Mario has just kicked doesn't hurt him while they still overlap, and a touch that began while he couldn't be hurt doesn't hurt him once he can, until they have parted. | [D] `PlayerEnemyCollision` l. 11293-11314, `HandlePECollisions` l. 11328-11335 |
| A moving shell and other enemies | `EnemiesCollision` runs on frames with `FrameCounter` bit 0 **set**, the ones the Mario-enemy check skips, for pairs both on the screen. If either has d7 set (and neither d5), `ProcEnemyCollisions` defeats the other (`ShellOrBlockDefeat`: it jumps away from Mario and falls through everything) and scores floatey number `ShellChainCounter + 4` (500, 800, 1000, ...; from `$0B` a 1-UP), then adds 1 to the shell's `ShellChainCounter`, which only `EraseEnemyObject` clears: it counts for the shell's whole life. Two moving shells defeat each other. | [D] `EnemiesCollision` l. 11552-11621, `ProcEnemyCollisions`/`ShellCollisions` l. 11623-11675, `EraseEnemyObject` l. 9173-9182, `FloateyNumbersRoutine` l. 1283-1312 |
| A moving shell at a wall, and in the air | It turns at walls as a walking enemy does (`DoEnemySideCheck`, `RXSpd`). Off a ledge, `ChkForRedKoopa` sets d6 on a d7 shell, and `MoveNormalEnemy` then moves it along at its speed less 24 (`SlowM`, `XSpeedAdderData`) until it lands (`NMovShellFallBit`). A walking enemy falling (state `$01`, no d6) keeps its speed. | [D] `ChkForRedKoopa`/`DoEnemySideCheck` l. 12572-12604, `MoveNormalEnemy`/`SlowM`/`SteadM` l. 9311-9336, `LandEnemyInitState`/`NMovShellFallBit` l. 12555-12568 |
| Waking | Each frame a still shell runs `ReviveStunned`: once `EnemyIntervalTimer` is 0, its state goes back to normal (a walking Koopa) and its X speed is `RevivedXSpeed` ±8 (0.5 px/f): **right if `FrameCounter` bit 0 is clear, left if set**. It moves from the next frame. | [D] `ReviveStunned` l. 9338-9351, `RevivedXSpeed` l. 9209-9210 |
| A Koopa on a bumped block | 100 points (`GiveOEPoints`), but no defeat: `ChkToStunEnemies`/`SetStun` give it state `$02`, lift it 2 px, Y speed −3 and X speed ±1 px/f away from Mario; it falls and moves along (`FallE`, `MEHor`) until it lands, when `ChkLandedEnemyState` sets `EnemyIntervalTimer` = `$10` and state `$03` (an upside-down still shell). | [D] `HandleEToBGCollision`/`GiveOEPoints` l. 12436-12454, `SetStun` l. 12466-12493, `MoveNormalEnemy` l. 9311-9320, `ChkLandedEnemyState`/`SetForStn` l. 12512-12530 |
| The shell's revival timer | `EnemyIntervalTimer` (`$0796`) is one of the `Timers` (`$0780`-`$07A3`), which `DecTimers` runs down by 1 every 21st frame to 0, **whatever the enemy is doing**: it keeps running while the shell slides, and stops at 0. A green Koopa's init (`InitNormalEnemy`) never sets it and `EraseEnemyObject` clears it when a slot is freed, so **a Koopa never stomped has it at 0**; `SetStun` (a bumped block) leaves it as it is. So kicking a never-stomped Koopa flipped by a bumped block, while it hops, reads timer 0 and scores **8000** (`KickedShellPtsData` `$0A`); a shell kicked, then bumped and kicked again, scores by what is left of its timer. | [D] `Timers`/`EnemyIntervalTimer` l. 81, l. 97, `DecTimers`/`DecTimersLoop` l. 789-799, `InitNormalEnemy` l. 8072, l. 8166-8173, `EraseEnemyObject` l. 9173-9182, `SetStun` l. 12466-12493, `HandlePECollisions` l. 11369-11373, `KickedShellPtsData` l. 11325-11326, `FloateyNumTileData` l. 1273 (`"8000"`) |
| Koopa tile probes and box | The green Koopa (`$00`) is a normal enemy (`InitNormalEnemy`). Its tile probes are every enemy's, whatever its kind (`BlockBufferChk_Enemy` only offsets the object slot): foot probe `$15` at sprite (8, 24) (`ChkUnderEnemy`), side probes `$16`/`$17` at (0, 20) and (16, 20) (`DoEnemySideCheck`), as the Goomba's. So the replica gives it the Goomba's **16 × 16 box at sprite offset (0, 8)**, and its shell keeps it (nothing re-probes or resizes it). Its own bounding box for touching Mario, `TallBBox`'s control `$03` = sprite (2, 9) to (14, 21), is not used, as the Goomba's isn't. | [D] `InitNormalEnemy`/`TallBBox` l. 8072, l. 8166-8173, l. 8223-8224, `ChkUnderEnemy` l. 12707-12710, `DoEnemySideCheck` l. 12592-12610, `BlockBufferChk_Enemy` l. 12998-13005, `BlockBuffer_X_Adder`/`_Y_Adder` l. 13030-13041, `BoundBoxCtrlData` l. 12770 |
| A fireball and a Koopa | Walking or in its shell, it is defeated as any enemy below `$15` (`ShellOrBlockDefeat`): 200 points (floatey number `$02`). | [D] `ChkOtherEnemies`/`ShellOrBlockDefeat` l. 11164-11199 |
| Koopa sprites | The Koopa Troopa fills the whole 16 × 24 enemy object (only its top-left tile is blank). Its shell, upright or upside down, leaves the top row blank: **16 × 16**, as its box. | [D] `EnemyGraphicsTable` l. 13554-13555 (`;koopa troopa`), l. 13567-13570 (`;koopa shell`) |

**Replica choices**:
- **Timing phase:** as with `STOMPED_GOOMBA_TICKS`, a shell wakes after the longest the interval clock allows, 16 × 21 = **336 ticks** after the stomp (or after a bumped shell lands). The timer then runs down a tick at a time in every stage, as `DecTimers` runs it. The shell's `EnemyIntervalTimer`, for the kick's points, is its ticks left divided by 21, rounded up. The replica's tick number stands in for `FrameCounter`, so the wake-up direction follows its parity (a stomp falls on an even tick, so a stomped shell left alone wakes walking right).
- **A bumped moving shell** is flipped into a hopping shell like a walking Koopa; the original keeps d7 on it (`SetStun` keeps the high nybble), a case 1-1's single Koopa practically never meets.
- **Not reproduced:** two moving shells meeting (1-1 has one Koopa), and the 1-UP beyond the score table (as for the stomp chain, a step beyond it scores nothing). Walking enemies turning each other round (`ProcEnemyCollisions`, `MoveEOfs`) is not built for any enemy, a still shell included.

## Added during the build (#21)

These facts were sourced from [D] while building the Starman. Line numbers refer to the same file. Its speeds and gravity are in section 5.

### The Starman

| Fact | Value | Source |
|---|---|---|
| Releasing it | The Starman brick's block number runs `StarBlock`: power-up type 2, set up by `SetupPowerUp` as every power-up is (slot 5, from the block's position), so it rises out of its block as the mushroom does. | [D] `BumpBlock` jump table l. 7326-7334, `StarBlock` l. 7342-7344, `SetupPowerUp` l. 7125-7155, `GrowThePowerUp` l. 7181-7199 |
| Setting off | On the 17th rise step `GrowThePowerUp` gives it X speed `$10` (**1 px/f**) and moving direction right, as for a mushroom; its Y speed is 0. It moves from the next frame. | [D] `GrowThePowerUp` l. 7181-7199 |
| Moving | Each frame without a freeze, `PowerUpObjHandler` runs only `MoveJumpingEnemy` then `EnemyJump` for type 2: `MoveJ_EnemyVertically` (`ImposeGravity` with downward force **`$1C`** and maximum **3 px/f**, the same ≥ `$80` clamp), then `MoveEnemyHorizontally`. No `EnemyToBGCollisionDet`: a bumped block under it does nothing to it. | [D] `PowerUpObjHandler` l. 7159-7179, `MoveJumpingEnemy` l. 9371-9373, `MoveJ_EnemyVertically`/`SetHiMax` l. 7642-7650, `ImposeGravity` l. 7704-7735 |
| Landing and bouncing | `EnemyJump`, after it has moved: only when its Y speed byte + 2 is 3 or more, unsigned (the byte is **1 or more, or −3 or less**: not while it rises slowly, hangs at the top of a bounce or has only just started to fall), and its foot probe (`ChkUnderEnemy`, block buffer adder `$15`: **sprite (8, 24)**, just under its box) finds a tile other than the non-solid ones (`ChkForNonSolids`), it lands: `EnemyLanding` sets its Y speed and the speed's fraction (`Enemy_Y_MoveForce`) to 0 (`InitVStf`) and its sprite y to `(y & $F0) + 8`, keeping its position's sub-pixel (`Enemy_YMF_Dummy`), then Y speed **`$FD` (−3 px/f)**. It is skipped while `(y + $3E) & $FF < $44`: sprite y below 6 or from 194 on. | [D] `EnemyJump` l. 12661-12676, `SubtEnemyYPos` l. 12654-12659, `EnemyLanding` l. 12646-12652, `InitVStf` l. 8227-8230, `ChkUnderEnemy` l. 12707-12710, `ChkForNonSolids` l. 12712-12722, `BlockBuffer_X_Adder`/`_Y_Adder` l. 13030-13041 |
| Walls | Then `DoEnemySideCheck`: one probe, on the side it moves to, block buffer adder `$16` at **sprite (0, 20)** moving left, `$17` at **(16, 20)** moving right; a solid tile there turns it around (`ChkForBump_HammerBroJ` → `InvEnemyDir` → `RXSpd`: X speed negated, moving direction flipped). Skipped while its sprite y is above `$20`. | [D] `DoEnemySideCheck` l. 12592-12611, `ChkForBump_HammerBroJ`/`InvEnemyDir` l. 12613-12630, `RXSpd` l. 11696-11704 |
| No head probe | Nothing checks above it, so rising it goes up into a block over it. | [D] `EnemyJump` l. 12661-12676 |
| Collecting it | `HandlePowerUpCollision`: **1000 points** (floatey number `$06`), as for every power-up but the 1-UP, and for type 2 `StarInvincibleTimer` = **`$23`**. Mario's power state doesn't change. | [D] `HandlePowerUpCollision` l. 11237-11252, `FloateyNumTileData` l. 1262-1274 |
| How long it lasts | `StarInvincibleTimer` (`$079F`) is one of the interval timers (`$0795`-`$07A3`), which `DecTimers` counts down once every 21 frames, and not while `TimerControl` is set (a freeze). **`$23` = 35 interval ticks: 715-735 frames.** It is cleared only when a new level's timer is set (`FetchNewGameTimerFlag`), not on entering an area such as the bonus room. | [D] `Timers`/`StarInvincibleTimer` l. 81-100, `DecTimers` l. 785-799, l. 2863-2874 |
| Touching an enemy | `PlayerEnemyCollision` (every other frame, skipping an enemy with d5 set, a defeated one) jumps to `CheckForPUpCollision`; for an enemy, `EColl`: while `StarInvincibleTimer` isn't 0, it goes straight to **`ShellOrBlockDefeat`**, before `HandlePECollisions` and its collision bit, so any touch, from any side and on any enemy, shells and moving shells too, defeats it; Mario is never hurt and never stomps. | [D] `PlayerEnemyCollision` l. 11293-11314, `CheckForPUpCollision`/`EColl` l. 11316-11323 |
| What the defeat does | `ShellOrBlockDefeat` → `ChkToStunEnemies`/`SetStun`: lifted 2 px, Y speed −3 px/f (`$FD`), X speed ±1 px/f away from Mario, then state d5 (it falls through everything). **A Goomba scores 100** (floatey number `$01`), **every other enemy (the Koopa) 200** (`$02`), as for a fireball. | [D] `ShellOrBlockDefeat`/`GoombaPoints`/`EnemySmackScore` l. 11172-11199, `ChkToStunEnemies`/`SetStun` l. 12455-12493 |
| Pits | `PlayerHole` doesn't look at the timer: a pit still kills an invincible Mario. | [D] `PlayerHole` l. 5624-5627 |
| His look | While the timer runs, `GameEngine` cycles his palette (`CyclePlayerPalette`) every other frame, every 8th once the timer is below 8, and resets it (`ResetPalStar`) once it is 0. | [D] `GameEngine` l. 5338-5355, `CyclePlayerPalette`/`ResetPalStar` l. 5787-5803 |

**Replica choices**:
- **Timing phase:** as with `INJURY_INVULNERABLE_TICKS`, the invincibility always lasts the longest the interval clock allows: 35 × 21 = **735 ticks** from the tick he collects it. It doesn't count down during a freeze, as `DecTimers` doesn't.
- **Probes, not a box:** the Starman's bounce, its walls and its passing up into blocks are all defined by its probes, so it uses the original's probes (as the fireball does), not the box collision of the walking enemies. Its 16 × 16 box (an item's) is still what Mario touches.
- **The 17th step:** as for the mushroom, it rises 16 px and sets off with its feet on the block's top; the original's last rise puts it 1 px higher. Its fall is then the same: it sinks into the block (about 5 px) until its speed byte reaches 1, when the foot probe lands it back on top.
- **Its look:** both views draw an invincible Mario in one colour, `INVINCIBLE_MARIO_COLOUR` (the Sprite view's `mario_small_invincible` and `mario_big_invincible` sprites fall back to it), whatever his power state, as the star palette replaces fire Mario's. The palette cycling is left to the texture pass.
- **Not reproduced:** the landing skip near the top and bottom of the screen (`SubtEnemyYPos`) and the side check's skip above sprite y `$20`: in 1-1 the Starman never comes within 6 px of the screen's top, lands on the ground before its sprite y reaches 194, and never rises above sprite y `$20`. A squashed Goomba (state `$04`, not d5) touched by an invincible Mario: the original would defeat it again (100 more points); the replica counts it as defeated already and lets it be, as its fireballs and shells do. It can only happen when Mario stomps a Goomba and collects the Starman within the 42 ticks it lies squashed.

## Added during the build (#56)

These facts were sourced from [D] while drawing Mario and the enemies facing the way they face. Line numbers refer to the same file.

| Fact | Value | Source |
|---|---|---|
| The flip | Every two-tile row of a sprite is drawn by `DrawSpriteObject`, whose flip control `$03` is a direction (1 right, 2 left): with d1 set (left) it swaps the row's two tiles and sets the OAM horizontal-flip bit on both. The graphics face right; a thing facing left is drawn mirrored, in the same place. | [D] `DrawSpriteObject`/`NoHFlip`/`SetHFAt` l. 15000-15017 |
| Mario's facing | `RenderPlayerSub` hands `PlayerFacingDir` to it as the flip control. | [D] `RenderPlayerSub` l. 14562-14575 |
| An enemy's facing | `EnemyGfxHandler` hands `Enemy_MovingDir`, the way the enemy moves, to it as the flip control: an enemy faces the way it walks. | [D] `EnemyGfxHandler` l. 13614-13626 |
| The Goomba | Its flip control is inverted on 8 frames of every 16 (`FrameCounter` d3 clear), unless it is defeated or time is stopped: its walk is its own picture mirrored back and forth, whichever way it moves. | [D] `CheckForGoomba`/`GmbaAnim` l. 13688-13705 |
| Shells | For an enemy in state 2 or more (a Koopa's shell, still, moving or flipped), `MirrorEnemyGfx` rewrites the right column as the left one mirrored: the shell is symmetric, so which way it moves doesn't show. | [D] `CheckForESymmetry`/`MirrorEnemyGfx`/`EggExc` l. 13932-13981 |

**Replica choices**:
- **Facing by mirroring:** `MarioSnapshot.faces_right` is `Mario.facing_direction`, and `EnemySnapshot.faces_right` is the enemy's walking direction (`Enemy.walks_right`, the sign of its speed). The Sprite view draws every sprite facing right and mirrors it, in the same place, for a thing facing left; a ghost faces as his Mario does (`AgentSnapshot.faces_right`). A shell is never mirrored, since its picture is drawn symmetric as the original's is.
- **The Goomba faces the way it walks:** its mirrored walk (above) is an animation, left to the walking frames (#57).

## Added during the build (#57)

These facts were sourced from [D] while designing the knight's and the enemies' animation frames. Line numbers refer to the same file.

| Fact | Value | Source |
|---|---|---|
| The player's frames | `PlayerGraphicsTable` holds, for each size, three walking frames, a skid, a jump, three swimming and two climbing frames. Big Mario also has a crouch, 16 × 24 with its top row blank, and a fireball-throwing frame. The standing frames come after both sizes' rows. `PlayerGfxTblOffsets` picks a row by action, plus 8 for small Mario (`GetGfxOffsetAdder`). | [D] `PlayerGfxTblOffsets` l. 14393-14395, `PlayerGraphicsTable` l. 14399-14430, `GetGfxOffsetAdder` l. 14680-14687 |
| Which frame shows | `ProcessPlayerAction` runs every frame from `PlayerGfxHandler`, after everything has moved. **Jumping** (`Player_State` 1): the crouch frame if `CrouchingFlag` is set, otherwise the jump frame. **On the ground**: the crouch frame if crouching; standing if `Player_X_Speed` and `Left_Right_Buttons` are both 0; the skid frame if `Player_XSpeedAbsolute` ≥ 9 while his moving and facing directions differ; otherwise the walk. **Falling** (`Player_State` 2, walked off a ledge): the walking frame he had, not stepped on, even if crouching. The standing, skid, jump and crouch frames set the walk back to its first frame (`PlayerAnimCtrl` = 0). | [D] `ProcessPlayerAction`/`ProcOnGroundActs`/`NonAnimatedActs`/`ActionFalling`/`ActionWalkRun` l. 14585-14632, `GetCurrentAnimOffset` l. 14651-14653 |
| The walk cycle | `PlayerAnimCtrl` counts 0, 1, 2, 0 … (the upper extent is 3, despite `FourFrameExtent`'s name): walking frames 1 to 3. The frame drawn is the counter's value before it steps. When `PlayerAnimTimer` is 0, it is reset to `PlayerAnimTimerSet` and the counter steps, so each walking frame shows for `PlayerAnimTimerSet` frames. | [D] `FourFrameExtent`/`AnimationControl`/`SetAnimC` l. 14655-14678 |
| The animation timer | `PlayerAnimTimer` ($0781) is one of the frame timers. `DecTimers` takes 1 off it every frame that it isn't 0, except while `TimerControl` is set (while Mario grows or shrinks, for one). | [D] `Timers` l. 81-83, `DecTimers` l. 785-800 |
| Walk speed follows running speed | `GetPlayerAnimSpeed` runs at the start of each frame on the ground (`OnGroundStateSub`), from the last frame's `Player_XSpeedAbsolute`: at ≥ 28 ($1c), 2 frames per walking frame; at ≥ 14 ($0e), 4; below that, 7 (`PlayerAnimTmrData`). In the air the setting keeps its last value. A step cycle of three walking frames therefore takes 6 frames at the run's top speed (40), 12 at the walk's (24), and 21 below 14. | [D] `PlayerAnimTmrData`/`GetPlayerAnimSpeed`/`SetAnimSpd` l. 6192-6223, `OnGroundStateSub` l. 5903-5904 |
| A size change | `InitChangeSize` sets `PlayerAnimCtrl` to 0 as the change starts. `HandleChangeSize` then uses it as its own counter and leaves it at 0, so the walk starts again from its first frame. | [D] `InitChangeSize` l. 5753-5761, `HandleChangeSize` l. 14693-14703 |
| Not in the frame choice | Fire Mario's throwing frame replaces the frame for a few frames after a shot, and shortens the animation timer (`PlayerAnimTimer` = `PlayerAnimTimerSet` − 1). While `InjuryTimer` runs, `PlayerGfxHandler` leaves at once on every other frame (the blink), so the walk doesn't step on those frames. On the flagpole Mario is climbing (`Player_State` 3) and shows the climbing frames. | [D] `PlayerGfxProcessing` l. 14486-14509, `ProcFireball_Bubble` l. 6299-6302, `PlayerGfxHandler` l. 14435-14440, `PutPlayerOnVine` l. 12206-12208 |
| The enemies' walk | `CheckForSecondFrame`: on frames with `FrameCounter` d3 clear (8 frames of every 16; the mask `EnemyAnimTimingBMask` is $08), a walking enemy's graphics offset moves 6 bytes on, to its second frame (the Koopa's frames 1 and 2). This doesn't happen if its state has d7 or d5 set or `TimerControl` is set. The Goomba never gets here: it is mirrored on the same frames instead (`GmbaAnim`, #56). | [D] `EnemyAnimTimingBMask` l. 13608-13609, `CheckToAnimateEnemy`/`CheckForSecondFrame`/`CheckAnimationStop` l. 13831-13866, `EnemyGraphicsTable` l. 13554-13555 |

**Replica choices** (designed in part 1 of #57, built in part 2):
- **The frame is game state:** the Sprite view keeps no clock.
  - A `MarioAnimation` (in `mario/simulation/`, its timings named in `mario/constants/animation.py`) replays the original's frame choice. At the start of Mario's tick on the ground it sets the frame timing from `x_speed_absolute` (`GetPlayerAnimSpeed`). Once per tick, after everything has moved, it runs `ProcessPlayerAction` and `AnimationControl`, as `PlayerGfxHandler` runs after the enemies.
  - It stands still while the game does for a power-state change. The change sets the walk back to its first frame.
- **What the snapshot carries:** `MarioSnapshot.pose`, a `MarioPose`: `STANDING`, `WALKING`, `SKIDDING`, `JUMPING` or `CROUCHING`. Falling off a ledge is `WALKING`, with the frame kept. `MarioSnapshot.walk_frame` is 1, 2 or 3: the walking frame drawn this tick, numbered as the files are. A ghost has both through his `MarioSnapshot`, and watch-live's snapshot slot carries them. During a power-state change the pose is `STANDING`, so the change is drawn as it is now.
- **The enemies' walk:** `EnemySnapshot.walk_frame` is 1 or 2. It is 2 on a tick whose number has d3 clear, taken from the last tick the enemy moved, so it stops while the game stands still. A shell and a defeated enemy are drawn without it. The slime (Goomba) keeps the original's timing but has a second picture of its own instead of the mirror trick, and it faces the way it walks (#56).
- **Choosing the picture:** the name is Mario's standing picture's name plus `_walk_<n>`, `_skid`, `_jump` or `_crouch`; `STANDING` uses the standing picture itself. An enemy's walk frame 1 is its own picture, and frame 2 adds `_walk_2`. If the frame's PNG is missing, the standing picture is drawn; if that is missing too, its box is drawn in the thing's colour.
- **Frame names** (`<sprite>_<frame>`, after any state already in the name):
  - Small Mario (16 × 16): `mario_small_walk_1` to `_3`, `mario_small_skid` and `mario_small_jump`. The same frames exist for `mario_small_invincible`.
  - Big Mario (16 × 32): `mario_big_walk_1` to `_3`, `mario_big_skid`, `mario_big_jump`, and `mario_big_crouch` at 16 × 24. The same frames exist for `mario_fiery` and `mario_big_invincible`.
  - The enemies: `goomba_walk_2` and `koopa_walk_2`.
  - That makes 28 knight frames and 2 enemy frames. The fiery and invincible knights reuse the small and big rows with their own palettes.
- **Not reproduced:** the swimming and climbing frames, the throwing frame, the injury blink, the grow and shrink frames' own pictures, and the killed frame. On the flagpole the replica's Mario is falling, not climbing, so he keeps his walking frame.

## Not covered or uncertain

- **Swimming** (rows 5–6 of the jump tables), **springboards** (Y −12 if A held, −7 otherwise [S]), **vines** and **whirlpools**. None of these appear in 1-1.
- The **airborne kicked-shell slowdown** and **Goomba removal timing** come from reading [D] only (the slowdown was re-read in #22, see above).
- **Collision resolution** (wall push-out, ceiling bonk geometry). [S] points to Dan Salvato's *SMB1 Tile Collision Flowchart* for this. It probably needs its own ticket.
