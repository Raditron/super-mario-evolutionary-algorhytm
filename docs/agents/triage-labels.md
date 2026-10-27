# Triage Labels

The skills speak in terms of five canonical triage roles. This file maps those roles to the actual label strings used in this repo's issue tracker.

| Label in mattpocock/skills | Label in our tracker | Meaning                                  |
| -------------------------- | -------------------- | ---------------------------------------- |
| `needs-triage`             | `needs-triage`       | Maintainer needs to evaluate this issue  |
| `needs-info`               | `needs-info`         | Waiting on reporter for more information |
| `ready-for-agent`          | `ready-for-agent`    | Fully specified, ready for an AFK agent  |
| `ready-for-human`          | `ready-for-human`    | Requires human implementation            |
| `wontfix`                  | `wontfix`            | Will not be actioned                     |

When a skill mentions a role (e.g. "apply the AFK-ready triage label"), use the corresponding label string from this table.

**Algorithm issues are always `ready-for-human`.** Any issue whose work is the learning algorithm (neural network, genetic algorithm, fitness function, anything in `neuroevolution/`) is written by the user, never by an agent (see `CLAUDE.md`). Never label one `ready-for-agent`, and never implement one, whatever its label. Agents may only explain, plan and review. Game-side harness work that only calls the user's package (e.g. #26) is game code and may be `ready-for-agent`.

Edit the "Label in our tracker" column to match whatever vocabulary you actually use.
