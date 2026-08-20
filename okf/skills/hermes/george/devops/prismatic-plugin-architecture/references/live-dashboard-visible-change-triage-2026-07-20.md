# Live dashboard “I don’t see anything new” triage — 2026-07-20

Use when Michael reports that `/dashboard` loads but looks unchanged, or asks whether UI/UX/governance changes were actually pushed live.

## Core lesson

Do not answer from repo state, monitor percent, or agent reports alone. Split the diagnosis into three separately verified planes:

```text
1. Live shell / HTML visibility
2. Public API hydration / proxy exposure
3. Merge/deploy/runtime completeness
```

A dashboard can be public and nonblank while still being only partially live:

- UI shell/cards may be deployed.
- A tab may contain new UX markers but fail to hydrate because a public API path 404s.
- newer dashboard panels may exist only as dirty/untracked dev work and not in the durable runtime checkout.
- external host-level governance bridges may be running but not first-class PE dashboard/API state.

## Required checks

Run these before the explanation:

```bash
cd /home/ubuntu/work/prismatic-engine
git status --short
git rev-parse --abbrev-ref HEAD
git rev-parse HEAD
cd /home/ubuntu/.prismatic/runtime/prismatic-engine
git status --short
git rev-parse --abbrev-ref HEAD
git rev-parse HEAD
systemctl is-active prismatic-gateway.service
systemctl show prismatic-gateway.service -p WorkingDirectory -p ExecStart --no-pager
```

Probe local and public routes separately:

```bash
curl -k -sS -m 12 -D /tmp/h -o /tmp/b http://127.0.0.1:9000/dashboard
curl -k -sS -m 12 -D /tmp/h -o /tmp/b https://prismatic.growthwebdev.com/dashboard
curl -k -sS -m 12 -D /tmp/h -o /tmp/b http://127.0.0.1:9000/api/plugins/governance
curl -k -sS -m 12 -D /tmp/h -o /tmp/b https://prismatic.growthwebdev.com/api/plugins/governance
curl -k -sS -m 12 -D /tmp/h -o /tmp/b http://127.0.0.1:9000/api/gateway/agents/governance-status
curl -k -sS -m 12 -D /tmp/h -o /tmp/b https://prismatic.growthwebdev.com/api/gateway/agents/governance-status
```

Then browser-check at least:

- main Dashboard tab body text / headings;
- relevant tab click, especially Plugins or Resources;
- console errors/warnings;
- whether visible error text says an API path failed, e.g. `governance HTTP 404`.

## Report shape

Lead with the user-facing answer, not the full audit:

```text
You are not crazy. The dashboard is loading, and some changes did go live, but the result is partial.
```

Then present buckets:

| Bucket | Meaning |
|---|---|
| Shell/cards live | public HTML has the dashboard and cards; visual change may be subtle |
| UI/UX tab live but API broken | UX markers present, but public API hydration/proxy route fails |
| Dev-only / not deployed | dirty or untracked files exist in dev worktree but are absent from durable runtime |
| External bridge not first-class | filesystem bus/autopacer exists outside PE Core/dashboard/API |

## Pitfalls

- Do not say “nothing changed” if live HTML has new cards or tab UX markers.
- Do not say “it’s live” if key public APIs 404 while local APIs return 200.
- Do not equate `origin/main == runtime HEAD` with “all work is deployed”; dirty/untracked dev changes may still be missing.
- Do not call plugin UI/UX complete if the Plugins tab renders but says governance refresh failed.
- Do not call governance dashboard complete until agent lane status, proof links, audit history, approval/side-effect policy, and source/runtime durability are dashboard/API-visible and browser-proven.

## Useful marker

```text
PRISMATIC_DASHBOARD_LIVE_VISIBILITY_DIAGNOSIS_OK
```
