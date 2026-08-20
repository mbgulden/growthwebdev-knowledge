# AOT Kailua kayak commercial-intent refresh — 2026-07-10

## When this applies

Use this pattern for Active Oahu product/rental pages that already rank but need stronger commercial-intent conversion copy — especially pages with GSC impressions in positions 2–10 for booking queries like `kailua kayak rental`, `kayak rental kailua`, or destination + rental variants.

## Evidence pattern

1. Pull GSC query/page data for the exact page URL over the last ~90 days.
2. Identify query clusters where the page is already close enough to win more clicks:
   - high/improving impressions
   - average position roughly 2–10
   - commercial modifiers: `rental`, `rentals`, `near me`, `price`, destination + activity
3. Use Ubersuggest SERP spot-checks for 2–3 priority queries to understand who owns the click above us and which title/value propositions appear in SERP.
4. Translate evidence into copy decisions, not generic SEO stuffing.

## Kailua kayak rental example

GSC showed the page had strong commercial-query visibility:

| Query | Signal |
|---|---|
| `kailua kayak rental` | position ~3, hundreds of impressions |
| `kayak rental kailua` | position ~3, commercial phrasing reversed |
| `kailua kayak` / `kailua kayaking` | broader activity intent, page 1 but lower CTR opportunity |
| `kailua beach kayak rental` / `kayak rentals in kailua` | destination + rental intent |

Ubersuggest SERP checks showed Active Oahu ranking #2 for primary rental phrases behind Kailua Beach Adventures, and lower for `lanikai kayak rental`, where route/location clarity matters.

## Implementation moves

For a commercial-intent rental page:

1. Refresh title/meta/OG/Twitter/Product schema around the exact buyer decision:
   - activity + location
   - primary destination variants
   - starting price if already visible on-page
   - pickup/delivery logistics
   - transport constraints, e.g. `4-door vehicle`, pads/straps
2. Rework hero copy to answer the booking question immediately:
   - where pickup happens
   - what is included
   - which routes fit which skill levels
   - what conditions determine route choice
3. Add a visible `.aot-quick-answer` near the hero with concise answer-style copy.
4. Add a route/comparison section before visual gallery or long story blocks, not buried after reviews.
5. Add a visible FAQ section that mirrors common buyer questions.
6. Refresh FAQPage JSON-LD to match visible FAQ text; do not keep stale schema from older work if the page intent changed.
7. Promote skipped article headings (`h5`) to real section headings (`h2`/`h3`) where they are content structure, while leaving legitimate footer/related-card headings alone.
8. Preserve FareHarbor links, item IDs, flow IDs, and displayed prices unless the task explicitly authorizes booking changes.

## Verification checklist

Run a focused `/tmp/hermes-verify-*` ad-hoc verifier before opening a PR:

- HTML parses.
- title and meta description include commercial markers and remain reasonable lengths.
- exactly one H1 exists.
- quick-answer block exists.
- route/comparison section exists.
- visible FAQ section exists.
- Product schema parses and name/description reflect updated visible copy.
- FAQPage schema parses and question count/content mirror visible FAQ.
- known stale typos or markers are gone.
- FareHarbor booking link count is unchanged from baseline.
- `git diff --check` passes.

After merge:

1. Wait for Cloudflare Pages production deploy by commit hash.
2. Purge exact apex and `www` URLs for the changed page.
3. Run a production `/tmp/hermes-verify-*` script against cache-busted production URL, checking the same markers/schema and FareHarbor link count.
4. Comment Linear with GSC/SERP evidence, PR URL, production commit, and verifier results before marking Done.

## Pitfalls

- Do not recommend business model changes when copy/logistics clarity is the actual problem. First verify whether the page simply fails to communicate pickup, transport, duration, route fit, or value proposition.
- Do not change FareHarbor links or prices while doing content/SEO improvements.
- Do not add schema claims that are not visible on the page.
- Do not flatten all H5s blindly; footer/related-card headings may be template artifacts. Promote only content-section headings inside the main page body.
