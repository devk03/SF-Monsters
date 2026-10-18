# Build one piece of SF Mini Monsters

Contributors own contained experiences. The shared game owns geography, connections,
badge order, story prerequisites, traversal unlocks, save identity and safe exits.
The current world is a tested geometry blockout; a complete polished city and final
story scenes are not implied by the working routes.

## Start with an assignment

Choose an available package from [the module index](romhack/modules/README.md).
The maintainer confirms the assignment; all current slots are unassigned. Work in
a fork and a feature branch. You do not need write access to the main repository.

Give your coding agent this prompt, replacing the ID and creative direction:

> Use `.agents/skills/sf-module/SKILL.md` to implement `gym_1`. Read its
> `romhack/modules/gym_1/HANDOFF.md` and AGENTS.md. My idea is: [your idea].
> Keep the shared world contract intact, test locally, and prepare a focused PR.

Humans can follow the same instructions without an agent. The skill is stored in
the repo so a fork carries the workflow with it; no personal Codex setup is needed
to read the file directly.

## Your package

Everything for one assignment belongs under `romhack/modules/<id>/`:

- `HANDOFF.md`: setting, story inputs/outputs, creative freedom, decisions and QA.
- `module.json`: `stub`, `draft` or `ready_for_review`; optional native NPCs/teams.
- `content.inc`: native script entry `SFMod_<id>_Run`. Return `VAR_RESULT = 1`
  only on success; return 0 on cancellation or unfinished work. Core guards run
  before this entry and core awards run only after success.
- Optional `layout.json`: gym room rows, exactly 32 columns by 24 rows, using the
  existing legend. The assigned entrance, exit, scientist/checkpoint approach and
  safe arrival stay accessible. Neighborhood geometry remains shared.

Set status to `draft` to enable your content in private builds. A stub does not
alter the tested world. `ready_for_review` requests review; it never means approved.
The maintainer owns [contracts.json](romhack/modules/contracts.json): bindings,
two persistent puzzle flags plus a core-owned completion flag per package and unique native trainer slots.
Use scratch `VAR_TEMP_1..3` and `VAR_RESULT` for temporary work. Never write badge,
crisis, starter, save-identity or other modules' state directly.

Inside those boundaries, design your own dialogue, jokes, puzzle, trainer teams,
NPC scenes and revisit behavior. Keep both GBA and web playable with standard GBA
controls. The blockout loan monster is a traversal tool, not a final balance target.
Propose your own leader/persona and casting for owner review; keep those proposals
separate from confirmed participation. Preserve the shared plot. Record unresolved casting/plot choices in the handoff for review.

Native single-battle teams use the existing JSON format in
`scripts/romhack/battle_content.py`: assigned `id`, short uppercase `name`, `class`,
`portrait`, and `party` entries with `species`, `level`, `moves` and optional `item`.
Define each team in your own `module.json`; do not edit global trainer tables.
See [the working example](docs/module-example.md). Additional rooms, custom tile
allocations, new battle mechanics or more persistent state need an integrator
extension to the shared contract. They are not supported by silently adding files.

## Local checks and build

```sh
make module-check MODULE=gym_1
make world-check
make world-draft
```

The first two use Python's standard library and do not need ROM bytes. The private
native build needs the [existing native toolchain setup](romhack/README.md).
It compiles the same cartridge for native mGBA and the web WASM emulator, without
deploying. Full ROMs, saves and build outputs stay in ignored `.tools/`.

Before the PR, fetch your chosen upstream base and check the entire diff:

```sh
python3 scripts/romhack/check_module.py --module gym_1 --base upstream/main
```

Use `origin/main` if that is your actual upstream. This check includes tracked and
untracked changes; keep unrelated local files out of the contribution checkout.
It rejects edits outside the assigned folder. Shared changes need a separately
reviewed integration PR. The validator checks source contracts and geometry;
passing it does not prove a battle, puzzle or save works.

Play the module through entry, cancellation, loss/retry, success, revisit, exit,
ordinary Save and cold Continue. Include native and web evidence in HANDOFF.md.
Progress must not disappear on loss or trap the player behind a closed exit.

## PR and review

Use the PR template, name the module, summarize the experience, list the exact
commands you ran, include gameplay evidence and credit original assets/sources.
Provide failure/retry and save checks, not just a victory screenshot. A PR may be
accepted, sent back for changes or rejected by the project owner. No contributor
status or passing local check grants merge approval.

CODEOWNERS requests owner review where GitHub applies it; this repository file
does not itself enable branch protection. Never merge without the owner's explicit
approval. GitHub Actions stays manual-only; use local checks and `[skip ci]` commits.
No contributor outreach, account access, automatic deployment or recurring monitor
is part of this workflow. Keep commercial cartridges and extracted assets out of PRs.
