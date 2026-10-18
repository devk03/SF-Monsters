# Gym 3: Clout

Module: `gym_3`. Owner: **unassigned**. Reviewer: project owner.
Status: scaffold; no final encounter, casting, dialogue or balance is approved.

## Story input

Badge 2 earned; player has reached Marina.

## Fixed output and interface

Core grants badge 3 only after your Run entry signals success.

Theme: clout. Native room: Route126. Entry/arrival/exit remain the world interface: arrival (16,16), exit trigger (16,20), scientist (12,9), interaction standing tile (12,10).

Run entry: `SFMod_gym_3_Run`. Finish with `sfmodule_return 1` only on success;
use `sfmodule_return 0` on cancellation/unfinished work. Core prerequisites execute before this
entry. Core rewards, safe exits and badge/crisis state are outside your ownership.
Your module must remain usable after a loss, ordinary Save and cold Continue.

## Your creative space

Own the leader/persona proposal, puzzle, trainer teams, dialogue, jokes and revisit. The old startup/leader slate is historical; it does not fix your casting. Keep the assigned theme and district. Full art/custom rooms require an integration allocation.

Propose characters and final scene details in this file. Do not imply a real person
has agreed to participate. Exact rosters and difficulty remain proposals until
playtested against the eventual campaign teams; the current level-100 loan is QA.

## Native allocation

Persistent puzzle flags: `FLAG_UNUSED_0x026`, `FLAG_UNUSED_0x027`.
Core completion (read only): `FLAG_UNUSED_0x028`. This is separate from
old blockout access stamps; an existing badge never proves this new module was won.
Scratch: `VAR_TEMP_1`, `VAR_TEMP_2`, `VAR_TEMP_3`, `VAR_RESULT`.
Trainer slots: `TRAINER_WATTSON_1`, `TRAINER_WATTSON_2`, `TRAINER_WATTSON_3`.
Define teams in your module.json. Internal stock slot names do not prescribe the
visible trainer identity. Every native label uses `SFMod_gym_3_`.

## Implement and submit

1. Read CONTRIBUTING.md and the package AGENTS.md. Set status `draft` to enable work.
2. Implement your local script/NPC/team data; use only assigned state and files.
3. Run `make module-check MODULE=gym_3`, `make world-check`, and private build.
4. Play entry, cancel, loss/retry, success, revisit, exit, Save and cold Continue
   on native and web. Record exact commands/evidence and remaining gaps below.
5. Mark `ready_for_review` and submit a focused PR for owner acceptance or rejection.
   Passing checks is not merge approval. Never publish full ROMs or private saves.

## Author notes and review evidence

- Proposed character / encounter / puzzle:
- Decisions needed from the story or balance editor:
- Commands and results:
- Native and web evidence:
- Cancel / loss / success / revisit / exit / save results:
- Credits / research sources:
- Remaining limitations:
