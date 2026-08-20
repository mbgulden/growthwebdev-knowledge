# GSC + Ubersuggest Counter-Content Workflow

Use this when Ubersuggest competitor monitoring flags territory movement and Google Search Console access is available for Active Oahu.

## Purpose

Pair Ubersuggest competitor movement with GSC own-site truth before creating content tasks. Ubersuggest tells us where competitors are gaining visibility; GSC tells us whether AOT already has impressions, weak CTR, or page-2/3 rankings we can improve without guessing.

## Workflow

1. **Start from competitor alerts**
   - Pull the competitor velocity JSON/output.
   - Identify territory alerts, especially pages in AOT target geographies or rental/service intent.
   - Normalize competitor URLs from the saved `domain_top_pages` baseline before using page tools. Titles may be truncated in alerts; the baseline has the real URL.

2. **Inspect competitor pages with Ubersuggest**
   - `page_overview` works for canonical page URLs and returns page-level traffic/organic keyword counts. **Pass the URL under the argument key `page`** (not `url`), e.g. `{"page":"https://example.com/path"}`.
   - `page_keywords` also expects `{"page":"https://example.com/path"}`. It may return HTTP 405 on the current tier/API path. If so, do **not** stop; fall back to `domain_keywords(domain, limit=200-300)` and filter rows where `url` matches the competitor page path.
   - Keep the top keyword signals with position, volume, traffic, and URL.

3. **Pull GSC own-site rows**
   - Use `sc-domain:activeoahutours.com` unless there is a clear reason to use a URL-prefix property.
   - Pull ~90 days of `searchAnalytics.query` with `dimensions: ['query','page']` and `dataState: 'final'`.
   - Filter queries by the competitor intent terms, e.g. `lanikai`, `kailua`, `snorkel`, `beach chair`, `umbrella`, `beach day`, `beach rental`, `gear rental`.
   - Aggregate both by query and by page: clicks, impressions, CTR, impression-weighted average position.

4. **Inspect existing AOT page inventory**
   - Search static site files for likely target terms.
   - Prefer refreshing pages that already have GSC impressions and topical fit over creating orphan pages.
   - Watch for title/body mismatch: if a page title targets one place but headings/body talk about another (e.g. Lanikai title with Sharks Cove/Pūpūkea copy), prioritize that as a trust/relevance fix.

5. **Create counter-content briefs**
   - Each brief should name exact target URL(s), GSC evidence, Ubersuggest competitor evidence, content direction, and acceptance criteria.
   - Preserve private competitive analysis in `active-oahu-business`, not the public site mirror.
   - For implementation, create/update Linear once API quota is available; if rate-limited, save the exact issue draft in the private repo.

## Output shape

Recommended private files:

```text
okf/reports/seo/YYYY-MM-DD-<competitor>-<territory>-countermove.md
okf/reports/seo/YYYY-MM-DD-<competitor>-<territory>-countermove.json
okf/reports/seo/briefs/YYYY-MM-DD-<territory>-countercontent-briefs.md
okf/reports/seo/briefs/YYYY-MM-DD-linear-issue-draft-<topic>.md  # if Linear is rate-limited
```

## Pitfalls

- Do not treat Ubersuggest traffic estimates as AOT truth; GSC is the own-site source of truth.
- Do not abandon page-level analysis if `page_keywords` returns 405; use `domain_keywords` + URL filtering.
- Do not create broad “write a blog post” tasks. Counter-content tasks need exact target pages, target queries, competitor evidence, and acceptance criteria.
- Do not store competitive/business analysis in the public deployable mirror repo; use the private `active-oahu-business` repo.
- If Linear is rate-limited, preserve the issue body as a markdown draft and report the blocker honestly instead of pretending the task was created.
