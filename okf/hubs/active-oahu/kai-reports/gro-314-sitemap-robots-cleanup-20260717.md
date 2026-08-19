---
type: Report
title: GRO-314 — Sitemap/robots cleanup follow-up (2026-07-17)
description: Implemented the SEO cleanup that was safe to do without Google Search Console credentials:
tags: [active-oahu, hub, migrated]
timestamp: 2026-08-19T14:27:09Z
status: current
resource: okf/hubs/active-oahu/kai-reports/gro-314-sitemap-robots-cleanup-20260717.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/active-oahu-tours-mirror
last_verified: 2026-08-19
verified_by: kai
---

# GRO-314 — Sitemap/robots cleanup follow-up (2026-07-17)

## Status

Implemented the SEO cleanup that was safe to do without Google Search Console credentials:

- Removed the two 404 page URLs from the production sitemap source at `site/sitemap.xml`:
  - `https://activeoahutours.com/404.html`
  - `https://activeoahutours.com/ja/404.html`
- Added the production sitemap directive to `site/robots.txt`:
  - `Sitemap: https://activeoahutours.com/sitemap.xml`

I did **not** submit the sitemap to Google Search Console because this cron still does not have a Search Console API OAuth/service-account credential with verified access, and Google no longer supports unauthenticated sitemap ping submission.

## Verification output

```text
xml_valid=True
loc_count=264
unique_loc_count=264
activeoahutours_count=264
contains_404_html=False
robots_has_sitemap=True
http://127.0.0.1:8093/robots.txt 200 265 has_sitemap_directive=True has_404=False
http://127.0.0.1:8093/sitemap.xml 200 53873 has_sitemap_directive=False has_404=False
```

## Fact-check gates

Named facts touched and verification method:

- Production sitemap URL `https://activeoahutours.com/sitemap.xml`: verified from the existing GRO-314 readiness audit and kept as the canonical robots directive target.
- Removed URLs `https://activeoahutours.com/404.html` and `https://activeoahutours.com/ja/404.html`: verified present in `site/sitemap.xml` before cleanup and absent after XML parse/loc-count verification.
- Sitemap URL count changed from 266 to 264: verified by parsing `site/sitemap.xml` with Python `xml.etree.ElementTree` after the edit.
- Google Search Console submission remains blocked: verified by prior credential audit in `reports/content/gro-314-sitemap-submission-readiness-20260716.md`; no new GSC credential was used or invented.

## Image/GPS verification

No imagery was selected, copied, edited, optimized, renamed, metadata-edited, reviewed, or placed. No NAS assets were touched.

## Next step

Open PR for the sitemap/robots cleanup. After merge/deploy, re-check live `https://activeoahutours.com/robots.txt` and `https://activeoahutours.com/sitemap.xml`, then submit the sitemap in Google Search Console once Michael provides browser-auth access or a Search Console API credential.
