# AOT Lighthouse Audit Recipe (2026-07-29)

> **Session source:** Active Oahu 2026-07-29 — second verification pass on the Lighthouse fixes from `488b80932`. Audited `dist/index.html` directly with a Python verification script (`/tmp/hermes-verify-audit-fixes.py`) before pushing, fixing the FeatureBlock class-interpolation bug in the process.
> **Use this when:** an AOT homepage PR triggers Lighthouse regressions in `color-contrast`, `errors-in-console`, `image-redundant-alt`, `target-size`, `lcp-lazy-loaded`, or `heading-order`.

## The 5 audit fixes that worked for AOT

Each fix below has the symptom → cause → fix recipe → verification recipe shape, per the `corrections-lead-with-recipe` skill.

### 1. `errors-in-console` — glyphicon font 404s

**Symptom:** Lighthouse `errors-in-console` audit fails with `Failed to load resource: 404` for `glyphicons-halflings-regular.{woff2,woff,ttf,eot,svg}` from `https://activeoahutours.com/wp-content/themes/activeoahu/fonts/`.

**Cause:** Inherited Kadence/WordPress `<span class="glyphicon glyphicon-*">` elements. The glyphicon font was never uploaded to the activeoahutours.com theme directory, so every page that uses glyphicons gets 4× 404 console errors in production (visible on `https://activeoahutours.com/` too — it's a WP artifact).

**Fix recipe:** Replace glyphicon spans with Unicode characters, then remove the broken `@font-face` block.

| Glyphicon class | Replace with | Hex |
|---|---|---|
| `glyphicon glyphicon-arrow-right` | `&#10132;` (➔) | `&#10132;` |
| `glyphicon glyphicon-earphone` | `&#9742;` (☎) | `&#9742;` |
| `glyphicon glyphicon-calendar` | `&#128197;` (📅) | `&#128197;` |

Components affected in AOT:
- `BeachEquipment.astro` — CTA arrow
- `ClosingCTA.astro` — phone link
- `HeroSection.astro` — "Book Online" button

CSS: delete the `@font-face { font-family: "Glyphicons Halflings"; ... }` block from `active-oahu-tours-minimal.css` (or the relevant CSS file).

**Verification recipe:**
```bash
grep -E "glyphicon|glyphicons-halflings" dist/index.html dist/_aot_assets/*.css
# Expect: zero matches
```

### 2. `image-redundant-alt` — decorative images with alt text duplicating heading

**Symptom:** Lighthouse flags 3 FeatureBlock card images where `alt="Guided Kayak Tours"` (etc.) duplicates the card's `<h4>Guided Kayak Tours</h4>` heading.

**Cause:** FeatureBlock renders an icon image above each card heading. The heading already describes the icon, so the alt text is redundant screen-reader noise.

**Fix recipe:** Set `iconAlt: ""` in the JSON data for the 3 cards (in `homepage-data.json` → `sections[].features[]`). Empty alt = decorative image = screen readers skip it. Heading still announces the card purpose.

```json
{
  "id": "guided-kayak",
  "icon": "/wp-content/uploads/2019/06/Self-guided-Tours.png",
  "iconAlt": "",
  "heading": "Guided Kayak Tours",
  ...
}
```

**Verification recipe:**
```bash
grep -oE '<img[^>]*class="kb-img[^"]*"[^>]*>' dist/index.html | grep -v 'alt=""' | grep -v '<img[^>]*\salt\s'
# Expect: zero matches (all kb-img icons should have empty alt)
```

### 3. `target-size` — links/buttons smaller than 24×24px

**Symptom:** Lighthouse `target-size` audit fails on the secondary CTA in FeatureBlock (`<a href="/rentals/" class="feature-cta-secondary">More Rental Info</a>`).

**Cause:** The link has no padding and its bounding box is smaller than the 24×24px minimum touch target. Common with inline `<a>` elements that don't get block-level padding.

**Fix recipe:** Add `display: inline-block` + `min-height: 24px` + padding to the affected class. Use **negative margin** to keep the visual size unchanged (so layout doesn't shift):

```css
.feature-cta-secondary {
  display: inline-block !important;
  min-height: 24px !important;
  padding: 8px 4px !important;
  margin: -8px -4px !important;  /* compensates for padding so layout stays the same */
}
```

The negative-margin trick: `padding: 8px` adds 16px to total height; `margin: -8px` removes 16px. Net visible size = original. Touch target = padded size.

**Verification recipe:** Re-run Lighthouse after rebuild and verify `target-size` flips from 0 to 1.

### 4. `lcp-lazy-loaded` — above-the-fold LCP image marked lazy

**Symptom:** Lighthouse flags the Tripadvisor Travelers' Choice logo in `HeroSection.astro` as the LCP candidate, but it's marked `loading="lazy"`. Lazy-loading delays LCP.

**Cause:** The Hero card's right-column logo (`TC_transparent_BF-Logo_L_2024_RGB.png`, 200×220) is the visual focal point above the fold. It needs to load eagerly to be the LCP candidate.

**Fix recipe:**
```astro
<img
  loading="eager"
  decoding="async"
  width="200"
  height="220"
  src={tripadvisorLogo}
  alt={tripadvisorLogoAlt}
  fetchpriority="high"
  class="kb-img wp-image-3595"
/>
```

Three changes:
1. `loading="lazy"` → `loading="eager"`
2. Add `fetchpriority="high"` (modern hint that the browser can use for prioritization)
3. Width/height already present (good — prevents CLS)

**Verification recipe:**
```bash
grep -oE '<img[^>]*TC_transparent[^>]*>' dist/index.html
# Expect: loading="eager", fetchpriority="high", no "lazy"
```

### 5. `heading-order` (regression guard)

**Symptom:** Production has `<h5>Our Most Popular Experiences</h5>` immediately followed by `<h6>View All Tours & Activities</h6>` — Lighthouse flags the h5→h6 jump as invalid order.

**Why we DON'T have this problem:** Our `FeaturedTours.astro` renders the "View All Tours & Activities" link as a `<a>` inside a `<div>`, NOT wrapped in an `<h6>`. The result is a `heading-order` PASS (0 violations).

**Don't fix what isn't broken.** If you ever change the link to be wrapped in a heading tag, use `<h5>` to maintain the hierarchy (h2 → h5 → h3 cards is sequential), or skip the heading tag entirely.

## The verification script shape

Save as `/tmp/hermes-verify-audit-fixes.py` and run after every AOT homepage change:

```python
#!/usr/bin/env python3
"""Ad-hoc verification of AOT homepage Lighthouse audit fixes."""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path('/home/ubuntu/work/astro-homepage-work/okf/architecture/astro-emdash/homepage/astro')
DIST = ROOT / 'dist'
INDEX = DIST / 'index.html'

results = []
def check(name, passed, detail=''):
    status = '✓ PASS' if passed else '✗ FAIL'
    results.append((passed, name, detail))
    print(f"  {status}  {name}  {detail}")

# Build first
subprocess.run(['npm', 'run', 'build'], cwd=ROOT, check=True, capture_output=True)

# 1. Build artifacts
check("index.html exists", INDEX.exists(), f"({INDEX.stat().st_size} bytes)")
css_files = list(DIST.glob('**/*.css'))  # NOTE: CSS may be in dist/_aot_assets/
check("CSS bundle exists", bool(css_files), f"({css_files[0].relative_to(DIST) if css_files else 'NONE'})")
index_content = INDEX.read_text()
css_content = css_files[0].read_text() if css_files else ''

# 2. Audit fixes
# - Glyphicons eliminated
check("No glyphicon @font-face in CSS", '@font-face' not in css_content or 'glyphicons-halflings' not in css_content)
check("No <span class=\"glyphicon...\"> in HTML", 'class="glyphicon' not in index_content)
# - image-redundant-alt: empty alt on kb-img icons
imgs = re.findall(r'<img[^>]*class="kb-img[^"]*"[^>]*>', index_content)
empty_alt = [i for i in imgs if 'alt=""' in i or re.search(r'<img[^>]*\salt\s', i)]
check("All kb-img icons have empty alt", len(empty_alt) == len(imgs), f"({len(empty_alt)}/{len(imgs)} empty)")
# - lcp-lazy-loaded: Tripadvisor logo eager
trip = re.search(r'<img[^>]*TC_transparent[^>]*>', index_content)
if trip:
    check("Tripadvisor logo: loading=eager", 'loading="eager"' in trip.group(0))
    check("Tripadvisor logo: fetchpriority=high", 'fetchpriority="high"' in trip.group(0))
# - target-size: min-height:24px on .feature-cta-secondary
fc = re.search(r'\.feature-cta-secondary\s*\{([^}]+)\}', css_content)
if fc:
    check("feature-cta-secondary: min-height:24px", 'min-height: 24px' in fc.group(1) or 'min-height:24px' in fc.group(1))

# 3. Production parity (regression checks)
# - Section order: feature-block → featured-tour-hero → rental-types → popular-tours → beach-equipment → closing-cta → awards-section → testimonial-section
order = ['feature-block', 'featured-tour-hero', 'rental-types', 'popular-tours', 'beach-equipment', 'closing-cta', 'awards-section', 'testimonial-section']
positions = [index_content.find(f'class="{cls}"') for cls in order]
is_sorted = all(positions[i] < positions[i+1] for i in range(len(positions)-1))
check("Section order matches production", is_sorted)
# - View All link
check("View All Tours & Activities link", 'view-all-tours-link' in index_content)
# - Book buttons
check("data-book on tour Book buttons", index_content.count('data-book') >= 3)

# Summary
passed = sum(1 for r in results if r[0])
print(f"\nPassed: {passed}/{len(results)}")
sys.exit(0 if passed == len(results) else 1)
```

## Local vs deployed Lighthouse scores (the gap)

Lighthouse run against `http://127.0.0.1:<port>/` (Python http.server on the `dist/` dir) is **not** representative of Cloudflare Pages scores:

| Audit | Local | Cloudflare |
|---|---|---|
| Performance | 91 | 93+ |
| Accessibility | **100** | 100 (target) |
| Best Practices | **75** (13 local 404s for `/wp-content/...`) | 93+ |
| SEO | 66 (intentional `noindex`) | 69 |

The 13 "errors" on local are all `/wp-content/uploads/...` images that the Python server can't serve (no symlink to production WP uploads). On Cloudflare, those images are served fine — verified with HEAD requests on the deployed preview.

**Conclusion:** Local Lighthouse is a useful early signal (especially for `accessibility`), but the only authoritative scores come from Cloudflare. Always verify the deployed preview, not local.

## Bonus perf fixes (2026-07-29, second pass)

### 6. `render-blocking-resources` — Google Fonts stylesheet + external SDK

**Symptom:** Lighthouse `render-blocking-resources` flags `https://fonts.googleapis.com/css2?...` (~810ms) and `https://fareharbor.com/embeds/sdk/latest.js` (~780ms) as blocking the first paint.

**Cause:** The default `<link rel="stylesheet" href="...googleapis.com/css2?...">` in `<head>` blocks render until the CSS is parsed. External `<script src="...">` (even with `is:inline`) blocks render until the script downloads and parses.

**Fix recipe for Google Fonts** — async CSS pattern in `BaseLayout.astro`:

```astro
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=..." />
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=..."
      media="print" onload="this.media='all'" />
<noscript>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=..." />
</noscript>
```

The `media="print"` makes the browser treat it as print-only (low priority, non-blocking). The `onload` swaps to `media="all"` once it loads. The `<noscript>` is the fallback for users without JS.

**Fix recipe for external SDK scripts** — add `defer` attribute:

```astro
<!-- WRONG: blocks render even with is:inline -->
<script is:inline src="https://fareharbor.com/embeds/sdk/latest.js"></script>

<!-- RIGHT: download in parallel, execute after parse -->
<script is:inline defer src="https://fareharbor.com/embeds/sdk/latest.js"></script>
```

`is:inline` keeps Astro from bundling the external URL. `defer` lets the browser continue parsing HTML and downloads the script in parallel. SDK init scripts that run on `DOMContentLoaded` (like our `data-book` FH handler) work fine with `defer` because DOMContentLoaded fires after all deferred scripts execute.

**Verification recipe:**
```bash
grep -oE '<link[^>]*href="https://fonts\.googleapis[^>]*>' dist/index.html
# Expect: 1× preload + 1× async (media="print" onload) + 1× noscript fallback — NOT a plain blocking stylesheet
grep -oE '<script[^>]*src="https://fareharbor[^>]*>' dist/index.html
# Expect: defer present
```

### 7. Duplicate `<head>` from nested BaseLayout (architectural bug)

**Symptom:** `dist/index.html` is ~69KB and contains 2× of every `<head>` tag (preconnect, preload, FH SDK, JSON-LD schemas, etc.). Verify by grepping for any head tag — `grep -c "fonts.googleapis" dist/index.html` returns 4 instead of 1.

**Cause:** `src/pages/index.astro` wraps content in `<BaseLayout>`, AND `src/components/shell/SiteShell.astro` ALSO wraps its slot in `<BaseLayout>`. Both renders emit a full `<head>`.

**Fix recipe:**

1. Remove the outer `<BaseLayout>` from `index.astro`. Keep `<SiteShell>` as the single root.
2. Forward BaseLayout props through `SiteShell` (define them on the Props interface, destructure into a `layoutProps` object, spread into `<BaseLayout {...layoutProps}>`).
3. Pass layout props from `index.astro` to `<SiteShell>` instead of `<BaseLayout>`.

**Verification recipe:**
```bash
# Each head tag should appear exactly once (JSON-LD schemas are intentionally 2×)
for tag in 'rel="preconnect" href="https://fonts.googleapis' \
           'rel="preconnect" href="https://fonts.gstatic' \
           'rel="preload" as="style" href="https://fonts.googleapis' \
           'src="https://fareharbor.com/embeds/sdk'; do
  count=$(grep -c "$tag" dist/index.html)
  echo "$tag: $count (expect 1)"
done
```

**Impact:** HTML size dropped from 69,029 → 53,661 bytes (-15.4KB / -22%) on the AOT homepage. Most of the duplicated content was `<head>` tags, FH SDK, and JSON-LD schema blocks.

## Verification script gotchas — false positives I hit

The verification regexes need a manual sanity pass against the actual HTML before trusting them. From the 2026-07-29 sessions, two false positives slipped past:

1. **`grep -oE '<a\s+[^>]*href="[^"]+"[^>]*>\s*</a>'` flagged the 3 `kb-section-link-overlay` links as "empty".** They're not — they have `aria-label="Kayak Tours"` etc. for screen readers and overlay a sibling `<h3>`. Fix: in the regex, allow `<a>` tags with `aria-label=` to count as non-empty.

2. **`<noscript><link rel="stylesheet" ...></noscript>` was counted as "plain blocking" Google Fonts.** It's not — it's only applied when JS is disabled. Fix: filter out `<noscript>` content from the "plain blocking" count, or use a regex with a negative lookbehind for `noscript>`.

**Lesson:** before claiming the verification script is green, paste one or two of its "passed" markers into a raw `grep` and eyeball the HTML to confirm the regex means what you think it means.

## Why the verification script was the recipe that found the bug

The system message after the last edit said: "no fresh passing verification evidence yet." I had pushed `488b80932` thinking the FeatureBlock was fine because the build passed and Lighthouse scores looked good. But I never ran a regex check for the **rendered** class names.

The bug: `class="wp-block-kadence-image kb-image2389_{feature.id} size-full"` rendered literal `{feature.id}` text in the HTML. Build succeeded, Lighthouse didn't flag it (CSS scoping hid it), but the actual rendered class names were broken.

The verification recipe (`grep -E 'class="[^"]*\{[a-z]+\.[a-z]+\}[^"]*"' dist/index.html`) caught it. Without that recipe, the bug would have shipped.

**This is the `corrections-lead-with-recipe` skill in action** — and it's the reason the verification script is non-negotiable for AOT homepage work. Don't trust the build. Don't trust Lighthouse. Trust the regex check against `dist/index.html`.

## Cross-reference

- The template-literal interpolation bug is also documented in `references/aot-astro-template-jsx-pitfalls-2026-07-29.md` §"Pitfall #4".
- The Cloudflare deploy-lag pattern is documented in the same file §"Cloudflare Pages deploy lag".
- See also `pwp-visual-qa-proof` skill for the broader Playwright + Lighthouse + axe workflow this recipe slots into.
