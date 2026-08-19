---
type: Index
title: Photo Library Mapping
description: Index of the Synology NAS photo library (14,490 photos) mapped to activeoahutours.com pages.
tags: [index, photos, aot, mapping, asset-library]
timestamp: 2026-06-19T13:00:00Z
linear_issue: null
git_path: okf/photos/index.md
status: current
resource: okf/hubs/active-oahu/seo/photos/index.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/aot-seo-knowledge
last_verified: 2026-08-19
verified_by: kai
---

# Photo Library Mapping

The Synology NAS at `/home/ubuntu/mounts/synology-photo/Active Oahu's shared workspace/` holds ~14,490 photo + video files across 19 top-level categories.

## Documents

| File | Purpose | Status |
|---|---|---|
| [mapping-strategy.md](./mapping-strategy.md) | Complete strategy: folder → page mapping, priority queue (P0/P1/P2/P3), per-page photo requirements, alt-text style guide, deployment workflow | current |
| [photo-index.json](./photo-index.json) | Machine-readable sample index of ~200 priority photos from key subfolders | sample (~200/14490) |

## TL;DR

The library is **already organized** by Michael into tour-specific subfolders. Most mapping work is connecting existing folders to AOT website pages.

**Top 5 highest-impact deployments (P0, Month 1):**
1. SUP rental page — AOT's #1 traffic page (845 visits/mo). Use Haleiwa + Kahana SUP folders.
2. Sharks Cove snorkeling — AOT ranks #3 (124 clicks/mo). Refresh imagery.
3. Kailua kayak rental — Position #2 (46 clicks/mo). Refresh imagery.
4. Kaneohe Sandbar kayak — AOT owns position #1 (59 clicks/mo). Page must be world-class.
5. Chinamans Hat kayak — Position #1 but low CTR. Add more photos + FAQ schema.

**Estimated photos needed:** 150-200 new image placements across top 20 revenue pages.

## Quick wins

- **Use Active Oahu Lifestyle-3XX.jpg series** (15+ files, 25-40 MB each) as homepage hero and lifestyle imagery. These are 360-degree professional photos.
- **Use `Edited Photos/`** (34 MB final outputs) for ad creative — already web-optimized.
- **Map `Tour & Rental Package Images/`** subfolders directly to AOT pages — the folder names match the tour names almost 1:1.

## Sample photo index

A machine-readable JSON index of priority photos is at [photo-index.json](./photo-index.json). Currently a sample of ~200 photos from priority subfolders. Full library scan would take ~10 minutes and produce ~14,000 entries.

## What still needs work

- [ ] Full library scan (14,490 photos with EXIF metadata + GPS coordinates for geo-SEO)
- [ ] Image compression pipeline (Cloudflare Images integration)
- [ ] Photo selection automation (auto-suggest best photos per page based on category)
- [ ] Alt-text generation (filename + AI vision captioning for bulk drafts)
- [ ] Watermark + brand overlay automation

See [mapping-strategy.md](./mapping-strategy.md) for the full priority queue, per-page photo requirements, and alt-text style guide.
