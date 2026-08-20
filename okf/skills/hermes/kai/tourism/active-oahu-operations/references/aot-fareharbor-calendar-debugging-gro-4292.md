# AOT FareHarbor Calendar Debugging — GRO-4292 Fix

**Date:** 2026-07-26
**Issue:** [GRO-4292](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-4292) — Fix broken booking calendar on /rentals/
**PR:** [github.com/mbgulden/active-oahu-tours-mirror/pull/104](https://github.com/mbgulden/active-oahu-tours-mirror/pull/104)
**Branch:** `feature/gro-4025`

---

## Problem

The `/rentals/` page had two instances of a lazy-load FareHarbor calendar mechanism:
- A `<div class="aot-lazy-fh-calendar" data-src="..."><button>Load booking calendar</button></div>`
- Clicking the button triggered `aot-lazy-fareharbor-calendar.js` to dynamically inject the FareHarbor script
- The script returned HTTP 200 but threw **3 silent JS exceptions** in the browser before initializing
- Result: "Loading booking calendar..." persisted indefinitely

## Diagnosis

### 1. Check if FareHarbor script URL loads
```bash
curl -sS -I "https://fareharbor.com/embeds/script/calendar/activeoahutours/?fallback=simple&flow=728039"
# Returns HTTP 302 → HTTP 200 text/javascript — script IS accessible
```

### 2. Check browser console
Browser console showed `TypeError: Cannot read properties of undefined (reading 'destination')` from `embed.js` — the FareHarbor integration kit had runtime errors.

### 3. Check CSP headers
```bash
curl -sS -I "https://activeoahutours.com/rentals/" | grep "content-security-policy"
```
CSP allows `script-src ... fareharbor.com` — script loading is not blocked by headers.
CSP allows `frame-src https://fareharbor.com` — iframe embedding is allowed.

### 4. Check FH_IntegrationKit global
In browser console, `window.FH_IntegrationKit` was `undefined` — the script errored before setting the global.

## Root Cause

The FareHarbor integration kit script (`embed.js`) has runtime errors in the browser context that prevent it from initializing. This is NOT a CSP issue — the script loads fine. The script itself has compatibility issues with the browser environment.

## Fix: Direct Iframe Embed

Replaced the broken JS lazy-load with a direct FareHarbor iframe:

```html
<iframe
  src="https://fareharbor.com/embeds/calendar/activeoahutours/?flow=728039"
  width="100%" height="700" frameborder="0"
  style="border: 0; max-width: 100%;"
  title="Active Oahu Tours Booking Calendar"
  loading="lazy">
</iframe>
```

**Key differences:**
- `/embeds/calendar/` (direct iframe) not `/embeds/script/calendar/` (JS embed)
- No JS dependency — iframe renders directly
- `loading="lazy"` for performance
- CSP `frame-src` already allows `https://fareharbor.com`

## Verification Checklist

```bash
MIRROR="/home/ubuntu/work/active-oahu-tours-mirror/site/rentals/index.html"

# 1. No broken lazy-load divs remain
LAZY_COUNT=$(grep -c 'aot-lazy-fh-calendar' "$MIRROR" || echo "0")
[ "$LAZY_COUNT" -eq 0 ] && echo "PASS: No lazy-load divs"

# 2. Correct number of iframe embeds (2)
IFRAME_COUNT=$(grep -c 'fareharbor.com/embeds/calendar/activeoahutours/' "$MIRROR")
[ "$IFRAME_COUNT" -eq 2 ] && echo "PASS: $IFRAME_COUNT iframes found"

# 3. Iframe has required attributes
grep -q 'width="100%"' "$MIRROR" && echo "PASS: width found"
grep -q 'height="700"' "$MIRROR" && echo "PASS: height found"
grep -q 'frameborder="0"' "$MIRROR" && echo "PASS: frameborder found"
grep -q 'loading="lazy"' "$MIRROR" && echo "PASS: loading=lazy found"

# 4. FareHarbor iframe URL returns 200
HTTP_CODE=$(curl -sS -o /dev/null -w "%{http_code}" \
  "https://fareharbor.com/embeds/calendar/activeoahutours/?flow=728039")
[ "$HTTP_CODE" = "200" ] && echo "PASS: FareHarbor iframe HTTP $HTTP_CODE"

# 5. CSP allows fareharbor frame-src
curl -sS -I "https://activeoahutours.com/" | grep -i "content-security-policy" | \
  tr ';' '\n' | grep -q "frame-src" && echo "PASS: CSP allows frame-src"
```

## Other Pages With Same Broken Pattern

The `aot-lazy-fareharbor-calendar.js` script is still referenced on:
- `/activities/kawela-bay-self-guided-kayak-tour/`
- `/activities/chinamans-hat-self-guided-oahu-kayak-tour/`
- `/activities/kailua-kayak-twin-islands-guided-tour/`
- `/oahu-equipment-rentals/`
- `/oahu-equipment-rentals/page/2/`
- `/multi-day-kayak-and-beach-gear-rentals/`
- Japanese locale variants under `/ja/`

These may need the same iframe replacement if they exhibit the same symptom. Check each page's browser console for the same `TypeError: Cannot read properties of undefined` pattern from `embed.js`.
