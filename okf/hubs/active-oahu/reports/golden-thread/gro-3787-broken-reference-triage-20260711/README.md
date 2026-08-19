---
type: Report
title: GRO-3787 Broken Internal Reference Triage + PWP Visual Audit
description: Timestamp UTC: `2026-07-11T20:29:32Z`
tags: [active-oahu, hub, migrated]
timestamp: 2026-08-19T14:27:09Z
status: current
resource: okf/hubs/active-oahu/reports/golden-thread/gro-3787-broken-reference-triage-20260711/README.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/active-oahu-tours-mirror
last_verified: 2026-08-19
verified_by: kai
---

# GRO-3787 Broken Internal Reference Triage + PWP Visual Audit

Timestamp UTC: `2026-07-11T20:29:32Z`

Source issue: [GRO-3787](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3787)
Site root scanned: `/home/ubuntu/work/aot-gro-3787-broken-ref-triage/site`

## Executive summary

The stale July 5 audit reported `1,139` broken/missing internal references. A fresh scan of current `origin/main` after the latest AOT work finds `518` remaining broken internal references across `310` HTML files.

The revenue-path slice is materially safer now: after patching the obvious booking/tour/rental references, the focused classifier finds **0 remaining `booking_revenue_path` broken references**. The remaining broken refs are mostly Cloudflare email-decoder noise, template-relative artifacts, Japanese locale/nav gaps, and one orphan author skip-link target.

## Bucket counts after patch

| Bucket | Count | Interpretation |
|---|---:|---|
| Cloudflare email decoder noise | 287 | Scanner sees Cloudflare `/cdn-cgi` email-decoder/protection URLs as local missing files; mostly not revenue-route defects. |
| Asset/template path | 172 | Broken relative assets or links inside templates/asset refs; needs separate cleanup, lower immediate booking risk. |
| Japanese locale/nav | 58 | JA alternate/nav targets missing or malformed; SEO/localization risk. |
| Orphan/author path | 1 | Legacy author/skip-link target. |
| Booking/revenue path | 0 | No remaining classified broken booking/tour/rental refs after this patch. |

## Safe revenue-path slice patched

| Source | Ref type | Old target | New target |
|---|---|---|---|
| `activities/rainforest-oahu-kayak-tour.html` | hreflang alternate | `https://activeoahutours.com/rainforest-oahu-kayak-tour.html` | `https://activeoahutours.com/activities/rainforest-oahu-kayak-tour.html` |
| `activities/kahana-rainforest-river-oahu-kayak-tour/index.html` | hreflang en | `https://activeoahutours.com/../rainforest-oahu-kayak-tour.html` | `https://activeoahutours.com/activities/kahana-rainforest-river-oahu-kayak-tour/` |
| `activities/kahana-rainforest-river-oahu-kayak-tour/index.html` | hreflang ja | `https://activeoahutours.com/../../ja/activities/kahana-rainforest-river-oahu-kayak-tour/index.html` | `https://activeoahutours.com/ja/activities/kahana-rainforest-river-oahu-kayak-tour/` |
| `oahu-kayaking-and-beach-adventures/ultimate-guide-to-lanikai-beach/index.html` | rental CTA fragment | `../../rentals/index#rental-gear` | `/rentals/index.html#rental-gear` |


These were selected because they were concrete file/path fixes with existing local targets and direct tour/rental context. I did not attempt to bulk-fix the full scanner output because most remaining rows are noise or lower-risk structural cleanup.

## Top remaining non-revenue cleanup candidates

| Priority | Bucket | Evidence / next action |
|---:|---|---|
| 1 | `japanese_locale_nav` | Fix repeated `/ja/rentals/index.html` and `/ja/rentals/` misses where a current JA rentals target can be verified. |
| 2 | `asset_template_path` | Fix template-relative `_templates/...` URLs by making template links root-relative before export. |
| 3 | `asset_template_path` | Repair missing `wp-content/uploads/...` image/icon refs or remove stale references if unused. |
| 4 | `orphan_author_path` | Replace remaining `/ja/author/mbgulden/index#content` style skip/author target with a live same-page `#content` pattern. |
| 5 | `cloudflare_email_decoder_noise` | Treat as scanner-noise unless the live page has visible email obfuscation/runtime failures. |

## PWP visual audit on new/recent pages

Audited these recent/new content surfaces at mobile `390x844` and desktop `1366x900` on the local patched site:

- `/guides/eating-your-way-windward-to-north-shore/`
- `/ja/guides/eating-your-way-windward-to-north-shore/`
- `/rentals/snorkel-gear-rentals/`
- `/ja/rentals/snorkel-gear-rentals/`
- `/multi-day-kayak-and-beach-gear-rentals/kayak-beach-gear-rental-partners/become-a-partner/`

PWP checks: HTTP status, H1 presence, horizontal overflow, visible-button count, and computed text contrast in page content/footer scopes. Initial run found low-contrast CTA/pricing/footer text; this patch fixes them.

| Page | Viewport | Status | Contrast issues after patch | Horizontal overflow | Buttons | Screenshot |
|---|---|---:|---:|---|---:|---|
| eating-guide | mobile | 200 | 0 | False | 3 | `/tmp/aot-pwp-eating-guide-mobile.png` |
| eating-guide | desktop | 200 | 0 | False | 3 | `/tmp/aot-pwp-eating-guide-desktop.png` |
| ja-eating-guide | mobile | 200 | 0 | False | 0 | `/tmp/aot-pwp-ja-eating-guide-mobile.png` |
| ja-eating-guide | desktop | 200 | 0 | False | 0 | `/tmp/aot-pwp-ja-eating-guide-desktop.png` |
| snorkel-rentals | mobile | 200 | 0 | False | 8 | `/tmp/aot-pwp-snorkel-rentals-mobile.png` |
| snorkel-rentals | desktop | 200 | 0 | False | 8 | `/tmp/aot-pwp-snorkel-rentals-desktop.png` |
| ja-snorkel-rentals | mobile | 200 | 0 | False | 7 | `/tmp/aot-pwp-ja-snorkel-rentals-mobile.png` |
| ja-snorkel-rentals | desktop | 200 | 0 | False | 7 | `/tmp/aot-pwp-ja-snorkel-rentals-desktop.png` |
| partner-signup | mobile | 200 | 0 | False | 2 | `/tmp/aot-pwp-partner-signup-mobile.png` |
| partner-signup | desktop | 200 | 0 | False | 2 | `/tmp/aot-pwp-partner-signup-desktop.png` |


Local static-server caveat: some pages still emit existing static-export console noise like `jQuery is not defined`, `wp is not defined`, or missing local-only resources. Those are not contrast/style failures from this patch and were not treated as PWP blockers.

## Artifacts

- `broken-reference-scan-after.json` — compact current scan summary.
- `pwp-visual-audit.json` — rendered local PWP audit output with screenshot paths.

## Recommended next slice

Do not chase all 518 rows blindly. Next safe implementation slice should be: **Japanese locale/nav cleanup for verified existing JA routes**, then template-relative asset cleanup. That keeps us on revenue/SEO risk instead of burning time on Cloudflare scanner noise.
