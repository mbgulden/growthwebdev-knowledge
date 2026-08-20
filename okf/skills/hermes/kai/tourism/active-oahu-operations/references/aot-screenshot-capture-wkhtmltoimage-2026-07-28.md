# AOT Screenshot Capture — Staging Visual QA

**Date:** 2026-07-28
**Updated:** 2026-07-29 — added wkhtmltoimage external-URL limitation warning

## ⚠️ Critical: wkhtmltoimage Cannot Fetch External HTTPS URLs

`wkhtmltoimage` on this VM **cannot access external HTTPS resources** (e.g. hero background
images from `activeoahutours.com`, CDN assets, Google Fonts). Screenshots it produces will
show missing images and broken backgrounds even when the page renders correctly in a real browser.

**Always verify visual correctness with the browser tool, not wkhtmltoimage.**

`wkhtmltoimage` is useful ONLY for structural comparisons (section heights, element positioning,
footer nav group verification). Never trust it for image backgrounds or external fonts.

Exit code `1 due to network error: OperationCanceledError` is normal — the page still renders
but external resources will be missing from the screenshot.

## Production Color Reference (from browser_console on activeoahutours.com 2026-07-29)

| Element | Color | Hex |
|---------|-------|-----|
| Header/branding bg | white | `rgb(255, 255, 255)` |
| Nav bg | #006699 | `rgb(0, 102, 153)` |
| Nav text | white | `rgb(255, 255, 255)` |
| Hero bg image | Active-Oahu-Lifestyle-225-2X1-1000.jpg | URL: `https://activeoahutours.com/wp-content/uploads/2024/01/Active-Oahu-Lifestyle-225-2X1-1000.jpg` |
| Hero overlay | rgba(0,0,0,0.3) | from `kb-section-has-overlay::before` |
| Footer bg | #006699 | `rgb(0, 102, 153)` |
| Font: h1 | Open Sans Condensed | `"Open Sans Condensed", "Arial Narrow", Arial, sans-serif` |
| Font: body | Open Sans | `"Open Sans", Arial, sans-serif` |

## Verify External Resources with browser_console (authoritative)

```javascript
// Hero background image — if this returns the URL, the image IS loading
var hbg = document.querySelector('.hero-bg');
hbg ? window.getComputedStyle(hbg).backgroundImage : 'NOT FOUND'

// Nav link colors in real browser
var nl = document.querySelector('.nav-link');
nl ? window.getComputedStyle(nl).color : 'NOT FOUND'

// Footer computed background
var f = document.querySelector('footer');
f ? window.getComputedStyle(f).backgroundColor : 'NOT FOUND'
```

## Tool Decision Tree

1. **Need a specific element's computed color/font/image?** → `browser_console` with `getComputedStyle`
2. **Need to see overall page structure?** → `browser_navigate` + `browser_snapshot`  
3. **Need side-by-side prod vs staging for layout comparison?** → `wkhtmltoimage` on BOTH (structural only, no external images)

## wkhtmltoimage Usage (Structural Comparisons Only)

```bash
wkhtmltoimage --width 1280 --quality 80 \
  "https://deploy-fresh.active-oahu-tours-mirror.pages.dev/" \
  /tmp/staging_full.jpg
```

## aria-current on Homepage: Absence Is Correct

On the homepage (`/`), `aria-current="page"` is **absent**. This is correct —
`aria-current` only renders when `Astro.url.pathname` matches the nav item href.
On the homepage, no nav link points to `/`, so no item gets `aria-current`.

## Sending Screenshots to Telegram

```
MEDIA:/tmp/aot_01_header_nav.jpg
MEDIA:/tmp/aot_02_hero.jpg
...
```
Width 1280px fits the Telegram mobile viewport.
