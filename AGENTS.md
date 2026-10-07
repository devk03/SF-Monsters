# Project instructions

Be very concise.

## Authorization and safety

- Always ask permission for database migrations. Read operations need none.
- Never drop databases without asking.
- NEVER run `rm` in any form. Do not ask for an exception; use a non-destructive
  alternative or have the user remove files manually.
- Do not merge PRs without asking the user.
- Commit after each approximately 300–500 changed lines, with coherent diffs.
- Smaller commits are appropriate for initial setup or completed small changes.
- Do not pad changes or split working code merely to meet a line count.
- Verify important changes and stage explicit files before committing.

## Agent orchestration

For complex tasks where independent parallel work materially improves speed
or quality, keep the desktop task as coordinator and use subagent orchestration.

- Use native Codex subagents for ordinary parallel lanes and the installed
  `delegate-secondary-codex` skill for at least one suitable independent lane
  on the separately authenticated account.
- Prefer bounded read-heavy exploration, review, triage, research, and test analysis.
- Do not delegate trivial work or create redundant work to consume usage.
- Default the secondary account to read-only.
- Pass compact task briefs; workers inspect the repository and applicable instructions.
- Never let agents edit the same checkout concurrently. Parallel write lanes
  require separate Git worktrees and non-overlapping ownership.
- Wait for requested workers, verify important findings, and return one
  consolidated result rather than raw intermediate output.
- For recurring secondary-account work, use a stable persistent thread keyed
  by repository, branch, and worker role. Keep one-shot work ephemeral and
  start fresh when the objective or role changes materially.
- If the secondary account is unavailable, report it clearly. Do not silently
  replace its lane with additional primary-account workers.
- Delegation does not expand authorization for migrations, destructive actions,
  commits, publication, pull requests, or other external changes.
