# 2026-07 Prismatic/Jules PR cleanup example

## Context
Michael asked Ned to review PRs, especially Jules/Jules-like PRs, and then follow the golden path until everything Ned could handle was handled or assigned to AGY.

Repo inspected: `mbgulden/prismatic-engine`.

Initial live inventory:
- 126 open PRs.
- Bases: `main` 58, `deploy-fresh` 56, `ned/pwp-ai-theme-master-plan` 8, plus stacked feature bases.
- Mergeability: 89 mergeable, 16 conflicting, 21 unknown in the first capped view; later full list had 126 open.
- Failed checks: plugin load gate failures on current PRs plus old failed PR cluster (#14–#28).

## Actions taken

### Closed as no-op / stale / superseded / unsafe raw merge
Closed with explanatory PR comments:

- #2 — old `[Jules] Deploy pre-push hook...`; conflicting and superseded by current Ned git push guard.
- #12, #13 — `.env`/`.venv_dev` ignore coverage already present on current `main`; no clean extraction needed.
- #100 — zero changed files; no-op.
- #101, #102 — stale/conflicting mega-diffs with broad unrelated file churn and sensitive-looking config paths.
- #103, #104/#111 cluster partial — duplicate/supersedence supervisor heartbeat/result cluster handling; #104 left for AGY comparison, #103/#111 closed.
- #105 — explicitly superseded/finalize-style and conflicting.
- #107 — stale/conflicting lifecycle mega-diff.
- #109 — included `prismatic_state/event_router.db`; unsafe raw merge.
- #110 — explicitly superseded API gateway feature and conflicting.
- #141 — broad stale/conflicting queue-cleanup mega-PR; unsafe raw merge.
- #199 — broad stale/conflicting PWP token override PR with unsafe raw-merge profile.

### Routed to AGY
Created Linear issues:

- `GRO-3790` — `[AGY] Extract/close stale Jules-like PR backlog`.
  - Labels: `agent:agy`, `dispatch:ready`, `prismatic-engine`.
  - Included remaining source PRs requiring extract/close synthesis: #181, #108, #104, #106, #116, #204, old failed/conflicting cluster (#3, #8, #9, #11, #14–#21, #25, #26, #28, #32), plus addendum for #141/#199/#204.
  - Instruction: do not raw-merge stale/conflicting agent PRs; extract clean scoped deltas only.

- `GRO-3791` — `[AGY] Prismatic PR merge-train triage after stale cleanup`.
  - Labels: `agent:agy`, `dispatch:ready`, `prismatic-engine`.
  - Purpose: ordered review/merge train for the 91 mergeable PRs and failed-check blockers after stale cleanup.

### Attempted extraction blocked by lock
PR #181 (`[Ned] Jules host-path pre-screen`) looked useful and focused:
- changed `prismatic/dispatcher.py`, `prismatic/tests/test_jules_host_path_routing.py`, and `scripts/reports/GRO-3570.md`;
- tests passed on the original PR;
- current PR was conflicting.

Ned attempted the clean extraction path but `prismatic/dispatcher.py` was actively locked by Fred. Correct action: do not break lock; route to AGY / leave source comment. This avoids concurrent agent edits on dispatcher.

## Useful patterns learned

### Close comment pattern
Use a short, explicit disposition comment:

```md
Closing as PR cleanup: <reason>. Golden-path disposition: do not merge raw; any still-useful delta should be re-extracted into a clean scoped PR with focused verification.
```

### AGY routing issue body pattern
Include:

- exact PR numbers + URLs;
- why each is included;
- instruction not to raw-merge stale/conflicting branches;
- extraction rules for unsafe files;
- verification requirement;
- timestamp and source of triage.

### Dangerous raw-merge signals
- broad unrelated file churn;
- `*.pem`, `*.key`, credential-like config paths;
- `*.db`, `prismatic_state/*`, generated state artifacts;
- huge diffs that exceed GitHub API diff limits;
- title/body says `Finalize`, `superseded`, or duplicate/validation-only;
- branch names with long numeric generated suffixes.

### CLI pitfalls
- `gh pr diff --stat` may not exist. Use `gh pr view --json files` or `gh pr diff --name-only`.
- `gh search prs --json` does not provide every field available from `gh pr list`; use repo-local `gh pr list` for mergeability/base/head analysis.
- Large PR diffs can fail with GitHub API `diff exceeded maximum files/lines`; classify first from file lists.

## Verification from the session
After cleanup:
- open `prismatic-engine` PRs: 126 → 112;
- mergeable: 91;
- conflicting: 21;
- failed checks: 14;
- AGY routing issues `GRO-3790` and `GRO-3791` existed in Todo with `agent:agy`, `dispatch:ready`, `prismatic-engine`.

## Future use
When Michael asks to clean PRs, especially Jules/agent PRs, start from the class-level process in `github-pr-backlog-hygiene` and use this reference as the concrete pattern for:
- safe closure;
- AGY routing;
- lock-boundary handling;
- avoiding raw merge of stale generated agent branches.
