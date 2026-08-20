# UI / Command Center Production-Readiness Audit — 2026-07-20

Use this reference when Michael asks for a read-only Prismatic UI/dashboard/command-center production-readiness audit with rendered browser proof.

## Durable audit pattern

Audit five planes before scoring readiness:

1. **Rendered browser proof** — public and local `/dashboard`, desktop and mobile viewport screenshots, console errors, DOM/snapshot text, scroll width vs client width, tab click behavior, and deep links.
2. **API hydration and public/local parity** — visible tabs must have working public API routes, not only local Gateway handlers. Probe local `127.0.0.1:9000` and public `https://prismatic.growthwebdev.com` separately.
3. **Authorization and exposure boundary** — check whether public dashboard, operational APIs, POST controls, workspaces, source preview, artifacts, quotas, jobs, and webhook queue data are reachable without auth. Record security headers. Do not exercise mutating POST routes in a read-only audit.
4. **Runtime durability/source alignment** — compare audited repo branch/HEAD with durable runtime checkout HEAD, dirty/untracked files, service working directory, and public behavior. A detached/dirty runtime blocks production-readiness even when UI works.
5. **Operator Golden Flow / North Star** — compare observed UX against install/run → dashboard readiness → plugin catalog → connect plugin → create/start job → policy preview → approval → artifact/provenance → audit history → export/publish → safe disconnect → evidence/report.

## P0 blockers to look for

- Public dashboard and operational data unauthenticated.
- Workspace Tree/source viewer exposes broad host filesystem roots or readable source files publicly, even if traversal is blocked.
- Public tabs hydrate from local-only routes or nginx-unproxied APIs and show 404/failed status.
- Production runtime is dirty/detached or differs from the clean audited source branch.
- Visible controls imply real execution but backend returns `accepted_noop`, dry-run, or intent-only without a pre-click label.
- Dashboard presents stale/contradictory truth, e.g. systemd offline/heartbeat missing, queue depth zero but pending rows, stale merge scans, unknown quota freshness, or adapter import errors hidden as benign empty states.

## Rendered proof checklist

Desktop:

- capture screenshot and DOM/snapshot;
- inspect console and network/API failures;
- measure horizontal overflow (`documentElement.scrollWidth` vs `clientWidth`);
- click every top-level tab enough to verify visible content and route hydration;
- check URL/hash behavior and reload/deep-link persistence;
- identify whether default home answers “what needs my attention now?” or just displays proof ledgers.

Mobile:

- use a real narrow viewport around `390x844`;
- capture screenshot/DOM;
- check nav height/wrap, first-screen usefulness, touch target heights, table overflow, and readable dense IDs/timestamps;
- do not call mobile-ready from CSS/static checks alone.

Accessibility:

- count tab semantics (`role=tab`, `aria-selected`), form labels, modal labels, focus traps, and color-only status reliance;
- report as not WCAG-ready if dashboard is a div/button tab shell without semantic state.

## Read-only safety boundary

For a production audit, GET/HEAD/browser inspection is allowed. Do not click or POST controls such as Start/Stop/Restart, Save caps, install/uninstall, approve/reject, retry/purge, lifecycle demo, or export unless Michael explicitly authorizes state changes. If inspecting source reveals POST routes, report route count/categories without exercising them.

## Reporting shape

Lead with `BLOCKED` when P0s exist. Use compact proof:

```text
RESULT=<PASS|PARTIAL|BLOCKED>
SCOPE=Prismatic UI / Command Center production-readiness
AD_HOC_OR_CANONICAL=ad-hoc targeted read-only audit with rendered browser proof
PUBLIC_DASHBOARD=<url>
LOCAL_DASHBOARD=<url>
CONSOLE=<summary>
NOT_CLAIMING=canonical suite green, production readiness, authenticated security review
MARKER=PRISMATIC_UI_COMMAND_CENTER_PRODUCTION_READINESS_AUDIT_<PASS|PARTIAL|BLOCKED>
```

Then structure the report as: executive verdict, P0/P1 findings, rendered desktop/mobile findings, API hydration matrix, security/exposure boundary, runtime/source drift, North Star Golden Flow matrix, accessibility, scores, proof artifacts, files modified, and non-claims.

## Session-specific evidence pattern

The 2026-07-20 audit found the public dashboard rendered, but production-readiness was `BLOCKED` by unauthenticated public command-center/API exposure, public Workspace Tree/source preview of broad host roots, local/public route mismatch for PWP/native cron/arming/governance status APIs, a detached dirty runtime, no-op controls not pre-labeled, mobile command-center weakness, and missing tab/deep-link semantics. Use these as example finding classes, not permanent fixed facts; always re-probe live state before repeating them.