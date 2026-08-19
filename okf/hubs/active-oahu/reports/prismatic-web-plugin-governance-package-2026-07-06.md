---
type: Report
title: Prismatic Web Governance Plugin Package — 2026-07-06
description: Finalize the Active Oahu governance work as a reusable Prismatic Web Plugin component, not just a one-off AOT fix.
tags: [active-oahu, hub, migrated]
timestamp: 2026-08-19T14:27:09Z
status: current
resource: okf/hubs/active-oahu/reports/prismatic-web-plugin-governance-package-2026-07-06.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/active-oahu-tours-mirror
last_verified: 2026-08-19
verified_by: kai
---

# Prismatic Web Governance Plugin Package — 2026-07-06

## Purpose

Finalize the Active Oahu governance work as a reusable Prismatic Web Plugin component, not just a one-off AOT fix.

## Package location

```text
prismatic-web-plugin/governance/
```

## Package contents

| Path | Purpose |
|---|---|
| `README.md` | Human install/operating guide for the governance package |
| `templates/prismatic-web-governance.json.tmpl` | Site-specific config template |
| `templates/prismatic-web-governance.yml.tmpl` | GitHub Actions workflow template |
| `scripts/install_prismatic_web_governance.py` | Stdlib installer that renders templates and copies the guard into a target repo |

The installer writes these files into a target website repo:

```text
.prismatic-web-governance.json
.github/workflows/prismatic-web-governance.yml
scripts/prismatic_web_governance.py
```

## Active Oahu validation baseline

The package is based on the recovered Active Oahu Tours state:

```text
production homepage HTTP 200
nav-fix.css?v=10 present
Active Oahu outfitter copy present
aot-quick-answer absent
open PRs = 0
origin/staging behind origin/main = 0
origin/main tree == origin/staging tree
```

## What makes it plugin-worthy

1. **Config-driven:** site-specific state lives in `.prismatic-web-governance.json`, not hardcoded scripts.
2. **Portable:** the guard is stdlib-only and shell-outs only to `git` and optional `gh`.
3. **CI-ready:** the workflow can run on schedule, manual dispatch, and pull requests.
4. **Cron-ready:** JSON output is suitable for Hermes no-agent watchdogs.
5. **Governance-aware:** it distinguishes deployable tree equality from history-only drift.
6. **Safe by default:** it reports stale branches but does not delete them automatically.
7. **Agent-compatible:** docs require guard evidence before staging/production/PR safety claims.

## Stale branch policy

The package intentionally does **not** auto-delete stale remote branches. Branch deletion requires owner/dependency review.

Required stale-branch review loop:

1. Generate the guard report.
2. Identify stale branches and authors.
3. Check for open PRs or recent work depending on each branch.
4. Check whether branch commits are reachable from `main` or patch-equivalent.
5. Delete only branches confirmed as archived, merged, or superseded.
6. Record deletion evidence in OKF or PR comments.

## Plugin install command shape

```bash
python3 prismatic-web-plugin/governance/scripts/install_prismatic_web_governance.py \
  --target /path/to/site-repo \
  --site-name "Example Site" \
  --repo owner/example-site \
  --production-url https://example.com/ \
  --staging-url https://example.pages.dev/ \
  --homepage-path site/index.html \
  --required-marker "Example Site" \
  --forbidden-marker "old-broken-block"
```

## Definition of done for a governed website

A site is governed when:

- the package artifacts are installed
- the guard compiles and writes Markdown + JSON reports
- live production markers are site-specific and pass
- production/staging branch state is understood and documented
- open PR queue is reviewed and clean or intentionally waived
- stale branch backlog is reported
- project OKF records define source-of-truth repos and ownership
- optional watchdog is scheduled for ongoing drift reports

## Conditional PWP QA modules

PWP visual/content QA should support conditional modules that activate based on site context, not only generic HTTP/layout checks.

The standing conditional added from AOT is **Cultural Diacritics & Search Compatibility**. It must trigger when a governed site is in Hawaiʻi, includes Hawaiian place names, already contains diacritical marks, or belongs to another culture/language where marks are meaningful and users may omit them in search.

When triggered, PWP reports should check:

- culturally correct visible place-name spelling;
- preservation of operational strings, domains, URLs, IDs, analytics labels, and vendor names;
- natural common/tourist search bridges;
- meta/schema/hreflang URL validity;
- malformed over-application such as `ActiveOʻahu.com`, `Hawaiʻian`, or diacritic-mutated slugs.

AOT-specific doctrine lives in:

- `okf/governance/cultural-diacritics-search-policy.md`
- `okf/reports/golden-thread/pwp-cultural-diacritics-conditional-20260712.md`

## Long-term Active Oahu model

Every future Active Oahu tourism-adjacent site should start with this package before content work begins. That keeps Michael from inheriting another messy branch/PR/staging tangle.
