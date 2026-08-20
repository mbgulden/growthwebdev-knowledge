---
name: prismatic-task-admission-smoke
description: End-to-end smoke test for the prismatic-gateway durable task admission API. Verifies auth, schema, policy permissions, worktree state, and idempotency replay. Use after rotating operator credentials, after editing the admission policy file, after worktree setup, or whenever a 5xx admission_policy_unavailable / schema_validation_failed / worktree_dirty needs to be debugged.
---

# Prismatic task admission smoke

Use this skill whenever you need to prove the
`POST /api/dashboard/task-admissions` endpoint is end-to-end functional
on a running gateway, or to debug the canonical failure modes.

## When this skill applies

- ✅ After rotating `operator-runtime` credentials in
  `/home/ubuntu/.prismatic/secrets/control-auth.json`.
- ✅ After modifying the admission policy file at
  `/home/ubuntu/.prismatic/policy/task-admission.json`.
- ✅ After provisioning a new worktree that should accept admissions.
- ✅ After restarting `prismatic-gateway.service`.
- ✅ When `POST` returns 503 `admission_policy_unavailable`, 422
  `schema_validation_failed`, or 422 `worktree_dirty`.
- ❌ DO NOT use this for readback-only checks (use `GET` directly with
  the bearer wrapper).

## The 6 tests

The smoke script (filename prefix `hermes-verify-gro-*`) runs six tests
in order. All must pass for a green smoke.

| # | Test | Pass criteria |
|---|---|---|
| T1 | GET `/api/dashboard/task-admissions?limit=20` | HTTP 200, body contains the prior task_id (`GRO-4628`) with `status=admitted` |
| T2 | POST fresh admission with unique `task_id` | HTTP 201, `ok=true`, `replayed=false` |
| T3 | POST replay (same `idempotency_key`) | HTTP 200, `replayed=true` |
| T4 | Policy file mode bits | `mode & 0o077 == 0` (must be `0o600` or stricter) |
| T5 | Bearer file mode bits | `mode & 0o077 == 0` |
| T6 | Worktree clean + HEAD/tree match | `git status --porcelain` empty, `HEAD` and `HEAD^{tree}` match the committed base |

## Canonical failure modes and fixes

### T1 fails with HTTP 401

The bearer token does not match what's in `control-auth.json`. Causes:

1. **Stale gateway after credential rotation.** Fix:
   `sudo systemctl restart prismatic-gateway.service` — the gateway
   reads `control-auth.json` once at startup.
2. **`control-auth.json` has extra keys.** Fix: ensure exactly
   `{actor, token_sha256, roles}` per credential (see
   `prismatic/gateway/control_auth.py:114`).
3. **Systemd drop-in missing.** Fix: ensure
   `/etc/systemd/system/prismatic-gateway.service.d/95-operator-auth.conf`
   sets `Environment=PRISMATIC_CONTROL_AUTH_FILE=...`.

### T1 returns 200 but the prior task_id is not in the list

Either (a) the prior admission never succeeded, or (b) it's an older
admission outside the `limit`. Increase `limit` or check the raw DB.

### T2 returns HTTP 503 `admission_policy_unavailable`

**Most common cause:** policy file mode is `0o644` or another value
with world/other permission bits set. The validator at
`prismatic/task_admission.py:_read_policy_bytes()` requires
`stat.S_IMODE(mode) & 0o077 == 0`.

**Fix:** `chmod 600 /home/ubuntu/.prismatic/policy/task-admission.json`.

Other 503 causes (rare):
- Policy file is a symlink
- Policy file is larger than 1 MiB
- Policy file changes mid-read (TOCTOU — should be impossible from
  here, but logged if it happens)

### T2 returns HTTP 415 `content_type_required`

The `Content-Type: application/json` header is missing. The body is
present but the validator rejects it.

**Fix:** add `-H "Content-Type: application/json"` to the curl args.

### T2 returns HTTP 422 `schema_validation_failed`

Schema is strict (`additionalProperties: false`). Common shape issues:

| Field | Constraint |
|---|---|
| `version` | integer `1` |
| `task_id` | `^[A-Z][A-Z0-9]{1,15}-[1-9][0-9]{0,9}$` (single dash, ≤10 digit suffix) |
| `base_commit` | `^[0-9a-f]{40}$` |
| `base_tree` | `^[0-9a-f]{40}$` |
| `task_file` | string 1-512 chars, **must be relative, no `..` or `.`** |
| `task_file_sha256` | `^[0-9a-f]{64}$` |
| `producer_identity` | `^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$` |
| `worktree` | absolute path string 1-1024 chars |
| `writer_cap` | integer `1` (not boolean — `True` is rejected) |
| `idempotency_key` | `^[A-Za-z0-9][A-Za-z0-9._:-]{31,127}$` (**32+ chars total**) |
| `created_at` | ISO 8601 with trailing `Z` |
| `status` | string `"admitted"` |

### T2 returns HTTP 422 `worktree_dirty`

The worktree's `git status --porcelain` is not empty. Untracked task
fixture files count as dirty.

**Fix:** `git add` and `git commit` the task file into the worktree
before posting.

### T2 returns HTTP 409 `task_already_admitted`

The `task_id` is already in the durable store from a prior admission.
Either (a) pick a fresh `task_id`, or (b) reuse the prior
`idempotency_key` to get a replay (HTTP 200 + `replayed=true`).

### T2 returns HTTP 409 `idempotency_conflict`

The `idempotency_key` was used previously with a different payload.
Either pick a fresh key or send the original payload.

### T3 returns HTTP 409 instead of HTTP 200 replayed=true

The same `idempotency_key` is replaying a payload that was rejected
earlier. The store only replays successful admissions. Pick a fresh
key.

### T4 fails (policy file world/other bits > 0)

`chmod 600 /home/ubuntu/.prismatic/policy/task-admission.json`. The
validator will refuse to load any policy file with bits set in
`0o077`.

### T6 fails (worktree dirty)

Commit the worktree's changes before posting. The validator does a
`git status --porcelain` before and after task-file hashing to detect
concurrent mutations.

## Pre-flight checklist

Before running the smoke:

```bash
# Confirm gateway is up and reachable
curl -sS -o /dev/null -w 'HTTP=%{http_code}\n' http://127.0.0.1:9000/healthz || true

# Confirm systemd drop-in is in place
sudo systemctl cat prismatic-gateway.service 2>&1 | grep -E 'PRISMATIC_CONTROL_AUTH_FILE|PRISMATIC_TASK_ADMISSION_POLICY_FILE' | head -5

# Confirm the running gateway has the env vars loaded
PID=$(pgrep -f 'prismatic.gateway.server' | head -1)
sudo cat /proc/$PID/environ 2>/dev/null | tr '\0' '\n' | grep -E 'PRISMATIC_(CONTROL_AUTH|TASK_ADMISSION)_' | sort -u
```

## Run the smoke

The smoke script and bearer wrapper live under `/tmp/`. Both are
retained across runs but are NOT committed anywhere.

```bash
# 1) Wrapper (one-time setup, persists across runs)
ls -la /tmp/hermes-verify-bearer.sh   # must exist + be executable

# 2) Smoke script (regenerate with a fresh timestamp each session)
python3 /tmp/hermes-verify-gro-4628-freshrun-<TIMESTAMP>.py

# 3) Expected output
# OVERALL: ALL PASS  (exit 0)
```

## Prerequisite skill

- `bearer-token-via-shell-substitution` — the bearer wrapper is what
  this skill builds on.

## Related OKF docs

- `prismatic-engine/docs/task-admission-control-plane.md` — API contract
- `prismatic-engine/docs/dashboard-control-auth.md` — credential model
- `prismatic-engine/docs/incidents/2026-08-09-gro-4628-task-admission-policy-permission.md` — full incident postmortem
- `prismatic-engine/okf/index.yaml` — `durable-task-admission` objective