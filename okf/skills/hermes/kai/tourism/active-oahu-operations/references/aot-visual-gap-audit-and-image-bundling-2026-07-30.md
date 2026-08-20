# AOT Visual Gap Audit + Image Bundling Fix — Round 4-6 Session

> **Use this when:** Michael reports "missing images / broken images / needs layout work / ensure content is all there" for the Astro staging site. This is the end-to-end playbook from Rounds 4-6: pixel-diff diagnosis → root cause (image bundling) → layout fixes (FeaturedTourHero 50/50, Awards 2-column) → header/footer parity.

## Diagnostic ladder (in priority order)

When Michael says "images are missing," run these in order:

1. **HTML structural diff** — does the staging HTML reference the same `<img src>` / `background-image` URLs as production? (Use `aot-staging-vs-prod-diff.py`.)
2. **Image-load file-type check** — for each URL referenced, does the actual response body match the expected MIME type? **HTTP 200 alone is insufficient** (CF Pages serves `index.html` as SPA fallback for any unknown route). See `aot-cloudflare-spa-fallback-asset-404-2026-07-30.md`.
3. **Pixel-diff against cached production screenshot** — when no vision tool is available, this is the objective visual recovery measurement. See "Pixel-diff technique" below.
4. **Browser DOM verification** — use `browser_console getComputedStyle()` to confirm CSS rules actually applied (catches the case where new CSS is bundled but a stale cached version is served).

## Pixel-diff technique (no vision required)

When you can't see the image but need to know which page areas are visually empty vs full:

```python
from PIL import Image

def slice_mid_pct(img, slice_height=350):
    """Mid-tone = pixels with brightness 50-200 (real content, not white, not text)."""
    w, h = img.size
    results = []
    for i in range(h // slice_height):
        y0, y1 = i * slice_height, (i + 1) * slice_height
        crop = img.crop((0, y0, w, y1))
        rgb = crop.resize((200, 200 * crop.size[1] // crop.size[0]))
        px = list(rgb.getdata())
        mid = sum(1 for r, g, b in px if 50 <= (r + g + b) / 3 < 200) / len(px) * 100
        results.append({'slice': i, 'y_range': (y0, y1), 'mid_pct': round(mid, 1)})
    return results
```

**Key thresholds:**
- Mid-tone delta **< -30%**: critical missing content (broken images, missing sections, 404 fallback HTML)
- Mid-tone delta **-15% to -30%**: moderate gap
- Mid-tone delta **> +15%**: staging has MORE mid-tone than prod (could be intentional — nav CTAs, larger images)

**Important caveat:** production screenshots from prior sessions may be cached. Take a fresh production screenshot before pixel-diffing if possible. Staging screenshots must be taken at viewport height ≥ document height (CF Pages staging typically renders 7000-8000px tall; default 3500px screenshot truncates the footer).

## Image bundling fix (Astro + Cloudflare Pages)

When staging shows `<img src="/wp-content/uploads/...">` referencing images that aren't bundled:

```bash
# 1. Find all image URLs referenced in built HTML
grep -oE 'wp-content/uploads/[^"' "'" ' )]+\.(jpg|jpeg|png|svg)' \
  astro/dist/index.html | sort -u > /tmp/needed-images.txt

# 2. Download to astro/public/ preserving directory structure
# CRITICAL: strip leading "wp-content/" from URL because PUBLIC_DIR already
# includes "wp-content/uploads/". Otherwise you get astro/public/wp-content/wp-content/uploads/
while read -r url; do
  rel=$(echo "$url" | sed 's|^/||; s|^wp-content/||')
  out="astro/public/wp-content/${rel}"
  mkdir -p "$(dirname "$out")"
  curl -sf --max-time 20 -o "$out" "https://preview.pages.dev/${url}" \
    && [[ $(stat -c%s "$out") -ne 65413 ]] \
    && [[ $(file "$out") =~ image|JPEG|PNG ]] \
    || rm -f "$out"
done < /tmp/needed-images.txt

# 3. Rebuild — Astro copies public/ verbatim into dist/
cd astro && npm run build

# 4. Verify dist/ now has the images
find dist -type f \( -name "*.jpg" -o -name "*.png" \) | wc -l
# Should equal len(/tmp/needed-images.txt)

# 5. Push, wait for CF Pages auto-deploy, re-run image-load check
```

**CDN cache survivor pitfall:** Some images "work" before the fix because they're cached at CF's edge from a prior deployment that had them. Once cache TTL expires, those images also break. The fix MUST address the source (bundle images) — not rely on cache.

## CSS bundle hash check (avoid the silent failure)

When you update CSS but the served HTML references a stale CSS bundle:

```bash
# 1. Find the bundle URL in built HTML
grep -oE 'index\.[A-Za-z0-9_-]+\.css' astro/dist/index.html

# 2. Fetch from the correct path — it's /_aot_assets/, NOT /
curl -s https://preview.pages.dev/_aot_assets/index.C9Tlk8rR.css | sha256sum

# 3. Compare to local
sha256sum astro/dist/_aot_assets/index.C9Tlk8rR.css
```

If local hash ≠ served hash → CF Pages is serving stale CSS (CDN cache lag, usually resolves in 30-90 seconds, but trigger fresh deployment via git push).

**Bug in my own hermes-verify-round5 script:** I compared the local CSS bundle hash to the **HTML** hash (different files). The fix is to fetch the CSS bundle at `/_aot_assets/<bundle-name>` and compare CSS-to-CSS.

## Production-style layout verification (browser DOM check)

When CSS changes don't seem to take effect in screenshots, verify the rules actually applied:

```javascript
// In browser_console
const el = document.querySelector('.featured-tour-hero');
const cs = window.getComputedStyle(el);
const csImg = window.getComputedStyle(el.querySelector('img'));
JSON.stringify({
  containerDisplay: cs.display,
  containerFlexDir: cs.flexDirection,
  figureFlex: window.getComputedStyle(el.querySelector('figure')).flex,
  imgWidth: csImg.width,
  imgHeight: csImg.height,
  rect: { top: el.getBoundingClientRect().top, height: el.getBoundingClientRect().height },
});
```

**Case in point:** Round 5 changed FeaturedTourHero CSS from `flex: 0 0 300px` (image) / `height: 200px` to `flex: 1 1 50%` / `min-height: 380px`. The CSS was bundled correctly (`sha256sum` matched). But pixel-diff showed slice 3 (y=1050-1400) unchanged. The browser_console check revealed: container is `flex-direction: row`, figure is `flex: 1 1 50%`, image is `592.5px × 480px` — **the CSS worked**. The FeaturedTourHero was just at y=1529 in document space, NOT y=1050 like the previous build. The "stale-looking" pixel diff was because the arbitrary 350px slice grid didn't align with the new section boundaries.

**Lesson:** verify CSS via DOM (getComputedStyle) before assuming the diff failed. Don't trust the slice grid.

## Layout fixes (production patterns to match)

### FeaturedTourHero: 50/50 layout (production pattern)

Production uses Kadence `kt-row-layout-equal` with `kt-has-2-columns`:
- LEFT column: `<figure>` with `<img>` at **full row width × 600px height**
- RIGHT column: text with H3 + P + CTA button

Staging CSS that matches:
```css
.featured-tour-hero {
  display: flex;
  flex-direction: row;
  gap: 2rem;
  max-width: 1280px;
  margin: 0 auto;
  padding: 2rem 0;
}
.featured-tour-hero figure {
  flex: 1 1 50%;        /* not 300px — half the row */
  min-width: 0;
  overflow: hidden;
}
.featured-tour-hero img {
  width: 100%;
  height: 100%;          /* not 200px — fills column */
  min-height: 380px;
  max-height: 480px;
  object-fit: cover;
}
.featured-tour-hero .content {
  flex: 1 1 50%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 1rem 1.5rem;
}
```

### Awards: 2-column layout (production pattern)

Production uses `col-sm-4` (image) + `col-sm-8` (text), with logos stacked vertically in the image column at `max-width: 170px`:

```astro
<section class="awards-section">
  <div class="kt-row-column-wrap kt-has-2-columns">
    <div class="awards-image-col">  <!-- 33% width -->
      <div class="awards-logos">
        <img src="..." alt="..." />  <!-- each logo max-width 170px, stacked -->
      </div>
    </div>
    <div class="awards-text-col">  <!-- 67% width -->
      <h2>Awards</h2>
      <h3>Active Oahu Wins 2022 Tripadvisor Travelers' Choice Award</h3>
      <p>...</p>
    </div>
  </div>
</section>
```

**Anti-pattern (staging before fix):** centered single-column with logos in a horizontal flex row.

## Footer parity (production is white, not dark blue)

Production's `<footer>` has **no class, no inline style, no special background** — it inherits white from the body. Staging had `<footer style="background-color: #006699">` with white text and white-on-dark CSS.

```css
/* Production parity */
.aot-site-footer {
  color: #333;
  background: #f8f9fa;   /* was #006699 dark blue */
  padding: 2.5rem 1rem 1.5rem;
  border-top: 1px solid #e0e0e0;
}
.footer-business-name { color: #003366; }  /* was #fff */
.footer-nav-link { color: #555; }            /* was rgba(255,255,255,0.8) */
.footer-legal-links a { color: #666; }       /* was rgba(255,255,255,0.8) */
```

**Also remove the inline `style="background-color: #006699"` from the `<footer>` tag** in the component template — even with CSS overrides, inline styles win.

Production footer legal row has exactly **2 links**: Privacy Policy + Cancellation Policy (no Terms of Service, no Accessibility statement — those were staging additions).

## Footer gallery (production has 8 images, 2x4 grid)

Production's "Awesome Photos" gallery uses exactly these 8 image URLs in this order:
1. `/wp-content/uploads/2018/11/DSC5447_2000-115x115.jpg` — Oahu Beach Equipment Rental Packages
2. `/wp-content/uploads/2016/11/Oahu-Kayaking-Tours_31-2-115x115.jpg` — Kayaking to Mokolii
3. `/wp-content/uploads/2016/11/Oahu-Kayaking-Tours_13-115x115.jpg` — Hiking Mokoli'i on Oahu
4. `/wp-content/uploads/2016/11/Oahu-Kayak-Tours_11_thumb-1-115x115.jpg` — Best Oahu Kayak Tour
5. `/wp-content/uploads/2016/11/Oahu-Snorkeling_6-1-115x115.jpg` — Oahu Snorkel Tours
6. `/wp-content/uploads/2016/11/Standup-Paddleboard-Lessons_Thumbnail-1-115x115.jpg` — Stand up paddle boarding in Oahu
7. `/wp-content/uploads/2018/11/DJI_0988_2000_1x2-115x115.jpg` — Aerial Active Oahu photo gallery thumbnail
8. `/wp-content/uploads/2018/11/DSC5297_2000-115x115.jpg` — Oahu malibu kayaks pro 2 tandem ocean Kayak Rentals

Layout: `grid-template-columns: repeat(4, 1fr)` (4 columns × 2 rows), `gap: 2px`, images `width: 100%; height: 115px; object-fit: cover`. Below the grid: `<a href="/active-oahu-photo-gallery/">View the Gallery →</a>`.

**Note:** 4 of these images overlap with `RentalGrid` thumbnails. The "zero duplicates" goal from Round 3 was relaxed in Round 6 to match production exactly — production has these overlaps too.

## Header (already correct)

Staging already had the right header structure from Round 3:
- Logo: `Active-Oahu-Logo.jpg` 232×65
- Phone: `(808)498-1894` as h3 link
- Book Online button (FareHarbor)
- 4 top-level nav items: Activities & Tours, Rentals, Adventure Guide, Contact Us
- Sub-menus (26 total nav items matching production count)
- Call + Book Now CTA cluster (added in Round 3)

No Round 6 changes needed to Header.astro.

## Lighthouse scores progression (Rounds 3-6)

| Round | Performance | Accessibility | Best Practices | SEO |
|---|---|---|---|---|
| R3 (start) | 77 | 100 | 92 | 69 |
| R3 (end, deps added) | 80 | 100 | 77 | 69 |
| R4 (image bundling) | **98** | 100 | 77 | 69 |
| R5 (layout fixes) | 98 | 100 | 77 | 69 |
| R6 (header/footer parity) | 98 | 100 | 77 | 69 |

The Performance jump in R4 (80→98) was because real images started loading — LCP element changed from HTML 404 fallback (no real bytes) to actual JPEG (226KB), but the real image loaded fast and was correctly sized via srcset.

## Mid-tone content recovery across rounds

| Round | Total mid-tone % | % of production (40.0%) |
|---|---|---|
| R3 (pre-image-bundling) | 15.3% | 38% |
| R4 (after image bundling) | 28.4% | 71% |
| R5 (after layout fixes) | 36.0% | 90% |
| R6 (after header/footer parity) | unchanged for main content (header/footer were the focus) |

## When this recipe applies

- Michael reports "missing images / broken images / content gaps" on the Astro staging preview
- After an image-bundling fix, you want to verify per-slice recovery
- Production layout uses 50/50 or 2-column patterns but staging uses single-column or fixed-width
- Footer has dark background in staging but production is white
- Lighthouse Performance drops despite "nothing changed" (often a sign images are HTML fallbacks)

## Related references (under same umbrella)

- `references/aot-cloudflare-spa-fallback-asset-404-2026-07-30.md` — the CF Pages SPA fallback root cause + fix
- `references/aot-staging-vs-prod-structural-diff-2026-07-30.md` — the 5-signal structural audit
- `references/aot-production-parity-implementation-playbook-2026-07-30.md` — the end-to-end fix workflow
- `scripts/aot-staging-vs-prod-diff.py` — runs the 5 structural signals
- `scripts/aot-pixel-diff.py` — PIL-based per-slice visual diff (script template)
- `scripts/aot-check-images.py` — file-type aware image-load verification