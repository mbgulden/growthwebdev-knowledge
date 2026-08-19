---
type: Reference
title: Photo Library Mapping Strategy — Active Oahu Tours
description: Strategy for indexing and deploying the 14,490 photos in the Synology NAS library (/home/ubuntu/mounts/synology-photo/Active Oahu's shared workspace) to activeoahutours.com pages. Maps categories to revenue pages with priority queues and alt-text style guide.
tags: [photos, aot, content, mapping, asset-library, priority]
timestamp: 2026-06-19T13:00:00Z
linear_issue: null
git_path: okf/photos/mapping-strategy.md
status: current
visibility: private
photo_root: /home/ubuntu/mounts/synology-photo/Active Oahu's shared workspace
total_estimated_files: 14490
resource: okf/hubs/active-oahu/seo/photos/mapping-strategy.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/aot-seo-knowledge
last_verified: 2026-08-19
verified_by: kai
---

# Photo Library Mapping Strategy — Active Oahu Tours

## Library overview

The Synology NAS photo library at `/home/ubuntu/mounts/synology-photo/Active Oahu's shared workspace/` holds an estimated **14,490 files** across 19 top-level categories. The library is already organized by Michael into tour-specific subfolders — most of the mapping work below is connecting existing folders to AOT website pages.

### Top-level categories

| Category | Size hint | Content type |
|---|---|---|
| **Tour & Rental Package Images/** | 1 GB | **The crown jewel** — subfoldered per tour (Kayaking - Chinamans Hat, Snorkeling - Sharks Cove, etc.). This is the directly deployable set. |
| `_All Tour & Rental Photos/` | 2.8 GB | High-res 360 lifestyle photos (Active Oahu Lifestyle-313.jpg etc.). Hero shots for pages. |
| `_Active Oahu/` | 832 MB | Curated AOT-specific imagery |
| `Photos and Videos/` | 11 GB | Dated session archives (e.g., "10.1.20 Sony - Mokes Kayaking"). The bulk — needs curation. |
| `Kailua Photos and Videos/` | 584 MB | Kailua-specific b-roll + drone footage |
| `Edited Photos/` | 34 MB | Final-edited outputs ready for marketing |
| `Blog Posts/` | 130 MB | Blog post imagery |
| `Company Documentation/` | 1.5 GB | Logos, branding assets, business docs |
| `Instructional Videos/` | 624 MB | How-to content |
| `Profile Pics/` | 60 MB | Founder/team portraits |
| `Reseller Contracts/` | 638 MB | Business docs |
| `Waikiki Advertisement/` | 98 MB | Waikiki ad campaigns |
| `Vacation Rentals/` | 260 MB | Vacation rental partner imagery |
| `Wordpress Plugins/` | 968 MB | Plugin source archives |
| `All Finished Videos/` | 614 MB | Finished video cuts |
| `SD dump 4.9/` | 14 MB | One SD card dump |

---

## Folder → Page Mapping (P0 priority)

These are the highest-impact mappings. Each tour/rental package subfolder maps directly to an existing AOT page.

### Kayaking tours

| Source folder | Target AOT page | Priority | Notes |
|---|---|---|---|
| `Tour & Rental Package Images/Kayaking - Chinamans Hat/` | `/activities/chinamans-hat-self-guided-oahu-kayak-tour/` | **P0** | AOT's #1 keyword is `chinaman's hat kayak` (per baseline audit). Page is weak on imagery — high ROI. |
| `Tour & Rental Package Images/Kayaking - Mokulua Islands Self-Guided Kayak Adventure/` | `/activities/kailua-bay-mokulua-island-self-guided-kayak-tour/` | **P0** | "mokulua islands kayak" is position #7 striking-distance. |
| `Tour & Rental Package Images/Kayaking - Kaneohe Bay Sandbar Experience/` | `/oahu-kayaking-and-beach-adventures/kaneohe-sandbar-kayak-experience/` | **P0** | AOT owns position #1 for `kaneohe sandbar kayak` — page must be visually stunning. |
| `Tour & Rental Package Images/Kayaking - Kaneohe Bay 10 Reef Adventure/` | `/oahu-kayaking-and-beach-adventures/` (general hub) | P1 | Reef tour, currently under-promoted |
| `Tour & Rental Package Images/Kayaking - Kailua Bay & Popoia Island Self-Guided/` | `/oahu-kayaking-and-beach-adventures/popoia-island-and-kailua-bay-guided-kayak-tour/` | **P0** | Beginner-friendly tour with high conversion intent |
| `Tour & Rental Package Images/Kayaking - Kahana Rainforest River/` | `/activities/kahana-rainforest-river-oahu-kayak-tour/` | **P0** | River kayaking — unique offering |
| `Tour & Rental Package Images/Kayaking - Kawela Bay/` | (no AOT page yet — needs creation) | P1 | North Shore kayak tour |

### Snorkeling tours

| Source folder | Target AOT page | Priority | Notes |
|---|---|---|---|
| `Tour & Rental Package Images/Snorkeling - Sharks Cove/` | `/activities/sharks-cove-self-guided-snorkel/` | **P0** | AOT ranks #3 for `sharks cove snorkeling` (124 clicks/mo). Strong page already — keep imagery fresh. |

### E-bike tours

| Source folder | Target AOT page | Priority | Notes |
|---|---|---|---|
| `Tour & Rental Package Images/Electric Bike - Kailua Rental/` | `/tours/` (e-bike landing) | **P0** | E-bike rental page is weak. Need 10+ high-quality images. |
| `Kailua Photos and Videos/Ebike for Web Edited Photos/` | `/tours/` | **P0** | Already "Edited for Web" — drop-in ready |

### Standup paddleboard (SUP)

| Source folder | Target AOT page | Priority | Notes |
|---|---|---|---|
| `Tour & Rental Package Images/Standup Paddleboarding - Haleiwa SUP/` | `/rentals/oahu-stand-up-paddle-board-rentals-sup-hire/` | **P0** | SUP is AOT's **#1 traffic page (845 visits/mo)**. Page must be world-class. |
| `Tour & Rental Package Images/Standup Paddleboarding - Kahana/` | `/oahu-equipment-rentals/` (SUP listing) | P1 | Kahana SUP variant |
| `Tour & Rental Package Images/Surfing - Laie Lessons/` | `/oahu-equipment-rentals/` (surf lessons) | P2 | North Shore offering |

### Yoga, Hiking, Misc

| Source folder | Target AOT page | Priority | Notes |
|---|---|---|---|
| `Tour & Rental Package Images/Hiking - Kahana/` | `/oahu-kayaking-and-beach-adventures/` (or new hiking page) | P2 | Hiking is a complementary offering |
| `Tour & Rental Package Images/Yoga - Destination/` | (no AOT page — partner service) | P3 | Likely partner imagery |

### Lifestyle / Hero shots

| Source folder | Target | Priority | Notes |
|---|---|---|---|
| `_All Tour & Rental Photos/Active Oahu Lifestyle-3XX.jpg` (15+ files, 25-40 MB each, high-res 360) | All revenue pages — replace placeholder hero images | **P0** | These are the premium lifestyle shots. Best of the library. Use as hero image + 2-3 inline shots per revenue page. |
| `Edited Photos/` (34 MB final outputs) | Ad creative + meta OG images | **P0** | Pre-edited for web — no post-processing needed |

### Beach + scenery

| Source folder | Target | Priority | Notes |
|---|---|---|---|
| `Kailua Photos and Videos/Kailua Kayak Tour Photos/` | Kailua guide + tour pages | P1 | Authentic in-action imagery |
| `Kailua Photos and Videos/Kailua - Lanikai Snorkel Photos/` | Lanikai guide | P1 | |
| `Kailua Photos and Videos/Mokulua, Popoia & Ebikes/` | Mokulua tour pages | P1 | |
| `Kailua Photos and Videos/Raw Photos From Drone Videos/` | Aerial / hero shots for ALL beach pages | P1 | Drone footage frames |

### Blog + guide pages

| Source folder | Target | Priority | Notes |
|---|---|---|---|
| `Blog Posts/` (130 MB) | /guides/* and new blog posts | P1 | Review file dates — most recent first |
| `Photos and Videos/15.6.25 Paddleboard Haleiwa/` | Haleiwa SUP blog post | P2 | Recent session, ready to use |

---

## Per-page photo requirements (page → photo)

### Top 20 revenue pages — current state vs. needed

| Page | Current Photos (est.) | Recommended | Photos needed |
|---|:---:|:---:|:---:|
| `/` (homepage) | 5-8 | 12+ | 5-7 new hero/lifestyle |
| `/tours/` (e-bike + guided) | 6-10 | 15+ | 5-9 new (ebike folder) |
| `/rentals/` | 4-6 | 12+ | 6-8 (SUP + kayak + snorkel) |
| `/rentals/oahu-tandem-kayak-rentals/kailua-kayak-rentals/` | 5-8 | 12+ | 4-7 new |
| `/rentals/oahu-stand-up-paddle-board-rentals-sup-hire/` | 8-12 | 15+ | 3-7 new (page is already strong) |
| `/rentals/oahu-snorkel-mask-and-fin-rentals/` | 3-5 | 10+ | 5-7 new |
| `/activities/chinamans-hat-self-guided-oahu-kayak-tour/` | 4-6 | 10+ | **4-6 new (P0)** |
| `/activities/kailua-bay-mokulua-island-self-guided-kayak-tour/` | 4-6 | 10+ | **4-6 new (P0)** |
| `/activities/sharks-cove-self-guided-snorkel/` | 6-10 | 12+ | 2-6 new |
| `/activities/kahana-rainforest-river-oahu-kayak-tour/` | 3-5 | 10+ | **5-7 new (P0)** |
| `/oahu-kayaking-and-beach-adventures/kaneohe-sandbar-kayak-experience/` | 5-8 | 12+ | 4-7 new (position #1 — must look great) |
| `/oahu-kayaking-and-beach-adventures/popoia-island-and-kailua-bay-guided-kayak-tour/` | 3-5 | 10+ | **5-7 new (P0)** |
| `/guides/kailua-beach-park-guide/` | 3-5 | 10+ | 5-7 new |
| `/guides/lanikai-beach-guide/` | 3-5 | 10+ | 5-7 new |
| `/guides/waimanalo-beach-guide/` | 3-5 | 10+ | 5-7 new (per GRO-795 priority) |
| `/guides/best-beaches-windward-oahu/` | 5-8 | 15+ | 7-10 new (per GRO-795 master pillar) |
| `/guides/things-to-do-in-kailua/` | 2-3 | 8+ | 5-6 new |
| `/guides/things-to-do-in-waimanalo/` | 2-3 | 8+ | 5-6 new |
| `/about/` | 4-6 | 8+ | 2-4 new (team/staff) |
| `/contact/` | 1-2 | 4+ | 2-3 new (storefront, staff) |

**Total estimated photos needed:** ~150-200 new image placements (some pages use the same image, but each page needs 4-10 unique shots).

---

## Priority queue (deploy order)

### P0 — deploy in Month 1 (next 30 days)
- **5 high-traffic pages**: SUP rental, Sharks Cove, Kailua kayak, Kaneohe Sandbar, Mokulua Islands
- **Striking-distance pages**: Chinamans Hat, Popoia Island, Kahana River
- **E-bike rental page**: needs 8+ new e-bike images

### P1 — deploy in Month 2-3
- **3 hub guide pages**: Kailua, Lanikai, Waimanalo (per GRO-795)
- **Pillar page**: Best Beaches Windward Oahu
- **Blog posts**: 5-8 new posts using blog/ folder imagery
- **Lifestyle refresh**: Update homepage hero with Active Oahu Lifestyle-3XX shots

### P2 — deploy in Month 3-6
- **About + Contact pages**: storefront, team photos, branded imagery
- **Seasonal campaigns**: hero rotation by season
- **Hiking + partner services**: Hiking - Kahana folder

### P3 — archive
- Reseller Contracts, WordPress Plugins, raw video dumps — keep on NAS, don't deploy

---

## Alt-text style guide

Each photo deployed to the site needs:
1. **Filename** (kept as-is, but normalize spaces to hyphens for SEO)
2. **Alt text** (max 125 chars, descriptive, includes location + activity + mood)
3. **Caption** (1 sentence, AOT brand voice: friendly, local, knowledgeable)
4. **Credit** (photographer, if not Michael)

### Alt text templates

**For action shots (kayaking, SUP, snorkeling):**
> "[Activity] [location], Oahu — [subject detail]"

Examples:
- `alt="Kayakers paddling toward Chinaman's Hat island, Oahu"`
- `alt="Standup paddleboarder on calm Kailua Bay at sunrise"`
- `alt="Snorkeler viewing Hawaiian green sea turtle at Sharks Cove, Oahu"`

**For scenery/landscape:**
> "[Location] view, [mood/time of day]"

Examples:
- `alt="Lanikai Beach sunrise panorama, Mokulua Islands in distance"`
- `alt="Aerial drone shot of Kaneohe Sandbar at low tide"`
- `alt="Kailua Beach Park shoreline with Na Mokulua islands"`

**For group/family shots:**
> "[Group description] [activity] at [location]"

Examples:
- `alt="Family of four on guided kayak tour in Kailua Bay"`
- `alt="Couple on e-bike exploring Kailua neighborhood"`

**Brand-voice caption template:**
> "[Sensory detail + personal moment + AOT call-to-action]"

Examples:
- *"Glassy morning waters at Chinaman's Hat — paddling out with friends is the Oahu morning we want every guest to have. Book your self-guided kayak rental today."*

### Don'ts
- ❌ Don't use generic alt text like "image1.jpg" or "photo"
- ❌ Don't stuff keywords ("kayak rental Oahu kayak Oahu best kayak kayak kayak")
- ❌ Don't use the same alt text on multiple photos
- ❌ Don't omit alt text (Google penalizes for AI Overview eligibility)

---

## Workflow: Adding photos to a page

1. **Select 3-5 photos** from the appropriate subfolder based on the per-page photo requirements table above
2. **Rename files** for SEO (kebab-case, descriptive)
3. **Compress** if over 2 MB (Cloudflare Pages serving speed)
4. **Upload** to `site/assets/images/<page-slug>/`
5. **Write alt text + caption** per style guide
6. **Update page HTML** with `<img src="..." alt="..." />` tags
7. **Update OG image** if this is the page's primary hero (for social shares)
8. **Verify** the page still loads correctly (Cloudflare Pages auto-deploys)

**Automation opportunity:** A Python script could:
1. Read `assets/images/<page-slug>/`
2. Auto-generate alt text candidates using filename heuristics
3. Push them to Linear as a content production task for Ella to review + finalize

---

## Cloudflare Images recommendation

Currently AOT hosts all images on the static site via Cloudflare Pages. With 14,490 photos (even if only 500 are deployed), the deployment bundle size grows. Consider:

- **Cloudflare Images** ($5/mo for 100K images, $1/100K transforms) — auto-resize, WebP conversion, CDN delivery
- **Cloudflare R2** + **Cloudflare Image Resizing** — cheaper if most images are archival
- **R2 alone** ($0.015/GB/mo) — for the 14,490 photos that aren't deployed, just kept on the NAS cloud mirror

**Recommendation:** Stay on direct Cloudflare Pages hosting for the ~200 deployed photos. Use the existing Synology NAS as the archival cold-store. No need for Cloudflare Images until traffic justifies it.

---

## Sample photo index (first 50 from priority subfolders)

A machine-readable index of priority photos is being built at `okf/photos/photo-index.json`. Currently tracks ~200 sampled photos from priority subfolders. To extend, run:

```bash
python3 okf/photos/build_full_index.py
```

(Future — will scan all 14,490 photos with metadata extraction, EXIF parsing, GPS coordinates for geo-tagged SEO.)
