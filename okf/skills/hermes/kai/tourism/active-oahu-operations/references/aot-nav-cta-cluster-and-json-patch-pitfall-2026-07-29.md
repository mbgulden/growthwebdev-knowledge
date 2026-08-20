# AOT Nav CTA Cluster + JSON Patch Pitfall (2026-07-29)

> **Session source:** Active Oahu 2026-07-29 — third verification pass. Added Call + Book Now CTA cluster to `PrimaryNav.astro` (Tier 1.1 of the nav improvement plan). Also discovered a JSON `replace_all=true` pitfall that corrupted unrelated entries.
> **Use this when:** adding CTA elements to `PrimaryNav.astro` (or any nav), or when patching JSON config files via `patch`/`write_file` where field names may repeat.

## Net-new vs prior PrimaryNav a11y pattern

The `aot-primary-nav-a11y-pattern-2026-07-28.md` reference documented the 4 top-level nav items + dropdown system. This session added a **CTA cluster** (right-aligned Call + Book buttons) at the end of the nav. The base nav pattern is unchanged.

## The CTA cluster pattern

### Markup (in `PrimaryNav.astro`, after the `<ul class="nav-menu">`)

```astro
<!-- CTA cluster (desktop only — mobile shows these in header utility bar) -->
<div class="nav-cta-cluster" data-nav-cta-cluster>
  <a href={phoneHref} class="nav-cta nav-cta--phone"
     aria-label={`${phoneLabel} (808)498-1894`}>
    <svg class="nav-cta-icon" aria-hidden="true" viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
      <path d="M20 15.5c-1.25 0-2.45-.2-3.57-.57a1 1 0 0 0-1.02.24l-2.2 2.2a15.05 15.05 0 0 1-6.59-6.58l2.2-2.21a1 1 0 0 0 .25-1.02A11.36 11.36 0 0 1 8.5 4a1 1 0 0 0-1-1H4a1 1 0 0 0-1 1c0 9.39 7.61 17 17 17a1 1 0 0 0 1-1v-3.5a1 1 0 0 0-1-1z"/>
    </svg>
    <span class="nav-cta-label">{phoneLabel}</span>
  </a>
  {bookingHref && (
    <a href={bookingHref} class="nav-cta nav-cta--book" data-book>
      <svg class="nav-cta-icon" aria-hidden="true" viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
        <path d="M19 4h-1V2h-2v2H8V2H6v2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 16H5V10h14v10zm0-12H5V6h14v2zM7 12h5v5H7v-5z"/>
      </svg>
      <span class="nav-cta-label">{bookingLabel}</span>
    </a>
  )}
</div>
```

### CSS pattern

```css
.nav-cta-cluster {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-left: auto;   /* right-align within the nav */
  padding-left: 1rem;
}
.nav-cta {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.875rem;
  min-height: 44px;    /* touch target */
  border-radius: 4px;
  font-weight: 700;
  text-decoration: none;
  color: #ffffff;
  transition: background-color 0.15s ease, transform 0.15s ease;
}
.nav-cta:focus-visible { outline: 2px solid #ffffff; outline-offset: 2px; }

/* Phone CTA — ghost outline style */
.nav-cta--phone {
  background: transparent;
  border: 1.5px solid rgba(255, 255, 255, 0.5);
}
.nav-cta--phone:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: #ffffff;
}

/* Book CTA — primary filled accent (orange) */
.nav-cta--book {
  background: #f5a623;
  color: #1a3a5c;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
}
.nav-cta--book:hover {
  background: #ffc44d;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

/* Mobile: hide cluster — header utility bar already shows Call + Book Online */
@media (max-width: 767px) {
  .nav-cta-cluster { display: none; }
}
```

### Data wiring (in `Header.astro`)

```astro
<PrimaryNav
  bookingHref={business.bookingUrl}
  bookingLabel="Book Now"
  phoneHref={business.telephoneHref}
/>
```

Add `business.bookingUrl` to `aot-shell-data.json`:
```json
"business": {
  ...
  "bookingUrl": "https://fareharbor.com/embeds/book/activeoahutours/?u=f9b48d18-715e-4919-9c8e-077c045cf4bf&from-ssl=yes",
  ...
}
```

### Why `data-book` on the nav CTA — the FH modal handler is generic

The FareHarbor init script in `BaseLayout.astro` already handles any `[data-book]` anchor via:
```js
document.querySelectorAll('[data-book]').forEach(link => {
  link.addEventListener('click', e => {
    e.preventDefault();
    if (window.FH) {
      window.FH.open({ shortname: 'activeoahutours', fallback: 'simple', url: link.href });
    }
  });
});
```

So adding `data-book` to ANY anchor — whether in FeaturedTours cards, Hero, or the nav — gets FareHarbor modal behavior automatically. The nav CTA simply reuses the existing pattern. This is why no JS changes were needed for this fix.

## Verification recipe for nav CTA changes

```python
#!/usr/bin/env python3
"""Verify Nav CTA cluster (AOT homepage)."""
import re, sys
from pathlib import Path

ROOT = Path('/home/ubuntu/work/astro-homepage-work/okf/architecture/astro-emdash/homepage/astro')
INDEX = ROOT / 'dist' / 'index.html'
results = []
def check(name, ok, detail=''):
    results.append((ok, name, detail))
    print(f"  {'✓' if ok else '✗'} {name} {detail}")

html = INDEX.read_text()
css_files = list((ROOT / 'dist').glob('**/*.css'))
css = css_files[0].read_text() if css_files else ''

# Cluster + buttons rendered
check("nav-cta-cluster wrapper present", 'class="nav-cta-cluster' in html)
phone = re.search(r'<a[^>]*class="nav-cta nav-cta--phone"[^>]*>', html)
book  = re.search(r'<a[^>]*class="nav-cta nav-cta--book"[^>]*>', html)
check("Call CTA button rendered", phone is not None)
check("Book CTA button rendered", book is not None)

# Book CTA wired to FH with data-book
if book:
    tag = book.group(0)
    check("Book CTA href → FareHarbor", 'fareharbor.com/embeds/book' in tag)
    check("Book CTA has data-book (FH modal trigger)", 'data-book' in tag)

# Phone CTA wired
if phone:
    tag = phone.group(0)
    check("Phone CTA href → tel:", 'href="tel:' in tag)
    check("Phone CTA has aria-label", 'aria-label="Call ' in tag)

# SVG icons present + aria-hidden (decorative)
check("Phone + calendar SVG icons present", html.count('class="nav-cta-icon"') >= 2)
check("CTA SVGs aria-hidden", 'aria-hidden="true"' in html)

# CSS: mobile hides, desktop right-aligns, 44px touch target, orange accent
check("Mobile rule hides cluster", '@media (max-width:767px)' in css.replace(' ', '') and 'nav-cta-cluster{display:none' in css.replace(' ', ''))
check("margin-left:auto for right-align", 'margin-left:auto' in css)
check("44px touch target", 'min-height:44px' in css)
check("Book CTA orange accent", '#f5a623' in css.lower() or 'rgb(245,166,35)' in css.lower())

# Regression: existing nav items intact
check("Activities & Tours intact", 'Activities &amp; Tours' in html)
check("Rentals intact", '>Rentals<' in html)
check("Sub-menu items intact", 'Kailua Kayak Rentals' in html and 'How to Transport Kayaks' in html)

# Hero regression
check("Hero Book Online intact", 'Book Online' in html)
check("Hero Book Online has FH onclick", 'FH.open' in html)

passed = sum(1 for r in results if r[0])
print(f"\nPassed: {passed}/{len(results)}")
sys.exit(0 if passed == len(results) else 1)
```

## Pitfall: `patch --replace_all=true` can clobber unrelated JSON entries

**What happened:** Adding `business.bookingUrl` to `aot-shell-data.json` via `patch --replace_all=true` (because the source string ` "telephoneHref": "tel:+180****1894",\n "email": "info@activeoahutours.com",` appeared twice — once in the `business` block, once in a `utilityLinks[]` entry that happened to share the field structure).

The result: the second occurrence (an email contact entry in `utilityLinks`) got its `sourceText`/`href` fields replaced with `telephoneHref`/`bookingUrl`/`email`. The build still passed because JSON was still valid — but the email contact entry now had wrong fields, and a downstream consumer reading `mailto:info@...` would have hit the wrong href.

**Fix recipe:** When patching JSON config files:

1. **First try `patch` WITHOUT `replace_all=true`.** If the source string is unique, it patches cleanly and exits.
2. **If patch returns "Found 2 matches", DO NOT use `replace_all=true` blindly.** Look at the other match — it's almost always a different entry that just happens to share field structure.
3. **Use a more specific anchor.** Include enough surrounding JSON to make the source string unique. For example, instead of patching from `"telephoneHref":`, anchor on `,"name": "Active Oahu Tours",\n    "phone": "(808)498-1894",\n    "telephoneHref"` — that includes the unique business.name field.
4. **Verify after patch:** `git diff path/to/file.json` and confirm only the intended entry changed.

**Generalized rule:** For JSON / config files, NEVER use `replace_all=true` on a partial key. If the patch tool reports multiple matches, treat it as a signal that your anchor is too generic, not as a hint to use replace_all.

## Pitfall: regex verification scripts can have false positives AND false negatives

Two failure modes from the 2026-07-29 verification scripts:

**False positive (misses real bugs):** A regex like `<a\s+[^>]*href="[^"]+"[^>]*>\s*</a>` for "empty link" detection flagged the Kadence `kb-section-link-overlay` `<a>` tags as empty. They weren't — they had `aria-label="Kayak Tours"` (decorative overlay with accessible name). The fix: explicitly allow `aria-label`-bearing tags to count as non-empty.

**False negative (overlooks real bugs):** A regex for "plain blocking stylesheet" matched `<noscript><link rel="stylesheet" href="...googleapis..."></noscript>` as plain blocking. It isn't — it's only rendered when JS is disabled. The fix: use a negative lookbehind to exclude `<noscript>` content.

**Recipe to catch this class of error:** After writing a verification script, manually paste one or two of its PASS markers into a raw `grep` against `dist/index.html` and eyeball the matches. If the matches look different than you expected, the regex is wrong.

This is the `corrections-lead-with-recipe` skill in action: when a verification check is suspicious, the recipe is to spot-check the regex against raw output, not to trust the script.

## Cross-references

- Base nav a11y pattern (mobile toggle, dropdowns, keyboard nav, menubar role): `references/aot-primary-nav-a11y-pattern-2026-07-28.md`
- JSX pitfalls (template-literal class interpolation, parens-around-conditional, etc.): `references/aot-astro-template-jsx-pitfalls-2026-07-29.md`
- Lighthouse audit fixes (image-redundant-alt, target-size, lcp-lazy-loaded, glyphicon replacement, render-blocking fix, duplicate-head dedup): `references/aot-lighthouse-audit-recipe-2026-07-29.md`
- Cloudflare Pages deploy lag diagnostic (HTTP 200 lies; content-marker probe): `references/aot-astro-template-jsx-pitfalls-2026-07-29.md` §"Cloudflare Pages deploy lag"
- Prismatic Engine lane-violation on push (override pattern): `references/aot-astro-template-jsx-pitfalls-2026-07-29.md` §"Prismatic Engine: lane-violation can hit without you editing the file"

## Net Lighthouse impact (with CTA cluster)

| Metric | Before CTA | After CTA |
|---|---|---|
| Performance | 97 | 97 (no change) |
| Accessibility | 100 | 100 (no change) |
| Best Practices | 75 (local artifacts) | 75 |
| SEO | 66 (intentional noindex) | 66 |

CTA cluster added ~1.3KB to HTML (53,661 → 54,940 bytes). No regression on any Lighthouse metric.

## Browser-based nav verification (programmatic)

If you have access to a browser tool, the live DOM can confirm wiring beyond regex:

```js
// In browser console
Array.from(document.querySelectorAll('.nav-cta')).map(el => ({
  text: el.textContent.trim().slice(0, 30),
  href: el.getAttribute('href'),
  hasDataBook: el.hasAttribute('data-book'),
  hasAriaLabel: el.hasAttribute('aria-label'),
  visible: el.offsetParent !== null,  // false if hidden via CSS
}));
```

Expected:
```
[
  { text: "Call", href: "tel:+180****1894", hasDataBook: false, hasAriaLabel: true,  visible: true },
  { text: "Book Now", href: "https://fareharbor.com/embeds/book/...", hasDataBook: true, hasAriaLabel: false, visible: true }
]
```

At mobile viewport (<768px), both should have `visible: false` (display:none via media query).
