# Profile-safe cron wrapper + registry shape drift — 2026-07

## When this applies

Use this pattern when a Hermes no-agent cron is surfaced by Tier-1 Silent Failure Watchdog and the root cause is either:

- the scheduler rejects an absolute script path outside the active profile `scripts/` directory, or
- a durable JSON source changed shape and a cron wrapper assumes one rigid type.

## Pattern

### 1. Recover exact failure output first

Read the latest cron output file before editing. Two useful examples:

- `Blocked: script path resolves outside the scripts directory (...)`
- `AttributeError: 'str' object has no attribute 'get'` from code assuming a dict where the registry currently stores a string.

### 2. For blocked absolute scripts, create a profile-local wrapper

Hermes no-agent cron scripts should resolve under the active profile scripts directory. If the real workload lives elsewhere, add a small wrapper under:

```text
/home/ubuntu/.hermes/profiles/orchestrator/scripts/<job_name>.py
```

The wrapper should:

- call the canonical project script with an explicit `cwd`
- use a bounded timeout
- parse/validate stdout instead of blindly passing it through
- write a deterministic artifact when useful
- print a compact JSON success payload

Then update the cron to use the relative wrapper name, not the absolute external path.

### 3. For registry shape drift, accept durable variants

If a registry field can historically be either a dict or a scalar string, make the reader tolerant:

- `dict` path: preserve the existing structured summary
- non-empty scalar path: emit a compact fallback line such as `Last sync: <value>`
- malformed/unreadable path: return a warning string, not a traceback

Do not rewrite the entire registry just to satisfy one reader.

### 4. Verification

Create a fresh `/tmp/hermes-verify-*` script that checks:

- `py_compile` for changed Python files
- isolated fixture for both registry shapes
- wrapper foreground run returns JSON and writes expected artifact
- Tier-1 watchdog dry-run/no-linear reports `silent_failures=0`
- verifier and scratch workdir are removed

Report as **ad hoc targeted verification**, never full suite green.
