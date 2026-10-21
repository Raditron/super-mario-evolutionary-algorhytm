# Super Mario Bros. (NES, NTSC) movement and physics constants

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

## Not covered or uncertain

- **Swimming** (rows 5–6 of the jump tables), **springboards** (Y −12 if A held, −7 otherwise [S]), **vines** and **whirlpools**. None of these appear in 1-1.
- The **airborne kicked-shell slowdown** and **Goomba removal timing** come from reading [D] only.
- **Collision resolution** (wall push-out, ceiling bonk geometry). [S] points to Dan Salvato's *SMB1 Tile Collision Flowchart* for this. It probably needs its own ticket.
