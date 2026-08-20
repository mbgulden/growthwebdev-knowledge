# Hero Font-Size: Production's `html { font-size: 62.5% }` + `clamp()` pattern (Round 14 — 2026-07-31)

**Class:** AOT homepage production-parity CSS, **specifically: hero typography sizing**.
**Scope:** Why hero H1/H2 looked huge on staging even when our CSS matched production's source.

## The Problem

User reported: "the hero text is way too big on the home page on staging."

What I had written in `HeroSection.astro`:
```css
.hero-banner h1 { font-size: 1.25rem; }   /* = 20px */
.hero-banner h2 { font-size: 5rem; }      /* = 80px */
```

The CSS **matched production's source values exactly** (from `nav-fix.css` and `kadence-homepage.css`). But:
- Production's rendered H2 = **60px**
- My staging's rendered H2 = **80px**

Difference: **20px**, with my H2 occupying 65% of the 444px hero (288px tall), vs production's 144px tall (32% of hero).

## The Root Cause: `html { font-size: 62.5% }`

Production sets:
```css
html { font-size: 62.5%; -webkit-overflow-scrolling: touch; -webkit-tap-highlight-color: rgba(0, 0, 0, 0); }
```

This is the classic "1rem = 10px" trick used by WordPress themes (and Bootstrap, etc.):
- Default browser root: 16px
- 62.5% × 16px = **10px** root
- Now `1rem = 10px`, `5rem = 50px`, `6rem = 60px`

Production's H2 CSS uses **Kadence's clamp()** with the `xxxl` size token:
```css
--global-kb-font-size-xxxl: clamp(2.75rem, 0.489rem + 7.065vw, 6rem);
.kt-adv-heading2389_1c90f7-e5 {
  font-size: var(--global-kb-font-size-xxxl, 5rem);
}
```

At 1280px viewport with 10px root, the clamp resolves to:
- min: `2.75 × 10 = 27.5px`
- preferred: `4.89 + 7.065 × 12.8 = 95.32px`
- max: `6 × 10 = 60px`
- result: **60px** (the max wins)

Without the 62.5% root, with default 16px:
- min: `2.75 × 16 = 44px`
- preferred: `7.82 + 7.065 × 12.8 = 98.24px`
- max: `6 × 16 = 96px`
- result: **96px** (the max wins, but the preferred was always going to clamp to it anyway, so it stays huge)

## The Fix (3 files)

### 1. `src/styles/tokens.css` — add the root font-size rule

```css
html {
  font-size: 62.5%;  /* 1rem = 10px — matches production */
  -webkit-overflow-scrolling: touch;
  -webkit-tap-highlight-color: rgba(0, 0, 0, 0);
}
```

⚠️ **Watch out:** setting `font-size: 62.5%` on `<html>` affects every `rem` value
across the entire site. Any existing component that hard-coded `1rem = 16px`
will silently halve. Run a full visual regression after this change.

### 2. `src/components/homepage/HeroSection.astro` — use clamp() for responsive sizing

Replace fixed `font-size: Xrem` with Kadence-style clamp:

```css
.hero-banner h1 {
  font-size: clamp(1.25rem, 0.995rem + 1.265vw, 1.5rem);  /* 12.5 - 24px responsive */
  font-family: 'Open Sans Condensed', 'Arial Narrow', Arial, sans-serif;
  font-weight: 700;
  /* ... */
}
.hero-banner h2 {
  font-size: clamp(2.75rem, 0.489rem + 7.065vw, 6rem);    /* 27.5 - 60px responsive */
  /* H2 production's exact clamp curve */
  /* ... */
}
```

The `0.489rem + 7.065vw` midpoint curve is what makes the H2 grow smoothly from
`27.5px` on a phone up to `60px` on a wide desktop, without ever exceeding `60px`.

### 3. `src/components/primitives/Heading.astro` — `xxxl` size = 6rem (was 5rem)

The Heading primitive's size map had `xxxl: "5rem"` to match production's
fallback in `--global-kb-font-size-xxxl: clamp(..., 6rem)`. With the 62.5%
root, the production **clamp maximum** is `6rem × 10px = 60px`, not `5rem ×
10px = 50px`. The size map should reflect the production max:

```ts
const sizeMap: Record<string, string> = {
  sm: "1rem",     // sm
  md: "1.25rem",  // md
  lg: "2rem",     // lg
  xl: "3rem",     // xl
  xxl: "4rem",    // xxl
  xxxl: "6rem",   // xxxl (was 5rem — now matches production clamp max in 62.5% root)
};
```

⚠️ **If you skip step 1 (the 62.5% root), bumping xxxl to 6rem produces an
86px H2** (6rem × 16px default). The two changes must be applied together.

## Diagnostic Recipe

When "hero text too big" or "heading sizes wrong" is reported, check the chain:

```bash
# 1. Read production's hero CSS directly (ground truth)
curl -s https://activeoahutours.com/wp-content/themes/activeoahu/css/style.css \
  | grep -A 1 "^html"

# 2. Check what production ACTUALLY renders (computed styles, not CSS values)
# In browser_console on production:
var h2 = document.querySelector('main h2');
JSON.stringify({
  fontSize: getComputedStyle(h2).fontSize,
  rootFontSize: getComputedStyle(document.documentElement).fontSize,
})
# → {"fontSize": "60px", "rootFontSize": "10px"}

# 3. Compare to staging computed styles
# 4. If they differ, trace which layer is wrong:
#    - html font-size (62.5% rule)
#    - clamp() formula in CSS
#    - token map values in primitives
#    - which CSS wins specificity (Component-scoped vs global vs inline)
```

The 3-layer ladder matches: tokens → primitives → component-scoped overrides.
If the component sets `font-size: 5rem` (fixed) on the hero h1, that wins over
both the primitive's `xxxl` and the tokens — even with the 62.5% root fix.

## Verification Recipe

```bash
# After build, check the bundled CSS has the 62.5% root (minified):
grep -oE 'html\{font-size:62\.5%' dist/_aot_assets/*.css

# Check the H2 clamp with minified whitespace (no spaces inside clamp):
grep -oE 'clamp\(2\.75rem,\.489rem\s*\+\s*7\.065vw,6rem\)' dist/_aot_assets/*.css

# Browser visual check (most reliable):
var h2 = document.querySelector('.aot-hero-section h2');
return {
  fontSize: getComputedStyle(h2).fontSize,    // expect: 60px (or less on small viewport)
  root: getComputedStyle(document.documentElement).fontSize,  // expect: 10px
};
```

## Pitfalls

1. **The 16px default is invisible until you measure.** Without `getComputedStyle(
   document.documentElement).fontSize`, you can't tell if `<html>` is 16px or 10px.
   Add this to every hero CSS verification.

2. **Components that hardcode `rem` values silently break** when you switch to
   62.5% root. The FeaturedTours cards, the footer gallery, the test grid — every
   `2rem`, `1rem`, `0.5rem` is now 10/16 = 62.5% of its previous size. Run a full
   visual regression sweep before pushing.

3. **`getComputedStyle().fontSize` clamping math in JavaScript:**
   ```js
   const min = 2.75 * 16;  // 44 if root is 16, 27.5 if root is 10
   const pref = 0.489 * 16 + 7.065 * (window.innerWidth / 100);  // vw math is root-independent
   const max = 6 * 16;     // 96 if root is 16, 60 if root is 10
   const result = Math.min(Math.max(pref, min), max);
   ```
   `vw` units in the clamp do NOT depend on root font-size. Only `rem` units do.
   Production's `0.489rem + 7.065vw` produces the same `pref` regardless of root.

4. **Local dev `npm run dev` may not exercise the production CSS order.**
   Compare in the actual deployed bundle, not in `dist/`, when debugging.

5. **Production's `--global-kb-font-size-xxxl` max is `6rem`, but the variable
   default fallback in `--global-kb-font-size-xxxl, 5rem` is `5rem`.** This is
   not a contradiction — the fallback only matters if the variable is undefined.
   The active rule uses the clamp value, which resolves to 60px at 1280px.

## When to Reach for This Pattern

This is a **class-level technique** for any modern WP theme that uses Kadence Blocks
(or similar block libraries). Use it whenever:
- The site uses `--global-kb-font-size-*` clamp variables
- The hero/landing page has noticeably oversized headings vs production
- A lighthouse report flags "font-size-too-large" warnings
- Component-scoped CSS overrides are visibly bigger than the production clone

Don't apply if:
- The site uses pixel units throughout (`font-size: 60px`, no `rem`)
- The design system wants `1rem = 16px` (math becomes harder)
- Any third-party CSS expects the 16px default (rare but possible with math expressions in calc())

## Related references

- `references/aot-astro-css-minification-verifier-2026-07-31.md` — companion:
  CSS minification (e.g., `0.489rem + 7.065vw` becomes `clamp(2.75rem,.489rem
  + 7.065vw,6rem)` in the bundle; verify with regex that allows no-space forms).
- `references/aot-modular-primitives-design-system-2026-07-31.md` — the 3-layer
  design system (tokens + primitives + adopt) that this fix slots into.
- `references/aot-production-header-css-extraction-round-9b-2026-07-31.md` —
  read production's `nav-fix.css` for ground truth on phone color, font, etc.
- `references/aot-hallucinated-commit-verification-2026-07-31.md` —
  confirmed-completion discipline (i.e., grep the source, not `dist/`).
