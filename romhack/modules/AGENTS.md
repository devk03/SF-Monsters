# Contributor package instructions

Read the repo AGENTS.md, DEVELOPMENT_AGENT.md, CONTRIBUTING.md and your package's
HANDOFF.md. The maintainer-owned contracts.json binds modules to the shared world.

Edit only your assigned package unless the human explicitly requests an integration
change. Use `SFMod_<id>_` for every label, the allocated flags for persistent puzzle
work, and the allocated trainer slots for local teams. `content.inc` returns to
the core; it does not own global warps, badges, crisis flags or save identity.

Mark work `draft` while implementing and `ready_for_review` only with honest QA.
Neither status is merge approval. Leave a working cancellation and exit route,
preserve loss/retry state, and implement useful revisit behavior. Checkpoint-style
development stamps are placeholders, not finished leader battles.

Run the local module/world checks and private native build. Test actual native
and web play before claiming support. Record remaining plot/casting choices and
unsupported asset/room/mechanics extensions; don't change shared files to hide gaps.
Use the PR template. No automatic workflows, publication, outreach or merge.
