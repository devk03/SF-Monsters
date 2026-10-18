# Sutro Tower quest

Module: `mission_sutro_tower`. Owner: **unassigned**. Reviewer: project owner.
Status: scaffold; no final encounter, casting, dialogue or balance is approved.

## Story input

Treasure Island checkpoint is complete. The player has reached the tower through existing routes..

## Fixed output and interface

Core sets `VAR_UNUSED_0x40FB = 1` only after your Run entry signals success.

Hook: the existing neighborhood scientist interaction in `sutro_tower`. Own the contained scene and optional local NPCs; keep the shared neighborhood layout and routes.

Run entry: `SFMod_mission_sutro_tower_Run`. Finish with `sfmodule_return 1` only on success;
use `sfmodule_return 0` on cancellation/unfinished work. Core prerequisites execute before this
entry. Core rewards, safe exits and badge/crisis state are outside your ownership.
Your module must remain usable after a loss, ordinary Save and cold Continue.

## Your creative space

Advance the legendary investigation toward Lands End without resolving the final crisis here.

Propose characters and final scene details in this file. Do not imply a real person
has agreed to participate. Exact rosters and difficulty remain proposals until
playtested against the eventual campaign teams; the current level-100 loan is QA.

## Native allocation

Core NPC IDs 1–3 are reserved. Append your NPCs from ID 4;
keep the combined active-object total at 15 or fewer. These allocations are
stable for this finishing revision; changing them needs integrator review.

Persistent puzzle flags: `FLAG_UNUSED_0x044`, `FLAG_UNUSED_0x045`.
Core completion (read only): `FLAG_UNUSED_0x046`. This is separate from
old blockout access stamps; an existing badge never proves this new module was won.
Scratch: `VAR_TEMP_1`, `VAR_TEMP_2`, `VAR_TEMP_3`, `VAR_RESULT`.
Trainer slots: `TRAINER_GRUNT_AQUA_HIDEOUT_2`.
Define teams in your module.json. Internal stock slot names do not prescribe the
visible trainer identity. Every native label uses `SFMod_mission_sutro_tower_`.

## Implement and submit

1. Read CONTRIBUTING.md and the package AGENTS.md. Set status `draft` to enable work.
2. Implement your local script/NPC/team data; use only assigned state and files.
3. Run `make module-check MODULE=mission_sutro_tower`, `make world-check`, and private build.
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
