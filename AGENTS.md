# Project instructions

Be very concise and always ask for permission on db migrations and none on read operations. Never drop our dbs without asking.

NEVER run `rm` in any form. Do not ask for an exception; use a non-destructive alternative or have the user remove files manually.

No merging prs without asking me.

Commit frequently.

## CI budget

GitHub Actions runs only through manual dispatch. Use local checks for routine
commits. Dispatch CI only for a meaningful release or validation checkpoint;
do not trigger it for each incremental code, asset, or documentation commit.

## Active implementation workflow

Always read `docs/game-spec.md` as the source of truth for scope and acceptance.
Use section 15 as the active Emerald parity goal; section 14 records the earlier technical prototype.
The main path is now an Emerald ROM hack with player-supplied local ROM upload.
Publish SF contributions and patches; keep full Emerald-derived ROMs private.
Update acceptance evidence and progress in the specification at meaningful checkpoints.
Validate both the website and a standard GBA emulator; mGBA is the reference target.
Commit coherent changes every 200–300 handwritten code lines when practical.
Commit smaller completed fixes or reviews at logical boundaries; count generated assets separately.
Do not pad code or reformat unrelated files to reach a commit-size quota.
Emerald parity requires user approval of comparison clips, not just passing build tests.
