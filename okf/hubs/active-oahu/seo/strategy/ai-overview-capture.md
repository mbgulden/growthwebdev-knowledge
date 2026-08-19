---
type: Standard
title: AI Overview Capture Strategy (GEO/AEO for AOT)
description: How AOT gets cited inside Google's AI Overviews (and ChatGPT/Perplexity/Claude answers) for Oahu tourism queries. Per-keyword strategy with schema + content patterns.
tags: [ai-overview, geo, aeo, aot, seo, citation, schema, content-strategy]
timestamp: 2026-06-19T15:45:00Z
linear_issue: null
git_path: okf/strategy/ai-overview-capture.md
status: current
resource: okf/hubs/active-oahu/seo/strategy/ai-overview-capture.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/aot-seo-knowledge
last_verified: 2026-08-19
verified_by: kai
---

# AI Overview Capture Strategy (GEO/AEO for AOT)

## What is GEO/AEO?

**GEO** = Generative Engine Optimization = getting cited inside AI-generated answers (Google AI Overviews, ChatGPT, Perplexity, Claude)
**AEO** = Answer Engine Optimization = getting featured in "People Also Ask" boxes, featured snippets, voice search answers

For AOT, the GEO/AEO priority is **Google AI Overviews** because:
- Google has 90%+ search market share
- AI Overviews appear above position #1 organic
- Being CITED in the AI Overview = massive brand visibility
- Click-through from AI Overview is lower than #1 organic BUT the citation is "earned media" worth more than the click

## How AI Overviews are built

Google's AI Overview is generated from the top ~10 organic results for the query, with citations going to:
1. Pages with **direct answers** (40-80 word paragraphs)
2. Pages with **FAQPage schema**
3. Pages with **HowTo schema**
4. Pages with **authoritative E-E-A-T signals** (author bio, citations, last-updated)
5. Pages with **structured data** (Product, LocalBusiness, TouristTrip)

## AOT's current AI Overview capture rate

**Estimated: ~10-15% of priority queries** (based on Ubersuggest SERP feature detection in baseline audit).

Most priority queries DO trigger AI Overviews — but AOT isn't being cited inside them. The current citers are:
- Wikipedia / .gov / .edu pages (background info)
- Reddit threads (user recommendations)
- Major travel blogs (operational content)
- Tripadvisor / Viator (aggregators)

AOT needs to **displace these** by being more authoritative + better structured.

## The 5-step AEO pattern (per-page)

For each page AOT wants cited in AI Overviews:

### Step 1: Answer block (40-80 words above the fold)

Every page should have a **direct answer to the implied question** as the first paragraph. Not "Welcome to..." — actual information.

**Example for /activities/sharks-cove-self-guided-snorkel/:**

> Sharks Cove is a tidepool-filled lava-rock cove on Oahu's North Shore and one of Hawaii's best shore snorkeling spots. Self-guided snorkelers can see Hawaiian green sea turtles, octopus, butterflyfish, and occasionally moray eels in water 3-15 feet deep. Best conditions: April-October, mornings before 10am. Entry is free; gear rentals start at $X from AOT.

That's 70 words. It directly answers: "Is Sharks Cove good for snorkeling?"

### Step 2: FAQ schema (4-6 Q&As)

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Is Sharks Cove good for snorkeling?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes, Sharks Cove is one of the best shore snorkeling spots in Hawaii. The protected cove has calm water, lava rock formations, and abundant marine life..."
      }
    },
    ...
  ]
}
```

### Step 3: HowTo schema (where applicable)

For activity pages (kayak tour, snorkel tour), add HowTo schema with step-by-step.

### Step 4: E-E-A-T signals

- **Author bio** with photo (Kimo, founder)
- **Last-updated date** prominently displayed
- **Sources/citations** (link to NOAA, DLNR, Hawaii Tourism Authority)
- **Real customer reviews** with photos
- **"As seen in"** press logos (Honolulu Magazine, Hawaii News Now, etc.)

### Step 5: LocalBusiness + TouristTrip schema

Layered on top of FAQPage:
- LocalBusiness (for the storefront)
- TouristTrip (for the activity)
- Product (for pricing)
- BreadcrumbList (for navigation context)

## Per-keyword AEO target list

Based on GSC data, these are the queries where AEO capture has highest ROI:

### Tier 1 — Highest priority (Tier 1 briefs in `content/brief-registry.md`)

| Query | Monthly impr | Current pos | AEO strategy |
|---|---:|---:|---|
| sharks cove snorkeling | 2,162 | 6.1 | FAQ block + HowTo + author bio |
| sharks cove oahu | 4,800 | 4.2 | Same page, AEO block needs rewrite |
| electric beach | 5,935 | 6.5 | Refresh Electric Beach page |
| sharks cove | 4,987 | 5.9 | Same as above |
| kailua beach park | 2,853 | 9.7 | AEO block needs adding |
| kaneohe sandbar kayak | 294 | 5.2 | Kanohe page needs AEO block |
| chinamans hat kayak | 123 | 1.1 | DEFEND — currently winning |
| mokolii island kayak | 47 | 18.9 | Striking distance, needs AEO |

### Tier 2 — Secondary priority (Month 2-3)

- best snorkeling oahu
- best snorkel oahu hawaii
- best oahu beaches
- best kayak rental kailua
- best paddleboard rental oahu
- best things to do in kailua

### Tier 3 — Brand defense (don't lose these)

- active oahu tours (#1)
- active oahu (#2)
- chinamans hat kayak (#1)
- kaneohe sandbar kayak (#1)

## Schema deployment order

**Phase 1 (Week 1-2):** Top 5 revenue pages
1. `/` (homepage) — LocalBusiness + Organization
2. `/rentals/oahu-stand-up-paddle-board-rentals-sup-hire/` — Product + Offer + FAQ
3. `/rentals/oahu-tandem-kayak-rentals/kailua-kayak-rentals/` — Product + Offer + FAQ
4. `/activities/sharks-cove-self-guided-snorkel/` — TouristTrip + FAQ + HowTo
5. `/oahu-kayaking-and-beach-adventures/kaneohe-sandbar-kayak-experience/` — TouristTrip + FAQ + HowTo

**Phase 2 (Week 3-4):** Top 10 guide pages

**Phase 3 (Month 2):** All revenue pages get FAQPage schema

**Phase 4 (Month 3):** All guide pages get FAQPage schema

**Phase 5 (Month 4):** Blog posts get FAQPage + Article schema

## Voice search optimization

Voice searches are different from typed searches:
- Longer, more conversational
- Often questions
- Often "near me"
- Often specify time/conditions

AOT has 153 GSC queries with "near me" pattern. Voice queries are ~5-10x of that estimate in volume.

**Voice search content pattern:**

For each activity, add:
- `<h2>What is X?</h2>` followed by 30-word direct answer
- `<h2>How much does X cost?</h2>` followed by pricing summary
- `<h2>Where is X?</h2>` followed by address + map
- `<h2>When is X open?</h2>` followed by hours
- `<h2>Is X good for beginners?</h2>` followed by skill level

These match voice search patterns 1:1.

## Perplexity / ChatGPT / Claude citation strategy

These AI engines pull from:
- Web search results (high-ranking pages)
- Wikipedia (for factual claims)
- Reddit (for "real user" opinions)
- Authoritative review sites (Tripadvisor, Yelp)

AOT can win citations in these engines by:
1. **Wikipedia presence** — submit a draft article for Active Oahu Tours as a Hawaii tour operator
2. **Reddit engagement** — Kimo or team members contribute honestly to r/Hawaii, r/VisitingHawaii threads
3. **Yelp / Tripadvisor** — actively request reviews from customers
4. **Quora / Medium articles** — Kimo writes articles linking back to AOT

**Target:** 5+ Perplexity citations per top 20 priority query by Q4.

## Measurement

AI Overview citation rate is hard to measure directly. Use proxies:

- **Google Search Console:** Track queries where position improves from 10-15 → 3-5 (often happens after AI Overview capture)
- **Branded search volume:** Track `active oahu tours` queries — increases as citations drive awareness
- **Direct traffic:** Track direct traffic to activeoahutours.com — citations drive awareness + direct visits

**Success criteria:** 8+ AI Overview citations by Q3, 15+ by Q4.

---

## Per-page AEO audit template

For each top-priority page, audit:

- [ ] Direct answer block (40-80 words) above the fold
- [ ] FAQPage schema with 4-6 Q&As
- [ ] HowTo schema (if applicable)
- [ ] Author bio + photo
- [ ] Last-updated date visible
- [ ] Citations to authoritative sources
- [ ] LocalBusiness / TouristTrip / Product schema layered
- [ ] BreadcrumbList
- [ ] Image alt text (descriptive, with location + activity)
- [ ] FAQ-style subheadings (`<h2>What is X?</h2>`, `<h2>How much...</h2>`, etc.)
- [ ] Real customer reviews with photos

If any of these are missing, it's an AEO opportunity.

---

## What NOT to do

- ❌ Don't stuff keywords into schema (Google ignores)
- ❌ Don't add fake FAQ Q&As that don't match page content
- ❌ Don't use AI-generated content verbatim without editing (Google penalizes)
- ❌ Don't ignore mobile UX (63% of AOT traffic is mobile)
- ❌ Don't break existing backlinks by changing URLs

---

## Open questions

- [ ] Will Kimo write a Wikipedia article about AOT?
- [ ] Should we engage a Reddit marketing person?
- [ ] Are there budget for an AEO audit tool (Surfer, Frase, MarketMuse)?
- [ ] Should we hire a copywriter specifically for FAQ content?

---

*Strategy authored by Kai on 2026-06-19 based on GSC + Ubersuggest + research/ai-seo-strategy.md.*
