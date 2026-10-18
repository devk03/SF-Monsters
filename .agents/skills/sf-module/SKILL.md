---
name: sf-module
description: Implement an assigned SF Mini Monsters gym or mission as a contained contributor package, validate its shared-world contract, and prepare it for owner PR review. Use for module authoring, not shared world redesign or deployment.
---

# SF gym or mission authoring

Read the repository AGENTS.md and DEVELOPMENT_AGENT.md, then
[CONTRIBUTING.md](../../../CONTRIBUTING.md) and the assigned package's HANDOFF.md
and AGENTS.md. Resolve the repo root with Git. If the human has not named an
assignment, show the available modules and ask which one they want to own.

Work in `romhack/modules/<id>/` on a feature branch. The maintainer owns contracts.json:
the shared geography, badge order, prerequisites, rewards, native save allocation,
entry/exit bindings and other packages must stay intact. Propose a separate
integration change when a requested idea needs more room, assets or engine support.

Turn the human's idea into that package's dialogue, puzzle, supported trainer teams
and revisit behavior. Use `SFMod_<id>_` labels, allocated persistent flags and trainer
slots, and documented temporary variables. Enable private work with `status: draft`.
Finish with `sfmodule_return 1` only after local success and `sfmodule_return 0` on cancellation; the core owns
the final badge/story output. Preserve loss/retry and a usable exit at every stage.
Treat casting and story decisions marked unresolved in the handoff as decisions
to record or clarify, not facts to invent. Credit original assets and research.

Run `make module-check MODULE=<id>` and `make world-check`, then the private native
build and actual native/web play. `make module-playtest MODULE=<id> SCENARIO=ready`
creates a fresh-game fixture without a private save; `make module-preview` serves
it on localhost for a finite session. Use the example linked from CONTRIBUTING.md for
native battle team data. Record commands, evidence and missing gates in HANDOFF.md.
Do not describe source validation as runtime approval.

Before a PR, run `scripts/romhack/check_module.py --module <id> --base <upstream-ref>`.
Include all tracked and untracked changes in the scope review. Stage only the
assigned package, commit coherent changes frequently with `[skip ci]`, and prepare
the repository PR template. Open the PR when the human requests it. Leave final
accept/reject and merge to the project owner; do not deploy, contact people or
start automatic/recurring workflows as part of content authoring.
