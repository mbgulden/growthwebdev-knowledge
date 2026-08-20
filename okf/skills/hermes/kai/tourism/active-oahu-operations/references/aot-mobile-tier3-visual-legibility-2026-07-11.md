# AOT mobile tier-3 nav visual legibility lesson (2026-07-11)

## Trigger
Michael reported that the mobile third-tier Kayak Rentals submenu text still did not look white, and the screenshots themselves showed the problem. Computed CSS said `rgb(255,255,255)`, but the visual receipt was not convincing.

## Durable lesson
For visual nav fixes, do not stop at computed styles/contrast. Review the screenshot as a user would. If the screenshot looks wrong, treat that as a failing verification signal and harden the visual treatment.

## Working fix pattern
- Target the actual known menu items when generic submenu selectors are not visually convincing:
  - `li.menu-item-1375` — Kayak Rentals parent
  - `li.menu-item-2857` — Mokolii Kayak Rentals
  - `li.menu-item-3036` — Kailua Kayak Rentals
- On mobile, force both CSS color systems:
  - `color: #ffffff !important`
  - `-webkit-text-fill-color: #ffffff !important`
- Make the panel dark enough to visibly separate the links:
  - `background-color: #003f5e !important`
- Increase visual weight if the text still reads weak in screenshots:
  - `font-weight: 800 !important`
  - subtle dark `text-shadow`
- Cache-bust `nav-fix.css` and verify clean production loads the new query key.

## Verification pattern
Use a fresh `/tmp/hermes-verify-*` ad-hoc verifier after every edit guard. It should assert:
- local CSS contains the item-specific selectors and `-webkit-text-fill-color`
- production HTML references the current `nav-fix.css?v=N`
- rendered mobile production tier-3 links have:
  - `color` white
  - `webkitTextFillColor` white
  - dark background
  - visible geometry
  - contrast >= 4.5
- screenshot is attached and visually inspected; if it does not look white/readable, keep fixing.

Label this as focused ad-hoc verification, not canonical suite green.
