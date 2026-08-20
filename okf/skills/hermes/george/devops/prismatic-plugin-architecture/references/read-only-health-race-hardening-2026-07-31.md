# Read-only health plugin race hardening — 2026-07-31

Session-specific detail for the class-level Prismatic shipped-plugin hardening workflow. Use when reviewing or implementing read-only operations/health plugins that inspect mutable operator state.

## Durable lessons

### 1. Directory enumeration must be killable as a tree

A timeout around `Path.iterdir()` in the main process is not a hard bound if the filesystem call blocks or a malicious/buggy iterator forks descendants. Move enumeration into a helper process that:

- starts its own process group/session before touching the target tree;
- reports through bounded IPC only;
- is killed via process-group cleanup on timeout, success, limit/error status, EOF, oversized payload, or IPC exception;
- joins/reaps the leader and uses direct-process kill as fallback;
- returns redacted generic findings rather than exception text.

Regression shape: monkeypatch enumeration to fork a marker-writing grandchild, force timeout/completion paths, sleep past the child write window, and assert no marker appeared and no stale process survives.

### 2. SQLite/WAL read-only inspection cannot claim a complete live snapshot

Opening a live SQLite DB read-only does not prove a complete state snapshot when WAL exists or can appear/change during inspection. Treat live WAL as a conservative boundary:

- capture DB and WAL identities before and after inspection;
- if DB identity changes, WAL identity changes, WAL appears, disappears, grows, shrinks, or is replaced, set `identity_stable=false` and `snapshot_complete=false`;
- suppress stale size/threshold/page/freelist claims on drift (`size_bytes`, `wal_bytes`, `total_bytes`, `over_size`, page metrics should become null/absent as appropriate);
- even when pre/post identities are stable, keep `snapshot_complete=false` for unfenced live WAL reads unless a separate writer-exclusion/snapshot contract exists.

Regression shape: seed non-empty WAL and monkeypatch identity reads to mutate/grow/shrink/remove/replace WAL between pre/post checks; require warning/fail-closed evidence without stale numeric claims.

### 3. Public findings should be deterministic and redacted

Adversarial read-only plugins must not reflect caller-controlled paths, branch names, Git identity strings, field names, or exception text. Use stable check IDs/path digests and generic error classes; validate JSON finiteness before return.

### 4. Exact-head review loop

For each blocker repair, preserve the candidate head, add persistent regression tests for the exact blocker, run focused + architecture/load gates, then send exact head/tree/parent to independent reviewers. Fresh guard proofs after edits are ad-hoc targeted unless the canonical suite actually ran green.
