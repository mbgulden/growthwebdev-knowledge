# 2026-09-03 — Coach-portal mobile-first dashboard + population/consent endpoints

Session: Michael asked (1) the coach dashboard to "work great on small screens" and
leave room for future population/platform visibility, and (2) a per-client consent
toggle in the population view. Built on the promoted `api.humandesignengine.com/coach/*`
portal (see `references/hde-coach-portal-promotion-2026-08-25.md` +
`references/2026-09-coach-premium-promotion.md`).

## Where the dashboard lives
- `hd-platform-staging/landing/coach_dashboard.html` — single self-contained file
  (inline CSS + JS). Served by the staging orchestrator `:8011`; the `coach/dashboard`
  route **re-reads the file per request**, so HTML edits need NO service restart. Only
  Python endpoint changes need `sudo systemctl reload-or-restart hde_orchestrator_staging`.
- Endpoints live in `hd-platform-staging/scripts/vm_orchestrator.py` (the coach block near
  the bottom; `request_has_coach_portal_access(token, request)` is the shared gate, used
  by every `/api/coach/*` route).

## Mobile-first, multi-view rebuild (shipped)
- <900px: bottom tab bar (Clients / Population / Platform) + stacked master-detail (list
  page → detail page with back button); safe-area insets; 44px+ tap targets.
- >=900px: left nav rail + 3-pane Clients (list + 2-col dossier grid) + tabular roster
  with a column header row.
- Auth unchanged: CF-Access session + legacy-token fallback; `esc()` on all interpolated
  data (XSS-safe).
- Pitfall (hit this session): a desktop-only element like `.roster-head` needs a **base**
  `display:none` (its `display:grid` lives only inside the `min-width:900px` media query),
  or it renders on mobile as a bare `display:block` div with run-together labels. Verify
  **zero horizontal overflow** at both widths.

## New endpoints (coach block, same CF-Access/token gate)
- `GET /api/coach/population` → `{stats, coaching, roster, generated_at}`. Whole-customer-base
  KPIs (totals, by_subscription, by_access, premium, onboarded_containers,
  containers_by_status) + coaching KPIs (active_clients, never_expire, expiring_14d,
  suspended_clients, consented_pipeline) + a lightweight roster (identity + status only;
  **no journal/step content, no API keys**). Deliberately separate from `/api/coach/clients`
  so population/platform can grow independently.
- `POST /api/coach/clients/{id}/consent` (body `{granted: bool, token: str}`) — grant or
  revoke `coach_review_consent`. grant → consent=True, `consent_at=now`,
  `source=coach_dashboard_toggle`, `revoked_at=NULL`; revoke → consent=False,
  `revoked_at=now` (audit kept). Deliberately **not** the per-client review gate. This is the
  **first DB-write on the coach surface** (the rest are read-only workspace ops), so it must
  `await session.commit()` explicitly — `async_session_factory` does NOT auto-commit writes
  (`expire_on_commit=False`).

## Frontend JS contract
- GETs use `?token=<coachToken>` (the `apiQuery()` helper); POSTs put `token` in the JSON
  body. `coachToken` comes from `sessionStorage("COACH_ACCESS_TOKEN")` (legacy fallback) —
  empty string is fine when CF-Access email auth is active.
- Consent UI = an iOS-style switch in **both** the mobile roster card and the desktop grid's
  Consent column; optimistic flip + toast; **event-delegated** handler on `#rosterList`
  (rows re-render on every filter/search, so attach via delegation, not per-row).
- After a toggle, call `loadPopulation()` again so the KPIs reflect the new consent set.

## Local verification recipe (no shared CDP browser)
- Stand up a small local rig: serve `coach_dashboard.html` at `/coach/dashboard` and proxy
  `/api/coach/*` to the real origin `:8091` **with simulated CF-Access headers**
  (`Cf-Access-Jwt-Assertion: <anything>` +
  `Cf-Access-Authenticated-User-Email: mbgulden@gmail.com`). The origin `:8091` 403-gates
  missing CF headers and the public edge 302s without auth — so you must inject the headers
  locally to exercise the live endpoints.
- Drive it with local headless Playwright at 390x844 (mobile) and 1280x800 (desktop). See
  `webtop-shared-eyes/references/local-headless-playwright-responsive-qa.md` for the
  Playwright setup + the mobile/desktop selector gotcha (`.rr-mobile` vs `.rr-desktop` both
  contain a `.ct` switch; scope the locator by breakpoint or Playwright times out waiting for
  the hidden one to become visible).
- Toggle verification must round-trip on a **SAFE synthetic test account** (e.g. id 1,
  `example.com`) and **restore its exact baseline consent tuple** (consent, revoked_at,
  source, consent_at) afterward — the grant/revoke pair leaves `source=coach_dashboard_toggle`
  set, which is NOT the original baseline.

## Deploy context (this session)
- The staging worktree had **other agents' uncommitted hunks** in `vm_orchestrator.py`
  (Sanctuary prompt + qwen provider, ~lines 134–230). Stage only your hunks:
  `git diff scripts/vm_orchestrator.py > /tmp/d.txt`, a tiny Python filter that keeps only
  your `@@` hunk ranges (file header + the blocks you own), `git apply --cached
  /tmp/my-hunks.patch`, then `git add landing/coach_dashboard.html`. Verify no leak:
  `git diff --cached scripts/vm_orchestrator.py | grep -ci sanctuary` → 0.
- Pushed to `ned/hde-phase4-paid-bot-onboarding-quality-2026-07-15` (the live portal branch).
  The related OKF doc PR had to be rebuilt from `origin/main` (auto-regen conflict — see
  `okf-knowledge-capture`).
