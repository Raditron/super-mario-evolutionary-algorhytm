# The frozen game drives the generation loop

The game package (AI-written, frozen once built) owns `py -m mario train`: the generation loop, the worker pool, watch-live, timing and the run recorder. The user's `neuroevolution` package plugs in by implementing the abstract `NeuroevolutionAlgorithm` that the game defines (`initial_genomes`, `build_brain`, `fitness`, `next_genomes`), reached through one fixed import, `from neuroevolution import create_algorithm`, in train mode only. We chose this so the frozen game keeps everything it must guarantee (complete generation folders, reproducible seeds, real-time pacing) while every learning decision stays in the user's code as plain functions testable without the game.

## Considered Options

- **The algorithm drives the loop and calls game services** (`evaluate_population`, `RunRecorder`). Rejected: the user would re-wire recording, timing and the pool, and the frozen game's `train` command would have to call back into user code anyway.

## Consequences

- Because the game can't change after freezing, `AttemptResult` hands fitness everything the game knows: the end-of-attempt facts plus the full timed game event list.
- `play` and `replay` never import `neuroevolution`, so they work while the algorithm is unwritten.
