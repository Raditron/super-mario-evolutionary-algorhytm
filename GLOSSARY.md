# Mario Neuroevolution

A replica of Super Mario Bros. World 1-1 in which a population of AI-controlled Marios learns to play the level by evolution: each generation the fittest reproduce.

## Training

**Run**:
One complete training session, from the first generation to the last, whose results are recorded in their own folder.
_Avoid_: Simulation, session, experiment

**Run folder**:
The folder holding everything recorded about one run, read afterwards to replay its generations and produce its statistics.
_Avoid_: Output folder, log folder, save

**Generation**:
One round of a run in which every agent of the population plays the level once.
_Avoid_: Epoch, iteration, round

**Population**:
The set of agents playing in one generation; its size is chosen per run.
_Avoid_: Swarm, batch

**Agent**:
One Mario together with the genome that controls it.
_Avoid_: Player, bot, individual

**Chunk**:
A run of consecutive agents of one generation that play their attempts side by side, tick for tick, under one brain.
_Avoid_: Batch, slice, group

**Attempt**:
One single life in the level, from spawn until death, a stall, the level timer running out, or touching the flagpole; when a human plays, each life is its own attempt.
_Avoid_: Episode, game, try

**Stall**:
The end of a training attempt because Mario has gone too long without getting further right than before in the place he is in (the level or the bonus room).
_Avoid_: Stuck, idle timeout

**Genome**:
The inheritable description of an agent's brain (the weights of its neural network) that is mutated and recombined between generations.
_Avoid_: DNA, chromosome, brain

**Brain**:
What turns Observations into Controller presses, built from the genomes of a chunk and deciding for all of its agents at once, every tick.
_Avoid_: Network, model, policy, controller

**Observation**:
What an agent perceives on one tick: the grid of tiles and enemies around Mario plus Mario's own movement state; the agent's brain turns it into Controller presses.
_Avoid_: State, input, sensors, vision

**Fitness**:
The score an agent earns for its attempt, used to decide who reproduces.
_Avoid_: Reward (except for a single scored event), score

**Best agent**:
The agent of a generation with the highest fitness; on a tie, the one with the lowest index. Its genome is the only one a run folder keeps.
_Avoid_: Champion, winner, elite (the elite is the algorithm's to define)

## The level

**Controller**:
The set of buttons (left, right, down, jump, run) through which Mario is driven; a human and an agent press the same buttons, and the game cannot tell them apart.
_Avoid_: Input, gamepad, actions

**Controller log**:
The record of which Controller buttons were held on every tick of an attempt, from which the attempt can be replayed exactly.
_Avoid_: Input log, recording, replay file

**Game event**:
A fact the game reports about an attempt, such as distance travelled, falling into a pit, or hitting the hidden block; fitness is computed from game events.
_Avoid_: Signal, trigger

**Item**:
A thing a block releases for Mario to collect: the Super Mushroom, the fire flower, the Starman or the 1-UP mushroom. An attempt holds at most one at a time.
_Avoid_: Power-up (except in the original's names, such as the power-up ? block), pickup, collectible

**Shell**:
What a stomped Koopa becomes, or one a bumped block flips: a still shell until Mario touches it, which kicks it into a moving shell that defeats the enemies it hits and hurts Mario; a still shell left alone wakes back into a Koopa.
_Avoid_: Koopa shell (as a separate thing from the Koopa), stunned Koopa, projectile

**Power state**:
What Mario has become through the items he collected: small, big or fiery. Big or fiery, an enemy's touch makes him small instead of ending the attempt.
_Avoid_: Status, form

**Bonus room**:
The underground coin room entered through the warp pipe, whose exit pipe puts Mario back in the level much further along.
_Avoid_: Secret room, warp zone, underground level

**Checkpoint**:
The midway point of the level where a human player starts again after losing a life; training attempts always start at the beginning.
_Avoid_: Save point, midpoint, respawn point

**Flag-height points**:
The points for touching the flagpole, more the higher the touch, in the original's five bands from 100 to 5000.
_Avoid_: Flag bonus, pole score

**Remaining-time points**:
The points for the units left on the level timer when Mario touches the flagpole, 50 for each.
_Avoid_: Time bonus, timer score

**End-of-level sequence**:
What plays out after Mario touches the flagpole, with no Controller presses, in play and replay only: the flag slide, the castle walk, then the level timer counting down into the score.
_Avoid_: Ending, cutscene, victory animation

**Flag slide**:
The part of the end-of-level sequence in which Mario slides down the flagpole while the flag slides down to its foot.
_Avoid_: Pole slide, flag drop

**Castle walk**:
The part of the end-of-level sequence in which Mario hops round the flagpole, lets go of it and walks right until the castle door stops him.
_Avoid_: Victory walk, exit walk

## Viewing

**Sprite view**:
The level drawn as humans see it, with textured sprites.
_Avoid_: Normal mode

**Background scenery**:
The clouds, hills, bushes and castle drawn behind the level (layer 2 of its grid); never solid, never seen by the game or the AI, and drawn only by the Sprite view.
_Avoid_: Background, decoration, layer 2

**Debug view**:
The level drawn as the game and AI treat it: hitboxes, and the game events and rewards being scored.
_Avoid_: Hitbox mode, AI view

**Followed agent**:
The agent the view's camera tracks: the Mario furthest right in the level among those still in their attempt; with one Mario, simply him.
_Avoid_: Leader, focused agent, selected agent, best agent

**Ghost**:
Another agent still in his attempt, drawn see-through behind the followed agent while a generation is watched (in the Debug view, as his hitbox's outline); only the rightmost ones are drawn, and each vanishes when his attempt ends.
_Avoid_: Shadow, clone, other player

**Replay**:
An attempt watched again, rebuilt tick by tick from its Controller log in a freshly loaded level, never by re-running its genome; it ends where the recorded attempt ended (after the end-of-level sequence, if it reached the flag).
_Avoid_: Playback, rerun, re-evaluation

**Headless mode**:
Training with nothing drawn, so generations run as fast as the machine allows.
_Avoid_: Fast mode, background mode

**Watch-live**:
Training with each generation shown as it is played, at the game's own speed: the followed agent with his world, the ghosts, and how many agents are still in their attempt.
_Avoid_: Live mode, spectate, visual training
