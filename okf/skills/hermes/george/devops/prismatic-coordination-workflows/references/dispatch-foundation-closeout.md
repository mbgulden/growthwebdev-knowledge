# Dispatch Foundation Closeout Checklist

Use this reference when a Prismatic session asks whether George/AGY dispatch is efficient or working end-to-end, or after a supervisor merge that must be promoted into runtime operations.

## Layered dispatch audit

Treat dispatch readiness as a chain, not a single green light. When Michael asks whether George is efficient or whether Linear/AGY/Fred dispatch is “actually working,” report each layer separately rather than collapsing the answer into pass/fail:

1. **Gateway ingress** — prove the webhook/API process is alive with a local health check and relevant route checks.
2. **Bus database identity** — confirm the consumer is reading the same SQLite bus that the gateway writes.
3. **Consumer checkpoint sanity** — compare the consumer `last_rowid`/state file against the current database `max(rowid)`. If `last_rowid` is ahead of `max(rowid)`, the service may be running but blind to current events.
4. **Consumer query contract** — inspect whether it filters `rowid > last_rowid` and `processed = 0`; a stale/ahead checkpoint can create a silent no-op loop. For the Prismatic bus `events` table, prefer `rowid`, `dedup_key`, `topic`, `payload_json`, `ts`, and `processed`; do not assume columns named `id` or `created_at` exist.
5. **Repository state versus remote main** — read both local `HEAD` and `origin/main`. A local repo behind remote `main` can make handoff/control-state output stale even after a PR is merged.
6. **GitHub PR/CI/merge truth** — read PR state, merge SHA, and check rollup from GitHub. Treat this as merge proof only, not runtime proof.
7. **Immutable release/runtime truth** — compare systemd `WorkingDirectory`/effective release SHA with the GitHub merge SHA. A merged PR is not live protection if production still runs a pre-merge immutable release.
8. **Operational supervisor bytes** — compare the live profile/wrapper script used by systemd to merged current-main/release bytes. Profile-script overlays can lag behind the repository.
9. **Active producer truth** — check for live AGY supervisors/children, but avoid counting the inspection command itself as a producer. Prefer exact process patterns, parent/child inspection, or filtering out the current shell command.
10. **Child runtime environment** — verify supervisor HOME/state and child AGY auth HOME separately.
11. **Exact task file consumed** — hash/check the actual sandbox `AGY_TASK.md` before allowing a producer to run.
12. **Completion semantics** — replay the real failure packet against the operational supervisor, not just against a development worktree.
13. **Completed-work integration truth** — distinguish records visible in dashboard/API from real writeback. `linear_dry_run=True`, `linear_posted=False`, or `github_pr_present=False` means the completed-work path is only a dry-run preview, not an end-to-end Linear/PR workflow.
14. **Dry-run canary** — run a no-agent/no-Linear-write dispatch canary before resuming real generic dispatch.
15. **One producer only** — after repair, restart with one exact issue at cap 1 and independently review the candidate before launching another task.

## Efficiency audit signals

Do not equate many monitors with useful work. When Michael asks whether George is efficient, quantify and classify:

- Active producers/slices versus watcher/reporting jobs.
- No-agent change-only monitors versus LLM-driven reviewers.
- Empty-queue LLM reviewer cadence; convert to event-triggered or script-gated if it runs repeatedly with no work.
- Handoff size/staleness; keep `PRISMATIC_CURRENT_HANDOFF.md` current and compact, with history archived to references/reports.
- Stale watcher jobs from completed slices; pause or retarget them after merge/deploy.

## Closeout packet shape

```text
COMMAND=<gateway health; SQLite checkpoint/max rowid; systemd ExecStart/env; live supervisor hash; replay/canary>
RESULT=<PASS|PARTIAL|BLOCKED>
LOG=<path or grouped live outputs>
SCOPE=dispatch foundation: gateway, bus, consumer, operational supervisor, exact task source, dry-run canary
AD_HOC_OR_CANONICAL=ad-hoc operational audit
NOT_CLAIMING=generic dispatch readiness; cap increase; producer completion; deploy/merge unless separately authorized
MARKER=PRISMATIC_DISPATCH_FOUNDATION_CLOSEOUT_<OK|REQUIRED>
```

## Common overclaim traps

- `systemd ActiveState=active` does not prove the consumer is consuming current events.
- A merged GitHub PR does not prove the runtime/profile script imports the fix.
- GitHub CI green proves the submitted diff passed CI; it does not prove the local checkout, control-state JSON, handoff, or immutable runtime have advanced to that SHA.
- A clean Linear description/comment does not prove AGY consumed that task text.
- Gateway health does not prove dispatch; it only proves ingress.
- A queue or completed-work API with rows does not prove real Linear/PR automation when all records are dry-run or missing downstream artifacts.
- A `pgrep` result can include the audit command itself; verify parent/child identity before reporting active producers.
- Cap-1 recovery from a real incident is not cap-2 readiness; require controlled recovery drills and exact-artifact candidate review first.
