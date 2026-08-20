# Read-only operations and cron durability hardening — 2026-07-31

## Trigger

Use this reference when implementing or reviewing Prismatic shipped plugins that inspect Hermes/operator state, produce health findings, or export cron durability artifacts. The session produced two class-level patterns:

- a read-only Hermes operations health plugin; and
- a non-authoritative cron history/snapshot/restore-plan plugin.

## Read-only health plugin hardening checklist

- Treat read-only as adversarial: prove the checker did not mutate profile DB/WAL/cron/state metadata or Git index metadata.
- Avoid importing operational loaders that may auto-repair or persist state during inspection. Prefer direct JSON/text/SQLite inspection where the persistence side effects are known.
- Git checks must avoid index refresh and hooks/monitors:
  - `git --no-optional-locks ...`
  - `GIT_OPTIONAL_LOCKS=0`
  - `core.fsmonitor=false`
  - tracked-only status when possible;
  - bounded timeout and output limits.
- SQLite checks must not overclaim when WAL is active. A non-empty WAL is a `WARN`/degraded boundary; do not report page/freelist thresholds as stale truth from `immutable=1` alone.
- Build SQLite URIs with safe path encoding (`Path.as_uri()` or equivalent), not string concatenation that breaks on `?`, `#`, or other URI metacharacters.
- Reject profile/worktree roots and inspected path components that are symlinks or escape configured roots. Dangling symlink directory entries count as present for `expected_absent` migration checks.
- Redact arbitrary evidence aggressively: hash IDs, job names, paths, migration entries, field names, prompts, targets, and other user-controlled strings. Findings should expose counts/statuses and stable digests, not raw operational content.
- Validate strict types and finite/ranged numeric CLI/API options. Reject NaN, infinity, negative thresholds where invalid, and unbounded scans.
- Bound worktree inventory by both entry count and deadline; reject symlink entries rather than following them.
- Registered plugin tools should execute the exact same reviewed runner/API path as the CLI, not a placeholder method.

## Test expectations

Each blocker should become a persistent reproduction, not a one-time manual check. Include tests for:

- Git index metadata invariance;
- active WAL handling;
- URI metacharacter paths;
- symlink root/path escape;
- dangling symlink migration semantics;
- raw evidence redaction digests;
- duplicate cron IDs independent of other row validation failures;
- strict cron/state schema typing;
- invalid scan/time settings from both CLI and direct API calls;
- executable registered tool behavior.

## Cron durability plugin contract

Do not make PE helper code a second cron authority. The safe plugin pattern is export/verify/plan only:

1. **Deterministic redacted history** — preserve structural facts, but hash job IDs, names, schedules, prompts, delivery targets, paths, context sources, and arbitrary field names. Emit canonical hashes using stable JSON with `allow_nan=False`.
2. **Private snapshots** — write only outside the live Hermes authority path, under an operator-provided private directory. Require directory mode `0700` and snapshot mode `0600`.
3. **Atomic no-overwrite writes** — write temp file, fsync, hard-link/no-overwrite into final name, fsync directory, and remove temps on failure. Reuse an exact existing snapshot only when digest matches.
4. **Authority binding** — include source-byte hash, canonical projection hash, and private envelope/authority digest. Restore planning must reject tampered or malformed digests.
5. **Restore/readback plans only** — compute added/removed/changed jobs with redacted ID hashes and explicit operator steps. Do not patch `jobs.json` directly. Live restore requires the canonical Hermes writer and any needed writer-exclusion gate.
6. **Symlink rejection** — reject symlink components in snapshot output paths and inspected roots.

## Reporting boundary

Use proof packets that separate:

- focused plugin tests;
- plugin architecture/load gates;
- live read-only canary with metadata invariance;
- environment-workaround parity runs;
- canonical full-suite green;
- publication/merge/deploy gates.

If a full-suite command fails due to import/collection environment, report it as a verification-environment blocker until exact failed nodes can be compared. Do not convert import-bound or preloaded-package workaround runs into canonical full-suite claims.
