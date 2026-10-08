# Project instructions

Be very concise and always ask for permission on db migrations and none on read operations. Never drop our dbs without asking.

NEVER run `rm` in any form. Do not ask for an exception; use a non-destructive alternative or have the user remove files manually.

No merging prs without asking me.

Commit frequently.

Never start monitors that do not end within under two hours. Do not create indefinitely recurring jobs. Every monitor needs a finite end condition, including a time limit when appropriate.

Do not use GitHub workflow credits pointlessly. Do not run a GitHub workflow on every pushed commit. Use local checks for routine changes; GitHub Actions stays manual-only.
