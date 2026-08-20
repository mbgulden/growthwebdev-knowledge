---
name: okf-knowledge-capture
description: Capture user/business/project knowledge into the OKF without duplicating existing work. Use when the user asks to record, sync, consolidate, or update project knowledge, especially when prior OKF/docs/research may already exist.
---

# OKF Knowledge Capture

## Trigger

Use this skill when the user asks to:

- record information in the OKF
- sync new context with existing project/business docs
- consolidate project ideas, operating plans, research, or strategy notes
- make sure future agents do not duplicate already-completed research
- update a project knowledge base after a planning conversation

## Core principle

The job is not to create a pretty new document in isolation. The job is to preserve durable knowledge **inside the existing project structure** while making the next agent less likely to redo work.

Default stance: **source-map first, write second**. Existing OKF/docs/research artifacts are usually more valuable than a fresh standalone note.

## Workflow

1. **Locate the canonical project area**
   - Search likely roots: `~/work/<project>`, `~/work/growthwebdev-knowledge/okf`, project-specific `okf/`, `docs/`, `research/`, and related repo names.
   - Identify whether there is a hub OKF, spoke OKF, or both.
   - Prefer the project spoke OKF when it exists; cross-reference from indexes rather than duplicating content in multiple places.

2. **Read existing project context before writing**
   - Read project `README.md`, `okf/index.md`, `okf/research/index.md`, relevant docs, audit notes, and prior generated reports.
   - Look for existing lead lists, research nets, outreach kits, valuation scripts, templates, or operational workflows.
   - If the user explicitly says work already exists, treat that as a hard non-duplication requirement.
   - If the user later asks whether you found *all* prior content, do not defend the first pass; run a second content-map pass across adjacent repos, Drive/Gemini extraction scripts, research folders, and lead/contact databases, then write a dedicated map.

3. **Create or update the right artifact shape**
   - For a new consolidated note: add `okf/research/<topic>-<date>.md` with frontmatter.
   - For current-state pointers: update `okf/index.md` and/or `okf/research/index.md`.
   - For operational procedures: update `docs/` or link existing docs rather than burying SOPs in a research note.
   - When the user asks to document a workflow for both a project OKF and a live platform/domain (for example Belief Deprogrammer OKF plus humandesignengine.com docs), write the durable methodology/source-map note in the project spoke OKF, write or update a shorter operational mirror in the platform docs, update indexes/runbooks on both sides, and verify cross-repo links with a fresh `/tmp/hermes-verify-*` script.
   - For scripts/calculators: update existing `ops/` scripts rather than creating parallel tables.
   - For physical inventory/archive work, prefer a canonical NAS folder plus `sentinel-inventory-master.csv` over a prose-only report; Google Drive is for client exports/convenience copies, not the bulk source of truth.
   - When the user identifies a batch item from a photo/link (for example “10x HP DL380 Gen10”), immediately update the tracker row with known values and mark unknown specs as `TBD` rather than leaving an “unknown item” placeholder.
   - When consolidating a loose legacy folder into a canonical repo, migrate into domain folders (`docs/operations/`, `docs/outreach/`, `docs/partners/`, `docs/resale/`, `ops/`) and add a `docs/workspace-index.md` that marks the old folder as legacy source material.
   - When a project vision/gap audit needs to drive execution, capture the North Star, green-state rubric, source map, and operational-file governance in the project repo before or alongside task execution. Treat stray `/tmp`, profile, and runtime files as inventory/classification work first: copy reusable source into repo, summarize durable evidence into docs, and avoid deleting active cron/systemd inputs until references are repointed and verified. See `references/hde-north-star-okf-operational-consolidation-2026-07-18.md`.
   - When the user asks "where are we at for X?" after the North Star / rubric / source map are in place, the durable answer is a **state-of-things report** that triangulates Git + Linear + GitHub + live services against the canonical vision doc. Capture the pattern (not the answer) in a reference under `worktree-hygiene-and-cleanup-safety/references/2026-07-hde-state-of-things-audit.md` so the next audit reuses the same probes and drift categories.
   - For public trust/lead-generation website repos, create the operational trust collateral the site needs instead of only writing strategy docs: placeholder logo/public assets in `public/assets/`, printable receipts and sample certificates/logs/stickers in `docs/templates/`, workflow/tooling plans in `docs/operations/`, and downstream partner candidates in `docs/partners/`.

4. **Record non-duplication instructions explicitly**
   - If the user warns that a lead net, contact database, or prior research already exists, write an explicit section such as `Do not duplicate existing work`.
   - Name concrete artifacts already found.
   - Add a future-agent rule: locate and summarize the existing artifact before doing new research.

5. **Preserve user-provided facts as facts, not vague strategy**
   - Capture concrete values: location, capacity, phone/email/domain, equipment, constraints, target customer types, current bottlenecks, inventory priorities.
   - Separate facts from recommendations.
   - Mark capability gaps honestly; do not imply compliance/certification capabilities that are not yet established.

6. **Verify Markdown/script consolidation ad hoc when no canonical suite exists**
   - If no canonical test/lint/build exists, create a temporary script under `/tmp` with prefix `hermes-verify-`, or adapt `scripts/verify_okf_markdown.py` from this skill.
   - Check changed Markdown for non-empty content, frontmatter delimiters where expected, required user facts, non-duplication warnings, resolvable relative links, and cleanup of temporary helper files.
   - For repo consolidation that migrates scripts, also check expected migrated files exist, `.env`/`__pycache__` were not migrated, obvious secret literals are absent, moved Markdown links resolve, and Python scripts compile with `python3 -m py_compile`; remove any generated `__pycache__` afterward.
   - For public static website repos with no suite, verify changed artifacts exist, HTML parses, required lead/trust copy is present, compliance caveats are present, custom-domain marker files such as `CNAME` are correct, and the site serves locally with HTTP 200 from a simple static server.
   - When a website style preference is corrected (for example: “light theme, not dark background”), codify it as a theme invariant in docs/tokens/components/verifiers — not just a one-line CSS patch. For Sentinel specifically, the global site must stay light; dark backgrounds are scoped to modules, buttons, banners, or selected sections only.
   - When static marketing repos begin migrating to Astro/EmDash, keep the current static `public/` deployment working while adding Astro-ready `src/` structure, theme tokens, standard modules, content schema, gated EmDash integration, and a verifier. Gate EmDash behind an env var so normal static builds do not require CMS database/Cloudflare bindings.
   - When planning reusable PWP/Astro theme systems, use open-standard package thinking instead of page-template thinking: theme manifests, W3C-style design tokens, Style Dictionary-compatible transforms, Astro module contracts, JSON Schema/Zod validation, EmDash edit maps with locked fields, visual/a11y/performance gates, deployment provenance, and phased delivery. If working in Prismatic Engine under Ned, put PWP-specific docs under `plugins/pwp/docs/` rather than top-level `docs/` unless explicitly routed.
   - When checking compliance wording, avoid naive substring bans that flag negated safety rules like “Do not claim X”; distinguish those from unqualified positive claims.
    - When checking compliance wording, avoid naive substring bans that flag negated safety rules like “Do not claim X”; distinguish those from unqualified positive claims.
   - When checking compliance wording, avoid naive substring bans that flag negated safety rules like “Do not claim X”; distinguish those from unqualified positive claims.
   - Run `git diff --check` before committing; legacy docs often carry trailing whitespace.
   - Run it, remove any temporary script/helper files, and report the result as **ad-hoc verification**, not suite green.
   - If an external verifier insists on a canonical command such as `npm run test`, run it and quote the result. If the command is a placeholder (`Error: no test specified`), say canonical verification is blocked by the placeholder and keep the ad-hoc result clearly separate.
   - If the system repeats a stale/failed verification nudge, rerun a fresh verifier instead of arguing from prior output. Prefer `tempfile.mkstemp(prefix="hermes-verify-", dir="/tmp")` so the verifier path is OS-safe and visibly satisfies the `/tmp/hermes-verify-*` requirement; remove it afterward and report the run as **ad-hoc verification**, not suite green.
   - For OKF work that also posts Linear cross-reference comments (the typical "OKF authored + Linear trail" workflow where the durability requirement is bidirectional linking), **use `scripts/verify_okf_with_linear_trail.py` from this skill** before writing a bespoke `/tmp/hermes-verify-*` script. It accepts CLI args for `--entry-path`, `--section-index`, `--top-index`, `--linear-ids`, `--okf-link-marker`, and `--env-file`, asserts all four legs (entry shape, section index link, top index link + preservation, Linear comment trail), and prints `OVERALL: PASS/FAIL`. The pattern was extracted from the 2026-07-29 Zapier CLI OKF runbook work (GRO-4373..4376). Run it directly from the project repo or copy it to `/tmp/hermes-verify-okf-<topic>.py` per the temp-prefix pattern.

## Recommended OKF frontmatter

```yaml
---
type: Research Note
title: <Project/Topic> — <Short Description>
description: <One-sentence description>
resource: <absolute path or canonical URL>
tags: [research, project-name, topic]
timestamp: <UTC ISO timestamp>
linear_issue: null
git_repo: <owner/repo>
git_path: <repo-relative path>
last_verified: <YYYY-MM-DD>
verified_by: <agent-name>
status: current
---
```

## Pitfalls

- Do **not** build a new lead list if the user says a mature lead/contact net already exists. First find, link, and dedupe against the existing net.
- Do **not** stop at the first OKF/repo hit when the user emphasizes prior work exists; check adjacent project worktrees, research folders, local Drive/Gemini extraction scripts, and existing lead/contact JSON/Markdown.
- Do **not** leave a split-brain project once the canonical repo is identified. Copy valuable loose-folder docs/scripts into the canonical repo, mark the old folder as legacy source material, and add a workspace index.
- Do **not** migrate `.env`, credentials, local caches, or `__pycache__` from legacy folders.
- Do **not** forget to repair relative links after moving docs between `docs/operations/`, `docs/partners/`, etc.
- Do **not** turn a planning conversation into a one-off orphan file with no index links.
- Do **not** overclaim compliance, certification, or data-destruction capability. Record current capability and gaps separately.
- Do **not** overwrite unrelated dirty files in the repo. Stage and commit only the paths you intentionally changed.
- Do **not** leave temporary extraction/verification helpers behind; clean `/tmp/hermes-verify-*`, `/tmp/hermes-<project>-*` extraction folders, and any workspace-local `hermes_tmp_*` files you created.
- Do **not** claim full suite verification for Markdown/doc-only OKF work unless a real canonical suite ran. If `npm run test` is a placeholder that exits with `Error: no test specified`, report that as a blocker to canonical verification rather than “repairing” unrelated package scripts.
- Do **not** assume remembered Gemini content lives in the current extracted Gemini conversation JSON. It may instead be a Google Doc generated from Gemini, a My Activity export, or a different Takeout archive on NAS. Search/map the sources and record the caveat instead of declaring the remembered conversations absent.
- Do **not** raw-mirror huge Gemini/Drive strategy reports into the repo by default. Distill them into clean canonical summaries under the correct class folder (`docs/strategy/`, `docs/compliance/`, `docs/outreach/`) with Drive IDs and source-map links.
- **Do not deliver infrastructure facts via memory alone.** Host-specific hardware/access facts (Tailscale IPs, RAID topology, controller quirks, backup-chain details, drive bay mappings) **belong in the OKF** as the source of truth — `okf/standards/<host>-<topic>.md` for durable facts, `okf/operations/<date>-<topic>.md` for date-prefixed observations. Michael's standing rule: "infrastructure facts go to the OKF on the server, not memory." Memory is for cross-host pointers and agent-continuity facts; the full fact set lives in the OKF where any future agent can `read_file` without burning tokens on retrieval. Pair with the audit's class-level skill (e.g. `proxmox-raid-storage-audit`) for the canonical workflow.

## Reference files

- `references/sentinel-itad-okf-sync-2026-07-07.md` — Session-specific example of syncing Sentinel ITAD operating facts with an existing OKF, doing a second content-map pass across Drive/research/lead artifacts, and explicitly avoiding duplicate lead research.
- `references/sentinel-itad-repo-consolidation-2026-07-08.md` — Session-specific example of consolidating a loose legacy folder into the canonical project repo, adding a workspace index, skipping secrets/transients, repairing moved-doc links, and verifying migrated docs/scripts.
- `references/sentinel-itad-drive-gemini-ingestion-2026-07-08.md` — Session-specific example of exploring Drive/Gemini/Takeout/NAS sources, distinguishing generated Google Docs from Gemini conversation exports, writing source maps, summarizing primary Drive docs, and building a deduped lead/contact view.
- `references/sentinel-itad-valuation-extension-2026-07-08.md` — Session-specific example of extending an existing deterministic valuation script/table for newly identified inventory classes, adding an inspect mode, regenerating derived docs, and using OS-safe `/tmp/hermes-verify-*` ad-hoc verification when no canonical suite exists.
- `references/sentinel-itad-nas-inventory-tracker-2026-07-08.md` — Session-specific example of choosing NAS as the canonical Sentinel inventory archive, seeding the master CSV, converting “I have 10 of these” photo/link input into a real tracker row, and keeping Google Drive as export/share surface only.
- `references/sentinel-itad-website-repo-launch-2026-07-09.md` — Session-specific example of creating a separate public `sentinelitad.com` website repo, seeding a static trust/lead-generation site, keeping operations private in the canonical SIAL repo, documenting DNS rather than changing it without approval, and using `/tmp/hermes-verify-*` ad-hoc static-site verification.
- `references/sentinel-itad-astro-theme-emdash-2026-07-09.md` — Session-specific example of turning a public static marketing site into a codified light-theme system with Astro-ready modules, gated EmDash integration, typed tokens, redesign docs, and theme verification.
- `references/pwp-ai-first-astro-theme-system-2026-07-09.md` — Session-specific example of producing a PWP-level AI-first Astro theme-system master plan using open standards, phased delivery, EmDash edit maps, PWP provenance, and lane-correct `plugins/pwp/docs/` placement.
- `references/sentinel-itad-light-theme-cloudflare-pages-2026-07-09.md` — Session-specific follow-up covering Michael’s light-theme correction for trust/lead sites, MSP/pickup page expansion, Cloudflare Pages direct deployment/custom-domain pattern, and focused static-site verification checks.
- `references/sentinel-itad-light-theme-cloudflare-pages-2026-07-09.md` — Follow-up example capturing Michael’s light-theme preference for public trust sites, Cloudflare Pages setup/deploy/DNS workflow, ITAD trust artifact starter set, and theme-specific ad-hoc verification checks.
- `references/sentinel-itad-cloudflare-trust-artifacts-2026-07-09.md` — Session-specific example of updating public brand/email/insurance facts, adding trust collateral templates, deploying to Cloudflare Pages, adding custom domains/DNS, and verifying static/docs artifacts with a fresh `/tmp/hermes-verify-*` script.
- `scripts/verify_okf_markdown.py` — Reusable targeted Markdown verifier for OKF/doc-only updates; copy or run it for ad-hoc verification when no canonical suite exists.
- `scripts/verify_static_website_docs.py` — Reusable static marketing-site/docs verifier; copy it to a `/tmp/hermes-verify-*` script or adapt it when a public static website repo lacks a canonical test suite.
