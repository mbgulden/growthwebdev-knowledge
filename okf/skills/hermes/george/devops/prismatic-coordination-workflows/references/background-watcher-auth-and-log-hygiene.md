# Background watcher auth and log hygiene

Use this reference when George starts bounded read-only watchers for PR/head/status changes during Prismatic coordination, especially from Telegram/Hermes sessions where foreground shell state and background process state may diverge.

## Lesson

A watcher can be logically read-only and still fail operationally if the background shell does not receive the credential/env state that a foreground `gh` command used successfully. Treat watcher startup as unproven until the first authenticated poll is visible in the watcher log.

## Safe pattern

1. Keep the watcher read-only: use `gh api` / `gh pr view` only; no comments, merges, labels, branch deletion, deployments, Linear writes, or service actions.
2. If a foreground authenticated `gh` call works but the background worker reports `gh auth login`/missing token, pass auth explicitly without printing the token:
   - create a temporary file with `umask 077` / mode `0600`;
   - write `gh auth token` into it;
   - in the watcher, export `GH_TOKEN="$(<token_file)"`;
   - add `trap 'rm -f <token_file>' EXIT`.
3. Verify startup with a direct poll/readback of the watcher log. Do not claim monitoring is active until at least one authenticated poll records the target state/head.
4. If a failed watcher was started before the fixed watcher, terminate/contain stale processes by exact command marker before trusting the shared log.
5. Distinguish active stale processes from zombies: a `/proc/<pid>/stat` state of `Z` means non-executing process-table bookkeeping. It cannot poll further, but its parent may not have reaped it yet.
6. If stale failed watcher output contaminated the log, remove or clearly bracket those stale pre-fix lines only after proving no stale writer remains active. Keep the successful authenticated poll lines and the final log path.

## Compact proof fields

```text
WATCHER=<process/session id>
MODE=read-only bounded
FIRST_AUTH_POLL=<timestamp/state/head>
STALE_WATCHERS=<none|contained|zombie-only>
LOG=<path>
NOT_CLAIMING=<merge/comment/deploy/Linear/service mutation>
```

## Pitfalls

- Do not treat “background process started” as proof the watcher is authenticated or polling.
- Do not paste or expose tokens while debugging watcher auth.
- Do not let multiple watchers write to the same log unless you intentionally bracket their outputs by watcher id.
- Do not capture a one-time credential setup failure as a durable tool limitation; capture the safe explicit-auth watcher pattern instead.
