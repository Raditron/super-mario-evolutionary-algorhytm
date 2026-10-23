## Coding standards

These apply to every line of code in this repo. Never skip them.

- **Principles**: OOP, SOLID, YAGNI, KISS. Prefer small, single-purpose classes; build only what a current ticket needs.
- **Separation**: game, AI, training, run recording, and rendering live in separate modules. Nothing reaches across those seams except through a named interface.
- **No magic numbers**: every tunable value (physics constants, rewards, population size, mutation rate, screen size, colours...) is a clearly named constant in a dedicated config/constants file for its area, never inline.
- **Readable names**: variables, functions, and classes say exactly what they hold or do. No single-letter names outside tiny loops.
- **Use the glossary**: name domain concepts with the terms in `GLOSSARY.md`.

## Authorship split (coursework)

This is university coursework. The **game** (the World 1-1 replica, rendering, view toggle, run recording) is AI-written. The **learning algorithm** (neural network, genetic algorithm, fitness function) is written **by the user**: agents explain concepts, propose step-by-step plans, and review the user's code, but do not write the algorithm code for them.

## Agent skills

### Issue tracker

Issues are tracked in GitHub Issues on Raditron/super-mario-evolutionary-algorhytm, using the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

The five default labels are used: needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `GLOSSARY.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
