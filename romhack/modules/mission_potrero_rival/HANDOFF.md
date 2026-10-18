# First rival meeting

Module: `mission_potrero_rival`. Owner: **unassigned**. Reviewer: project owner.
Status: scaffold; no final encounter, casting, dialogue or balance is approved.

## Story input

The player has started in Dogpatch and reached Potrero Hill. Introduce the Berkeley rival and the starter matchup. Exact identity, dialogue and battle roster are contributor proposals..

## Fixed output and interface

No shared story reward is granted; track local success with your allocated flags.

Hook: the existing neighborhood scientist interaction in `potrero_hill`. Own the contained scene and optional local NPCs; keep the shared neighborhood layout and routes.

Run entry: `SFMod_mission_potrero_rival_Run`. Return `VAR_RESULT = 1` only on success;
return 0 on cancellation/unfinished work. Core prerequisites execute before this
entry. Core rewards, safe exits and badge/crisis state are outside your ownership.
Your module must remain usable after a loss, ordinary Save and cold Continue.

## Your creative space

Establish a recurring rival without settling the final League confrontation.

Propose characters and final scene details in this file. Do not imply a real person
has agreed to participate. Exact rosters and difficulty remain proposals until
playtested against the eventual campaign teams; the current level-100 loan is QA.

## Native allocation

Persistent flags: `FLAG_UNUSED_0x038`, `FLAG_UNUSED_0x039`, `FLAG_UNUSED_0x03A`.
Scratch: `VAR_TEMP_1`, `VAR_TEMP_2`, `VAR_TEMP_3`, `VAR_RESULT`.
Trainer slots: `TRAINER_CALVIN_1`.
Define teams in your module.json. Internal stock slot names do not prescribe the
visible trainer identity. Every native label uses `SFMod_mission_potrero_rival_`.

## Implement and submit

1. Read CONTRIBUTING.md and the package AGENTS.md. Set status `draft` to enable work.
2. Implement your local script/NPC/team data; use only assigned state and files.
3. Run `make module-check MODULE=mission_potrero_rival`, `make world-check`, and private build.
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
