# R21 — `!important` audit + inline-style → CSS refactor (2026-08-02)

Removed production-fight `!important` tags and moved inline `style="..."`
presentations out of `.astro` files into scoped CSS. Topped off the modular
rounds (R16-R20) before opening the next phase of homepage work.

## What changed

**Part 1 — `!important` reduction (migrated-component selectors).**

Used specificity-raised selectors instead of `!important`:

| Selector | Before | After | Specificity |
|---|---|---|---|
| `.tours-grid` | `... !important` | `section.tours-grid` | 0,0,1,1 |
| `.tours-grid .tour-card` | `... !important` | `.tours-grid > article.tour-card` | 0,0,2,1 |
| `.tours-grid img` | `... !important` | `.tours-grid > article img` | 0,0,2,1 |
| `.feature-cta` | `... !important` | `.feature-cta.feature-cta` | 0,0,2,0 |
| `.feature-cta-secondary` | `... !important` | `.feature-cta-secondary.feature-cta-secondary` | 0,0,2,0 |
| `.closing-cta-bg` | `... !important` | `section.closing-cta-bg` | 0,0,1,1 |
| `.feature-block` (bg) | `... !important` | `section.feature-block` | 0,0,1,1 |
| `.awards-section` (bg) | `... !important` | `section.awards-section` | 0,0,1,1 |
| `.testimonial-section` (bg) | `... !important` | `section.testimonial-section` | 0,0,1,1 |
| `.view-all-link` | `... !important` | `.view-all-link.view-all-link` | 0,0,2,0 |
| `.view-all-tours-link` | `... !important` | `.view-all-tours-link.view-all-tours-link` | 0,0,2,0 |

The element selector (`section`) prefix wins over the `<Section>` primitive's
`[data-astro-cid-*]` attribute selector (0,0,2,0) by adding element-level
specificity (0,0,1,1). The doubled-class trick (`.foo.foo`) raises specificity
to 0,0,2,0 — higher than single-class rules but equal to attribute-selector
rules, so the element-prefix pattern is preferred when fighting
`[data-astro-cid-*]`.

**Removed dead code (no matching HTML):**
- `.info-strip` rules (was replaced by FeatureBlock in R16)
- `#deal-banner` rules (DealBanner uses `.site-banner-announcement`)

**Numbers:**
- Source `!important` count in `active-oahu-tours-minimal.css`: ~80 → 66 (−17%)
- Built CSS bundle `!important` count: 115 → 59 (**−49%** — minification is
  much more efficient without `!important`)
- **`!important` fighting migrated components: 0**

**Part 2 — Inline style → CSS.**

5 inline `style="..."` values moved to scoped CSS using CSS custom properties
as the data channel:

| File | Inline value | CSS class |
|---|---|---|
| `DealBanner.astro` | `style="color: #069"` | `.site-banner-announcement__heading { color: #069 }` |
| `HeroSection.astro` | `style="background-image: url(...)"` | `style="--hero-bg-image: url(...)"` + `.hero-left-col { background-image: var(--hero-bg-image) }` |
| `BeachEquipment.astro` (×2) | `style="background-image: url(...)"` | `style="--bg-image: url(...)"` + scoped `background-image: var(--bg-image)` |
| `MokuluaFeatureBlock.astro` (×2) | same pattern as BeachEquipment |

The remaining inline `style=` attributes in the codebase are all CSS
**custom property setters** (`--bg-image`, `--hero-bg-image`, `style={inlineStyle}`
on the Heading primitive). That is the correct pattern for passing dynamic
data to CSS — the property value lives in the markup, the property
declaration lives in CSS.

**Part 3 — Tokens.**

Added 5 legacy token aliases to `tokens.css` so the refactored rules
resolve: `--aot-navy-light`, `--aot-orange`, `--aot-orange-dark`,
`--aot-closing-bg`, `--aot-light-gray`. These were defined in the OLD
`:root` block of `active-oahu-tours-minimal.css` (removed in R20) and
are still referenced via `var(--aot-*)` in the global stylesheet.

## Pitfalls (new for R21)

**P1. Module selector with `data-astro-cid-*` attribute wins over
single-class overrides.**

The Section primitive emits `class="aot-section aot-section--palette-X ..."
data-astro-cid-XYZ=""`. Any CSS rule trying to override its `background-color`
without `!important` needs to match `0,0,2,0` or higher specificity.
A plain `.feature-block { background-color: white; }` (0,0,1,0) loses to
`.aot-section--palette-none[data-astro-cid-X]` (0,0,2,0).

Fix: `section.feature-block { background-color: var(--aot-white); }` adds
the element selector → 0,0,1,1 → wins.

**P2. CSS custom property pattern for dynamic bg-images.**

`<div style="background-image: url('...')">` is the lazy way. The CSS-vars
pattern is cleaner and keeps the presentation in CSS:

```astro
<div class="bg" style={`--bg-image: url('${image}')`}>
```
```css
.bg { background-image: var(--bg-image); /* + size/position/repeat */ }
```

Works for any dynamic value: url, color, size, transform. The convention
to standardize on: **presentations in CSS, only data in inline style**.

**P3. Minifier shortens hex codes — specificity tables still match.**

`#003366` → `#036` after minification. Any pattern that uses the full
form will fail to match. See `aot-astro-css-minification-verifier-2026-07-31.md`
for the full allow-list pattern. Note that this only affects hash-search
verification scripts — the cascade itself doesn't care about hex form.

**P4. Orphan global CSS with `!important` keeps bleeding into the new component.**

Carry-forward from R17 (see `aot-modular-adoption-rounds-16-18-2026-07-31.md`
pitfall D). After every R-value refactor, grep the global stylesheet for
class names defined in the migrated component — there's almost always at
least one orphan `!important` rule waiting to ambush the new component.

Verified with: `grep -nE "selector-class-name" src/styles/active-oahu-tours-minimal.css`.
For `.closing-cta` specifically, R20 had to remove 4 orphan rules (2 with
`!important`, 2 cascading wins) before the new scoped styles could apply.

**P5. The "fresh verification evidence" trap.**

Tool reminders show "stale verification" when the last verification script
was from a different round. Solution: re-run a fresh verification script
with the new round's scope, even if the previous one passed. Don't claim
the work is verified just because the latest PR was successfully pushed.

## Verification (R21)

**23/23 PASS** across 9 categories. The verification script's scope:

1. Local hash matches live staging hash
2. Source `!important` count, with regex walking every CSS rule block
   (comments stripped first to avoid false positives)
3. Audit selectors against migrated-component class list
4. Inline style audit — removes all `--custom-prop: value;` declarations
   from the inline value, then checks if anything non-custom remains
5. Built CSS bundle `!important` count
6. Hero h2 still 60px (regression)
7. All 11 modules render
8. CSS custom property pattern in HTML (`--hero-bg-image`, `--bg-image`)
9. CSS bundle has `background-image: var(--xxx)` for all 5 elements
   (Hero, BeachEquipment×2, MokuluaFeatureBlock×2)

## Commit on content/astro-homepage

```
288e70fbf refactor(R21): remove !important tags + move inline styles to CSS
```

Staging URL: `https://content-astro-homepage.active-oahu-tours-mirror.pages.dev/`
