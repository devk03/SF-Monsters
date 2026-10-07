# Project instructions

Be very concise and always ask for permission on db migrations and none on read operations. Never drop our dbs without asking.

NEVER run `rm` in any form. Do not ask for an exception; use a non-destructive alternative or have the user remove files manually.

No merging prs without asking me.

Commit frequently.

## Active implementation workflow

Always read `docs/game-spec.md` as the source of truth for scope and acceptance.
Update its active MVP progress section at meaningful implementation checkpoints.
Validate both the website and a standard GBA emulator; mGBA is the reference target.
Commit coherent changes around 500–700 changed lines when it makes sense.
