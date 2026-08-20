# AOT Sprint: CRIT-01–04 + HIGH-01–06 (2026-07-27)

## Results

| # | Task | PR | Live | Files |
|---|------|-----|------|-------|
| CRIT-01 | Booking calendar iframe on /rentals/ | #104 | ✅ | site/rentals/index.html |
| CRIT-02 | FareHarbor `target="_blank"` removal | #104 | ✅ | 33 tour pages |
| CRIT-03 | H5→H3 heading hierarchy | #104 | ✅ | 134 files, 898 tags |
| HIGH-01 | Schema `openingHoursSpecification` (7-day) | #105 | ✅ | site/index.html, site/_templates/head.html |
| HIGH-02 | Descriptive alt text (filename→description) | #106 | ✅ | 88 files |
| HIGH-03 | TripAdvisor trust badge above booking CTAs | #107 | ✅ | 161 pages, 162 badges |
| HIGH-04 | `/adventure-guide/` → `/activities/` 301 | #108–111 | ✅ | site/_redirects + site/adventure-guide/index.html |
| HIGH-05 | Meta keywords (38 pages) | #112 | ✅ | site/index.html + 37 activity pages |
| HIGH-06 | Japanese hreflang (9 EN pages) | #113 | ✅ | 9 EN pages with JA counterparts |

**9 PRs merged in one session.**

## Key Lessons

### `site/_redirects` not repo root
CF Pages deploys from `site/` — only `site/_redirects` is read.
Repo root `_redirects` is ignored by CF Pages.

### CF Pages `/*` wildcard edge case
`/*` matches paths with a trailing slash + extra segment.
Bare `/adventure-guide` (no slash) falls through to `/* /404.html 404`.
Fix: create `site/adventure-guide/index.html` with meta refresh + JS redirect.

### PR body shell quoting
URLs with `/` in `--body` arguments cause shell "No such file" errors.
Always use `--body-file /tmp/pr-body.md` or single-quoted heredoc.

### CF Pages async deploy lag
Live `activeoahutours.com` may be stale for 30–90s after merge.
Check `origin/main` commit content first — commit-verified is sufficient evidence.

### Meta tag attribute order varies
Some pages use `<meta name="description" content="..."/>` (name before content).
Others use `<meta content="..." name="description"/>` (content before name).
Regex patterns for meta tag manipulation must handle both orderings.

### Meta description can span multiple lines
Long `<meta content="..." name="description"/>` tags can wrap across lines.
Use `re.DOTALL` flag when matching meta tag patterns across line boundaries.

### hreflang insertion: canonical attribute order varies
Some pages: `<link rel="canonical" href="..."/>` (rel before href).
Others: `<link href="..." rel="canonical"/>` (href before rel).
Pattern: `<link[^>]*rel=["']canonical["'][^>]*>` handles both.

## HIGH-05: Meta Keywords Details

**Scope:** 38 pages (homepage + rentals + 36 activity pages).
Keywords chosen for commercial search intent: "Oahu kayak rental", "Kailua kayak rentals", "Mokulua Islands kayak tour", etc.

**Script:** `/tmp/fix_meta_keywords.py` — HTMLParser-safe regex, handles both meta attribute orderings, idempotent (no double-injection guard).

**Slug-based keyword targeting:** URL slug determines keywords (e.g., `mokulua` slug → Mokulua-specific keywords). Added slug patterns for: `rainforest`, `sunset`, `yoga`, `surf`, `turtle`, `romantic`, `family` to cover pages previously missed.

## HIGH-06: Japanese hreflang Details

**Scope:** 9 EN pages that had JA counterparts but were missing hreflang tags.
JA pages already had correct hreflang pointing back to EN — just needed the EN side to complete the reciprocity.

**Insertion point:** After `<link rel="canonical">` (or before `</head>` as fallback).

**JA-only pages:** 10 JA guide pages have no EN counterpart — cannot add hreflang without a valid EN target. These are excluded.

## Verification Commands

```bash
# HIGH-05 meta keywords — count pages with keywords
grep -rl 'name="keywords"' site/activities/ | wc -l  # expect 36+
grep -l 'name="keywords"' site/index.html site/rentals/index.html  # expect 2 files

# HIGH-06 hreflang — EN pages with hreflang
grep -rl 'hreflang' site/activities/ | grep -v '/ja/' | wc -l  # expect 24+ (was 15 before fix)

# Schema openingHours
curl -sS "https://activeoahutours.com/" | python3 -c "
import sys, re, json
c = sys.stdin.read()
schemas = re.findall(r'<script type=\"application/ld\+json\">(.*?)</script>', c, re.DOTALL)
ta = next((d for d in [json.loads(s) for s in schemas] if d.get('@type') == 'TravelAgency'), None)
print('openingHoursSpecification:', len(ta.get('openingHoursSpecification', [])))
"

# Redirect live
curl -sS -I "https://activeoahutours.com/adventure-guide" | grep "HTTP\|location"
curl -sS -I "https://activeoahutours.com/adventure-guide/" | grep "HTTP\|location"
```

## HIGH-03 Trust Badge Details

Badge: inline SVG TripAdvisor stars (4 filled green, 1 white) + "4.8" rating + "356 reviews"
Links to: https://www.tripadvisor.com/Attraction_Review-g60659-d5079465-Reviews-Active_Oahu_Tours-Kailua_Oahu_Hawaii.html

CSS (scoped, no collisions):
```css
.tripadvisor-inline-badge{display:inline-flex;align-items:center;gap:4px;margin-bottom:6px;text-decoration:none;font-size:12px;color:#555;background:#f8f9fa;border:1px solid #e9ecef;border-radius:4px;padding:3px 8px 3px 6px}
.tripadvisor-inline-badge:hover{background:#fff;border-color:#34E0A1;color:#333}
.tripadvisor-badge-rating{font-weight:700;color:#34E0A1;font-size:13px}
```

## HIGH-04 Attempt History (4 PRs)

- v1 (#108): Added redirect to repo root `_redirects` — CF Pages ignored it
- v2 (#109): Added to `site/_redirects` — trailing-slash `/adventure-guide/` worked, bare `/adventure-guide` 404'd
- v3 (#110): Added explicit bare redirect `/adventure-guide /activities/ 301` — CF Pages still 404'd bare path
- v4 (#111): Created `site/adventure-guide/index.html` with meta refresh + JS redirect — both paths work
