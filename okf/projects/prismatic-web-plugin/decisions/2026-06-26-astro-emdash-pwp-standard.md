---
type: Architecture Decision Record
title: Astro + EmDash as the PWP Website Standard
project: prismatic-web-plugin
resource: okf/projects/prismatic-web-plugin/decisions/2026-06-26-astro-emdash-pwp-standard.md
tags: [adr, pwp, astro, emdash, cloudflare, editable-content, client-sites]
timestamp: 2026-06-26T03:25:00Z
linear_issue: GRO-2491
git_repo: mbgulden/prismatic-web-plugin
pr: https://github.com/mbgulden/prismatic-web-plugin/pull/7
commit: 87072c8
status: accepted
verified_by: fred
---

# ADR: Astro + EmDash as the PWP Website Standard

## Decision

PWP-managed client websites should default to **Astro + EmDash**.

```text
Astro = frontend/site framework
EmDash = editable CMS/admin/content layer
Cloudflare = runtime, storage, DNS, and deploy target
```

This stack becomes the durable standard for PWP website generation unless a client requirement explicitly calls for a different stack.

## Context

Valkyrie Arms Training needed urgent recovery work:

1. Microsoft 365 mail DNS was restored via Cloudflare.
2. A temporary Cloudflare Worker "coming soon" page was deployed so the domain no longer looked broken.
3. Michael clarified that this emergency page was built without client direction and must not become the standard for the eventual site.
4. Michael directed that the workflow/infrastructure build should be part of the PWP plugin and that future client sites should use EmDash + Astro.

The emergency landing page solved an immediate trust problem, but it is not a design source of truth.

## Policy: emergency placeholders are disposable

Emergency stabilization pages are disposable operational artifacts.

They may be deployed quickly when a domain is broken, blank, or client trust is at risk. They do **not** establish durable standards for:

- brand direction
- visual design
- layout
- imagery
- copywriting
- navigation
- content model
- CMS schema
- component architecture

When client-approved direction arrives, PWP must treat it as source of truth and set aside emergency-page decisions as if the placeholder never existed.

Generated scaffolds must encode this with:

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

## Implementation standard

The initial PWP kernel shipped in `mbgulden/prismatic-web-plugin#7`.

Generated sites should include:

| Concern | Standard |
|---|---|
| Astro app mode | server output |
| Deploy adapter | `@astrojs/cloudflare` |
| CMS package | `emdash@0.23.0` |
| Cloudflare CMS adapters | `@emdash-cms/cloudflare@0.23.0` |
| Database | Cloudflare D1 binding `DB` |
| Media storage | Cloudflare R2 binding `MEDIA` |
| Object cache | Cloudflare KV binding `CACHE` |
| Worker compatibility | `nodejs_compat` |
| Generated config | `wrangler.jsonc` with binding placeholders |

Verified integration import contract:

```ts
import emdash from 'emdash/astro';
import { d1, kvCache, r2 } from '@emdash-cms/cloudflare';
```

## Why this stack

Astro provides:

- fast frontend delivery
- clean component architecture
- strong Cloudflare deployment path
- good fit for content-heavy local business websites

EmDash provides:

- client-editable content
- admin UI
- media library
- menus/site settings/taxonomies
- preview/revisions
- structured Portable Text content that agents can manipulate safely

PWP provides:

- repeatable client-site generation
- Linear task decomposition
- agent dispatch/review/deploy loop
- OKF handoff and long-term operational memory

## Verification performed

The first implementation was not accepted on unit tests alone.

Verification included:

```text
PYTHONPATH=src python3 -m pytest tests/test_astro_emdash.py -q
→ 4 passed

PYTHONPATH=src python3 -m pytest -q
→ 122 passed
```

A real generated Valkyrie-style scaffold was also created at:

```text
/tmp/pwp-valkyrie-astro-emdash
```

Then built with:

```bash
npm install
npm run build
```

Result:

```text
Astro + EmDash + Cloudflare build completed successfully
```

## Important lesson from verification

The first smoke build caught a real integration issue: `emdash` alone is not enough for Cloudflare production. The correct Cloudflare scaffold also needs `@emdash-cms/cloudflare`, D1/R2/KV bindings, and `nodejs_compat`.

This reinforces the verification standard: **repo docs + tests are not enough; generated sites must actually build.**

## Consequences

### Positive

- Client sites become editable instead of hardcoded.
- Emergency pages no longer drift into accidental standards.
- PWP becomes a real website factory, not just planning/orchestration.
- Future sites can share a consistent content model and deploy path.

### Tradeoffs

- EmDash requires Cloudflare runtime resources (D1/R2/KV), not a pure static export.
- The PWP deployer must provision Cloudflare resources, not just publish static files.
- The generated site must support staging/approval before production for client-approved work.

## Next slice

Wire the scaffold into the PWP builder pipeline:

```text
ingest → synthesize → distill → scaffold Astro+EmDash site → staging deploy → approval → production deploy
```

The existing Valkyrie Worker page should remain only as a temporary stabilization page until client-approved direction is available.
