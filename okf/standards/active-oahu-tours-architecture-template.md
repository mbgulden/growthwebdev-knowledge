---
type: Standards
title: ActiveOahuTours.com — Architecture Template (MVP reference)
description: The AOT architecture that the Prismatic Web Plugin MVP will mirror. Astro 6 + Cloudflare Pages + D1 + Portable Text. Documents the working pieces so the MVP build can reuse them rather than start from scratch.
resource: https://github.com/mbgulden/active-oahu-tours-mirror
tags: [standards, architecture, template, active-oahu, prismatic-web-plugin, mvp]
timestamp: 2026-06-23T06:12:00Z
git_repo: mbgulden/active-oahu-tours-mirror
linear_issue: TBD
last_verified: 2026-06-23
verified_by: fred
status: current
---

# ActiveOahuTours.com — Architecture Template

> **Purpose:** The Prismatic Web Plugin MVP uses the same infrastructure route as ActiveOahuTours.com. This doc captures the working pieces of the AOT setup so the MVP build can reuse them.

## Stack (the proven route)

| Layer | Tool | Why |
|---|---|---|
| **Static site generator** | Astro 6 (or current stable) | Static-first with islands for interactive components; agent-friendly Portable Text for content |
| **Hosting** | Cloudflare Pages | Direct GitHub integration, preview deploys, fast global edge |
| **Database** | Cloudflare D1 (SQLite) | Serverless, no cold starts, agent-queryable |
| **Content schema** | Portable Text (JSON blocks) | LLM-parseable, decoupled from presentation |
| **Styling** | Custom CSS (per the AOT mirror's CSS) or Tailwind | Both work; AOT uses hand-rolled CSS for the design system |
| **Image hosting** | Cloudflare Images (or R2 + custom domain) | For client-provided + Unsplash + AGY-generated images |

## The working pieces (reuse, don't rebuild)

### 1. The AOT mirror repo
- **GitHub:** `mbgulden/active-oahu-tours-mirror`
- **Local:** `~/work/active-oahu-tours-mirror/`
- **What's in it:** the full Astro+CF+Pages source, the OKF docs, the build pipeline scripts, the content collection, the redirect rules (`_redirects`), the Japanese translations (83 pages), the schema.org markup (130 pages)
- **How to reuse:** clone as the starting point for the new MVP, replace the content collection + design system, keep the build/deploy pipeline

### 2. The AOT static export
- **Local:** `~/work/active-oahu-static/` (and `-mirror/`)
- **What's in it:** the same content but as static HTML, served from `activeoahutours.com` (prod) and `staging.active-oahu-tours-mirror.pages.dev` (staging)
- **How to reuse:** the redirect rules (`_redirects`), the URL shape (`.html` vs `/` trailing-slash), the meta tags, the schema markup — all reusable as patterns

### 3. The AOT OKF docs
- **Local:** `~/work/growthwebdev-knowledge/okf/plugins/active-oahu-tours-mirror/` (and other AOT-related OKF docs in `okf/audits/` and `okf/standards/`)
- **What's in it:** the architecture decisions, the SEO strategy, the Japanese translation approach, the deploy pipeline — all documented
- **How to reuse:** the OKF template structure (outcomes table, what shipped, decisions, outstanding items, future-agent runbook, verification commands, risk register) is a great pattern for the new project's OKF docs

### 4. The Cloudflare Pages deploy
- **Pipeline:** GitHub push → Cloudflare Pages build → deploy to `*.pages.dev` (preview) or custom domain (prod)
- **Auth:** the project's Cloudflare API token in `~/.hermes/profiles/orchestrator/.env` (`CLOUDFLARE_PAGES_API_TOKEN`, `CLOUDFLARE_PAGES_ACCOUNT_ID`)
- **How to reuse:** the same deploy pipeline, just create a new Cloudflare Pages project pointing at a new GitHub repo

## What needs to be different for the MVP

| AOT | MVP |
|---|---|
| 130 pages, 83 Japanese translations | 1-5 pages initially (per the 5 client docs) |
| ActiveOahu Tours brand (kayak, e-bike, etc.) | Client brand (TBD from Doc 3 brand design interview) |
| AOT-specific content (tours, pricing, etc.) | Client content (per Doc 1 content gathering) |
| Custom hand-rolled CSS | TBD — could be the same hand-rolled approach, or a framework |
| Static site only (no auth) | TBD — depends on the conversion flow per Doc 4 |

## The Cloudflare Pages setup (for the new project)

1. Create a new Cloudflare Pages project (e.g., `prismatic-web-mvp` or `clientname-mvp`)
2. Connect it to a new GitHub repo (e.g., `mbgulden/prismatic-web-mvp` or `mbgulden/clientname-mvp`)
3. Build settings: framework = Astro, build command = `npm run build`, output dir = `dist`
4. Environment variables: same as AOT (none required for the static-only MVP)
5. Custom domain: TBD (the client domain or a `*.growthwebdev.com` subdomain)

## The design system approach (per Michael's "not lame" directive)

- **Source pics** from the client's Drive (5 Website Dev docs)
- **Source logos** from the client's Drive
- **Source brand colors** from the brand design interview (Doc 3)
- **Fallback pics** from Unsplash (royalty-free)
- **AI-generated assets** via AGY SDK image gen (Gemini Omni Flash)
- **Mood board** built FIRST (per the Design Sudio doc's "stream of consciousness" workflow)
- **Layouts** generated AFTER mood board approval
- **Reviews** by a separate Antigravity instance for objectivity (per the Design Sudio doc)

## Reusable build scripts (in the AOT mirror)

- `_redirects` — canonical URL form (`/activities.html` vs `/activities/`)
- `add_schema.py` — schema.org markup generator
- `fix_button_colors.py`, `fix_kadence_css.py` — CSS fixes
- `fix_relative_asset_paths.py` — asset path canonicalization
- `generate_pages.py`, `generate_info_pages.py`, `generate_rental_pages.py` — content generators
- `inject_schema.py`, `inject-ja-schemas.py` — JSON-LD injectors
- `translate-ja-batch.py`, `translate-ja-remaining.py` — i18n (if MVP needs multi-language)
- `prismatic-publish` (in `~/.local/bin/`) — the OKF doc publisher (artifacts to files.growthwebdev.com)

## What still needs to be decided

- [ ] Which client is the MVP for? (Doc 1-5 don't name a specific client — could be a hypothetical)
- [ ] Brand colors and typography (from Doc 3 once we read it)
- [ ] Domain name (custom or `*.growthwebdev.com` subdomain)
- [ ] Repository name (something like `prismatic-web-mvp` or `clientname-website`)
- [ ] Whether to use the AOT mirror as the starting template or build from scratch

## Verification commands

```bash
# Clone the AOT mirror as a starting point
git clone https://github.com/mbgulden/active-oahu-tours-mirror ~/work/mvp-temp
cd ~/work/mvp-temp

# Check the build setup
cat package.json | head -30
cat astro.config.* 2>/dev/null
cat _redirects 2>/dev/null

# Check the AOT static export (if using as a starting point instead of the mirror)
ls ~/work/active-oahu-static/
```

## Related OKF docs
- `okf/projects/prismatic-web-plugin/index.md` — the Prismatic Web Plugin hub
- `okf/projects/active-oahu-tours-mirror/` — AOT plugin folder (the source)
- `okf/audits/active-oahu-tours-*.md` — AOT audit docs
- `okf/standards/active-oahu-tours-*.md` — AOT standards (if any)
- `okf/plugins/active-oahu-tours-mirror/` — AOT plugin folder

## Change log
- 2026-06-23 06:12 UTC: Created as the architecture reference for the Prismatic Web Plugin MVP
