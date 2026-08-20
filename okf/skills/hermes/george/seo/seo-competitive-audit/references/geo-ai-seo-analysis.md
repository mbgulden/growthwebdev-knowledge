# GEO & AI SEO Analysis — Reference

## What GEO Is

Generative Engine Optimization. Instead of optimizing for 10 blue links, you optimize to be **cited by AI models** (Google AI Overviews, ChatGPT Search, Perplexity, Gemini) when they generate answers to user queries.

The key difference: you're not trying to rank #1 — you're trying to be the source the AI quotes.

## SERP Features to Track

When running `serp_analysis`, note these `type` values in `serpEntries`:

| Feature | Meaning | GEO Strategy |
|---------|---------|--------------|
| `ai_overview` | Google's AI-generated answer at top of SERP | Structure pages with clear `<h2>What is [Topic]?</h2>`. Use HowTo schema. Cite authoritative sources (operator byline). |
| `people_also_ask` | PAA boxes — click-to-expand Q&A | Write direct 40-60 word answers as H2+paragraph. Start with the answer. Target featured snippets. |
| `local_pack` | Google Maps 3-pack | Optimize Google Business Profile. Add LocalBusiness schema. Include address, phone, hours. |
| `knowledge_graph` | Google's knowledge panel | Structured data (schema.org). Wikipedia/authoritative sources. |
| `product_considerations` | Shopping comparison results | Product schema. Pricing. Reviews. |
| `short_videos` | Video carousel | YouTube content. Video schema. |
| `discussions_and_forums` | Reddit/Forum results | Content gap signal — users want personal experiences, not generic info. Write first-person operator content. |
| `top_sights` | Travel/tourism feature | TouristTrip schema. Location data. |

## Zero-Click Search Analysis

Keywords where SERP features answer the query without a click. Flag these to avoid wasting effort on CTR-driven content.

**High zero-click risk:** Knowledge Graph + Google Reviews + PAA at top (e.g., beach parks, landmarks)
**Low zero-click risk:** Local Pack + organic results below (users scroll past maps)
**Medium:** AI Overview at #1 but organic results still get clicks below

**Strategy per risk level:**
- **High:** Optimize for AI citation (structured HowTo/FAQPage, authoritative byline). Don't chase CTR.
- **Medium:** Write for both — AI citation + traditional organic. Best of both.
- **Low:** Traditional SEO. Go for rankings and CTR.

## GEO Optimization Checklist

For any keyword that triggers `ai_overview`:

1. **Structure pages with `<h2>What is [Topic]?</h2>`** — AI models look for definition-style headers
2. **Use HowTo schema** — step-by-step format feeds AI step-by-step answers (most missing GEO schema type)
3. **Add FAQPage schema** with 5-7 realistic questions users actually ask
4. **Include author byline** — "Michael Gulden, Owner & Operator, Active Oahu — Kailua, Oahu" builds E-E-A-T
5. **Write in first-person operator voice** — AI models prefer authoritative first-hand content over generic descriptions
6. **Use clear H2/H3 hierarchy** with question/answer subheadings — AI parses headings as answer anchors

### HowTo Schema Template

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "How to [Action]: Complete Guide",
  "description": "Step-by-step guide for [topic].",
  "step": [
    {"@type":"HowToStep", "position":1, "name":"Step 1 title", "text":"Detailed description with location-specific details."},
    {"@type":"HowToStep", "position":2, "name":"Step 2 title", "text":"Detailed description."}
  ]
}
```

**Rules:** 4-7 steps, location-specific details in each step, natural language (not robotic).

## AI Overview Capture Playbook

When a keyword triggers `ai_overview`:
1. Identify what the AI Overview currently says (run the query manually or infer from top organic results)
2. Write a page section that directly answers the same question, better
3. Structure it as: definition → practical details → why-trust-us
4. Add HowTo schema with the exact steps the AI might cite
5. Add FAQPage schema with related questions the AI might expand
6. Add author byline + credentials (E-E-A-T signal)
7. Publish and monitor — if the AI cites you, you've captured the GEO slot

## Squeeze Play Calculation

Identifies keywords where you can win fast — high volume + low-DA competitors ahead = easy squeeze.

**Formula:**
```
Squeeze Score = (Keyword Volume / 100) * (Our DA / Average DA of top 5 competitors)
```

**Signal:** When sites with DA 15-25 are ranking in top 5 for a 2,000+ vol keyword and you have DA 26+, that's a squeeze play.

**Real example from Active Oahu:** "electric beach" — DA 21-22 blogs at #3-4 get 4,361 clicks. Our DA 26. A proper guide captures 2,000+ extra clicks.

## Files

- Full GEO report: `cron/output/seo-audit/20260603_GEO_READINESS_REPORT.md`
- SERP deep dive example: `cron/output/seo-audit/20260603_SERP_DEEP_DIVE.md`
