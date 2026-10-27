# Spec: the game half

The AI-written half of the coursework: a 1:1 replica of Super Mario Bros. World 1-1 (audio excluded), with play, train, replay and stats commands, a Sprite view and a Debug view, and one result folder per run. The user's algorithm plugs in through one interface (section 9). Its own plan is in [learning-plan.md](learning-plan.md).

Every decision here was settled in a ticket on the [map (#1)](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/1). Each section names its ticket, and the ticket holds the reasoning. Use the vocabulary of [`GLOSSARY.md`](../../GLOSSARY.md) and follow the standards in [`CLAUDE.md`](../../CLAUDE.md). In particular, every tunable value is a named constant in `mario/constants/`, never inline.

**Research to build from** (copied onto `main`):
- [docs/research/smb-physics-constants.md](../research/smb-physics-constants.md): every movement constant, with sources (#2)
- [docs/research/world-1-1-layout.md](../research/world-1-1-layout.md): the tile grid, blocks, pipes, enemies and scroll rules (#3)
- [docs/research/simulation-speed.md](../research/simulation-speed.md): the measured simulation shape and its speed (#4)

**Facts no research covers yet.** Examples are fireball physics, damage invincibility time, the score table, the multi-coin block's timer, Koopa shell wake-up, pipe-entry timing, the flagpole sequence and the bonus room's layout. Whichever build issue needs one sources it from doppelganger's disassembly ([gist 1wErt3r/4048722](https://gist.github.com/1wErt3r/4048722)), the same primary source as #2 and #3. It then adds the value, with its source line, to the matching research page. These are lookups, not open decisions: the rule is "as in the original".

---

## 1. Scope (#5)

Everything that appears in World 1-1 is built; only audio is out:

- the 1-1 layout, momentum running and jumping
- Goombas, one green Koopa with shell kicking
- brick and ? blocks, the multi-coin brick, the hidden 1-UP block
- mushroom, fire flower and fireballs, Starman, the 1-UP mushroom
- pipes and pits, the warp pipe and bonus room
- the flagpole slide and castle walk
- the score, coins, world and timer HUD
- in play mode only: lives, the midway checkpoint and game over

**Out:** audio, other levels, running several runs at once, the written report.

## 2. Commands

| Command | Does |
|---|---|
| `py -m mario play` | A human plays with the keyboard (section 6). |
| `py -m mario train [config] [--watch]` | Trains one run. `config` defaults to `config.toml` at the repo root. `--watch` turns on watch-live (section 11); without it, training is headless. |
| `py -m mario replay <run-folder> [--generation N] [--best]` | Replays generation `N` (default: the last one recorded): all agents as ghosts, or with `--best` only its best agent. |
| `py -m mario stats <run-folder> [more run folders...]` | Writes charts and a summary (section 13). |

Python 3.12, run as `py`. Dependencies (in `requirements.txt`): pygame, numpy, matplotlib, pytest. Nothing else.

## 3. Module map and dependency rules (#8)

```
mario/
  __main__.py     py -m mario play | train | replay | stats
  constants/      one Python module per area: physics, level, scoring,
                  observation, training, view, recording
  level/          StaticLevel: tile map + block/pipe/enemy tables, read-only
  simulation/     Attempt, Mario, enemies, items, blocks, collision, scroll,
                  GameEvent, AttemptResult, ObservationBuilder (no pygame)
  controller/     Controller bitmask, ControllerSource, ControllerLogSource,
                  BrainControllerSource (no pygame)
  snapshots/      WorldSnapshot + the shared-memory channel
  training/       NeuroevolutionAlgorithm, Trainer, AgentWorkerPool, ChunkPlayer
  recording/      RunFolder, RunRecorder (training's GenerationRecorder feeds it)
  statistics/     charts and summary from run folders (only matplotlib importer)
  view/           Window, KeyboardControllerSource, SpriteRenderer, DebugRenderer,
                  HUD, followed-agent camera (only pygame importer)
  modes/          PlayMode (+ PlaySession), TrainMode, ReplayMode, StatsMode
neuroevolution/   the user's package; exposes create_algorithm(settings)
assets/sprites/   textures, added last (section 12)
tests/game/       the game's pytest suite
runs/             git-ignored run folders (section 10)
config.toml       the run settings the user edits (section 10)
```

**Dependency rules**
- `simulation` depends only on `level`, `controller` and `constants`.
- `controller` depends only on `constants`: it never imports `simulation` or `training`, which both depend on it.
- `view` reads only `WorldSnapshot`s. It is the only package that imports pygame, so workers and headless training never load it.
- `recording` knows only `AttemptResult`s, Controller logs, floats and flat arrays.
- `statistics` reads only run-folder files. It never imports the simulation.
- Only `TrainMode` (in `modes/`) imports `neuroevolution`, through the one fixed import of section 9; `training` gets the algorithm by injection and never imports it (ADR 0001). `play`, `replay` and `stats` work while the algorithm is empty or half-written.

**The game package is frozen once built.** The user's code changes; the game's doesn't. That's why the seam (section 9) hands over everything the game knows.

## 4. The simulation (#4, #8)

- **`StaticLevel`** is loaded once per process and shared read-only by every Attempt. It holds layer 1 of the tile grid (stored as a data file next to the loader, copied from the research), the block contents, the pipes and the enemy spawn table. Layer 2 (background scenery) is drawing data for the Sprite view only.
- **`Attempt`** is one life of one Mario in a freshly loaded level. It owns his Mario, his own enemies, items, changed blocks, scroll, counters and events. Agents never collide with or affect each other. Its one way in is **`step(buttons)`**: one tick, given that tick's Controller bitmask. It never imports pygame.
- **Fixed timestep.** One tick is one NES frame; the game runs at 60 ticks per second. The simulation never reads the wall clock.
- **Integer fixed point.** Positions and speeds are integers in **1/4096 px** on both axes. Every #2 constant is an exact integer in this unit (X units ×256, Y units ×16).
- **Deterministic.** The simulation has no RNG and no floats. The same Controller log always gives the same attempt, bit for bit, and replays rely on this.
- **Where buttons come from** is the only difference between modes, through one `ControllerSource` interface:
  - `KeyboardControllerSource`: play
  - `BrainControllerSource`: train. It turns a brain's (agents × 5) bools for one tick into each agent's bitmask; training's `ChunkPlayer` runs the lock-step over a chunk: Observations → `brain.decide` → step every agent.
  - `ControllerLogSource`: replay

### Physics (#2, #8)
- Mario's movement uses the constants in the physics research **unchanged**: walk/run caps, accelerations, friction, skid, air control, the three jump bands with held-jump gravity, and terminal fall.
- **All three #2 quirks are reproduced:**
  - walking off a ledge reuses the last jump's falling gravity (`$28` before any jump in an area)
  - the Mario–enemy check runs every other tick
  - speed is capped *before* gravity is added, so a fall can overshoot to ≈ 4.5 px/f for one tick
- **Tile collision:** axis-separated boxes. Move along x and push out of solid tiles, then move along y and push out again. Landing snaps feet to the tile top. Hitting a tile from below stops the rise and bumps the block. The original's point probes are not copied.
- **Entity collision:** as in the original (`ChkForPlayerInjury`), when hitboxes overlap and Mario is moving down at 1 px/f or more, it's a stomp, wherever his feet are. Otherwise Mario takes damage, or with Starman the enemy is defeated. This is checked every other tick. A "feet above the enemy's centre" clause was dropped in #17: Mario falls up to ≈ 9 px between checks, and the clause made 224 of 386 jumps onto a Goomba fatal. Enemies use the same tile collision and turn around at walls.
- **Hitbox sizes** are on the 16 px grid. An enemy's box comes from its tile probes, as Mario's does (a Goomba is 16 × 16). The original's smaller bounding boxes are recorded in the physics research but not used.

### Level (#3, #8)
- **Enemies have fixed spawn positions** in level coordinates, so every agent faces the same level. Goomba pairs sit at `16·(data column − 3)` and `16·(data column − 1.5)` px.
- **Activation is as in the original:** an enemy appears once its spawn x is within 48 px past his screen's right edge. Enemies are removed once they are well off the left of the screen (a named constant).
- **No 5-slot enemy limit.** Every enemy activates when its turn comes. In 1-1 the limit almost never bites, so it isn't modelled.
- **Scroll is per-Attempt state.** It sets Mario's invisible left wall and when his enemies activate. It only moves right and follows the original's rule (scrolling starts past 80 px, full speed past 112 px).
- **The scroll stops with the screen's left edge at column 192.** The screen then shows columns 192–207. Check this against the original during the build.
- **The bonus room** is a fixed screen. The scroll position is restored when Mario comes out at column 163.
- **The hidden 1-UP block at (64,8) is present in every attempt.** It is invisible and solid only when hit from below.

## 5. Game events and when an attempt ends (#5)

**What ends a training attempt**, whichever comes first:
- **Death**: touched by an enemy while small, or fell into a pit.
- **Reaching the flag**: the moment Mario touches the flagpole. Flag-height and remaining-time points are counted then.
- **Level timer**: 400 units of 24 ticks (9,600 ticks ≈ 160 s).
- **Stall**: no new furthest-right position *in the current area* (level or bonus room) for `STALL_LIMIT_TICKS = 180`. The record resets when Mario changes area. Only a new furthest-right position resets the count.

**Play mode** uses the original's rules: death, flag and timer, with **no stall rule**. `PlaySession` gives 3 lives, adds one for a 1-UP (and for 100 coins, as the original does), keeps score and coins across lives, and restarts at the checkpoint (page 5, column 80) once the screen's left edge has reached it. Game over starts a new game. Each life is its own Attempt in a freshly loaded level. Training never sees `PlaySession`. **The stall rule depends on the mode**, not on who presses the Controller.

**Replay** ends where the recorded attempt ended. **The flagpole slide and castle walk** run as an input-free sequence after the touch, in play and replay only.

**`AttemptResult`** is a read-only dataclass:

| Field | Type | Meaning |
|---|---|---|
| `end_reason` | `EndReason` (a `StrEnum`) | `died_to_enemy`, `fell_in_pit`, `stalled`, `timer_ran_out`, `reached_flag` |
| `furthest_x` | `int`, px | Furthest-right left edge of Mario's hitbox, **in level coordinates only**. It stays at the warp pipe's value while he's in the bonus room, then jumps when he comes out at column 163. |
| `ticks_elapsed` | `int` | Ticks from spawn to the end. |
| `final_score` | `int` | The original's score. |
| `coins_collected` | `int` | |
| `events` | `tuple[GameEvent, ...]` | Everything below, in order. |

**`GameEvent(tick, kind, detail)`** is recorded during the attempt. `kind` is a `GameEventKind` `StrEnum`. `detail` is `str | int | None`.
- `defeated_enemy`, with `detail` saying how: `stomp`, `fireball`, `kicked_shell`, `starman` or `bumped`
- `kicked_shell`, `hit_question_block`, `broke_brick`, `collected_coin`
- `collected_mushroom`, `collected_fire_flower`, `collected_starman`, `collected_one_up`
- `shot_fireball`
- `took_damage`: fire to small, or big to small
- `hit_hidden_block`, `entered_pipe`, `exited_pipe`
- `scored_points`, with the amount as `detail`, following the original's scoring rules (stomp chains, blocks, coins, power-ups, flag height, remaining time)

## 6. Controller (#6)

- Five buttons: **left, right, down, jump, run**. The bitmask uses that order, from bit 0 to bit 4 (`CONTROLLER_BUTTONS` in the constants). It is 1 byte per tick.
- **Left and right held together count as no direction**, like a real d-pad, for humans and agents alike.
- A jump starts on the press. To jump again, jump must be released for at least one tick.
- **Down** crouches when big and enters the warp pipe when Mario stands on it.
- **Keyboard** (play only; in train and replay, keys only drive the viewer):
  - arrows for left, right and down
  - `X` for jump, `Z` for run
  - `F1` toggles Sprite/Debug view
  - `Esc` quits

  These are named constants in the view constants.

## 7. Observation (#6)

What an agent perceives each tick: **160 numbers**, built by `ObservationBuilder` on the game side. `DECISION_INTERVAL_TICKS = 1`, so agents decide every tick.

**Layout of the 1-D vector** (dtype `float64`). The user's code depends on this order:
1. **156 grid cells**: a 13 × 12 window, flattened **row by row from the top** (screen row 2 down to row 13), each row **from left to right** (3 columns behind Mario, his own column, 9 ahead). The window is anchored on the tile column holding Mario's centre x.
2. **4 Mario-state numbers**, in this order:
   1. horizontal speed ÷ run cap (2.5 px/f): the whole speed that moves him (`Player_X_Speed`), negative to the left, so −1 to 1
   2. vertical speed ÷ terminal fall (4 px/f), positive when falling; the one-tick overshoot can take it to about 1.1
   3. height: his feet within the 12-row band, 0 at the band's top edge (y = 32) and 1 standing on the ground (the top of row 13, y = 208). It isn't clipped at either end: it goes below 0 when he jumps from high ground such as the staircase, and above 1 as he falls into a pit.
   4. on the ground: 0 or 1

**Cell values**
- `0` empty
- `+1` solid: ground, brick, ? block (used or not), pipe, staircase block, the flagpole's base block
- `−1` enemy: Goomba, Koopa, shell

**Rules for the grid**
- Items aren't shown. Mario's fireballs aren't shown.
- The hidden 1-UP block shows as empty until it's hit. A broken brick becomes empty.
- Cells outside the area count as solid. Invisible walls aren't shown: neither the left camera wall nor the invisible castle stopper (column 205), which shows as empty.
- An enemy marks only the cell holding its hitbox centre, and overrides a solid tile in the same cell. A defeated enemy (a squashed Goomba) isn't shown.
- A cell is solid exactly when the physics treats its tile as solid and it can be seen, so the castle stopper is left out (built in #25).
- In the bonus room, the grid shows the room's tiles.

**Constants** (`mario/constants/observation.py`): `OBSERVATION_COLUMNS_BEHIND = 3`, `OBSERVATION_COLUMNS_AHEAD = 9`, `OBSERVATION_TOP_ROW = 2`, `OBSERVATION_BOTTOM_ROW = 13`, the cell values and the scaling divisors.

## 8. Views (#8, #13, #14)

- **The window** shows the NES screen (256 × 240) scaled by `WINDOW_SCALE`. It draws the latest `WorldSnapshot` at 60 fps. **Renderers only read** and never change simulation state. Headless means no renderer exists.
- **Debug view**: coloured, filled hitboxes, one colour per kind of thing. It also shows:
  - the followed agent's Observation, as a translucent overlay of the 13 × 12 window with each cell tinted by its value, plus the 4 state numbers as text
  - recent game events and points scored
- **Sprite view**: sprites at the original's sizes on the 16 px grid, loaded by `SpriteRenderer` from `assets/sprites/`, with the background scenery (layer 2). **A missing sprite falls back to its hitbox colour**, so the Sprite view works from day one and adding textures never touches game code.
- **`F1`** toggles between the two views in every mode.
- **HUD**: score, coins, world, time, as in the original. During training views (watch-live, all-ghost replay) it adds the line `generation N · alive A / P · reached flag F`.
- **The camera follows the followed agent.** That's the Mario with the greatest current level x among those still in their attempt; one in the bonus room counts as being at column 57. When his attempt ends, the camera cuts to the new rightmost living agent. Once everyone has ended, it stays on the last one. There's no manual override. With one Mario, he is the followed agent.
- **Many agents on screen** (watch-live and all-ghost replay):
  - The followed agent is drawn solid, with his own enemies, items and changed blocks.
  - Up to `GHOST_DRAW_LIMIT = 100` other living agents are drawn as translucent ghosts: the rightmost ones, with an agent in the bonus room counting as being at column 57. In the Debug view, ghosts are plain hitbox outlines.
  - An agent disappears as soon as its attempt ends.
  - Ghost opacity is a view constant.

## 9. The seam with the user's algorithm (#7, #8, ADR 0001)

See [ADR 0001](../adr/0001-frozen-game-drives-the-generation-loop.md). **The game runs the generation loop** and calls the user's code through an abstract `NeuroevolutionAlgorithm` (an `abc.ABC` in `mario/training/`):

```python
class NeuroevolutionAlgorithm(ABC):
    def initial_genomes(self, population_size: int, rng: np.random.Generator) -> list[np.ndarray]: ...
    def build_brain(self, genomes: list[np.ndarray]) -> Brain: ...
    def fitness(self, attempt_result: AttemptResult) -> float: ...
    def next_genomes(self, genomes: list[np.ndarray], fitnesses: np.ndarray,
                     rng: np.random.Generator) -> list[np.ndarray]: ...

class Brain(Protocol):
    def decide(self, observations: np.ndarray) -> np.ndarray: ...
    # (agents × 160) float64 -> (agents × 5) bool, columns in Controller order
```

- **One fixed import, in train mode only:** `from neuroevolution import create_algorithm`. `create_algorithm(settings: dict)` receives the `[algorithm]` table of `config.toml` as a plain dict; parsing it is the user's job. Each worker process calls it once to build brains locally.
- **Genome:** a flat 1-D numpy float array. **Fitness:** one float per agent. `fitnesses` lines up with `genomes` by agent index.
- **Brain rows:** a brain is built from one chunk's genomes. Every tick until the chunk's last attempt ends, `decide` gets one row per agent of the chunk, in genome order: row i is always agent i. An agent whose attempt has ended keeps its row, which repeats its last Observation, and its answer is ignored.
- **Randomness:** the game makes one `numpy.random.default_rng([run] seed)` per run and passes it to `initial_genomes` and `next_genomes`. The simulation itself uses none.
- **The Trainer takes the algorithm by injection.** `TrainMode` does the fixed import. The game's own tests drive the Trainer with a test double in `tests/game/` that presses random buttons. That double is not a neural network or a GA: the user writes those.

**One generation:**
1. Send genomes to the worker pool.
2. Each worker runs its chunk in lock-step with `build_brain` and `ChunkPlayer` (which reads the brain's buttons through `BrainControllerSource`).
3. `AttemptResult`s and Controller logs come back.
4. `fitness` is called on each result.
5. Record the generation (section 10).
6. Call `next_genomes`.

**Worker pool (#4):**
- a persistent `multiprocessing` pool with the spawn context, created once per run
- `TRAINING_WORKER_COUNT = 8`, 2 chunks per worker
- BLAS pinned to 1 thread per worker

**Speed bar:** 100 generations × 1000 agents in under ~2 h on the user's 4-core / 8-thread laptop. #4 measured ≈ 13–21 min on a reduced game. The full scope adds per-tick work, so the training build re-measures it (section 14).

## 10. Run folder and config (#7)

```
config.toml                  at the repo root: the settings for the next run
runs/YYYY-MM-DD_HH-MM_<run-name>/
  config.toml                copy of the config the run started with
  results.csv                one row per agent per generation
  generation_times.csv       one row per generation
  generations/
    0001/
      controller_logs.npz    every agent's Controller log, compressed
      best_genome.npy        the generation's best genome only
    0002/ ...
```

- `config.toml` holds only per-run settings:
  - `[run]`: `name` (used in the folder name), `seed`, `generations`, `population_size`
  - `[algorithm]`: the user's settings, with keys they choose

  Game constants never go in it.
- **Made when the run starts** (built in #27): `runs/` is at the repo root (git-ignored), whatever folder `train` is run from, and the run folder is made only once the user's algorithm has built, in the main process and in every worker, so a `train` that says the algorithm isn't ready leaves no folder. The folder gets the config copy, byte for byte, and both CSVs with just their header rows. A run of the same name started in the same minute is refused rather than mixed in.
- **Written once per generation**, after it finishes, in this order: append `results.csv`, append `generation_times.csv`, then write `generations/NNNN/`. A stopped run leaves only complete generations, and replay and stats still work on it. Generations are numbered from `0001`.
- **Both CSVs start with a header row** naming their columns. Floats (`fitness`, `seconds`) are written as Python's shortest round-trip text, so they read back to the same bits.
- `results.csv`: `generation, agent, fitness, end_reason, furthest_x, ticks_elapsed, final_score, coins_collected`. No summaries are stored. Events during an attempt aren't stored either, because replays rebuild them.
- `generation_times.csv`: `generation, seconds` (wall clock: playing and scoring the generation, not recording it).
- `controller_logs.npz`: one `uint8` array per agent (key = agent index as plain decimal text: `"0"`, `"1"`, ...), 1 byte per tick, compressed.
- `best_genome.npy`: `np.save` of the best agent's genome. Best = highest fitness; on a tie, the lowest agent index.
- `agent` is the agent's index within its generation, the same in every file.
- A run folder is read only by replay and stats. Runs can't be resumed, and genomes don't seed new runs.

## 11. Watch-live and replays (#8, #13)

- **Watch-live is truly live.** With `--watch`, workers keep stepping their agents in lock-step, **pace themselves to 60 ticks/s**, and write a per-tick `WorldSnapshot` into shared memory.
  - For every agent, the snapshot holds position, facing, power state, area, and alive/finished.
  - For the followed agent, it adds his enemies, items, changed blocks, Observation and recent game events.
  - The window draws the latest snapshot.
  - Without `--watch`, nothing is written and training runs at full speed. The budget at real time is about 25–40 s per generation.
  - *Suggested shape:* each worker publishes full detail for its own rightmost living agent, and the window uses the overall rightmost.
- **All-ghost replay** reuses the same worker + snapshot pipeline, with `ControllerLogSource` in place of the brain.
- **Best-agent replay** and **play** are one Mario each and run in the main process.
- The rule: **many agents → workers + snapshots; one Mario → main process.**
- Replays are always rebuilt from Controller logs, **never by re-running a genome**. Float rounding in a brain could flip a button that sits on the threshold (#4).

## 12. Graphics until the end (#14)

Until the very end, everything is drawn as coloured, filled hitboxes. The textures are hand-drawn last, by an agent in MS Paint via computer use (this needs the Claude desktop app). Their sprite list, sizes and animation frames get **their own ticket once the game is built**. Only three rules apply now: the original's sizes on the 16 px grid, loaded from `assets/sprites/`, and the hitbox-colour fallback.

## 13. Statistics (#12)

`py -m mario stats <run-folder> [more...]` lives in `mario/statistics/`, the only package that imports matplotlib.

For one run folder, it writes PNGs plus `summary.txt` into `<run-folder>/statistics/`, overwriting any earlier ones:
1. Fitness per generation: best, mean and median, with a shaded 10th–90th percentile band.
2. Distance per generation: best and median `furthest_x`, with dashed lines at the warp pipe (column 57) and the flag (column 198).
3. How attempts ended: each `end_reason`'s share per generation, as a stacked area chart.
4. Where attempts end: a heatmap of `furthest_x` against generation.
5. Coins and time: best and mean `coins_collected`, and the fastest flag time in seconds among finishers.
6. Seconds per generation.

`summary.txt` holds: the first generation to reach the flag, the best fitness (with generation and agent), the fastest finish, the most coins, and the total run time.

For several folders, it writes a comparison to `runs/comparisons/YYYY-MM-DD_HH-MM/`: best and mean fitness of every run on one chart, labelled by run name, plus the first-flag generation per run and the summaries side by side.

`final_score` isn't charted. Summaries are computed from the rows every time and never stored.

## 14. Build order

The game is built as vertical slices. Each is a `ready-for-agent` issue that stays blocked (GitHub's native issue dependencies) until the slices it needs are closed. Every slice:
- keeps `py -m mario play` working
- adds pytest cases in `tests/game/`
- puts every new tunable in `mario/constants/`
- sources unresearched facts as described at the top

| Issue | Slice | Blocked by |
|---|---|---|
| [#15](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/15) | Mario runs and jumps through 1-1 in play mode (tracer bullet) | — |
| [#16](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/16) | Level timer, score, HUD, lives, checkpoint and stall rule | [#15](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/15) |
| [#17](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/17) | Goombas: activation, stomping and death by enemy | [#16](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/16) |
| [#18](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/18) | Blocks and coins | [#17](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/17) |
| [#19](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/19) | Mushroom, big Mario, brick breaking, damage and the 1-UP | [#18](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/18) |
| [#20](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/20) | Fire flower and fireballs | [#19](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/19) |
| [#21](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/21) | Starman | [#18](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/18) |
| [#22](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/22) | Koopa and kicked shells | [#17](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/17) |
| [#23](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/23) | Warp pipe and bonus room | [#18](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/18) |
| [#24](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/24) | Flagpole, castle walk and end-of-level points | [#16](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/16) |
| [#25](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/25) | Observation and its Debug-view overlay | [#17](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/17) |
| [#26](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/26) | Headless training loop and worker pool | [#16](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/16), [#25](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/25) |
| [#27](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/27) | Run folder recording | [#26](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/26) |
| [#28](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/28) | Best-agent replay | [#27](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/27) |
| [#29](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/29) | Watch-live with ghosts | [#26](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/26) |
| [#30](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/30) | All-ghost replay | [#28](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/28), [#29](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/29) |
| [#31](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/31) | Statistics | [#27](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/27) |
| [#32](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/32) | Sprite view with hitbox fallback | [#15](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/15) |

After the last slice: the texture-pass ticket (section 12), then the game is frozen.
