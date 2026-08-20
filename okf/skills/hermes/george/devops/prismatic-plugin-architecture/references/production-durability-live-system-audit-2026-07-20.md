# Production durability / live-system readiness audit — 2026-07-20

Use this reference when auditing Prismatic Engine as a live hosted system, not merely as a local developer-preview repo.

## Durable audit planes

Audit all four planes before scoring readiness:

1. **Repository/release plane** — branch, PR, CI, tags/releases, protected branch, clean source, documented commands.
2. **Runtime/source plane** — systemd `WorkingDirectory`, executable command, runtime checkout SHA, dirty/untracked files, source-vs-runtime drift, rollback target.
3. **Live service/state plane** — service/timer status, queue/state stores, read-only SQLite/JSON integrity, disk/inode capacity, backup/restore proof.
4. **Public/browser/security plane** — public route responses, auth challenges, webhook signature behavior, security headers, browser DOM/console, public-vs-local proxy parity.

Do not collapse local smoke success, GitHub CI green, or a working dashboard into production readiness. A hosted operator surface can be useful and still blocked.

## P0 hard blockers observed

- **Unauthenticated public internal Gateway APIs:** dashboard/operator APIs returned `200` anonymously for workspaces, plugin jobs/artifacts/audit-events, agent/governance status, rate-limit status, and webhook queue status. Treat any public stateful/operator API without a general auth boundary as P0.
- **Webhook fail-open on missing signatures:** deployed handlers only validate when a signature header exists. Missing signatures continued into queue/event publication. Closure requires missing/invalid signatures and missing signing-secret configuration to fail closed with no queue/event rows.
- **Dirty detached runtime:** Gateway ran from `/home/ubuntu/.prismatic/runtime/prismatic-engine` but with modified tracked files plus untracked production modules/tests absent from `origin/main`. Runtime SHA alone is not a release proof when the checkout is dirty.
- **Mutable development checkout dependence:** consumer/curator/watchdog still used `/home/ubuntu/work/prismatic-engine` while gateway/drain used runtime. Every production unit must point at a clean durable checkout/artifact.

## P1 release gaps observed

- Public/local route mismatch: local `/api/pwp/status` was `200` while public `/api/pwp/status` was `404`, indicating missing nginx proxy exposure.
- Documented direct-run release/security/smoke commands failed without ad-hoc `PYTHONPATH`; they passed only after manually setting repo root. Treat this as non-hermetic release proof until package install/bootstrap is fixed.
- Dashboard health contract drift: dashboard reported consumer offline/missing heartbeat while systemd showed it active.
- Production dashboard still used Tailwind CDN while source branch had no-CDN portability changes; runtime/source drift hid the fix.
- Public responses lacked hardening headers such as CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, and Permissions-Policy.
- State quick checks can be good while backup/restore proof remains absent; require a restore drill, not just `PRAGMA quick_check`.
- Verifiers that receive bot/WAF `403` must not misclassify it as real access authentication; require browser/DOM proof for public operator surfaces.

## Closure gate template

```text
COMMAND=<grouped commands: git/runtime/systemd/curl/browser/tests>
RESULT=<PASS|PARTIAL|BLOCKED>
LOG=<paths or not needed>
SCOPE=live Prismatic production durability/readiness
AD_HOC_OR_CANONICAL=ad-hoc targeted audit unless canonical suite actually ran
NOT_CLAIMING=<e.g. clean release, public auth, backup restore, browser/mobile proof>
MARKER=PRISMATIC_PRODUCTION_DURABILITY_AUDIT_OK only for audit completion, not readiness
```

## Exact readiness criteria before PASS

Require all of these before saying production-ready:

- public operator APIs authenticated or isolated behind a proven access boundary;
- missing/invalid webhook signatures fail closed and valid signatures still work;
- all production services/timers execute from a clean durable runtime/release artifact;
- runtime SHA equals approved release/tag/merged commit and `git status --porcelain` is empty;
- local and public route parity is proven, including dashboard/API/browser console;
- documented release/security/smoke commands run exactly as documented without ad-hoc env hacks;
- security headers/rate limits/CORS policy are verified publicly;
- state backup, retention, restore drill, permissions, and rollback are proven;
- dashboard health state agrees with service/queue/runtime truth;
- CI/release/tag/protection evidence exists.

If any P0 is present, report `BLOCKED` even when local tests, focused runtime tests, and public dashboard rendering pass.