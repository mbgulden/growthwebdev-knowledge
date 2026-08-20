# Prismatic production-readiness audit pattern — 2026-07-20

Use this reference when Michael asks for a comprehensive read-only Prismatic Engine architecture/production-readiness audit against North Star/OKF/durability docs.

## Class-level audit shape

Do not answer from docs, dashboard appearance, or runtime markers alone. Treat readiness as a four-plane comparison:

1. **Doctrine/docs plane** — `docs/north-star.md`, `docs/okf-evidence-map.md`, `docs/dashboard-primary-touchpoint.md`, public launch/security docs, `research/rubric-inventory-matrix.md`, and `docs/prismatic-production-durability-standard.md`.
2. **Source plane** — changed modules, tests, route tables, scripts, monolith/orphan surfaces, fixture/demo paths, and whether implementation matches the docs.
3. **Durable runtime plane** — systemd WorkingDirectory/ExecStart, runtime checkout HEAD/branch/status, untracked files, state DB/JSON files, timers, services, and logs.
4. **Public/operator plane** — public and local route probes, dashboard browser interaction, console, API payloads, auth boundary, and explicit non-claims.

## Scoring/reporting pattern

Lead with `BLOCKED/PARTIAL/PASS`, then a numeric scorecard by dimension. A useful rubric from this session:

- Core boundaries
- Plugin system
- Jobs/artifacts/policy
- Completed-work integration
- Assigned-agent dispatch/writeback
- State/persistence
- Security/auth/CORS
- Observability/audit
- Dashboard/operator UX
- Release/portability
- Production durability
- Orphan/dead surfaces

Use tool-backed arithmetic for the average. Report developer-preview/local-first readiness separately from hosted/public production readiness.

## Blockers to check explicitly

These are durable audit checks, not one-off findings:

- Public Gateway/dashboard bound to `0.0.0.0` with unauthenticated operational APIs. Middleware may protect only `/metrics`, `/events/*`, and `/curator/*`; dashboard/plugin governance/queue/agent APIs still need app-layer auth or a verified edge auth boundary before hosted readiness.
- Webhook HMAC validation must fail closed for missing signatures, not only invalid signatures.
- Durable runtime checkout must be pinned, reviewed, and clean. Detached dirty runtime with untracked modules means public behavior is not reproducible from Git.
- Assigned-agent markers are not enough: verify live queue rows contain result/blocker/writeback fields before claiming `ASSIGNED_AGENT_RESULT_WRITEBACK_OK` or recovery complete.
- Focused suites that only pass with ambient credentials are not hermetic. If a test needs a fixture credential, the test should mock/supply it explicitly; report the implementation proof and hermeticity gap separately.
- State is often fragmented across JSON and SQLite stores; check file permissions, backup/restore, locking/atomicity, retention/export, and migration evidence.
- Dashboard health cards can disagree with systemd/live process truth; compare public API, local API, and systemd before trusting the dashboard.
- Canonical rubric ledgers with `TBD` rows or `REVIEW_PENDING` verdicts cannot support a 10/10/production-ready claim.
- CDN-dependent dashboard shells (`cdn.tailwindcss.com`) produce production warnings and should be treated as release-hardening gaps.

## Verification receipts from the session

Good compact evidence blocks to emulate:

```text
COMMAND=public_launch_smoke + public_security_readiness_audit + release_smoke
RESULT=PASS
LOG=/tmp/prismatic-source-smokes-20260720.log
MARKERS=PUBLIC_LAUNCH_SMOKE_OK,PUBLIC_SECURITY_READINESS_OK,RELEASE_SMOKE_OK
```

```text
COMMAND=focused architecture suite
RESULT=FAIL
LOG=/tmp/prismatic-focused-architecture-tests-20260720.log
SUMMARY=108 passed, 1 failed
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=canonical full-suite green
```

```text
COMMAND=targeted AGY wrapper test with non-secret fixture credential
RESULT=PASS
LOG=/tmp/prismatic-assigned-agent-test-with-fixture-auth-20260720.log
SUMMARY=1 passed
BOUNDARY=implementation path works; default suite is not hermetic
```

## Reporting boundary

For this audit class, be very explicit about non-claims. Do not claim production readiness, hosted multi-user safety, canonical full-suite green, live Linear writeback, auto-merge, mobile readiness, rollback readiness, backup/restore portability, or reproducible runtime source unless each is independently proven from live artifacts.
