# Header Refinement: Single-Banner + Nav Flex + Branding Layout (2026-07-31)

> **Session source:** Active Oahu Round 9. After 7 header production-parity changes in Round 8 (commit `ac84321a2`), live preview still had two compounding visual bugs: (a) two stacked banners (Kadence `#deal-banner` at y=0 + my `.site-banner-announcement` at y=40), and (b) the nav was 138px tall instead of ~48px because `.aot-primary-nav` was `display: block` and its children (menu + CTA cluster) stacked vertically. The duplicate-banner check and the per-element `getBoundingClientRect().height` measurement were the two diagnostics that caught them.
>
> **Use this when:** matching production header/nav layout in any Astro/React/Vue site where flex vs. block on the parent determines the child stacking behavior — and the bug is invisible without measuring element heights.

## Pitfall 1: Duplicated Role Elements from Prior Rounds

When adding a "production-style" element (e.g. `.site-banner-announcement`), always check whether the build ALREADY renders an element with the same role from a prior round. The Kadence-style `#deal-banner` was already rendering the same 15% off message; my new section added a duplicate without checking.

**Detection recipe (run before claiming the layout is correct):**

```bash
# After every header/footer change, look for duplicate semantic roles:
grep -c 'role="banner"\|<header\b' dist/index.html
grep -c 'site-banner-announcement\|"deal-banner"' dist/index.html
grep -c '<footer\b\|role="contentinfo"' dist/index.html
# Counts > 1 → probably a duplicate. Investigate before claiming complete.

# Browser-side confirmation (definitive):
#   Array.from(document.querySelectorAll(".site-banner-announcement, #deal-banner")).map(el => ({
#     y: Math.round(el.getBoundingClientRect().top),
#     h: Math.round(el.getBoundingClientRect().height),
#     role: el.className || el.id,
#   }))
# Expected: one element. Two elements → duplicate.
```

**Fix pattern:** Pick ONE element and remove the other. Don't try to keep both with different visual treatments — production has exactly one, so staging should too.

## Pitfall 2: Display: Block on Parent Causes Vertical Stack Even When Children Are Display: Flex

The `.aot-primary-nav` was rendering as `display: block` (the default — no flex CSS rule on the parent). Its children `.nav-menu` and `.nav-cta-cluster` had `display: flex` for their INTERNAL layout. But two flex children inside a block parent **stack vertically**. The nav was 138px tall because each child was on its own row.

```html
<nav class="aot-primary-nav">  <!-- display: block (DEFAULT) -->
  <ul class="nav-menu">         <!-- display: flex internally → items horizontal -->
  <div class="nav-cta-cluster"> <!-- display: flex internally → items horizontal -->
</nav>
<!-- 138px tall: menu 76px + cta 62px stacked -->
```

Fix: make the nav itself flex.

```css
.aot-primary-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;  /* menu left, cta right */
}
```

**Detection recipe (this is the killer — it does NOT show in HTML or in the standard Lighthouse audit):**

```javascript
// Run from browser_console AFTER every nav change:
var nav = document.querySelector(".aot-primary-nav");
var children = Array.from(nav.children).map(c => ({
  cls: c.className.split(" ")[0],
  h: Math.round(c.getBoundingClientRect().height),
  w: Math.round(c.getBoundingClientRect().width)
}));
return {
  navHeight: Math.round(nav.getBoundingClientRect().height),
  children: children,
};
// Expected output for a nav with menu + cta side by side:
//   navHeight: 50, children: [{cls: "nav-menu", h: 50, w: 580}, {cls: "nav-cta-cluster", h: 50, w: 97}]
// Got: navHeight: 138, children: [{cls: "nav-menu", h: 76, w: 1100}, {cls: "nav-cta-cluster", h: 62, w: 1100}]
// → children are STACKED (both w=1100 = full parent width). Add display:flex to parent.
```

This is invisible in:
- HTML source (no markup error)
- Static CSS (each child's CSS is correct)
- Lighthouse (it doesn't audit layout-vs-intent)
- Playwright screenshots unless you happen to look at the height

The ONLY way to catch it is to MEASURE the parent height and compare to the production target. Always run the height-measurement diagnostic after nav/grid changes.

## Pitfall 3: Nav Link Padding Inflates Nav Height Past Production Spec

`.nav-link { padding: 1rem 1.125rem }` = 16px vertical padding × 2 + ~22px line-height = ~54px, but production has 13px 18px = ~48px. The cumulative effect across the nav bar is significant (138px → 70px after fix).

**Recipe — production nav specs:**
```css
.nav-link {
  padding: 0.8125rem 1.125rem;  /* 13px 18px */
  font-size: 15px;                /* not 16px */
  line-height: 1.2;
}
```

## Pitfall 4: `word-wrap` and `hyphens` Default Behavior After CSS Resets

Production's nav and breadcrumb use natural word wrap. Some CSS resets (or `word-break: break-all`) inherited from Kadence would have forced mid-word breaks. Confirmed NOT a problem in the Astro `minimal.css` (no Kadence break rules remain), but if you add a new component that renders long strings (e.g. tour names), always verify word-wrap.

## The Final Round 9 Layout Numbers (Verified Live)

| Element | y | height | width |
|---|---:|---:|---:|
| `.site-banner-announcement` | 0 | 59 | 1265 |
| `header.clearfix` | 64 | 198 | 1265 |
| `#branding` | 64 | 120 | 1100 |
| `nav.aot-primary-nav` | 192 | **70** | 1108 |
| `.nav-menu` | 192 | 70 | 580 |
| `.nav-cta-cluster` | 196 | 62 | 97 |
| `.breadcrumb-container` | 262 | 35 | 1265 |

Total visible header region: 297px (from y=0 to y=297, where main starts at y=297). Down from ~392px before Round 9.

Production target: ~220-250px (banner 57 + header 144 + breadcrumb 30). Reasonably close — the remaining ~50px is branding padding that production handles differently (it uses inline `display: flex` with different padding values). Not worth chasing further until the rest of the page is parity-perfect.

## Related

- `aot-cdn-stale-js-after-deploy-2026-07-31.md` — when "it's still old" is a CDN layer issue, not a layout bug.
- `aot-browser-tool-cache-vs-cdn-cache-2026-07-31.md` — when `browser_navigate` keeps showing old DOM even after `curl` confirms the new HTML is deployed.
- `aot-hallucinated-commit-verification-2026-07-31.md` — when the file was never edited and the build/deploy look fine.
- `aot-staging-vs-prod-structural-diff-2026-07-30.md` — the broader structural diff recipe that would have flagged the dual-banner and nav-flex bugs as outlier signals.
- `astro-css-architecture.md` — Kadence CSS replacement patterns.
