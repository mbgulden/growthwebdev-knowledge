# Governance Dashboard Public / Live Verification Hardening

Use this reference when adding or maintaining the unified dashboard contract verifier.

## Goal

One portable verifier should answer whether the Prismatic Engine governance dashboard is live, canonical, API-backed, safe-control wired, and free of scoped mock/fake fallback.

## Core artifacts

```text
prismatic/dashboard_contracts.py
GET /api/gateway/dashboard/contracts
prismatic-dashboard-verify
```

## CLI examples

Source-only dashboard contract check:

```bash
python -m prismatic.dashboard_contracts --json --section all
```

Portable isolated live smoke:

```bash
python -m prismatic.dashboard_contracts --json --section all --isolated-state --start-local-gateway
```

Installed console entrypoint:

```bash
prismatic-dashboard-verify --json --section all --isolated-state --start-local-gateway
```

Public classification when authorized/reachable:

```bash
prismatic-dashboard-verify --json --section all --public-url https://prismatic.growthwebdev.com
```

## Contract manifest

`GET /api/gateway/dashboard/contracts` is read-only and returns:

```text
source
generated_at
dashboard_route
sections
required_endpoints
safe_controls
forbidden_patterns
verification_notes
```

Each section contract includes:

```text
id
name
dashboard_markers
fetches
actions
endpoints
detail_endpoints
control_endpoints
required_states
forbidden_patterns
evidence
```

## Sections covered

```text
agents
queue
timeline
workspaces
skills
agent_context
foundation
merge
quota
dispatcher_recovery
```

Some contracts are API-only if the dashboard has no visible section yet. Keep those in the manifest/endpoints but do not require nonexistent dashboard HTML markers.

## Safety model

Browser/dashboard controls must never directly shell out to:

```text
systemctl
git
gh
docker
agent CLIs
```

Safe controls should be explicit, allowlisted, audit-only unless a safe in-process mutation exists, timeline/event backed, and return empty `stdout` / `stderr` if the dashboard expects command-style responses.

Minimum safe-control proof:

```text
queue retry -> QueueControl timeline + stdout/stderr empty
queue purge -> QueueControl timeline + stdout/stderr empty
```

## Isolated fixture pattern

Use temp state, never real user state:

```text
PRISMATIC_STATE_DIR=/tmp/...
PRISMATIC_AGENT_REGISTRY=/tmp/.../agent_registry.json
PRISMATIC_MERGE_STATE_PATH=/tmp/.../merge_state.json
```

Seed run records that cover:

```text
active
idle
queue_starved
awaiting_user_feedback
completed_recently
failed retryable
dead_letter
skipped
```

## Verification stages

A focused `/tmp/hermes-verify-*.py` should check:

```text
changed paths exist
py_compile changed Python files
node --check extracted dashboard JS
focused pytest passes
python -m prismatic.dashboard_contracts --json --section all --isolated-state --start-local-gateway passes
GET /api/gateway/dashboard/contracts manifest shape
/dashboard canonical Prismatic Hub dashboard
QueueControl events for retry/purge
empty stdout/stderr for retry/purge
temp verifier removed
temp state removed
temp gateway killed
```

Report as ad-hoc targeted verification, not suite green, unless the full canonical suite was run.

## Public smoke classification

Public URL checks should classify, not guess:

```text
reachable
access_blocked
wrong_surface
unavailable
skipped
```

Do not bypass Cloudflare Access unless explicitly authorized through the Cloudflare Access remediation workflow.
