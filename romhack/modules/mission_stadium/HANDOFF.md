# Giants stadium event

Module: `mission_stadium`. Owner: **unassigned**. Reviewer: project owner.
Status: scaffold; no final encounter, casting, dialogue or balance is approved.

## Story input

The planned story visits the stadium after Mission Bay and before Financial District. This is a contained event; the exact comedy/puzzle is open..

## Fixed output and interface

No shared story reward is granted; track local success with your allocated flags.

Hook: the existing neighborhood scientist interaction in `giants_stadium`. Own the contained scene and optional local NPCs; keep the shared neighborhood layout and routes.

Run entry: `SFMod_mission_stadium_Run`. Finish with `sfmodule_return 1` only on success;
use `sfmodule_return 0` on cancellation/unfinished work. Core prerequisites execute before this
entry. Core rewards, safe exits and badge/crisis state are outside your ownership.
Your module must remain usable after a loss, ordinary Save and cold Continue.

## Your creative space

Deliver an SF stadium adventure without moving gym order or creating a new main villain.

Propose characters and final scene details in this file. Do not imply a real person
has agreed to participate. Exact rosters and difficulty remain proposals until
playtested against the eventual campaign teams; the current level-100 loan is QA.

## Native allocation

Core NPC IDs 1–9 are reserved. Append your NPCs from ID 10;
keep the combined active-object total at 15 or fewer. These allocations are
stable for this finishing revision; changing them needs integrator review.

Persistent puzzle flags: `FLAG_UNUSED_0x03E`, `FLAG_UNUSED_0x03F`.
Core completion (read only): `FLAG_UNUSED_0x040`. This is separate from
old blockout access stamps; an existing badge never proves this new module was won.
Scratch: `VAR_TEMP_1`, `VAR_TEMP_2`, `VAR_TEMP_3`, `VAR_RESULT`.
Trainer slots: `TRAINER_BILLY`.
Define teams in your module.json. Internal stock slot names do not prescribe the
visible trainer identity. Every native label uses `SFMod_mission_stadium_`.

## Implement and submit

1. Read CONTRIBUTING.md and the package AGENTS.md. Set status `draft` to enable work.
2. Implement your local script/NPC/team data; use only assigned state and files.
3. Run `make module-check MODULE=mission_stadium`, `make world-check`, and private build.
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
