---
type: Project Index
title: Prismatic Web Plugin
project: prismatic-web-plugin
resource: okf/projects/prismatic-web-plugin.md
tags: [project, pwp, websites, astro, emdash, cloudflare, client-sites]
timestamp: 2026-06-26T03:25:00Z
linear_issue: GRO-2491
git_repo: mbgulden/prismatic-web-plugin
git_path: okf/projects/prismatic-web-plugin.md
status: active
verified_by: fred
---

# Prismatic Web Plugin

The Prismatic Web Plugin (PWP) is the durable website-production system for Growth Web Dev client sites. It turns client inputs into editable, deployable websites through a repeatable pipeline instead of one-off bespoke builds.

## Current north star

Build the PWP website system correctly:

```text
ingest → synthesize → distill → scaffold Astro+EmDash site → staging deploy → approval → production deploy → OKF handoff
```

## Current default website stack

| Layer | Standard |
|---|---|
| Frontend/site framework | Astro |
| Client-editable CMS | EmDash |
| Runtime/hosting | Cloudflare Pages/Workers |
| CMS storage/runtime | Cloudflare D1 + R2 + KV |
| DNS/routing | Cloudflare DNS |
| Work tracking | Linear |
| Knowledge record | OKF |

## Core policy

Emergency stabilization pages are disposable artifacts.

If PWP or Fred deploys a quick landing page to keep a client domain from looking broken, that page **does not** set brand, UX, layout, content-model, imagery, or technical standards. When client-approved direction arrives, it supersedes the emergency page as if the placeholder never existed.

Generated scaffolds should mark temporary pages with:

```json
{
  "placeholderOnly": true,
  "pwpPolicy": {
    "emergencyPlaceholdersDoNotSetStandards": true,
    "clientApprovedDirectionSupersedesPlaceholder": true,
    "editableStack": "Astro + EmDash"
  }
}
```

## Current implementation state

| Item | Status |
|---|---|
| PWP Python pipeline: ingest/synthesize/distill | Existing |
| Astro + EmDash scaffold kernel | Shipped in PR #7 |
| Builder integration into `pwb run` | Next slice |
| PWP AI Design Operating System synthesis | Shipped by AGY in `GRO-2523` (`/archive/agy_sandboxes/GRO-2523` on the fast-SSD host when present; NAS copy remains evidence/archive only) |
| AGY active sandbox storage | **Moved off NAS** to local fast SSD: `/archive/agy_sandboxes` (`/storage` symlink). Logs/results: `/archive/agy_sandbox_logs`, `/archive/agy_sandbox_results`. NAS is archive/evidence only. |
| AGY reliability controls | Rich `AGY_TASK.md` from Linear, sandbox guard, and 120s inactivity-based kill are live; completion semantics still need fix so `RESULT.md` is progress, not final Done. |
| Live Valkyrie Worker placeholder | Temporary stabilization only |
| Valkyrie Astro+EmDash replacement | Wait for client-approved direction |

## Active AGY/PWP operations standard

PWP research/implementation waves must run from local fast SSD, not from NAS/NFS:

```text
active sandbox root: /archive/agy_sandboxes
friendly alias:      /storage -> /archive
active logs:         /archive/agy_sandbox_logs
active run JSON:     /archive/agy_sandbox_results
NAS archive:         /home/ubuntu/mounts/synology-agentic-context/agy_sandboxes
```

Rationale: AGY's workload is random-I/O heavy (`git`, `find`, package scans, RESULT/self-review writes). Direct `/archive` writes measured ~2.9 GB/s; boot-disk reads measured ~4.6 GB/s. NAS/NFS remains useful for bulk archive, but active random I/O is latency-bound and can stall AGY's background-tool loop.

## Key records

- [Decision: Astro + EmDash as default PWP website stack](./prismatic-web-plugin/decisions/2026-06-26-astro-emdash-pwp-standard.md)
- [Operations: AGY dispatch v2 lane supervisor + fast-SSD sandbox pivot](../operations/agy-dispatch-v2-lane-supervisor-2026-06-26.md)
- Linear: [GRO-2491](https://linear.app/growthwebdev/issue/GRO-2491/pwp-add-astro-emdash-editable-site-kernel)
- Linear: `GRO-2492`, `GRO-2551`, `GRO-2552`, `GRO-2553` — AGY/PWP reliability track
- PR: <https://github.com/mbgulden/prismatic-web-plugin/pull/7>

## Next action

Fix AGY completion semantics before the next PWP wave: `RESULT.md` should be treated as progress, while final completion requires `DONE:` or process exit after self-review. Then run a staggered `/archive` wave (`max-concurrent=2`, `jitter=15-30`) to retest the concurrency cliff on the fast SSD.
