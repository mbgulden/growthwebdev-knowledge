# HDE workspace / branch cleanup pattern — 2026-07

Use this as a concrete example for cleaning a live-ish product workspace without losing launch evidence.

## Trigger

Michael asked for Human Design Engine branch/worktree cleanup plus documentation cleanup so app/docs/site readers could easily find what they need.

## Pattern that worked

1. **Inventory first, mutate later.** Capture:
   - `git status --short`
   - current branch and HEAD
   - `git worktree list --porcelain`
   - local/remote HDE-related branches sorted by committer date
   - untracked artifact sizes/counts
2. **Classify before deleting.** Treat artifacts as:
   - private secret backups (`.env*`) → move to private archive, never print values
   - runtime state (`docker/data`, SQLite DBs) → archive outside repo
   - generated caches (`.astro`, `node_modules`) → archive or remove if reproducible
   - stale evidence reports → archive if superseded, do not silently delete
   - ambiguous docs/media/tests → archive, not discard
3. **Archive with manifest.** Use a timestamped archive outside the repo, e.g. `/home/ubuntu/work/_hde_cleanup_archive/<timestamp>/`, containing `manifest.txt`, `repo-artifacts/`, and restricted `secret-backups/`.
4. **Clean branches conservatively.** Delete only local branches that are mechanically superseded or integrated into the current pushed branch. Retain remote review branches for discoverability unless Michael explicitly asks to clean branches/remotes too.
   - If remote cleanup is in scope, first run `git push --dry-run origin --delete <branches...>` and only delete branches mechanically proven merged/superseded.
   - After deletion, verify each remote branch with `git ls-remote --heads origin <branch>` returning absent/gone.
   - Do not delete unmerged/ambiguous local branches just because they are old; report them as preserved/manual-review.
5. **Document a workflow map.** Commit a cleanup report that points to launch reports, runbooks, router scripts, canary/proof scripts, and coach-gate code.
6. **Update stale proof truthfully.** If a live watcher times out, record the timeout and keep launch status YELLOW instead of pretending proof exists.
7. **Verify the cleanup artifact itself.** For report-only changes, create `/tmp/hermes-verify-*` that parses JSON/Markdown, checks the archive exists, confirms removed clutter is gone from `git status`, and scans report text for token/API-key/DB-URL shaped secrets. Label as ad-hoc artifact verification.

## Pitfalls

- Do not `git clean -fdx` a live-ish workspace. Archive ambiguous work first.
- Do not commit `.env*`, DB dumps, Redis state, raw Telegram logs, or runtime customer data.
- Do not delete remote review branches during local cleanup unless explicitly asked.
- Do not call a launch report GREEN when the live Telegram watcher timed out or never saw documents.
- Do not let generated `__pycache__` dirt linger after Python verification; restore it before final status.
