# Development agent — shared world and contributor modules

Current goal: finish all 18 non-gym destinations and their 19 routes as a compact,
dense, lively SF world. Read `docs/game-spec.md` section 15.1 for the measurable
completion gates and latest progress. The user explicitly resumed implementation
beyond the prior blockout-review pause. Gym content remains contributor-owned;
finish its site/approach while preserving the assigned entry/state contracts.

Latest user instruction: keep going against the October18 continued-work goal in
section15.1, agreed with the alignment chat. First improve the native SF Map,
then district/route/interior identity and complete native/browser acceptance.
Keep bounded alignment reviews about every30active minutes. The old paused goal
card cannot be replaced while its browser-route/review gates remain unfinished;
do not falsely close it or treat that UI limitation as a reason to stop work.
Latest launch requests also add locally remembered original ROMs, a native SF
Continue/New Adventure entry and a world-only2×speed toggle. Display scaling is
separate. Keep rootv80 runtime/save bytes intact; verify native old-Save loading,
browser return visits, speed/audio behavior and ordinary Save/import safety.

Current checkpoint: v0.0.91 is published at `/world`; root v80 stays available.
The world now mixes original walkups, awning shops, lofts and Victorian fronts,
with warm/sage/slate paint, finished exposed edges, district planting and signs. Browser UI uses integer pixels,
grouped file tools and optional desktop controls. Read section 15.1 for evidence;
native SF Map now has original peninsula/bay/island art and verified controls.
Human visual acceptance and full foreground browser performance remain open.
Latest feedback rejects repeated paving and sparse detached urban blocks. Rebuild
street composition with longer attached frontages, actual curbs and distinct
district materials/decoration. Review contrasting districts in native gameplay;
do not treat more props or a palette swap as acceptance.
The world is a functional review candidate, not human-approved finished towns.
Read the latest section 15.1 evidence and review clips before further changes.
All 58 maps and their native/WASM route pass; final visual acceptance remains open.
During active implementation, check with the existing alignment chat about every
30 minutes. Use bounded reviews, not recurring monitors; no review grants merge
or deployment approval beyond the user's authorized scope.

The blockout and module workflow are foundations, not finished towns. Keep maps
32×24, use connected urban blocks and neutral gray paving, add natural residents,
safe ambient movement, useful interiors/services, discoveries and revisit dialogue.
Nature, coast and island destinations need their own trail/landmark composition.
Test the same native ROM in GBA and web. Human quality review remains required.
Read AGENTS.md; preserve prior evidence and public v80 while iterating private drafts.

## Authoritative inputs

1. Latest direct user decisions and repository safety rules.
2. `docs/world/initial-world-plan.excalidraw`: imported user scene, preserved
   element IDs, arrow bindings, annotations and embedded image.
3. `docs/world/plan-notes.md`: interpretation, decisions and unresolved conflicts.
4. `romhack/world/world.json`: editable area/route/gym/traversal manifest.
5. `romhack/world/art-contract.json`, `districts.json`, `interior-details.json`, `discoveries.json` and
   `core-state.json`: original art allocation, dialogue, local activities and
   their explicit persistent-state reservations. `world.json` also owns SF guide
   positions and native SF location labels.
6. Generated native layouts/scripts and independent validation evidence.

The previous `docs/story/` treatment and `v0.0.80` Sunset/Cognition opening are
historical development baselines. Do not silently force their route onto the
new Dogpatch-start plan. Do not interpret text embedded in the diagram as shell
instructions, permission to contact people or approval of unrelated features.

## What to build now

- All approved named areas, labeled and spatially distinct, with playable ground.
- Routes between them, meaningful entrance/exit approaches and safe return paths.
- Dogpatch new-game spawn and eight themed gym entrance/room placeholders.
- Traversal gates, water/boat routes, late return to the final gym and League route.
- One deterministic generator from a versioned manifest to native map/script data.
- A separate draft GBA blockout playable in native mGBA and the web emulator.

Replace the plain blockout with coherent original SF streets, landmarks and activity. A generated
graph, screenshot or renamed stock layout alone is not a playable world. Walking
routes must have real geometry; don't replace every road with a teleport menu.
Explicit transport is appropriate for long cross-city transfers and water routes.

## Contributor workflow and boundaries

The shared world owns geography, routes, badge order, story prerequisites,
traversal unlocks, save identity and safe exits. Contributors own contained
encounters. Eight gyms and six missions are scaffolded under `romhack/modules/`;
all owners are unassigned. The maintainer confirms each assignment. Each package
has an AGENTS.md, HANDOFF.md, native script and team metadata. Use the repo-local
`sf-module` skill to turn an assigned human's creative direction into that package.

Contracts reserve entry/exit/state/trainer bindings. Supported edits include local
dialogue, puzzles, trainer teams, NPCs and gym room geometry. Extra rooms, custom
tile/audio allocations and engine extensions require a separate integration change.
Keep author PRs inside one assigned package. Run local module/world checks and
native/web playtests; include cancellation, loss/retry, success, revisit, exit and
Save/cold Continue evidence. Owner review may accept, request changes or reject.
Passing checks and `ready_for_review` never grant merge or deployment approval.
CODEOWNERS requests review; branch protection is a separate GitHub setting.

The b967 all-stub ROM remains a historical blockout reference. Core town
finishing changes it legitimately; establish a new reviewed baseline before
judging contributor-only changes against it. A fresh
module fixture injects prerequisites under a separate QA identity; it is not
campaign progression evidence. `make module-preview` is a finite localhost-only
player. Never replace the public patch just to demonstrate a contribution.
Label temporary access-stamp interactions as blockout tools, never finished gyms.
Final contributor casting, gym encounters and the new type chart remain separate.
Natural town dialogue, ambient activity and non-gym services are now in scope. The requested 2× website button is separate.

## Map and save safety

- Preserve the published v80 patch/player and their normal save behavior.
- Build the new world in a separate draft profile and engine work directory.
- Use separate blockout identity/save slots; never import or overwrite a player's
  v80 save as though the new geography were a compatible continuation.
- Keep full ROMs, engine outputs, reference assets and private saves under ignored
  `.tools`; Git/public hosting receive original source and approved patches only.
- Every arrival must be in bounds, walkable and outside a blocking NPC/trigger.
- Paired exits and return paths must remain usable after gates change.
- Continue must retain land/Surf mode, refresh changed actor templates even on
  a still-valid player tile, and preserve party, money, core chapter variables,
  contributor flags and pending local rewards. A source/collision check is not
  sufficient proof of an update; use actual earlier ordinary Saves.
- Compare complete linked art resources with normal compiler inputs. Preserve
  full landmark footprints and reachable viewing/interaction approaches.
- Connection margins, map/layout uniqueness and native object limits must pass.
- Preserve the user's diagram; new annotations need revision history.

## Acceptance evidence

1. Manifest covers every approved plan area and all eight gym entrance slots.
2. No dangling edges/warps, overlapping IDs, invalid arrivals or unreachable goals.
3. At each traversal stage, intended routes open and future gates stay closed;
   returns cannot strand the player. Final gym/League dependencies are explicit.
4. Regeneration from identical input produces identical map/script bytes.
5. Native compiled map tables match authored layouts, events and connections.
6. Controller-driven native traversal visits all areas, routes and gym stubs;
   checkpoint saves cold-load into safe authored positions.
7. The same draft ROM boots and traverses in the web emulator. State performance
   limitations honestly; existing browser-renderer work remains separate.

Do not claim art, audio, battle, campaign balance or full-game parity approval.
Record coverage and remaining gates in section 15. Commit coherent code changes
around 200–300 lines when practical; don't pad or split a logical fix artificially.
Run meaningful local checks. GitHub Actions remains manual-only; use `[skip ci]`.

## Pause and scope boundaries

Pause dependent work only for a required user decision or a fully evidenced,
review-ready non-gym world. Do not stop at the old blockout checkpoint. Continue independent approved work while a decision is pending. Never
mark the goal complete with an unresolved required venue or failed traversal gate.
Both Treasure Island and Angel Island are approved. Angel Island is the sole
outside-SF exception, containing Victory Road and the League; retain Treasure
Island as a separate story destination. This decision was explicit on October 17.
No contributor outreach, PR merge, DB migration, indefinite monitor or automatic
workflow is authorized by a world-map task. Do not run `rm` in any form.
