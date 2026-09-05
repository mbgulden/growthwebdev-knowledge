---
type: Standard
title: Swarm Lockfile Dual-Format Spec + Sweeper Detector Discipline
description: Canonical format contract for ~/.antigravity/swarm_locks.json (Lightbringer dict leases + legacy list) and the swarm.js CLI that operates it, plus the anti-pattern rule that sweep detectors must never parse prose/error output for counts.
resource: okf/standards/swarm-lockfile-dual-format-spec.md
tags: [standard, swarm, locks, ned, infra-sweep, cron, detector, false-positive]
timestamp: 2026-09-05T05:45:00Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/swarm-lockfile-dual-format-spec.md
last_verified: 2026-09-05
verified_by: ned
status: current
---

# Swarm Lockfile Dual-Format Spec + Sweeper Detector Discipline

**Status:** Canonical (2026-09-05)
**Audience:** All agents that touch file locks or write sweep/alert detectors (Ned, Kai, AGY, Fred, Lightbringer/Antigravity)
**Incident that motivated this:** 2026-09-05 phantom stale-locks false-red in the daily infra sweep (see "Background incident" below)

---

## 1. The lock file: `~/.antigravity/swarm_locks.json`

Two writers coexist on this file. **Both formats are valid; the reader must
accept both and the writer must preserve whichever format it found.**

### Format A — dict (Lightbringer Antigravity SwarmLockManager)

```json
{
  "file:<repo-relative-path>": {
    "lease_id": "uuid",
    "resource": "<repo-relative-path>",
    "holder": "<agent name, e.g. 'Lightbringer Antigravity'>",
    "created_at": "ISO-8601",
    "expires_at": "ISO-8601",
    "ttl_seconds": 1800,
    "acquisition_count": 1,
    "idempotency_key": "<holder>:<path>:<ms>",
    "metadata": { }
  }
}
```

- Key convention: `file:<path>`.
- **A lease is active iff `expires_at` is in the future.** A past
  `expires_at` means the lock self-expired — it is NOT contention. Never
  treat a foreign stale lease as a blocker; read `expires_at` first.
- Default TTL 1800s (30 min); `heartbeat` extends `expires_at` by the
  lease's own `ttl_seconds`.

### Format B — legacy list (original swarm.js, pre-2026-09-05)

```json
[
  { "path": "<path>", "agent": "<name>", "heartbeat": <epoch-ms> }
]
```

- Stale iff `now - heartbeat > 5 * 60 * 1000` ms (5-min TTL).
- Retained for compatibility with older tooling/notes; new writers should
  prefer Format A when the file is already a dict.

### Format-preservation rule

A tool that writes the file **must not change its top-level shape**.
swarm.js detects the on-disk shape on read and writes it back in the same
shape. This is what lets Ned and Lightbringer share the file safely.

---

## 2. The CLI: `node /home/ubuntu/.antigravity/swarm.js`

```
swarm.js lock <path> [agent]      # acquire; reject (exit 1) if foreign ACTIVE lease
swarm.js unlock <path> [agent]    # release own lock; idempotent on dict format
swarm.js status                   # TSV: ACTIVE|STALE<TAB>path<TAB>agent<TAB>ts
swarm.js heartbeat <path> [agent] # extend TTL; exit 1 if no own lease
```

- `status` output is **machine-parseable TSV** — field 1 is `ACTIVE` or
  `STALE`, field 2 the path, field 3 the holder, field 4 the timestamp.
  Empty registry prints `No active locks.`
- Agent defaults to `ned`.
- Format A `lock` creates a full lease (30-min TTL, `lease_id` +
  `idempotency_key` populated, `metadata.source = "swarm.js"`).
- If the tool itself crashes, that is a **tooling fault**, not a lock
  condition. Callers must branch on exit code / empty output (see §3).

### Emergency fallback (if swarm.js ever breaks again)

Direct dict manipulation in Python: add
`{lease_id, resource, holder, expires_at: now+TTL, created_at, ...}` under
`file:<path>`; release by deleting the key. Check `expires_at` before
assuming contention. (This was the workaround used 2026-08-26 before the
dual-format rewrite — now only an emergency path.)

---

## 3. Detector discipline for sweeps/alerts (the anti-pattern)

**Never grep prose for a count when the producer can emit errors into the
same stream.**

The 2026-09-05 failure: the sweep ran `swarm.js status 2>&1 || echo DOWN`
and counted `/stale|expired/` case-insensitive matches. The crash
stacktrace contained `purgeStale` + `locks.filter(...)` → 2 matches →
phantom `stale-locks=2` → false 🔴 delivered to Telegram against an empty
lock file. A detector's own error output was parsed as evidence of the
condition it measures.

Rules (enforced in `ned_infra_health_sweep.sh` since 2026-09-05):

1. **Count on structured output** — TSV field match, exit code, or JSON.
   Never on free-text regex over a merged stderr.
2. **A detector-tool crash is its own condition** — report it (🟡
   `swarm.js-status-FAILED`), never as the measured condition (🔴
   `stale-locks=N`).
3. **`2>&1 || echo DOWN` is a red flag in alert scripts.** If you need the
   tool's output to compute a number, capture stdout and stderr
   separately, and treat non-zero exit as "tool broken", not "data found".
4. **Silent-on-green still holds** — a tooling fault that cannot be
   confirmed dangerous should be a yellow line in the report file, not a
   Telegram message that erodes trust in the real reds.

Companion contracts: `okf/standards/cron-alert-output-contract.md`
(Telegram digest shape) and `okf/standards/swarm-coordination-protocol.md`
(claim-work layer).

---

## Background incident (2026-09-05)

Nightly sweep job `7fe31b74350f` delivered 🔴 "Prismatic queue
db=10MB stale-locks=2" on 2026-09-04 23:55 UTC; the lock file was `{}`.
Root cause: swarm.js (list-only assumption) crashed on the dict file; the
sweep's case-insensitive grep counted two stacktrace lines. Fixed 2026-09-05:
swarm.js dual-format rewrite (this spec) + TSV-based counting with
tool-failure → yellow. Verified: all lock operations on both formats, full
sweep run all-green with empty stdout, `telegram-cron-output-check`
`verify.py` PASS.

Note: the full incident post-mortem was drafted for `okf/incidents/`
(outside Ned's lane in this repo — see the OKF lane table in
`PRISMATIC_ENGINE.yaml`; Fred owns the incidents category). The live skill
`ned-lane-discipline-check` (profile + OKF auto-regen mirror) carries the
superseded-workaround note and points here.

---

**Last updated:** 2026-09-05
**Author:** Ned
**Version:** 1.0
