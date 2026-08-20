---
name: mobile-nav-visual-verification
description: Fix and verify mobile navigation CSS issues where computed styles pass but screenshots still look wrong. Use for mobile menus, nested dropdowns, contrast/readability, overlap/jumbled layout, cache-busted deployments, and visual-change reports that require screenshot evidence.
tags:
  - mobile-nav
  - css
  - visual-qa
  - playwright
  - accessibility
  - screenshots
---

# Mobile Nav Visual Verification

Use this when a mobile navigation or dropdown fix is disputed visually, especially when DOM/computed styles say “pass” but screenshots or a human report still show broken styling.

## Core lesson

Do **not** stop at computed color/contrast. Mobile nav bugs often come from layout flow, floats, positioning, overflow, cache state, or device rendering. A link can be white and WCAG-passing while still being visually jumbled or overlapped.

## Workflow

1. **Reproduce the real visual state**
   - Use Playwright mobile viewport, e.g. `390x1200`, `isMobile: true`, `hasTouch: true`, `deviceScaleFactor: 2`.
   - Open the hamburger/menu using the actual UI control, not only DOM class injection.
   - Capture screenshots for:
     - closed nav
     - open hamburger
     - expanded target submenu / tier-3 state

2. **Inspect both CSS and geometry**
   - Collect computed styles for target links:
     - `color`
     - `-webkit-text-fill-color`
     - background color inherited from ancestors
     - font weight
     - opacity/visibility/display
     - bounding rect
   - Collect layout styles for submenu containers:
     - `display`
     - `position`
     - `float`
     - `clear`
     - `left/top/right`
     - `height`
     - `overflow`
   - Check vertical order: each visible link’s `rect.y` must be >= previous link’s bottom. This catches overlapping rows.

3. **If text is white but screenshots still look broken, check flow**
   - Common culprit: desktop dropdown rules surviving on mobile, especially floated submenu `<ul>` elements.
   - Mobile submenu panels should usually be in normal document flow:
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
     }
     ```
   - Parent menu items containing expanded submenus should not be fixed at a single-row height:
     ```css
     .main-navigation .menu-item-has-children,
     .main-navigation .sub-menu li {
       height: auto !important;
       min-height: 0 !important;
       overflow: visible !important;
     }
     ```

4. **For stubborn mobile Safari/Chromium text color issues**
   - Force both `color` and `-webkit-text-fill-color`:
     ```css
     .main-navigation .sub-menu .sub-menu a {
       color: #ffffff !important;
       -webkit-text-fill-color: #ffffff !important;
       opacity: 1 !important;
     }
     ```
   - Use a dark enough background and calculate contrast.

5. **Cache-bust and verify production assets**
   - Increment the CSS query key across static HTML, e.g. `nav-fix.css?v=15` → `v=16`.
   - After merge/deploy, verify both:
     - production HTML references the new CSS key
     - the CSS asset itself contains the new rules
   - Purge page HTML and the CSS asset URL if Cloudflare serves stale CSS despite fresh HTML.

6. **Use screenshot + OCR/pixel fallback if image-model analysis fails**
   - If the image model is unavailable or returns a challenge/error, do not claim image-model validation.
   - Use fallback evidence:
     - Playwright screenshots
     - OCR (`tesseract screenshot.png stdout --psm 6`) to confirm readable labels and order
     - computed geometry / overlap checks
     - pixel/computed contrast checks
   - State clearly: “image model unavailable; used screenshot + OCR/layout fallback.”

7. **Create ad-hoc verifier for edited-code guardrails**
   - When no canonical suite exists, create a temporary verifier under `/tmp` with a `hermes-verify-` prefix using `tempfile`.
   - The verifier should:
     - check source CSS markers
     - check production HTML/CSS cache markers
     - run Playwright against production
     - check submenu flow and row overlap
     - capture a screenshot
     - optionally run OCR on the screenshot
     - return nonzero on failures
   - Clean up the temporary verifier file afterward when possible.
   - Report it explicitly as **focused ad-hoc verification, not canonical suite green**.

## Playwright checks to include

Minimum rendered checks:

```js
const links = [...document.querySelectorAll('#primary-menu a')]
  .filter(a => a.getBoundingClientRect().height > 0)
  .map(a => {
    const cs = getComputedStyle(a);
    const r = a.getBoundingClientRect();
    return {
      text: a.textContent.trim(),
      color: cs.color,
      webkit: cs.webkitTextFillColor,
      display: cs.display,
      visibility: cs.visibility,
      opacity: cs.opacity,
      float: cs.float,
      rect: { x: r.x, y: r.y, w: r.width, h: r.height }
    };
  });

let prevBottom = 0;
const failures = [];
for (const link of links) {
  if (link.rect.y < prevBottom - 1) {
    failures.push(`overlap/order problem: ${link.text}`);
  }
  prevBottom = Math.max(prevBottom, link.rect.y + link.rect.h);
}
```

Submenu flow check:

```js
const submenus = [...document.querySelectorAll('#primary-menu .sub-menu')]
  .map(ul => {
    const cs = getComputedStyle(ul);
    const r = ul.getBoundingClientRect();
    return {
      text: ul.textContent.trim().slice(0, 40),
      display: cs.display,
      float: cs.float,
      position: cs.position,
      clear: cs.clear,
      rect: { x: r.x, y: r.y, w: r.width, h: r.height }
    };
  });

for (const sm of submenus) {
  if (sm.display === 'block' && sm.float !== 'none') {
    failures.push(`submenu still floated: ${sm.text}`);
  }
}
```

## Reporting format

For visual-change reports include:

- Status first: fixed / not fixed / blocked
- Live URL and PR URL
- Screenshot attachments with viewport/state labels
- Verification type:
  - canonical suite green, or
  - focused ad-hoc verification, not canonical suite green
- Source checks
- Production cache checks
- Rendered mobile checks
- Any caveats, especially if image-model verification was unavailable
- Next step aligned to the user’s golden path

## Pitfalls

- **Computed contrast is not enough.** Always inspect screenshot/geometry.
- **Fresh HTML can still load stale CSS.** Verify the CSS asset content, not just the query string.
- **Desktop dropdown CSS can leak into mobile.** Reset floats, positioning, and heights under the mobile media query.
- **Do not hide a tool failure.** If image-model analysis fails, say so and use fallback evidence.
- **Do not call it suite green unless a canonical test/lint/build suite actually ran and passed.**