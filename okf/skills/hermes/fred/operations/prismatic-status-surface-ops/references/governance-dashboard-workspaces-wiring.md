# Governance Dashboard Workspaces Wiring Pattern

Use this reference when the Prismatic governance dashboard has many half-connected panels and Michael asks where to start wiring.

## Selection heuristic

Start with the section that turns other surfaces into navigable context. In the July 2026 dashboard pass, that was **Workspaces** because it connects:

```text
Golden Thread ventures
→ local repo checkouts
→ git branch / dirty status
→ swarm locks
→ dashboard rows
→ register context action
→ optimize workspace action
```

This is higher leverage than polishing isolated panels because it answers: where does this thing live, what state is it in, and what action can an operator safely take?

## Signs a dashboard section is underwired

Search dashboard templates for:

```text
mockWorkspaces
mockSignals
mockSkills
placeholder
href="#"
buttons without onclick/fetch
render*View using hardcoded arrays
```

Then compare against existing backend primitives before inventing new storage:

- Golden Thread: `/home/ubuntu/work/project-registry.json`
- swarm locks: `/locks`, `/locks/stale`, `prismatic.lock._read_locks`
- run records: `/runs`, `AgentRunRecordStore`
- event bus / websocket broadcaster
- workspace optimizer: `prismatic.workspace_optimizer.optimize_workspace`
- skills registry: `prismatic.skills`

## Workspaces API contract that proved useful

Add a small adapter rather than embedding paths in dashboard JS:

```text
prismatic/workspaces.py
GET  /api/workspaces
POST /api/workspaces/register
POST /api/workspaces/optimize
```

The adapter should combine:

- Golden Thread ventures and repo list
- local checkout discovery under `/home/ubuntu/work`
- git branch and dirty status
- file count / approximate size
- swarm lock active/stale counts per workspace
- local operator-registered contexts in `PRISMATIC_STATE_DIR/dashboard_workspaces.json`

Statuses used:

```text
connected     exists, clean, no stale locks
dirty         git working tree has changes
stale-locks   at least one lock heartbeat stale
missing       registry points to a checkout not present locally
error         registry read/parse failed
```

## Dashboard wiring rules

- Remove hardcoded workspace arrays entirely; do not keep mock data as fallback unless explicitly marked fixture-only.
- Homepage workspace summary should fetch `/api/workspaces` and show the top contexts.
- Workspaces tab should show real registry rows, not only lock rows.
- `+ Register Context` should call `/api/workspaces/register`.
- Per-row `Optimize` should call `/api/workspaces/optimize` and then refresh the table.
- Use `data-*` attributes for dynamic paths in inline handlers; avoid interpolating raw paths inside quoted JavaScript strings.
- If the checkout has a dashboard template but no HTML route, wire canonical `/` and `/dashboard` to serve it before claiming UI wiring is reachable.

## Verification pattern

Create `/tmp/hermes-verify-*.py` and report as ad-hoc targeted verification, not suite green.

Verifier should check:

```text
changed paths exist
py_compile server/workspaces/tests
focused pytest for workspace API
mockWorkspaces absent
fetch("/api/workspaces") present
register/optimize fetches present
/ and /dashboard serve canonical template
real project-registry smoke returns venture_count/workspace_count/status_counts
isolated PRISMATIC_STATE_DIR register/list/optimize paths pass
cleanup removes verifier and temp state
```

For live UI/API smoke, starting a temporary gateway on a non-production port and hitting `/dashboard` + `/api/workspaces` is useful, then kill the temp process.