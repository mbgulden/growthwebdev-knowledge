# AOT homepage visual QA receipts pattern — 2026-07-10

## When this applies

Use this after homepage/nav/layout fixes when Michael asks to continue the “next step,” asks for proof, or says a visual change is done. A text-only summary is not enough for visual work; include screenshots and exact rendered assertions.

## Session learning

After fixing the AOT homepage hero markup and nested nav contrast, the useful next step was a production golden-path QA pass rather than another code edit. The QA verified desktop/mobile layout, desktop third-level nav, popular cards, and FareHarbor booking launch.

Michael also explicitly reinforced the reporting preference: when a visual change is marked done, include live/PR links and screenshots, not just textual verification.

## Golden-path QA scope

Run rendered Playwright on production `https://activeoahutours.com/` and verify:

1. Desktop hero layout
   - `.kb-row-layout-id2389_6ed5ef-6d > .kt-row-column-wrap` display is `grid`.
   - Desktop grid columns are expected (`580px 580px` at 1440px in this session).
   - Left hero column `.kadence-column2389_30e251-8a` and right column `.kadence-column2389_80c4a3-08` are siblings.
   - Assert `first.contains(second) === false`.
   - Right column x-position is to the right of left column.
   - No horizontal overflow.

2. Desktop nav, including nested depth
   - Hover `Rentals` then `Kayak Rentals`.
   - Verify third-level links `Mokolii Kayak Rentals` and `Kailua Kayak Rentals` are visible with nonzero geometry.
   - Measure computed color/background contrast for parent and third-level links; assert >= 4.5:1.

3. Popular experiences cards
   - Assert the first three `.activity-item` cards are aligned on the same y-coordinate.
   - Assert each has a visible Book link.

4. FareHarbor booking launch
   - Click the first visible `Book Online` link.
   - Evidence can be any of: `window.FH` present, FareHarbor iframe created, or `fareharbor.com` network requests fired.
   - Do not claim checkout fully completed unless the actual checkout path is exercised.

5. Mobile hero + nav
   - Use viewport around `390 x 844`.
   - Assert hero right column stacks below left and is not nested.
   - Assert no horizontal overflow.
   - Tap `button.menu-toggle` and assert `aria-expanded="true"`, menu visible, and top links present.

## Screenshot receipts

For visual QA reports, attach screenshots with `MEDIA:/tmp/...` and explain what each proves. Useful filenames:

- `/tmp/aot-qa-desktop-hero.png`
- `/tmp/aot-qa-desktop-third-nav.png`
- `/tmp/aot-qa-desktop-popular-cards.png`
- `/tmp/aot-qa-desktop-fareharbor-after-click.png`
- `/tmp/aot-qa-mobile-hero.png`
- `/tmp/aot-qa-mobile-nav-open.png`

If image analysis tools fail or produce oversized persisted errors, still include the raw screenshot artifacts and rely on Playwright geometry/assertions for verification. Do not turn that transient vision failure into a durable “vision is broken” rule.

## Reporting pattern

Final report should lead with:

- Status and live URL.
- PR link if a PR was involved.
- Verification type: e.g. “focused Playwright production QA, not full canonical Lighthouse suite.”
- Pass/fail table for each golden-path area.
- Screenshot attachments.
- Caveat separating third-party FareHarbor/GA warnings from first-party page errors.
- A concise **Next Step** aligned with the golden path.

## Known caveat

FareHarbor/GA can emit a warning like `embed.js getGA4ClientIds fetch list of tags from google_tag_manager failed...`. Treat it as third-party warning unless there are first-party `pageerror`s or booking launch evidence is absent.
