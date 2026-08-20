# AOT mobile tier-3 nav + homepage QA notes — 2026-07-11

## Trigger

Michael reported that desktop nav looked good, but mobile third-level `Kayak Rentals` submenu text still disappeared. He also asked for the “next step,” which in this run meant continuing into homepage Lighthouse spot-check after the visual QA path was stable.

## Durable workflow lessons

### Mobile nested nav depth differs from desktop

Desktop third-level contrast can pass while mobile still fails because mobile submenu display/color rules are inside a separate `@media (max-width: 767px)` block and may only target first-level toggled parents.

For AOT mobile nav, verify the path:

`Rentals → Kayak Rentals → Mokolii Kayak Rentals / Kailua Kayak Rentals`

The mobile CSS fix pattern that worked:

```css
@media (max-width: 767px) {
  .main-navigation .menu-item-has-children.toggled > .sub-menu,
  .main-navigation .menu-item-has-children:focus-within > .sub-menu {
    display: block !important;
  }

  .main-navigation .sub-menu .sub-menu,
  .main-navigation .menu .sub-menu .sub-menu,
  .main-navigation .sub-menu .sub-menu li,
  .main-navigation .menu .sub-menu .sub-menu li {
    background-color: #004466 !important;
  }

  .main-navigation .sub-menu .sub-menu a,
  .main-navigation .menu .sub-menu .sub-menu a,
  .main-navigation.toggled .sub-menu .sub-menu a {
    color: #ffffff !important;
    background-color: #004466 !important;
    opacity: 1 !important;
    text-shadow: 0 1px 1px rgba(0,0,0,0.35) !important;
  }

  .main-navigation .sub-menu .sub-menu a:hover,
  .main-navigation .sub-menu .sub-menu a:focus,
  .main-navigation .sub-menu .sub-menu li:hover > a,
  .main-navigation .sub-menu .sub-menu li:focus-within > a,
  .main-navigation.toggled .sub-menu .sub-menu a:hover,
  .main-navigation.toggled .sub-menu .sub-menu a:focus {
    color: #ffffff !important;
    background-color: #003f5e !important;
    text-decoration: underline !important;
    text-underline-offset: 0.16em !important;
  }
}
```

Cache-bust `nav-fix.css` after this change and verify clean production loads the new query key after Cloudflare purge.

### Verification script pattern

Use rendered Playwright mobile checks, not visual guessing. A deterministic check may force nested submenus open for measurement:

```js
document.querySelectorAll('#primary-menu .sub-menu').forEach(ul => {
  ul.style.display = 'block';
  ul.style.visibility = 'visible';
  ul.style.opacity = '1';
});
```

Then assert for both `Mokolii Kayak Rentals` and `Kailua Kayak Rentals`:

- computed `color === rgb(255, 255, 255)`
- inherited/effective background is dark (`#004466` in this session)
- contrast ≥ 4.5:1; target evidence here was `10.4:1`
- `display != none`, `visibility == visible`, `opacity != 0`, width/height > 0
- mobile hamburger opened with `aria-expanded="true"`

If Hermes raises the post-edit verification guard, do not cite an earlier verifier. Create a fresh `/tmp/hermes-verify-mobile-tier3-*.py` using Python `tempfile`, have it generate a temporary JS Playwright probe, run it, clean up both temporary scripts, and report the result explicitly as focused ad-hoc verification.

### Visual report receipts

When reporting visual fixes as done, include:

- live URL and PR link
- production screenshot(s) via `MEDIA:/tmp/...`
- viewport/state each screenshot proves, e.g. mobile menu open, desktop hover path, FareHarbor after click
- computed evidence, not only screenshots
- whether the evidence is focused ad-hoc verification vs canonical suite green

### Homepage golden-path QA after layout fixes

After fixing jumbled homepage/Kadence layout, run a production golden-path QA pass before calling the page stable:

1. Desktop hero grid and no column nesting.
2. Desktop nav including third-level submenu contrast.
3. Mobile hero stack.
4. Mobile hamburger open state.
5. Popular experiences card row alignment + visible Book links.
6. FareHarbor Book Online click produces `window.FH`, FareHarbor iframe, or FareHarbor network requests.

Useful screenshots from this class of run:

- desktop hero
- desktop third-level nav
- desktop popular cards
- FareHarbor after click
- mobile hero
- mobile nav open

### Lighthouse next-step pattern

When Michael asks for the “next step” after visual QA, a natural follow-on for AOT homepage is a production Lighthouse spot-check against thresholds:

| Metric | Target |
|---|---:|
| Performance | ≥ 70 |
| Accessibility | ≥ 85 |
| Best Practices | ≥ 80 |
| SEO | ≥ 90 |

In this run, homepage Lighthouse spot-check showed desktop performance/SEO/accessibility were strong, but mobile performance and Best Practices needed a follow-up remediation pass. Treat third-party FareHarbor/Google/Cloudflare warnings separately from controllable first-party items. Controllable items included remaining non-nav contrast flags, image delivery/weight, and cache/font/image optimizations.
