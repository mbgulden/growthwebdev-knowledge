# jQuery/magnificPopup Fix — GRO-4346 (2026-07-28)

## Problem

166 HTML pages have `magnificPopup` gallery code deployed WITHOUT jQuery in the `<head>`. The `head.html` template has jQuery (line 74), but these static exports were generated independently without template inheritance.

**Live JS errors on `/rentals/` (headless Chrome verified):**
- `ReferenceError: jQuery is not defined` — inline gallery code at line 1730
- `TypeError: a is not a function` — `magnific-popup.min.js` requires jQuery

**Affected scope:**
- 166 pages: `magnificPopup` + no jQuery
- 31 pages: inline lazyload (with `if (!$) { return; }` guard — silent)
- Total: 197 pages needing jQuery injection

## Root Cause

WordPress static export produced standalone HTML files that reference jQuery-dependent inline scripts but never included the jQuery CDN tag. The `head.html` template has jQuery, but these files were exported as complete HTML without templating.

## Fix

Inject one line before `</head>` in each affected file:

```html
<script src="/wp-includes/js/jquery/jquery.min.js?ver=3.7.1" id="jquery-core-js"></script>
```

jQuery URL verified accessible: HTTP 200 at `activeoahutours.com/wp-includes/js/jquery/jquery.min.js?ver=3.7.1`

## Injection Script (HTMLParser-based)

```python
#!/usr/bin/env python3
import os, re

JQUERY_TAG = '<script src="/wp-includes/js/jquery/jquery.min.js?ver=3.7.1" id="jquery-core-js"></script>'

def find_head_end_position(html):
    match = re.search(r'</head>', html, re.IGNORECASE)
    return match.start() if match else None

def inject_jquery(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        original = f.read()
    
    if 'jquery.min.js' in original and 'jquery-core-js' in original:
        return True, "already_has_jquery"
    
    pos = find_head_end_position(original)
    if pos is None:
        return False, "no_head_tag"
    
    modified = original[:pos] + JQUERY_TAG + original[pos:]
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(modified)
    return True, "injected"
```

## Verification

**Before fix (Playwright headless Chrome):**
```
/rentals/ — jsErrors: ["a is not a function", "jQuery is not defined"]
jqueryLoaded: false
```

**After fix (Playwright headless Chrome):**
```
/rentals/ — jsErrors: []
jqueryLoaded: true
jqueryVersion: 3.7.1
```

**Committed HTML verification via curl:**
```bash
curl -sSL "https://activeoahutours.com/rentals/" | grep "jquery-core-js"
# Should return: <script src="/wp-includes/js/jquery/jquery.min.js?ver=3.7.1" id="jquery-core-js"></script>
```

## Key Finding: magnificPopup vs lazyload

- `magnificPopup` galleries throw errors without jQuery — these 166 pages need the fix urgently
- Inline lazyload has `if (!$) { return; }` guard — these 31 pages are silent (no visible error) but still benefit from jQuery injection

## Cloudflare Pages Lag

After merging PR #128 to `main`, live `activeoahutours.com` was stale for ~90 seconds while Cloudflare Pages rebuilt. Committed HTML (`git show origin/main`) was used as ground truth during this window — curl-verified committed content is sufficient evidence even before the live site updates.

## Files Changed

PR #128: 197 files changed, 197 insertions(+), 197 deletions(-)
One line added per file (jQuery injection before `</head>`)

## Linear

- GRO-4346 — Fix jQuery errors on 166 pages (COMPLETED ✅)
