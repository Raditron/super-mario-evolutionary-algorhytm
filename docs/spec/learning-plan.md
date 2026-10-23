# Spec: the algorithm half (learning plan)

The user's half of the coursework: an artificial neural network whose weights are evolved by a genetic algorithm (**neuroevolution**), written from scratch with numpy and no ML libraries. **The user writes all of this code.** Agents explain concepts, propose plans and review, but never write the algorithm (see [`CLAUDE.md`](../../CLAUDE.md)). Decided in [#9](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/9).

**Assumption still open:** the teacher hasn't formally confirmed that neuroevolution counts as the course's "NN/ANN" item ([#11](https://github.com/Raditron/super-mario-evolutionary-algorhytm/issues/11)). If the teacher disagrees, reopen #11 and revisit this plan.

## Where your code meets the game

The game is frozen. Your `neuroevolution/` package plugs in through one interface. The exact shapes are in [game.md section 9](game.md#9-the-seam-with-the-users-algorithm-7-8-adr-0001), and the Observation layout is in [section 7](game.md#7-observation-6). In short:

- `from neuroevolution import create_algorithm` is the one fixed import. `create_algorithm(settings)` gets your `[algorithm]` table from `config.toml` as a dict, and returns your `NeuroevolutionAlgorithm`.
- `initial_genomes(population_size, rng)` returns a list of flat 1-D float arrays.
- `build_brain(genomes)` returns a `Brain` whose `decide(observations)` maps (agents × 160) to (agents × 5) bool. The columns are left, right, down, jump, run.
- `fitness(attempt_result)` returns one float.
- `next_genomes(genomes, fitnesses, rng)` returns the next population.
- Use only the `rng` the game passes in, so a run is reproducible from its seed.

`py -m mario play` and `py -m mario replay` never import your package, so the game works while your code is empty. `py -m mario stats` draws your fitness curves from a run folder.

## How every milestone is laid out
1. **Concept**: what the thing is and why it's there, in plain words.
2. **What to build**: class and function names with their inputs and outputs, but **no bodies**. The names exist only so the pieces fit the seam.
3. **Proof check**: pytest cases you write, plus a visible check from milestone 4 onwards.
4. **Alternatives to research**: every option passed over, with one line on why. This is your reading list.
5. **Review**: when the milestone is done, an agent reviews your code against its proof check and the `CLAUDE.md` standards before the next one starts.

## Every decision at a glance
All of these are per-run settings in `[algorithm]` of `config.toml`. You choose the key names; these are suggestions.

| Decision | Choice | Setting(s) |
|---|---|---|
| Network shape | 160 → 24 → 5, one hidden layer | `HIDDEN_LAYER_SIZE = 24` |
| Activation | tanh in both layers | |
| Press rule | a button is pressed when its output is > 0 | `BUTTON_PRESS_THRESHOLD = 0.0` |
| Genome | direct encoding, `W1, b1, W2, b2` flattened in that order, float64, 3,989 genes (≈ 32 KB) | |
| Initial weights | Normal(0, 1/√fan_in) (LeCun normal); biases 0 | |
| Fitness | distance + coins + (flag bonus − time used), see milestone 5 | `COIN_REWARD = 100`, `FLAG_REWARD = 20000`, `TIME_REWARD = 100/96` |
| Selection | tournament | `TOURNAMENT_SIZE = 3` |
| Mutation | Gaussian, gene by gene | `MUTATION_RATE = 0.05`, `MUTATION_STRENGTH = 0.05` |
| Crossover | uniform | `CROSSOVER_RATE = 0.7` |
| Elitism | the top 1% are copied unchanged | `ELITE_COUNT = 10` |
| Population × generations | 1000 × 100 (the speed bar); these live in `[run]`, not `[algorithm]` | |

**Success:** at least one agent reaches the flag in a 1000 × 100 run.

---

## Milestone 0: Setup
**Concept.** The game loads your code with one fixed import, in train mode only (ADR 0001). The game works without it.

**Build.**
- The `neuroevolution/` package.
- `create_algorithm(settings: dict) -> NeuroevolutionAlgorithm`, where `settings` is the raw `[algorithm]` table.
- `AlgorithmSettings`: a small read-only class that parses and checks that dict, so the rest of your code never touches raw keys.
- A pytest folder for your tests (the game's own tests live in `tests/game/`).

**Proof check.** pytest runs and finds a test. `AlgorithmSettings` reads a sample `[algorithm]` dict and rejects a missing key.

---

## Milestone 1: A neuron and tanh
**Concept.** A neuron computes a weighted sum of its inputs plus a bias, `z = w·x + b`, then squashes it: `a = tanh(z)`.
- The weights decide what the neuron "looks for", and the bias decides how easily it switches on.
- tanh maps any number to −1…+1 and is centred on 0, which suits the Observation, whose values are already −1…+1.
- Nothing is trained by gradients here. Only evolution changes the weights, so the activation doesn't need a convenient derivative.

**Build.** A function that gives one neuron's output from its inputs, weights and bias. It's a learning step: milestone 2 replaces it with matrix maths.

**Proof check.**
- Hand-calculated cases: all-zero weights give 0, and a known 3-input case matches a value worked out on paper.
- A very large `z` gives about ±1 (saturation).

**Alternatives to research.**
- **Sigmoid** (0…1): not centred on 0, so the next layer always gets a positive push.
- **ReLU / Leaky ReLU**: the deep-learning default because they help gradient descent, which isn't used here. ReLU's output is unbounded, so one big mutated weight can blow up.
- **Step / sign function** (the original perceptron): its output is only on or off, so a small mutation either changes nothing or flips everything.
- **Softsign**: tanh-like, but cheaper to compute.

---

## Milestone 2: A layer and the forward pass
**Concept.** A layer is many neurons reading the same inputs. Their weights form a matrix, so the whole layer is one matrix product: `hidden = tanh(x @ W1 + b1)`, then `outputs = tanh(hidden @ W2 + b2)`. Then **presses = outputs > `BUTTON_PRESS_THRESHOLD`**.

The hidden layer is what lets the network combine facts, such as "pit ahead **and** on the ground → jump". Without it, each button is just a weighted sum.

- **Monotonic outputs.** tanh only ever increases, so `tanh(z) > 0` is exactly `z > 0`. The output activation never changes *which* buttons are pressed. It only makes the numbers easier to read.
- **Batching.** Every agent has *its own* weights. The game hands `build_brain` all the genomes of a worker's chunk and asks the brain to turn (agents × 160) Observations into (agents × 5) presses in one go.
  - Stack the weights with a leading agent axis, e.g. `W1` of shape (agents, 160, 24), and `np.matmul` multiplies them all at once.
  - #4 measured this at about 2× faster than looping. It's an optimisation, so build the plain version first.

**Build.**
- `Layer(weights, biases)` with `forward(inputs) -> outputs`.
- `NeuralNetwork(layers)` with `forward(observations) -> outputs`.
- `Brain` with `decide(observations: (agents × 160)) -> presses: (agents × 5) bool`. This is the object `build_brain` returns.

**Proof check.**
- A tiny 2 → 2 → 1 network with chosen weights matches a value worked out by hand.
- The batched brain gives exactly the same presses as running each agent's network on its own in a loop.
- The output shapes are right.

**Alternatives to research.**
- **No hidden layer** (single-layer perceptron): it can't express "A and B" (look up the XOR problem).
- **Deeper MLPs**: a bigger search space for evolution, and slower.
- **Recurrent networks (RNN)**: memory across ticks, e.g. "I jumped a moment ago".
- **Convolutional networks (CNN)** over the 13 × 12 grid: the same small detector slides across the grid, so "Goomba ahead" is learned once instead of once per cell.
- **Softmax / argmax over actions**: picks *one* action. That's wrong here, because buttons combine (run + right + jump).

---

## Milestone 3: The genome
**Concept.** The game sees a genome only as a flat 1-D float array. Your code needs one fixed rule to turn it into weights and back. This is a **direct encoding**: one gene per weight, so mutation and crossover act on the weights themselves.

| Part | Shape | Genes |
|---|---|---|
| `W1` hidden weights | 160 × 24 | 3,840 |
| `b1` hidden biases | 24 | 24 |
| `W2` output weights | 24 × 5 | 120 |
| `b2` output biases | 5 | 5 |
| **Total** | | **3,989** (float64 ≈ 32 KB) |

The order is `W1` (flattened row by row), `b1`, `W2`, `b2`. With the layer sizes in a run's saved `config.toml`, a saved `best_genome.npy` can be rebuilt into its network.

**Build.** `GenomeLayout(layer_sizes)` with `gene_count`, `pack(weights_and_biases) -> genome` and `unpack(genome) -> weights_and_biases`.

**Proof check.**
- `gene_count == 3989` for 160 → 24 → 5.
- Round trip: `pack(unpack(g))` equals `g`.
- A genome of `0, 1, 2, …` puts each number in the expected place.

**Alternatives to research.**
- **Indirect encodings** (CPPN, HyperNEAT): a small genome *generates* the weights.
- **Compressed encodings**: evolve a few frequency coefficients that expand into the weights (Koutník et al., 2013).
- **NEAT** (Stanley & Miikkulainen, 2002): evolves the network's *structure* too. SethBling's *MarI/O* used it on Mario. It needs variable-length genomes, which the frozen seam allows in principle, but every brain in a batch would differ in shape.
- **float32 vs float64**: half the size, slightly different rounding.

---

## Milestone 4: Random agents
**Concept.** Before evolving anything, check that random brains play.
- **Initial weights.** With 160 inputs of ±1, Uniform(−1, 1) weights give sums several units wide. That pins tanh at ±1: "saturated" neurons that never change their mind.
  - Drawing weights from Normal(0, 1/√fan_in), where fan_in is the number of inputs to the neuron, keeps the sums around ±1. This is **LeCun normal** initialisation.
  - Biases start at 0. All-zero weights would make every agent identical, leaving no diversity to select from.
- **Random search.** If `next_genomes` simply returns fresh random genomes every generation, the run becomes **random search**. That's the baseline every later milestone must beat.
- **Randomness.** Only ever use the `rng` the game passes in.

**Build.** A first `NeuroevolutionAlgorithm` with `initial_genomes(population_size, rng)`, `build_brain(genomes)` and a placeholder `fitness` (e.g. `furthest_x`). `next_genomes` returns new random genomes.

**Proof check.**
- Unit: the initial genomes have the right shape, and the weight spread is about 1/√fan_in.
- Visible: with `py -m mario train --watch`, a 1000-agent generation runs, most agents stall or die at the first Goomba, and they do *different* things.
- `results.csv` fills in.

**Alternatives to research.** Uniform(−1, 1); Xavier/Glorot (Glorot & Bengio, 2010); He initialisation (made for ReLU); zero initialisation and why it fails.

---

## Milestone 5: Fitness
**Concept.** The goal: get as far right as possible, reach the flag, take the least time and collect the most coins. Two traps shape the formula:

1. **Time only counts for agents that reach the flag.** If "fewer ticks = better" counted for everyone, an agent dying after 2 s would beat one walking carefully for 30 s, and evolution would breed fast suicides.
2. **A coin needs a fixed price in distance and in time.** Priced too high, agents farm the first ? blocks and stall. Priced too low, they ignore the bonus room.
   - The original game sets a price: a coin is 200 points, and each time unit left is 50 points (1 unit = 24 ticks).
   - So **1 coin = 4 units = 96 ticks ≈ 1.6 s**. Stopping for a coin is worth it if it costs less than 1.6 s.

```
fitness = furthest_x                              px; ≈ 3,170 px from spawn to the flag (column 198)
        + COIN_REWARD × coins_collected           COIN_REWARD = 100, about 6 tiles of progress per coin
        + if end_reason == "reached_flag":
            FLAG_REWARD − TIME_REWARD × ticks_elapsed
                                                  FLAG_REWARD = 20000
                                                  TIME_REWARD = COIN_REWARD / 96 ≈ 1.04 per tick
```

"Bonus + reward × ticks left" equals "a bigger bonus − reward × ticks used", because ticks left = 9,600 − ticks used. This form doesn't need the game's timer length. Even the slowest finisher (9,600 ticks) gets ≥ 10,000 from the flag, more than any non-finisher can get from distance plus coins, so **reaching the flag always wins**.

`AttemptResult` already carries `end_reason`, `furthest_x`, `ticks_elapsed` and `coins_collected`. It also carries every timed game event, in case a later idea needs them.

**Build.** `FitnessFunction(settings)` with `score(attempt_result) -> float`, plugged in as `NeuroevolutionAlgorithm.fitness`.

**Proof check.** Tests on hand-built `AttemptResult`s:
- More distance scores higher.
- One coin is worth exactly 96 ticks for a finisher.
- The slowest finisher beats the best possible non-finisher.
- A death at x = 500 scores the same, however long it took.

Visible: in `results.csv`, fitness and `furthest_x` move together.

**Alternatives to research.**
- **The game's `final_score`**: it already carries these prices, but it also rewards stomping and breaking bricks.
- **Distance per tick**: the same trap as point 1 above.
- **Multi-objective optimisation**: Pareto ranking, NSGA-II (Deb et al., 2002). No weights to choose.
- **Lexicographic fitness**: compare distance first, then coins, then time.
- **Novelty search** (Lehman & Stanley, 2011): reward *new* behaviour instead of score. It helps when a fitness function is "deceptive", for example when it leads agents into a dead end.
- **Fitness shaping / rank-based fitness**: only the order of fitnesses matters, not their size.

---

## Milestone 6: Selection only
**Concept.** Selection picks which genomes become parents.
- **Tournament selection**: pick `TOURNAMENT_SIZE` agents at random and keep the fittest. Repeat for every parent slot.
- It only *compares* fitnesses, so the 10,000+ flag bonus doesn't distort it. Under roulette-wheel selection, one finisher would take almost every slot.
- A larger tournament means more **selection pressure**: faster progress, but diversity is lost sooner.

This milestone deliberately has **no mutation**, to show why it's needed. Selection alone can only reshuffle what already exists.

**Build.** `TournamentSelection(tournament_size)` with `select(fitnesses, count, rng) -> parent_indices`. `next_genomes` now returns copies of the selected parents.

**Proof check.**
- Unit: with a fixed `rng`, fitter agents are picked more often, and a tournament of size 1 picks uniformly.
- Visible (`py -m mario stats`): mean fitness climbs toward the best, the best **never exceeds** generation 1's best, and the 10–90% band collapses.

**Alternatives to research.** Fitness-proportionate (roulette-wheel) selection; stochastic universal sampling; rank selection; truncation selection; Boltzmann selection. Also the ideas of selection pressure, premature convergence and genetic drift.

---

## Milestone 7: Mutation, the first real evolution
**Concept.** Mutation adds small random changes, so children can be *better* than their parents.
- **Gaussian mutation**: each gene, with probability `MUTATION_RATE` (0.05, so about 200 of the 3,989 genes), gets Normal(0, `MUTATION_STRENGTH`) added. The strength is 0.05, on the same scale as the initial weights.
- Too strong, and children are random; too weak, and progress crawls. That's the **exploration vs exploitation** trade-off.

**Build.** `GaussianMutation(rate, strength)` with `mutate(genome, rng) -> new_genome`. It never changes the parent in place.

**Proof check.**
- Unit: with a fixed `rng`, about `rate × 3989` genes change, the changes have the expected spread, and the parent is unchanged.
- Visible: best fitness rises over 20 generations and beats the random-search baseline from milestone 4.
- Reproducibility: the same seed twice gives the same `results.csv`. (#4 warns that float rounding can very rarely flip a button sitting right at the threshold.)

**Alternatives to research.**
- **Uniform reset mutation**: replace the gene with a fresh random value.
- **Mutating every gene a little**: how evolution strategies work. See OpenAI's ES (Salimans et al., 2017) and CMA-ES (Hansen).
- **Self-adaptive mutation strength**: σ is evolved as part of the genome.
- **The 1/5 success rule** and **decaying σ schedules**.

---

## Milestone 8: Elitism
**Concept.** Copy the best `ELITE_COUNT` genomes (the top 1%) into the next generation **unchanged**, and breed the rest as before.
- The game is deterministic and every agent is replayed each generation, so an elite earns the same fitness again.
- So the best fitness can (almost) never drop, and progress is never lost to an unlucky generation.
- On a fitness tie, the lower agent index wins, the same rule the run folder uses.

**Build.** `Elitism(elite_count)` with `elites(genomes, fitnesses) -> genomes`. `next_genomes` = elites + (population − elites) bred children.

**Proof check.**
- Unit: the elites are exactly the top N by fitness, the tie rule holds, and the population size is preserved.
- Visible: the best-fitness curve never goes down.

**Alternatives to research.** No elitism; (μ + λ) vs (μ, λ) selection, i.e. whether parents compete with their children; steady-state GAs; a "hall of fame".

---

## Milestone 9: Crossover
**Concept.** Crossover makes a child from two parents, hoping to combine the good parts of each.
- **Uniform crossover**: for each gene, flip a coin to choose which parent it comes from.
- It's used with probability `CROSSOVER_RATE` (0.7); otherwise the child is a clone of the first parent. Mutation runs afterwards either way.

The catch is the **permutation (competing conventions) problem**. Two networks can do the same job with their hidden neurons in a *different order*. Mixing their genes then mixes unrelated neurons and can break both. That's why this milestone is an experiment, not a guaranteed improvement.

**Build.** `UniformCrossover(rate)` with `crossover(parent_a, parent_b, rng) -> child`.

**Proof check.**
- Unit: every child gene comes from one of the two parents, about half come from each, and at rate 0 the child is a clone.
- Visible: run crossover **on vs off, with the same seed**, compare the two runs with `py -m mario stats <run-a> <run-b>`, and record which was better and by how much.

**Alternatives to research.**
- **Single-point and two-point crossover.**
- **Arithmetic / blend crossover (BLX-α)** and **simulated binary crossover (SBX)**: children *between* their parents' values.
- **Neuron-wise crossover**: swap whole hidden neurons, which softens the permutation problem.
- **Mutation-only GAs**: Such et al. (2017), *Deep Neuroevolution*, evolved Atari players with no crossover at all.

---

## Milestone 10: The full run
**Concept.** Assemble everything into one `GeneticAlgorithm` (your `NeuroevolutionAlgorithm`, built by `create_algorithm`) and run 1000 agents × 100 generations. That takes about 13–20 minutes headless (#4).

**Build.** `GeneticAlgorithm` composing `GenomeLayout`, `FitnessFunction`, `TournamentSelection`, `GaussianMutation`, `UniformCrossover` and `Elitism`. Each piece is passed in, so each can be swapped while tuning.

**Proof check.**
- **Success: at least one agent reaches the flag.**
- `py -m mario replay <run-folder> --generation N --best` shows it.
- `py -m mario stats <run-folder>` gives the fitness, distance and end-reason curves.

---

## Milestone 11: Tuning
**Concept.** Change **one setting at a time**, keep the seed fixed, and compare curves. Run a few seeds before believing a difference.

Settings worth trying:
- hidden size (16 / 24 / 32)
- `MUTATION_RATE` and `MUTATION_STRENGTH`
- `TOURNAMENT_SIZE`
- `ELITE_COUNT`
- `COIN_REWARD`: does a higher coin price get agents into the bonus room, and at what cost in time?

**Proof check.** A short table of experiments: setting, value, the generation the flag was first reached, and the best fitness at generation 100. The comparison output of `py -m mario stats` gives most of it.

**Alternatives to research.** Speciation (from NEAT); novelty search; adaptive mutation; hyperparameter search methods (grid search vs random search).

---

## Further reading
- Stanley & Miikkulainen (2002), *Evolving Neural Networks through Augmenting Topologies* (NEAT).
- SethBling, *MarI/O* (video): NEAT playing Super Mario World.
- Such et al. (2017), *Deep Neuroevolution: Genetic Algorithms Are a Competitive Alternative for Training Deep Neural Networks for Reinforcement Learning*.
- Salimans et al. (2017), *Evolution Strategies as a Scalable Alternative to Reinforcement Learning*.
- Lehman & Stanley (2011), *Abandoning Objectives: Evolution Through the Search for Novelty Alone*.
- LeCun et al. (1998), *Efficient BackProp* (initialisation, and why tanh is centred).
