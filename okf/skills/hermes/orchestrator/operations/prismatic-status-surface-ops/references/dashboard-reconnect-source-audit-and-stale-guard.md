# Dashboard reconnect source audit + exact stale-guard proof

Use this when Michael provides a large dashboard/source audit digest and asks for a quick reconnect/preservation pass before returning to another project.

## Goal

Turn a sprawling source audit into a durable, execution-sized map without merging, resetting, or replacing the current dashboard shell.

## Worked pattern

1. **Pause the prior lane explicitly.** If another branch/project is active, leave it untouched and create a separate clean worktree/branch from the current dashboard base.
2. **Create a clean audit worktree.** Example:

```bash
cd /home/ubuntu/work/prismatic-engine
git fetch origin --quiet
git worktree add -B feature/fred-dashboard-reconnect-source-audit /home/ubuntu/work/prismatic-dashboard-reconnect-audit origin/main
```

3. **Anchor first.** Compare current clean branch, active prior branch, and durable runtime. For dashboard reconnect work, prove whether these are byte-identical before mining older sources:

```text
/home/ubuntu/.prismatic/runtime/prismatic-engine/prismatic/gateway/templates/dashboard.html
/home/ubuntu/.prismatic/runtime/prismatic-engine/prismatic/gateway/server.py
/home/ubuntu/work/prismatic-dashboard-reconnect-audit/prismatic/gateway/templates/dashboard.html
/home/ubuntu/work/prismatic-dashboard-reconnect-audit/prismatic/gateway/server.py
```

4. **Inspect A/C/B source buckets by evidence, not score alone.** High score means inspect first, not integrate. Dirty worktrees are evidence only.
5. **Classify sources into donor types:**
   - current shell anchor: compare against, do not replace;
   - UX/plugin reference: mine ideas only, especially if static/mock-heavy;
   - concrete integration candidate: small bounded diff with tests/reports;
   - polluted/archive fallback: inspect only for named missing tab/adapter.
6. **Write a source-map artifact** rather than applying code immediately. Include:
   - anchor table;
   - source findings;
   - non-candidates and red flags;
   - one next integration candidate;
   - exact next command plan;
   - non-claims.

## Useful findings from the July 2026 reconnect pass

- Current durable runtime/main dashboard already superseded older warm-cache/dashboard shells; older shells still contained `mockAgents`, `mockWorkspaces`, and `mockSignals`.
- `prismatic-hub-ui` contained valuable Hermes plugin UX prototypes, but several were static/mock-heavy (`Completed UI mockup`, fake event rows, hardcoded local fetches). Treat as inspiration, not a shell donor.
- `kai-gro-3355-resources-panel` was the best next bounded candidate because it added a Resources/budget-caps slice (`prismatic/budget_caps.py`, `GET/POST /api/quota/caps`, dashboard controls, dispatcher guard, tests/report) without requiring shell replacement.
- Broad dirty worktrees with venv junk or many deletions (for example native-crons design branches) should be fallback only despite tempting names.

## Exact stale-guard proof pattern

When Hermes stale guard lists both a real changed artifact and an old `/tmp/hermes-verify-...py` path, the verifier must cover **both**:

```text
changed_paths_checked=/path/to/real/artifact.md,/tmp/hermes-verify-old-name.py
stale_temp_path_absent=true
cleanup=PASS
```

Do not merely say the old temp path is irrelevant. Remove the exact stale temp path, create a fresh verifier using `tempfile.mkstemp(prefix='hermes-verify-...', dir='/tmp')`, run it, delete it, and assert the stale path is absent.

Minimum summary shape:

```text
COMMAND=tempfile-created /tmp/hermes-verify-dashboard-reconnect-final-*.py
RESULT=PASS
LOG=/tmp/fred-dashboard-reconnect-source-audit-verify.log
SCOPE=doc-only dashboard reconnect source audit artifact + stale temp-path absence + source existence + anchor equality + candidate evidence
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=resources_budget_caps_merged,dashboard_shell_changed,archive_sources_exhausted,agy_autopilot_phase2_resumed
cleanup=PASS
MARKER=DASHBOARD_RECONNECT_SOURCE_AUDIT_OK
```

## Pitfalls

- Do not apply source audit candidates in the same pass unless Michael explicitly asks for implementation. The first deliverable is a map.
- Do not let a dirty source branch become the new base. Recreate the small candidate on a fresh branch later.
- Do not treat plugin prototypes as real adapter restorations when they carry static data or hardcoded localhost fetches.
- Do not leave source-map artifacts stranded in temporary worktrees; commit and PR the doc-only artifact if useful.
- Do not claim suite green for doc/source assertion verifiers; label them ad hoc targeted.
