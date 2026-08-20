# HDE dirty staging checkpoint pattern — 2026-07

Use when HDE staging is running live-ish Telegram/runtime behavior from a dirty worktree and Michael asks to checkpoint before public traffic.

## Durable lesson

Checkpointing is not the same as `git add .`. HDE staging often contains a mix of valuable runtime changes, generated artifacts, stale reports, secrets, and runtime state. Preserve the useful runtime work on a `ned/` branch while refusing to commit raw secrets or caches.

## Safe sequence

1. Inspect branch/status/diffs first:
   - `git branch --show-current`
   - `git status --short`
   - `git diff --stat`
   - targeted `git diff -- <tracked paths>`
2. Inspect untracked file sizes and purpose before staging:
   - `.env*` backups are usually secret-bearing; do not commit.
   - `docker/data/` is runtime state; do not commit.
   - stale RED launch reports are not current evidence; leave untracked unless rewritten/sanitized.
   - visual snapshots/media/docs may be intentional, but inspect size/purpose before adding.
3. Switch to a `ned/` branch before committing. Never checkpoint directly on `staging`, `main`, or `deploy-fresh`.
4. Lock tracked and new commit candidates with the swarm lock tool before staging.
5. Stage only safe intentional files: runtime scripts, canary/watchdog scripts, sanitized docs, sanitized reports, cue libraries, orchestrator config invariants.
6. Run `git diff --cached --check` and a staged secret scan before commit. Redact tokens; do not print values.
7. Run real verification before commit:
   - Python compile for changed scripts.
   - `npm run build` when the HDE repo changed.
   - `python3 scripts/hde_guest_canary.py --guest-id 23 --pretty` for guest-runtime proof.
   - service/container health checks for router and guest.
8. Commit with Ned prefix: `[Ned] ... (#ISSUE)` or `#NO-ISSUE` if no issue exists.
9. Unlock files after commit.
10. If the push is blocked by lane guard because docs or other non-Ned paths are included, do not force. Preserve a local `git bundle` and report the branch/commit/blocked paths. Then either split the branch by lane or hand the bundle/commit to the owning lane/orchestrator.

## Reporting shape

Report:
- branch name,
- commit SHA,
- files committed,
- files intentionally left untracked and why,
- verification commands/results,
- whether push succeeded or was blocked,
- local bundle path if push was blocked.

## Pitfalls

- Do not commit `.env` backups, bot tokens, database URLs, Redis URLs, SMTP passwords, API keys, cookies, session files, or raw connection strings.
- Do not treat a stale launch report as fresh proof.
- Do not commit Redis dumps or runtime Docker state.
- Do not assume a push failure means the checkpoint is lost; create a Git bundle as a portable backup.
- Do not claim live Telegram proof from server-side canary or checkpoint verification alone; live Telegram media proof still requires a real tester message.
