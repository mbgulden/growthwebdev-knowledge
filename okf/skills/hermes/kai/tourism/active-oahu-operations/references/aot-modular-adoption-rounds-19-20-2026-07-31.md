# AOT Modular Adoption — Rounds 19-20 (2026-07-31)

Companion to `references/aot-modular-adoption-rounds-16-18-2026-07-31.md`.
Covers rounds 19-20: BeachEquipment + MokuluaFeatureBlock + ClosingCTA +
Awards + FooterExtras + DealBanner, plus the `:root` token consolidation
bug that surfaced during round 19.

## What shipped

- R19 — BeachEquipment + MokuluaFeatureBlock: 75/25 split blocks now use
  `<Section palette="white" container={false}>` + BEM scoping + tokens.
- R19 — **Token consolidation fix**: removed duplicate `:root` block from
  `active-oahu-tours-minimal.css`. Old CSS had `--aot-gray-600: #555555`
  silently overriding new tokens' `#586e75` (and several others).
- R20 — ClosingCTA + Awards + FooterExtras + DealBanner: bottom-of-page
  sections now use Section primitive + tokens + BEM scoping.

R19 verification: 35/35 PASS.
R20 verification: 36/36 PASS.
Hero h2 still 60px throughout — no regression.

## 4 new pitfalls (all bit during this session)

### Pitfall A — Duplicate `:root` blocks silently override tokens

When two CSS files both declare `:root { --aot-gray-600: ... }` with
different values, **the one loaded LATER wins the cascade**, even though
the source order in BaseLayout imports `tokens.css` first. Astro bundles
both files into a single CSS, and within a stylesheet, the later `:root`
block is the last `var()` source for that token.

Symptoms: brand-new components using `var(--aot-gray-600)` rendered in
the old color. BeachEquipment heading was `#555` (legacy) instead of
`#586e75` (token). No console errors, no Lighthouse warnings.

Fix:
1. Remove the duplicate `:root` block from `active-oahu-tours-minimal.css`.
2. Add the legacy token VALUES to `tokens.css` if old code still uses
   the old names (`gray-100: #e0e0e0`, `gray-400: #666666`,
   `gray-600: #555555`, `gray-900: #333333`, `--aot-off-white`,
   `--aot-text-light`, `--aot-hero-bg`, `--aot-skip-bg`).
3. Verification: `grep -oE ':root\{[^}]+\}' dist/_aot_assets/*.css`
   should show exactly ONE `:root` block defining `--aot-*` tokens.

Detection: bundle the dist CSS, find the `:root` blocks, sort them by
position, and check that all `--aot-gray-XXX` tokens have the same
value across the bundle. If the same token name appears with different
values, you have a duplicate.

### Pitfall B — Scoped CSS doesn't reach `<Section>`'s rendered DOM

When `<Section class="my-thing">` is used, the rendered `<section>` has
Section's `data-astro-cid-XXX`, NOT the parent's. So a parent component's
scoped CSS like:

```astro
<style>
  .my-thing { background-color: red; }
</style>
```

...does NOT match the Section's `<section>`, because Astro generates
`.my-thing[data-astro-cid-PARENT]` and the actual DOM has
`data-astro-cid-SECTION`.

Symptoms: closing-cta bg was transparent (rgba(0,0,0,0)) despite
`background-color: var(--aot-hero-bg)` being in the scoped style. The
CSS rule never matched the rendered element.

Fix: use `<style is:global>` when wrapping `<Section>` (or any other
child primitive) and styling it from the parent. This is appropriate
for "wrapper" components like ClosingCTA, Awards, and FooterExtras.

```astro
<style is:global>
  .closing-cta {
    background-color: var(--aot-hero-bg);
    color: var(--aot-white);
  }
</style>
```

Detection: `getComputedStyle(el).backgroundColor` returns `rgba(0,0,0,0)`
when expected bg is set. Or: the rule is in the scoped CSS bundle but
the selector is `data-astro-cid-X` for the parent — confirm by grepping
the bundle for the rule.

### Pitfall C — Card primitive's hardcoded `<Heading size="lg">` was too big

Card.astro used `<Heading level={3} size="lg" color="body">{title}</Heading>`
hardcoded. `size="lg"` resolves to `2rem` = `32px` (with 16px root).
FeaturedTours cards needed `1.1rem` (17.6px) to match production.

Fix: added `titleSize` prop to Card primitive with default `"lg"`,
then set `titleSize="sm"` in FeaturedTours:

```astro
// Card.astro
<Heading level={3} size={titleSize} color="body">{title}</Heading>

// FeaturedTours.astro
<Card ... titleSize="sm" />
```

Also: Card's price was `<span class="aot-card__price">`. Replaced with
`<PriceTag price={price} size="md" align="right" class="aot-card__price" />`
so prices get the canonical `.aot-price` styling (1.1rem navy,
font-heading, optional strike-through) consistently across all consumers.

### Pitfall D — Heading primitive sets inline `font-size` style

Heading primitive uses `style={inlineStyle}` where `inlineStyle` is
`font-size: ${sizeMap[size]}` (e.g. `font-size: 5rem` for `xxxl`).
Inline styles beat scoped CSS **even with `!important`** — unless the
inline style doesn't have `!important` (which is normal CSS cascade
behavior).

When migrating HeroSection to use `<Heading size="xxxl">`, the hero h2
rendered at `5rem` = `80px` (with 16px root). Scoped CSS rules with
`font-size: 60px !important` should have won, but they DIDN'T, because
the scoped CSS uses `[data-astro-cid-HERO]` on `.hero-banner h2`, and
the h2 has `data-astro-cid-HEADING` from the primitive.

Fix: use a **global CSS rule with attribute selector** to beat the
inline style:

```css
.hero-banner h2[style*="font-size"] {
  font-size: 60px !important;
}
```

The `[style*="font-size"]` matches any element with a `style`
attribute containing "font-size" (i.e., the primitive's output), and
`!important` in the global rule beats the inline style.

**DO NOT** try to fix this by setting `html { font-size: 62.5% }`
globally. Michael rejected this verbatim — "you made ALL the site
text smaller in order to make the header text slightly smaller".
That breaks every other `rem` value on the site. Use targeted
attribute selectors instead.

Detection: if browser shows h2 at wrong size despite scoped CSS
looking correct, check the element's `style` attribute — if it's
`style="font-size: Xrem"`, that's the inline style from Heading
primitive winning.

## Modular adoption recipe (R19-20)

For each module:

1. **Wrap with Section primitive:**
   ```astro
   import Section from "../primitives/Section.astro";
   <Section palette="white" padding="lg" container={false} class="my-section">
     ...
   </Section>
   ```
   Use `container={false}` for full-width sections (FeatureBlock,
   FeaturedTours, BeachEquipment, MokuluaFeatureBlock, Awards,
   FooterExtras). Use `container={true}` (default) for content-width
   sections (ClosingCTA, Testimonial).

2. **Add BEM-style class names** to all elements inside.

3. **Convert hex colors to tokens** (--aot-blue, --aot-gray-XXX, etc.).
   If a token doesn't exist, add it to `tokens.css`.

4. **Convert rem/font-family literals to tokens**:
   - `font-family: 'Open Sans Condensed'` → `var(--aot-font-heading)`
   - `font-family: 'Open Sans'` → `var(--aot-font-body)`
   - `0.5rem`, `1rem`, etc. → `var(--aot-space-2)`, `var(--aot-space-4)`
   - `#4px border-radius` → `var(--aot-border-radius)`

5. **If wrapping `<Section>`, use `<style is:global>`** (Pitfall B).

6. **Build + verify hash match + browser_console computed styles.**

## Verification script shape

```python
import urllib.request, hashlib, ssl, re
# ... fetch live HTML and CSS, hash-match ...
# Check BEM classes are present
# Check hero h2 60px !important override is still in CSS
# Check tokens are used (grep for var(--aot-) in scoped rules)
# Check no html font-size 62.5%
# Check other modules still work
```

## Files changed

- `src/components/homepage/BeachEquipment.astro` (228 → 213 lines)
- `src/components/homepage/MokuluaFeatureBlock.astro` (201 → ~190 lines)
- `src/components/homepage/ClosingCTA.astro` (~50 → 51 lines, `is:global`)
- `src/components/homepage/Awards.astro` (~110 → 105 lines, `is:global`)
- `src/components/homepage/FooterExtras.astro` (~218 → 226 lines, BEM, `is:global`)
- `src/components/homepage/DealBanner.astro` (tokens for colors)
- `src/styles/active-oahu-tours-minimal.css` (removed duplicate `:root`)
- `src/styles/tokens.css` (added legacy gray-100/400/600/900, off-white, text-light, hero-bg, skip-bg)
- `src/components/primitives/Card.astro` (added `titleSize` prop, uses `<PriceTag>`)

## Commits

```
2839914f9 feat(modular): migrate FeaturedTours to Section + Card + PriceTag + BookingButton primitives
b304c2a45 feat(card): add titleSize prop + use PriceTag primitive for price
ee3f1d187 feat(modular): migrate BeachEquipment + MokuluaFeatureBlock
f45ff81ab fix(css): consolidate :root blocks
1c14b2ab4 feat(modular): migrate ClosingCTA + Awards + FooterExtras + DealBanner
```