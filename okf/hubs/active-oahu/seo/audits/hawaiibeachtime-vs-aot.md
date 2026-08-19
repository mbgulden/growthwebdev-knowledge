---
type: Audit
title: Visual Inspection: hawaiibeachtime.com vs activeoahutours.com
description: Head-to-head competitor visual audit — site structure, page layout, content depth, schema, technical SEO.
tags: [aot, seo, geo, ai-seo, migrated-from-existing]
timestamp: 2026-06-19T12:28:24Z
linear_issue: null
git_path: okf/audits/hawaiibeachtime-vs-aot.md
status: current
migrated_from: /home/ubuntu/hawaiibeachtime_analysis.md
visibility: private
resource: okf/hubs/active-oahu/seo/audits/hawaiibeachtime-vs-aot.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/aot-seo-knowledge
last_verified: 2026-08-19
verified_by: kai
---

# Visual Inspection Report: hawaiibeachtime.com vs activeoahutours.com

## Methodology
- Visited homepages, /works/ (products), /contact/, /oahu-beach-guide/, /waikiki-snorkel-rentals/ on hawaiibeachtime.com
- Visited homepage, /contact-us/, /faq/, /about-active-oahu-tours/awards/ on activeoahutours.com
- Extracted DOM structure, schema markup, heading hierarchy, navigation, metadata, and page content

---

## 1. SITE STRUCTURE & NAVIGATION

### Hawaii Beach Time
- **Platform:** Custom WordPress theme "beach_apollo"
- **Navigation:** Single-level flat menu — HOME | GEAR | PACKAGES | HOW IT WORKS | BEACH BLOG | GO OAHU CARD | OAHU BEACH GUIDE | CONTACT
- **Site issues:**
  - /gear/ returns **403 Forbidden**
  - /packages/ returns **404 Not Found**
  - /how-it-works/ returns **404 Not Found**
  - /go-oahu-card/ returns **404 Not Found**
  - /beach-blog/ returns **404 Not Found**
  - /chinamens-hat-kayaking-kaneohe-sand-bar-kayaking/ returns **404 Not Found**
  - **Only 4 pages actually work:** Home, /works/ (products), /contact/, /oahu-beach-guide/, /waikiki-snorkel-rentals/
  - Many nav links point to broken/empty pages — this is a critical user experience failure
- **Nav behavior:** Clicking "GEAR" in nav actually goes to /works/ (product listing page), not /gear/
- **404 page sitemap reveals spam:** Blog category list includes ~15 gambling/casino categories (1Win Brasil, 1win India, casino en ligne fr, king johnnie, Mostbet Russia, pinco, etc.) — signs of a hacked/compromised WordPress site

### Active Oahu Tours
- **Platform:** Professional WordPress with multi-level mega menu
- **Navigation:** Rich hierarchical menu with 4 main sections:
  1. **Activities & Tours** → All Tours, Self Guided Tours, Guided Tours
  2. **Rentals** → All Rentals, Kayak Rentals (Mokolii, Kailua), Multi-Day Rentals, Electric Bike Rentals
  3. **Adventure Guide** → All Guides, Chinaman's Hat, Lanikai Beach, Kailua Beach, Transport Kayaks
  4. **Contact Us** → About (Our Kailua Storefront, Awards, Guides, Reviews), Gallery, FAQ
- **All pages function correctly** — no 403s or 404s encountered
- **Breadcrumbs** present on inner pages (e.g., Home / About / Awards)
- **Multi-language support:** English/Japanese language selector
- **Prominent promo bar:** "15% Off Groups of 4 or More" shown site-wide with coupon code

### Key Difference
> **HBT has a broken site with ~50% nav links leading to 404s; AOT has a fully functional, well-organized 3-level mega menu with breadcrumbs.**

---

## 2. PAGE LAYOUT & DESIGN

### Hawaii Beach Time
- **Homepage is extremely sparse:** Just navigation + "DELIVERY ANYWHERE ON OAHU / KAYAKS | SNORKELS | SUPS | & MORE" tagline + phone number + copyright + BOOK NOW CTA button
- **No hero section, no featured products, no testimonials, no imagery on homepage** — just plain text and a sticky CTA
- **Minimal visual design** — appears to be a very dated/basic WordPress theme
- **Works page:** Simple grid of product cards with prices — Double Kayak ($74/day), SUP ($56/day), Single Kayak ($64/day), Umbrella ($16/day), Cooler ($14/day), Snorkel Set ($14/day), Folding Chair ($14/day), Boogie Board ($12/day), plus hidden items behind "Load more"
- **Contact page:** Standard contact form (Name, Email, Subject, Message) + phone + hours
- **Oahu Beach Guide page:** Text-only guide with sections for top beaches, best kayaking beaches, best snorkeling, relaxing, SUP, beginner surfing — links to broken destination pages
- **Waikiki Snorkel Rentals:** Long-form content-heavy page with detailed snorkeling advice, beach recommendations, sizing info, delivery details
- **Footer:** Minimal — just tagline, phone number, copyright. Same across all pages. No footer menu, no social links (social links appear in header as icons only)

### Active Oahu Tours
- **Rich, modern homepage:**
  - Promo bar at top (15% off groups)
  - Professional hero section with imagery
  - Featured tour cards (Kailua E-Bike Kau Kau, Flat Island Guided Kayak & E-Bike, Mokulua Islands Kayak Adventure)
  - Category cards (Guided Kayak Tours, Beach Gear Rentals, Need Kayaks Today?)
  - Testimonial quote prominently displayed
  - Awards section (Tripadvisor Travelers' Choice)
  - Social proof throughout
- **Storefront photo** showing physical location
- **Professional photography** throughout with proper alt text
- **Footer:** Structured with 4 columns — social media links, contact info (phone, email, address), opening hours, and Instagram feed / newsletter signup
- **"Book Online" button** prominently displayed in header
- **Breadcrumb navigation** on all inner pages

### Key Difference
> **HBT has a bare-minimum, text-heavy layout with almost no homepage content. AOT has a rich visual design with professional photography, hero sections, testimonials, and social proof.**

---

## 3. CONTENT DEPTH

### Hawaii Beach Time
- **Homepage:** Essentially zero unique content — just nav and tagline
- **Product pages:** Very thin — just price lists on /works/
- **Waikiki Snorkel Rentals page:** Good depth (~1500+ words) with detailed snorkeling location info, delivery logistics, sizing guidance
- **Oahu Beach Guide page:** Moderate depth — lists top beaches with categories but many links are broken
- **No blog content accessible** — /beach-blog/ is 404
- **No FAQ page, no about page, no reviews page**
- **Total working content pages:** ~5 (Home, Works, Contact, Beach Guide, Waikiki Snorkel)
- **No testimonials, no reviews, no social proof**

### Active Oahu Tours
- **Homepage:** Rich content with multiple sections, tour descriptions, CTAs
- **Detailed product pages** for each tour/rental type
- **Adventure Guide section:** 5+ detailed guide articles (Chinaman's Hat, Lanikai Beach, Kailua Beach, Transporting Kayaks)
- **FAQ page:** 7 detailed answers with links to specific activity FAQs
- **Awards page:** 5 awards listed (2022 Tripadvisor Travelers' Choice, Top 10% Hospitality, 2020 Travelers' Choice, 2019 & 2018 Certificates of Excellence)
- **About pages:** Storefront info, Guides bios, Reviews
- **Gallery page**
- **Total working content pages:** ~20+ (home, tours, rentals, guides, about, FAQ, awards, gallery, contact)
- **Strong social proof:** Testimonials, awards, reviews page

### Key Difference
> **HBT has ~5 thin pages with mostly broken navigation; AOT has 20+ content-rich pages with guides, FAQs, awards, galleries, and reviews.**

---

## 4. SCHEMA & TECHNICAL SEO

### Hawaii Beach Time
- **Schema markup:** NONE — zero `application/ld+json` scripts
- **No Organization schema, no WebSite schema, no LocalBusiness schema**
- **Meta description:** Not present on homepage
- **No H1 tag on homepage**
- **Google Analytics:** Yes (G-RJ7HGKPXXH) — Universal Analytics (legacy)
- **Blog categories polluted with spam:** 15+ gambling/casino categories indicate likely WordPress compromise
- **oEmbed and RSS feeds present** (default WordPress)
- **No canonical issues detected**

### Active Oahu Tours
- **Schema markup:** 2 structured data scripts:
  1. **WebSite schema** — includes site name, alternate name, and search action
  2. **Organization schema** — includes name, URL, logo, and social media links (Facebook, Instagram, Twitter)
- **Proper H1 hierarchy** — single H1 per page, logical subheadings
- **Breadcrumbs implemented** on all inner pages
- **Multi-language hreflang** hint via language selector
- **Analytics present** (not inspected in detail)
- **Professional WordPress setup** with caching/optimization expected

### Key Difference
> **HBT has ZERO schema markup, no meta description, no H1 on homepage, and spam-inflated blog categories. AOT has proper WebSite + Organization schema, breadcrumbs, and clean SEO fundamentals.**

---

## 5. SOCIAL MEDIA & TRUST SIGNALS

| Signal | Hawaii Beach Time | Active Oahu Tours |
|--------|------------------|-------------------|
| Facebook | ✓ Link in header | ✓ Link in footer + Organization schema |
| Instagram | ✓ Link in header | ✓ Link in footer + Organization schema |
| Twitter/X | ✓ Link in header | ✓ Link in footer + Organization schema |
| YouTube | ✓ Link in header | ❌ Not found |
| Google Plus | ✓ Link (defunct platform) | ❌ Not found |
| Yelp | ❌ Not found | ✓ Link in footer |
| Tripadvisor | ❌ Not found | ✓ Link in footer + Awards page |
| Awards | ❌ None shown | ✓ 5 Tripadvisor awards |
| Reviews | ❌ No reviews page | ✓ Dedicated reviews page |
| Testimonials | ❌ None | ✓ Quote on homepage |
| Physical address | ❌ Not shown on site | ✓ 134B Hamakua Dr, Kailua, HI |
| Storefront photo | ❌ Not shown | ✓ Photo of physical location |

### Key Difference
> **HBT links to Google Plus (defunct) and has no trust signals. AOT actively showcases awards, reviews, physical location, and multiple review platforms.**

---

## 6. PRODUCT/SERVICE OFFERING COMPARISON

### Hawaii Beach Time
- **Beach gear delivery** ("Oahu's Only Beach Gear Delivery Service") — delivers to hotels, beaches, vacation rentals
- **Product catalog** (from /works/):
  - Single Kayak ($64/day, $192/week)
  - Double Kayak ($74/day, $222/week)
  - Stand Up Paddle Board ($56/day, $168/week)
  - Snorkel Set ($14/day, $42/week)
  - Kids Snorkel Set
  - Boogie Board ($12/day, $36/week)
  - Folding Beach Chair ($14/day, $36/week)
  - Umbrella ($16/day, $36/week)
  - Cooler w/ Ice ($14/day, $36/week)
  - Beginner Surfboard
  - Hammock
  - Life Vest
- **Delivery model** — drop off/pick up service
- **No guided tours, no e-bikes**

### Active Oahu Tours
- **Storefront + delivery model** — pickup at Kailua store OR delivery to private addresses
- **Products/Services:**
  - Kayak rentals (Mokolii/Chinaman's Hat, Kailua)
  - Electric bike rentals
  - Multi-day rentals
  - Guided kayak tours (Flat Island, Mokulua Islands)
  - Guided e-bike food tours (Kau Kau Adventure)
  - Self-guided tours
  - Beach gear (kayaks, SUPs, snorkel gear, beach chairs)
- **Broader service range** — guided + self-guided + rentals + e-bikes

### Key Difference
> **HBT is delivery-only beach gear rentals. AOT offers both a physical storefront and delivery, plus guided tours, e-bikes, and multi-day options — a more complete experience business.**

---

## 7. SUMMARY OF KEY DIFFERENCES

| Category | Hawaii Beach Time | Active Oahu Tours | Advantage |
|----------|------------------|-------------------|-----------|
| **Working pages** | ~5 (50% nav broken) | 20+ (all working) | AOT |
| **Homepage content** | Near-empty (just tagline) | Rich hero + tours + CTAs + testimonials | AOT |
| **Navigation** | Flat, single-level | 3-level mega menu with hierarchy | AOT |
| **Schema markup** | ZERO | WebSite + Organization | AOT |
| **Blog** | 404 (spam categories visible) | Adventure Guide with 5+ articles | AOT |
| **Social proof** | None | Awards, testimonials, reviews page | AOT |
| **Physical address** | Hidden/absent | Prominently displayed | AOT |
| **Design quality** | Dated, minimal | Modern, professional photography | AOT |
| **SEO fundamentals** | No meta desc, no H1 | Proper H1, breadcrumbs, schema | AOT |
| **Spam indicators** | Casino/gambling categories | None | AOT |
| **Multi-language** | No | English + Japanese | AOT |
| **Business model** | Delivery-only | Storefront + delivery + guided tours | AOT |

### Critical Issues for Hawaii Beach Time
1. **Site is mostly broken** — 4 of 8 nav links lead to 404 pages
2. **No schema markup** — missing critical local business SEO signals
3. **No meta description or H1** on homepage — poor on-page SEO
4. **Spam blog categories** — likely hacked/compromised WordPress install
5. **Zero social proof** — no testimonials, awards, or reviews visible
6. **Outdated social link** — still linking to Google Plus (defunct since 2019)
7. **Homepage has virtually no content** — just navigation and tagline
8. **No physical business address** shown on website (hurts Local SEO trust)

### What Active Oahu Tours Does Better
1. Proper schema.org structured data (WebSite + Organization)
2. Rich, content-dense homepage with hero, tours, CTAs, testimonials
3. Fully functional site with no broken pages
4. Strong social proof (Tripadvisor awards, testimonials, reviews)
5. Physical address displayed prominently
6. Breadcrumb navigation for UX and SEO
7. Multi-language support
8. Broader product line (guided tours + e-bikes + multi-day rentals)
