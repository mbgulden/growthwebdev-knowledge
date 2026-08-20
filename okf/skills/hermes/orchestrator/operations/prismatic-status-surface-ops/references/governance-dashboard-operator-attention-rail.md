# Governance dashboard operator attention rail pattern — 2026-07

## When to use

Use when the Prismatic governance dashboard has working underlying endpoints but the default view still forces operators to hunt across tabs to know what needs action.

## Pattern

1. Do a route/fetch matrix first. If the main endpoints return 200, treat the next slice as operator-signal ranking rather than another compatibility endpoint fix.
2. Add a single default-view attention rail that answers: **what should the operator inspect first?**
3. Feed the rail from existing live endpoints rather than mocks/fallbacks:

```text
/api/gateway/dispatcher/status
/api/gateway/recovery/status
/api/gateway/webhooks/queue
/api/quota
/api/gateway/merge/status
/api/gateway/timeline?limit=20
```

4. Rank signals in action order, for example:

```text
dispatcher silent stall
→ queue depth
→ recovery heartbeat/live/DLQ issue
→ stale quota snapshot
→ merge backlog
→ timeline warnings/errors
→ all-clear fallback
```

5. The rail should include:

- badge (`ACTION`, `QUEUE`, `CHECK`, `STALE`, `MERGE`, `SIGNALS`, `CLEAR`);
- direct title;
- one sentence of operator guidance;
- action button to the most relevant tab;
- compact reason chips.

## Verification

Because the dashboard uses inline JavaScript, extract inline script blocks and run:

```bash
node --check /tmp/hermes-dashboard-inline-check.js
```

Also verify:

- `origin/deploy-fresh:prismatic/gateway/templates/dashboard.html` contains the rail markers;
- local `/dashboard` serves the canonical operator dashboard with the rail;
- every endpoint used by the rail returns 200 locally;
- browser DOM proof shows the rail populated after async loading;
- browser console has 0 JS errors;
- PR merge is visible on `origin/deploy-fresh` after merge;
- no unmerged diff remains after merge.

Required stale-guard style:

```text
AD_HOC_VERIFICATION: PASS
scope: Fresh stale-guard verification for changed dashboard template operator attention rail; ad hoc targeted, not full suite green
changed_paths_checked:
- /home/ubuntu/work/prismatic-engine/prismatic/gateway/templates/dashboard.html
canonical_test_lint_build: node --check extracted inline dashboard JavaScript
cleanup=PASS removed /tmp/hermes-verify-xxxx.py
```

## Pitfalls

- Do not stop at route 200s when the user wants a helpful control plane; surface the highest-signal next action.
- Do not rank from synthetic/mock fallback data.
- Do not claim suite green from the rail verifier.
- If the stale verifier keeps resurfacing, emit the exact changed path in `changed_paths_checked` and name the inline JS `node --check` as the focused lint/build equivalent.