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
| Live Valkyrie Worker placeholder | Temporary stabilization only |
| Valkyrie Astro+EmDash replacement | Wait for client-approved direction |

## Key records

- [Decision: Astro + EmDash as default PWP website stack](./prismatic-web-plugin/decisions/2026-06-26-astro-emdash-pwp-standard.md)
- Linear: [GRO-2491](https://linear.app/growthwebdev/issue/GRO-2491/pwp-add-astro-emdash-editable-site-kernel)
- PR: <https://github.com/mbgulden/prismatic-web-plugin/pull/7>

## Next action

Wire the Astro+EmDash scaffold into `pwb run` after synthesis/distillation so the PWP pipeline produces a real editable site scaffold and staging deploy package automatically.
