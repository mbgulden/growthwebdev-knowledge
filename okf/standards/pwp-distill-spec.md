---
type: Standard
title: Prismatic Web Plugin — Task Distiller Spec (Step 3)
description: The Step 3 task distiller. Reads a website_build_plan.md (from Step 2) and creates a Linear epic + 10-20 child issues with proper agent:* labels and OKF context. Parses the markdown to extract pages, design specs, automations, then creates issues with appropriate agent lane assignments.
resource: https://github.com/mbgulden/growthwebdev-knowledge/blob/main/okf/standards/pwp-distill-spec.md
tags: [standard, prismatic-web-plugin, task-distillation, step-3, linear-automation, markdown-parser, agent-routing]
timestamp: 2026-06-23T06:50:00Z
linear_issue: GRO-2140
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/pwp-distill-spec.md
last_verified: 2026-06-25
verified_by: fred
status: current
---

# Prismatic Web Plugin — Task Distiller Spec (Step 3)

> **What this is:** Step 3 of the multi-agent website-build orchestration system (GRO-2137). Takes the `website_build_plan.md` (from Step 2) and creates a Linear epic + 10-20 child issues with proper agent:* labels and OKF context. This is the bridge between "we have a build plan" and "agents are executing."

## Why this exists

Per Michael: "everything we build going forward goes forth with speed and efficiency" + "agents contribute in the flow/build/review."

Without the distiller, the agent swarm has nothing to pick up. With it, every client onboarding produces a complete Linear epic tree, automatically routed to the right agents.

## Script

`~/.hermes/profiles/orchestrator/scripts/pwp/pwp_distill.py`

**Usage:**
```bash
python3 pwp_distill.py <path-to-website_build_plan.md>         # create issues
python3 pwp_distill.py <path-to-website_build_plan.md> --dry-run  # preview only
```

**Output:**
- 1 parent epic in the `Prismatic Engine` Linear project
- 6-N page-build child issues (one per page from the build plan)
- 1 design system child issue (routed to `agent:kai-css`)
- 1 asset curation child issue (routed to `agent:agy`)
- M automation child issues (one per workflow)
- 1 deploy child issue (routed to `agent:ned-infra`)

**Total:** typically 12-20 issues per build plan.

## Issue templates

### Parent epic
- Title: `[<ClientName>] Website build epic (from build plan)`
- Description: client name, page count, phase count, automation count, build plan path
- Labels: `agent:fred`
- Priority: P1

### Page-build issue
- Title: `[<ClientName>] Build page: <Title> (<slug>)`
- Description: slug, title, description, build plan reference, acceptance criteria, verification command
- Labels: `agent:agy`
- Priority: P2

### Design system
- Title: `[<ClientName>] Design system implementation (colors, type, components)`
- Description: design tokens from build plan, task list (colors, type, spacing, components), acceptance criteria
- Labels: `agent:kai-css`
- Priority: P1

### Asset curation
- Title: `[<ClientName>] Asset curation — hero images, class photos, instructor portraits, icons`
- Description: asset inventory from build plan, sources (Unsplash, AGY image gen, client-provided), attribution
- Labels: `agent:agy`
- Priority: P2

### Automation
- Title: `[<ClientName>] Automation: <workflow-name>`
- Description: workflow name, trigger, email sequence, acceptance criteria
- Labels: `agent:ned`
- Priority: P3

### Deploy
- Title: `[<ClientName>] Cloudflare Pages deploy + DNS + monitoring`
- Description: deploy steps, redirects, analytics, monitoring
- Labels: `agent:ned-infra`
- Priority: P1

## Parsing logic

The script parses the build plan markdown for:

1. **Client name** — from the first H1 title (`# ClientName: ...`)
2. **Pages** — from `## 1.1 Full Page List` section (looks for `**`slug`** (Title)**: description` patterns)
3. **Pages (backup)** — from `## 2. Per-Page Content Briefs` section (`### 2.X Title (slug)` patterns)
4. **Phases** — from `## 7. Build Sequence` section (`### Phase N: Name (duration)` patterns)
5. **Automations** — from `## 6. Automation Workflows` section (`### 6.X Workflow Name` patterns)

Robust to:
- Missing sections (skips gracefully)
- Extra whitespace
- Slug formatting variations
- Duplicate pages (deduplicates by slug)

## Verification (2026-06-23 06:50 UTC)

Test run on the Meridian Women's Defense build plan (produced by Step 2):

```bash
python3 pwp_distill.py okf/projects/website-dev/inputs/output/meridian-womens-defense-academy/website_build_plan.md
```

**Output:**
- 1 epic: GRO-2142 — "[Meridian Women's Defense Academy] Website build epic (from build plan)"
- 13 child issues, all parented to GRO-2142:
  - GRO-2143: Build page: Home (`/`)
  - GRO-2144: Build page: About Us (`/about/`)
  - GRO-2145: Build page: Classes Index (`/classes/`)
  - GRO-2146: Build page: Flagship Class Detail (`/classes/idaho-enhanced-concealed-carry-for-women/`)
  - GRO-2147: Build page: Contact (`/contact/`)
  - GRO-2148: Build page: Lead Magnet Landing Page (`/beginners-guide-to-personal-safety/`)
  - GRO-2149: Design system implementation
  - GRO-2150: Asset curation
  - GRO-2151 through GRO-2154: 4 automations
  - GRO-2155: Cloudflare Pages deploy + DNS + monitoring

**Note:** GRO-2141 was created as a duplicate epic from the first script run (before the fix); it has been canceled.

**Acceptance criteria met:**
- [x] Script exists at `scripts/pwp/pwp_distill.py`
- [x] Creates Linear epic + 13 child issues (within target of 10-20)
- [x] All children have proper labels, descriptions, parents, priorities
- [x] No manual Linear API calls needed

## Known limitations

1. **Markdown parsing is regex-based.** Could break on unusual formatting (e.g., nested bullets, code blocks with `## 1.1` in them). For typical AGY-generated build plans, works reliably.
2. **Label lookups are done once at startup.** If labels are added to Linear after the script runs, they won't be recognized.
3. **No retry logic on Linear API failures.** A flaky API call mid-batch could leave the epic created but children missing. Future enhancement: add idempotent batch operations.
4. **No peer-review issue creation yet.** Code-touching issues should get a companion `agent:agy-pro` peer-review issue (per the standard review loop). Currently manual.

## Next step

The agent swarm (AGY/Ned/Kai) will pick up the child issues on the next dispatcher tick (15min). Each agent routes to its lane based on the label:
- `agent:agy` → AGY Sandbox Supervisor
- `agent:kai-css` → Kai Delta Dispatcher
- `agent:ned` / `agent:ned-infra` → Ned Delta Dispatcher

The build proceeds through the canonical review loop (Worker → AGY peer review → Fred verify → Done).

## Change log
- 2026-06-23 06:50 UTC: Initial spec + script. Verified on Meridian Women's Defense build plan (1 epic + 13 children).