# Human Design Engine PWP audit pattern — 2026-07

This reference captures the reusable audit technique from the Human Design Engine website review.

## What mattered

The important discovery was a **live-vs-local split**:

- Local Astro source/build looked cleaner and `npm run build` passed.
- Live production at `https://humandesignengine.com/` appeared to be served from large static `docs/*.html` pages with inline CSS and missing metadata.

Future PWP audits should treat this split as a first-class possibility. Do not audit only local source if the user asks for the website.

## Evidence commands/patterns

- Build local source when available:

```bash
npm run build
```

- Lighthouse live production homepage, mobile and desktop:

```bash
npx --yes lighthouse https://example.com/ \
  --output=json \
  --output-path=/tmp/site-lighthouse-mobile.json \
  --chrome-flags='--headless --no-sandbox' \
  --quiet \
  --only-categories=performance,accessibility,best-practices,seo

npx --yes lighthouse https://example.com/ \
  --output=json \
  --output-path=/tmp/site-lighthouse-desktop.json \
  --chrome-flags='--headless --no-sandbox' \
  --quiet \
  --preset=desktop \
  --only-categories=performance,accessibility,best-practices,seo
```

- Parse rendered/live HTML for PWP acceptance signals:
  - title length
  - meta description present and non-empty
  - canonical present
  - OG/Twitter present
  - JSON-LD count
  - H1 count
  - heading-order skips
  - landmarks: `header`, `nav`, `main`, `footer`
  - input label coverage
  - broken same-origin links
  - inline `style=` count, `<style>` blocks, `!important`
  - heuristic PWP modules: BaseLayout, SiteHeader, SiteFooter, Hero, CardGrid, LeadCapture, TrustPanel, FAQ, RichTextPage, PricingOrPackages

## Findings pattern from Human Design Engine

- Lighthouse live homepage:
  - mobile: Performance 87, Accessibility 72, Best Practices 100, SEO 82
  - desktop: Performance 100, Accessibility 72, Best Practices 100, SEO 82
- Accessibility failures:
  - low contrast on dark trust-bar text
  - heading order jumps from `h2` to `h4`
  - unlabeled form fields
- SEO/static failures:
  - live core pages missing meta descriptions
  - no canonicals
  - OG mostly absent
- PWP contract failures:
  - production page dump had many inline styles
  - missing FAQ module on core marketing pages
  - no visible theme manifest/tokens/fixture evidence for live production output
- Broken links:
  - Cloudflare email-protection contact links on the coaching page returned 404 in crawler

## Recommended next-slice shape

When the site is visually promising but not PWP-compliant, recommend one bounded P0 slice:

**PWP Layout + Metadata + Accessibility Patch for live homepage**

Acceptance criteria:

- live homepage served from shared layout/module system, not static page dump
- metadata present: description, canonical, OG, Twitter
- trust-bar/text contrast passes WCAG AA
- heading skips fixed
- every form input has explicit accessible label
- duplicate primary chart CTA simplified
- build passes
- Lighthouse accessibility improves to 95+

## Reporting tone

Keep the audit blunt and decision-oriented:

- “Yellow/Red — visually promising, but not PWP-compliant yet.”
- Separate **live production findings** from **local repo findings**.
- Include raw artifact paths for Lighthouse JSON and crawl output.
