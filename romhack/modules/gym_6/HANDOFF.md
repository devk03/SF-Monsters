# Gym 6: Stealth

Module: `gym_6`. Owner: **unassigned**. Reviewer: project owner.
Status: scaffold; no final encounter, casting, dialogue or balance is approved.

## Story input

Badge 5 earned; player has reached Mission Bay.

## Fixed output and interface

Core grants badge 6 only after your Run entry signals success.

Theme: stealth. Native room: Route129. Entry/arrival/exit remain the world interface: arrival (16,16), exit trigger (16,20), scientist (12,9), interaction standing tile (12,10).

Run entry: `SFMod_gym_6_Run`. Finish with `sfmodule_return 1` only on success;
use `sfmodule_return 0` on cancellation/unfinished work. Core prerequisites execute before this
entry. Core rewards, safe exits and badge/crisis state are outside your ownership.
Your module must remain usable after a loss, ordinary Save and cold Continue.

## Your creative space

Own the leader/persona proposal, puzzle, trainer teams, dialogue, jokes and revisit. The old startup/leader slate is historical; it does not fix your casting. Keep the assigned theme and district. Full art/custom rooms require an integration allocation.

Propose characters and final scene details in this file. Do not imply a real person
has agreed to participate. Exact rosters and difficulty remain proposals until
playtested against the eventual campaign teams; the current level-100 loan is QA.

## Native allocation

Core NPC IDs 1–1 are reserved. Append your NPCs from ID 2;
keep the combined active-object total at 15 or fewer. These allocations are
stable for this finishing revision; changing them needs integrator review.

Persistent puzzle flags: `FLAG_UNUSED_0x02F`, `FLAG_UNUSED_0x030`.
Core completion (read only): `FLAG_UNUSED_0x031`. This is separate from
old blockout access stamps; an existing badge never proves this new module was won.
Scratch: `VAR_TEMP_1`, `VAR_TEMP_2`, `VAR_TEMP_3`, `VAR_RESULT`.
Trainer slots: `TRAINER_WINONA_1`, `TRAINER_WINONA_2`, `TRAINER_WINONA_3`.
Define teams in your module.json. Internal stock slot names do not prescribe the
visible trainer identity. Every native label uses `SFMod_gym_6_`.

## Implement and submit

1. Read CONTRIBUTING.md and the package AGENTS.md. Set status `draft` to enable work.
2. Implement your local script/NPC/team data; use only assigned state and files.
3. Run `make module-check MODULE=gym_6`, `make world-check`, and private build.
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
