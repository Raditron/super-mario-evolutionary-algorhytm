# Simulation speed for 1000 agents (prototype for #4)

> Copied from branch `prototype/simulation-speed` (#4). The throwaway code it mentions lives only on that branch.

**Throwaway prototype.** The code is in `prototype/simulation_speed/`. To run it, go to the repo root and run `py -m prototype.simulation_speed.benchmark` (it takes about 4 minutes). The "brain" in it is a **cost placeholder**: random weights that never learn. It is **not** the user's ANN or GA (see the authorship split in `CLAUDE.md`).

## Answer

**Yes, with a wide margin.** Clean OOP Python plus numpy, on 8 worker processes, plays a generation of 1000 agents in **about 8 s** when every agent crosses about three quarters of 1-1 (1514 ticks per attempt on average, brain asked every tick). Over 100 generations that is **about 13 minutes**.

Even with pessimistic assumptions the run stays under the budget:
- If every agent's attempt lasts **2400 ticks** (walking the whole level), 100 generations take **about 21 minutes**.
- At the hard ceiling, where every attempt lasts the full **400-second timer** (9600 ticks) and nobody dies, it takes **about 83 minutes**.

A single process, with no multiprocessing at all, would still fit 100 × 1000 at 2400 ticks in about 62 minutes using the batched shape.

## Machine

- **CPU:** Intel Core i5-9300HF. It has **4 physical cores and 8 logical processors**: `os.cpu_count()` = 8, but the "8-core laptop" is really 4 cores with hyper-threading.
- **Software:** Windows 11, Python 3.12.10, numpy 2.5.4.

## What was built

**Shared level.** There is one `StaticLevel` per process: the real 224 × 15 grid from #3, loaded from `level_1_1.txt`. It is read-only and shared by every agent.

**One attempt per agent.** Each agent has its own `Attempt`, which holds:
- its own `Mario`
- its own Goombas, all 16 at the #3 positions. A Goomba is activated when that agent's camera comes within screen width + 48 px of it, and inactive enemies cost nothing.
- the tick counter, best x, and the reason the attempt ended

Agents never interact.

**Physics.** The constants come from #2, at 60 ticks per second:
- walk/run momentum, friction, skid and air control
- jump velocity chosen by takeoff speed, with lower gravity while jump is held and rising
- terminal fall speed
- tile collision with axis-separated movement
- pits
- Goombas walk, turn at walls and fall; Mario stomps them (with a bounce) or dies

**Simplified or left out:** the Koopa, block bumping and breaking, mushrooms and big Mario, the hidden 1-UP (treated as empty), the 10-frame run-cap hold, and the left-screen-edge wall.

**Attempt ends** when Mario falls into a pit, is killed by a Goomba, reaches the flag (column 198), the timer runs out (9600 ticks), or **he makes no progress**: his best x does not improve for 180 ticks (3 s). The no-progress cutoff is my assumption. It is what keeps random generations short.

**Placeholder brain.**
- **Input:** 156 values, a 12 × 13 tile window around Mario (solid 1, Goomba -1, empty 0).
- **Network:** 156 inputs → 24 tanh → 4 outputs, mapped to left/right/jump/run.
- **Weights:** random, with a bias toward pressing right so that agents meet terrain and Goombas.
- **Cadence:** asked every tick, or every 4 ticks in the second set of rows.

**Two workloads:**
- **Random brains.** Honest early generations: about 201 ticks per attempt, mostly ended by the no-progress cutoff or the first Goomba.
- **Scripted pilot (long attempts).** A stand-in for late generations. The brain still runs (and its cost is paid) but its output is thrown away, and a hand-written pilot (hold right + run, jump at obstacles, pits and Goombas) presses the buttons. It reaches about column 170 in 1514 ticks, then dies to the column-174 Goomba pair. The pilot's own Python cost is included, so these rows are slightly pessimistic.

**Two shapes:**
- **A, per-agent objects.** Each agent plays its whole attempt alone, building its own observation and calling its own brain (a single-row matmul) every decision tick.
- **B, lock-step with a batched brain.** All agents in a chunk advance one tick together. Every decision tick has three steps:
  1. One numpy gather builds every observation.
  2. One stacked matmul evaluates every agent's brain, each with its own weights.
  3. Each agent's physics steps in plain OOP Python.

  The batch is compacted once half of its agents have finished.

**Parallelism.** `multiprocessing` uses the `spawn` context with a persistent pool:
- The pool is created once per run; start-up took 0.6–0.8 s.
- Each generation, the population is split into 16 chunks, 2 per worker.
- Genomes are sent from the parent each generation, as a GA would do.
- Results come back: the Controller log, the end reason, best x, and a state digest.
- BLAS threads are pinned to 1 per process.

## Results

All figures are seconds per generation of 1000 agents, and the median of 3 generations for the multi-process rows. They come from the second of two runs. The projections assume 100 generations.

**Single agent:**

| What is stepped | ticks/s |
|---|---|
| Physics only (replaying a recorded Controller log) | 134,000 (7.4 µs/tick) |
| Physics + observation + placeholder brain + pilot, every tick | 31,000–35,000 |

So for one agent, the brain and observation cost about three times what the physics costs. Most of that is numpy's per-call overhead, not arithmetic.

**Generations (decision every tick unless noted):**

| Workload / shape | s/gen | ticks/attempt | agent-ticks/s | 100 gen, measured | 100 gen at 2400 ticks | 100 gen at 9600 ticks |
|---|---|---|---|---|---|---|
| random / A per-agent, 1 process | 4.00 | 201 | 50,167 | 6.7 min | 79.7 min | 318.9 min |
| random / B lock-step, 1 process | 1.89 | 201 | 106,478 | 3.1 min | 37.6 min | 150.3 min |
| long / A per-agent, 1 process | 42.11 | 1514 | 35,950 | 70.2 min | 111.3 min | 445.1 min |
| long / B lock-step, 1 process | 23.53 | 1514 | 64,353 | 39.2 min | 62.2 min | 248.6 min |
| random / A per-agent, 8 processes | 1.43 | 201 | 138,964 | 2.4 min | 28.8 min | 115.1 min |
| random / B lock-step, 8 processes | 0.70 | 201 | 286,357 | 1.2 min | 14.0 min | 55.9 min |
| **long / A per-agent, 8 processes** | 14.67 | 1514 | 103,447 | 24.4 min | 38.7 min | 154.7 min |
| **long / B lock-step, 8 processes** | **7.84** | 1514 | 192,954 | **13.1 min** | **20.7 min** | **82.9 min** |
| long / B lock-step, 4 processes | 9.20 | 1514 | 170,031 | 15.3 min | 23.5 min | 94.1 min |
| random / A per-agent, 8 proc, decide every 4 ticks | 0.60 | 201 | 325,329 | 1.0 min | 12.3 min | 49.2 min |
| random / B lock-step, 8 proc, decide every 4 ticks | 0.42 | 201 | 453,046 | 0.7 min | 8.8 min | 35.3 min |
| long / A per-agent, 8 proc, decide every 4 ticks | 7.93 | 1514 | 192,691 | 13.2 min | 20.8 min | 83.0 min |
| long / B lock-step, 8 proc, decide every 4 ticks | 4.96 | 1514 | 305,331 | 8.3 min | 13.1 min | 52.4 min |

Columns: "100 gen, measured" is 100 × the measured s/gen. "100 gen at N ticks" is 1000 × N ticks / (agent-ticks/s) × 100.

**Readings:**
- **Shape B wins.** It is about 1.8–2× faster than A at every setting, because one stacked matmul replaces 1000 small numpy calls per tick.
- **8 processes give about 3× over 1 process** on long attempts, not 8×, because there are only 4 physical cores and clocks drop under full load. Hyper-threading adds about 17% (4 workers 9.2 s vs 8 workers 7.8 s).
- **Deciding every 4 ticks** saves another 35–45%. It is not needed to meet the budget.
- **Noise:** the laptop's numbers are noisy. Between the two runs, the single-process rows moved by up to about 40% (turbo and thermals); the 8-process rows moved by less than 10%. The first run's headline was 7.97 s/gen.

## Recommended simulation shape

1. **Shared static level, per-agent dynamic state.** Use one immutable level object per process, and keep the tile solidity in a structure that is fast to read from Python (rows of `bytearray`). An agent owns only its Mario, its own enemies (created lazily when its camera nears them, then forgotten), and its counters.
2. **Fixed timestep, with one tick = one NES frame (60 ticks/s).** The simulation never reads the wall clock. Headless mode runs ticks as fast as possible; a watched or replayed view just draws the current tick.
3. **Integer fixed-point positions** in **1/4096 px** sub-pixels. Every #2 constant (1/16 px/f speeds, 1/4096 px/f² acceleration, 1/256 px/f² gravity) is an exact integer in this unit, so there is no rounding at all. Tile lookup is a bit shift (`subpixels >> 16`).
4. **Lock-step stepping inside each worker, with a batched brain.**
   1. Gather all active agents' observations at once.
   2. Ask all brains at once.
   3. Step each agent's physics with plain OOP objects.

   The seam is "Controller states for a batch of agents". If the user's network only does one agent at a time, shape A still fits the budget (about 39 minutes at 2400 ticks on 8 processes), so batching is an optimisation, not a requirement.
5. **A persistent `multiprocessing` pool for the whole run**, using the spawn context. Set the worker count from config (default 8), use about 2 chunks per worker, and pin BLAS to 1 thread. Each generation, the parent sends genomes and gets back small per-agent results (Controller log, game events / fitness inputs, end reason).

## Determinism findings

**Verdict: the simulation is deterministic, and a replay rebuilt from recorded Controller inputs is bit-identical.**

**Why.** The game state is integers and booleans only. There is no RNG, no wall clock and no floats in the physics, and enemies are spawned in a fixed order by position. This is why I chose integer fixed-point: Python floats would most likely also be repeatable on one machine, but integers make it a guarantee across processes, machines and refactors of evaluation order.

**Checks.** Each check compares the final-state SHA-256 digest of 1000 attempts:
- Replaying from Controller logs in the same process, for both shapes: **0 mismatches**.
- Attempts simulated in **worker processes**, replayed in the **parent**, for both shapes and both workloads (4000 attempts): **0 mismatches**.
- The same genomes run twice on the pool, run on 1 process vs 8 processes, and run with the per-agent brain vs the batched brain: **0 agents differed** in any of these.

**The brain is the one float component.** The 0 differences between the per-agent and batched brains are luck of the threshold, not a guarantee: a different BLAS, numpy version, matrix shape or summation order can change a float in its last bit, and that can flip a button whose output is right at the threshold. So:
- **Replays must be rebuilt from the recorded Controller log**, not by re-running the genome.
- Record both the genome and the log; use the log for replay.

**Log size.**
- One byte per tick (4 button bits).
- A 1514-tick attempt is 1.5 KB raw and about 80 bytes after zlib.
- A random-brain attempt is about 16 bytes compressed.
- A full generation of long attempts is about 1.5 MB raw and about 80 KB compressed, so recording every generation is cheap.

## Caveats

**Fidelity.** The full replica adds the Koopa, block bumps, mushrooms, the flag sequence and game-event bookkeeping. Physics alone is about 7.4 µs of the roughly 15 µs one agent-tick costs in shape B (single process). Even if the full game **doubles** the physics cost, the 2400-tick projection on 8 processes moves from about 21 to about 30 minutes, which is still about 4× under budget.

**Network size.** In shape A, a larger network barely matters, because numpy call overhead dominates. In shape B the matmul cost grows with the layer sizes. 156 → 24 → 4 was timed; a hidden layer several times wider would still be cheap next to physics, but it was not measured.

**Attempt length is the main lever.**
- It depends on the no-progress cutoff and the timer, which belong to the fitness and training design.
- With no cutoff, everyone would idle until the timer runs out; that worst case is 83 minutes, still under budget, but with little room left.

**Workload realism.** The long-attempt workload is one scripted path. Every agent follows it, so chunks are perfectly balanced. Real populations have uneven attempt lengths; the 2-chunks-per-worker split is there to absorb that, but it was not stress-tested.

**Laptop conditions.** The numbers were measured on this one laptop; power plan and thermals were not controlled. Expect about ±10% on the multi-process numbers and more on single-process ones.

**Prototype quality.** No tests, and no error handling. The placeholder brain and the scripted pilot are timing tools only.
