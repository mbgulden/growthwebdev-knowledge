# AOT mobile nav flow + visual verification notes — 2026-07-11

## Trigger

Michael reported that the mobile nav styles still looked wrong after computed contrast checks were passing. The earlier fix made the third-level `Rentals → Kayak Rentals → Mokolii/Kailua Kayak Rentals` text white, but the actual screenshot still looked jumbled.

## Durable lesson

For mobile nav work, **computed color/contrast passing is not enough**. Also verify visual row flow and stacking. In this session the real remaining defect was not text color; it was mobile submenu layout:

- submenu `<ul>` elements retained desktop float behavior;
- parent menu rows stayed around `45px` high;
- submenu children rendered visually under later top-level rows;
- the menu looked overlapped/jumbled even though tier-3 text computed as white.

## Fix pattern

Inside the mobile `@media (max-width: 767px)` block, reset submenus into normal document flow:

```css
.main-navigation .sub-menu {
  position: static !important;
  float: none !important;
  clear: both !important;
  left: auto !important;
  right: auto !important;
  top: auto !important;
  transform: none !important;
  height: auto !important;
  overflow: visible !important;
  margin: 0 !important;
}

.main-navigation .menu-item-has-children.toggled > .sub-menu,
.main-navigation .menu-item-has-children:focus-within > .sub-menu {
  display: block !important;
  float: none !important;
  clear: both !important;
}

.main-navigation .menu-item-has-children,
.main-navigation .sub-menu li {
  height: auto !important;
  min-height: 0 !important;
  overflow: visible !important;
}

.main-navigation .sub-menu li {
  float: none !important;
  clear: both !important;
  width: 100% !important;
}
```

Cache-bust `nav-fix.css` after CSS changes and purge both HTML and CSS asset URLs when Cloudflare serves a new HTML query key with an old stylesheet body.

## Verification pattern

Use rendered mobile Playwright plus visual/OCR fallback, not DOM color only:

1. Open production or preview at `390 x 1200` mobile viewport.
2. Tap `button.menu-toggle`.
3. Capture a screenshot of the natural open menu.
4. Assert `nav-fix.css?v=<new>` is loaded.
5. Assert expanded `#primary-menu` height is large enough to include submenus; in this run the broken state was about `184px`, fixed state about `1228px`.
6. Walk visible `#primary-menu a` rows by `getBoundingClientRect()` and fail if any row starts above the previous row bottom.
7. Assert every visible submenu has `float: none`, `position: static`, and `clear: both`.
8. Still measure third-level Kayak Rentals contrast and visible geometry.
9. Run OCR on the screenshot and require the ordered labels to appear, especially:
   - `Activities & Tours`
   - `Rentals`
   - `All Rentals`
   - `Kayak Rentals`
   - `Mokolii Kayak Rentals`
   - `Kailua Kayak Rentals`
   - `Multi-Day Rentals`
   - `Adventure Guide`

If an image-model endpoint is unavailable or returns a challenge page, do **not** stop or claim visual success from computed CSS alone. Capture the screenshot and use OCR + pixel/layout checks as fallback evidence, while reporting the image-model blocker honestly.

## Reporting preference reinforced

For AOT visual fixes, final reports should include:

- live URL and PR link;
- screenshot attachments with the viewport/state each proves;
- computed/layout evidence;
- OCR or image-model visual findings when the user specifically asks for visual double-checking;
- a clear label that this is focused ad-hoc verification, not canonical suite green.
