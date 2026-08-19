---
type: Report
title: GRO-3101 image aspect-ratio follow-up — 2026-07-16
description: Opened branch `content/gro-3101-image-aspect-ratio` from `origin/main` to address the most actionable Lighthouse Best Practices blocker found in the 2026-07-16 GRO-3101 production re-check: incorrect aspect-ratio attribu
tags: [active-oahu, hub, migrated]
timestamp: 2026-08-19T14:27:09Z
status: current
resource: okf/hubs/active-oahu/kai-reports/gro-3101-image-aspect-ratio-fix-20260716.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/active-oahu-tours-mirror
last_verified: 2026-08-19
verified_by: kai
---

# GRO-3101 image aspect-ratio follow-up — 2026-07-16

## Scope

Opened branch `content/gro-3101-image-aspect-ratio` from `origin/main` to address the most actionable Lighthouse Best Practices blocker found in the 2026-07-16 GRO-3101 production re-check: incorrect aspect-ratio attributes for `/wp-content/uploads/2022/01/Mokolii-from-above-view-1.jpg` when rendered as `.front-page-img-bg`.

No force-pushes to shared branches and no direct push to `main` were performed. The PR branch was later updated with `--force-with-lease` after ad-hoc verification found 5 additional relative-src target tags that needed the same attribute fix.

## Change made

Updated the repeated static/template `<img>` dimensions for `/wp-content/uploads/2022/01/Mokolii-from-above-view-1.jpg` from `width="724" height="583"` to the actual repository image dimensions `width="820" height="615"`.

Implementation used an `HTMLParser`-based script that only touched matching `<img>` start tags with the target `src`; no regex-based bulk HTML rewrite was used.

Files changed: 68 tracked HTML/template files, including `site/index.html`, `site/_templates/body_bottom.html`, and 5 additional relative-src guide pages caught by ad-hoc verification.

## Verification output summary

```text
python3 /tmp/fix_mokolii_aspect.py
Actual image dimensions: 820x615
Files changed: 63

python3 /tmp/hermes-verify-fix-gro3101-relative-src.py
Actual image dimensions: 820x615
Additional files changed: 5
```

```text
PIL image verification
site/wp-content/uploads/2022/01/Mokolii-from-above-view-1.jpg (820, 615)
```

Ad-hoc verification script `/tmp/hermes-verify-gro3101-aspect.py` (removed after run):

```text
AD-HOC VERIFY PASS
intrinsic_image_size=820x615
target_img_tags_checked=68
dimension_counts={('820', '615'): 68}
all_target_img_attrs=width="820" height="615"
report_checked=okf/kai-reports/gro-3101-image-aspect-ratio-fix-20260716.md
```

Local rendered Lighthouse check against `python3 -m http.server 8087 --directory site`:

```text
scores {'performance': 84, 'accessibility': 96, 'best-practices': 100, 'seo': 100, 'agentic-browsing': 99}
image-aspect-ratio score=1 — Displays images with correct aspect ratio — items 0
```

Artifact: `reports/lighthouse-cycle-001-cron/20260716T-gro-3101-aspect-fix/lighthouse-local-desktop.json`

## Fact-check gates

No public copy, product claims, prices, routes, safety guidance, or operational content were changed. Named facts checked:

- PR #20 / GRO-3101 blocker context was taken from the fresh Lighthouse JSON/report already generated in `reports/lighthouse-cycle-001-cron/20260716T150547Z-gro-3101-cron-recheck/`.
- The actual image dimensions were verified from the repository image file with PIL: `820x615`.
- The Lighthouse result was verified from a fresh local run against the changed workspace.

## Image/GPS verification

- Intended subject/location claim: unchanged existing image asset, `/wp-content/uploads/2022/01/Mokolii-from-above-view-1.jpg`, used by existing site sections; no new factual imagery placement was introduced.
- Legal/source status: existing repository image already used by the site; no new third-party image was selected.
- GPS/location: no new GPS/location claim was added. This change only corrects HTML width/height attributes to match the image file's intrinsic pixel dimensions.
- NAS: no Synology/NAS original was accessed, copied, altered, optimized, resized, renamed, metadata-edited, or direct-linked.
