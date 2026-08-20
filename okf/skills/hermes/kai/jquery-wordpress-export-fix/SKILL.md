---
name: jquery-wordpress-export-fix
description: Diagnose and fix jQuery loading order issues on WordPress static exports
triggers:
  - "jQuery is not defined"
  - "magnificPopup" errors after WordPress export
  - jQuery gallery not working on static HTML pages
  - Cloudflare Rocket Loader breaking jQuery-dependent scripts
category: devops
---

# WordPress jQuery Export Bug — Diagnosis & Fix

## When to Use

Pages that use jQuery-dependent scripts (`magnificPopup`, gallery lightboxes, lazy-loaders) throw `jQuery is not defined` or `a is not a function` errors after migrating from WordPress static export. The root cause is WordPress's export process placing inline `<script>` blocks that call `jQuery()` **before** the jQuery library itself loads.

## Diagnosis

### 1. Get exact error location
```js
page.on('pageerror', err => console.log(err.stack))
```
This gives the line number in the rendered page.

### 2. Check jQuery load order in browser
```js
page.evaluate(() => {
  const scripts = Array.from(document.querySelectorAll('script'));
  return scripts.map(s => ({src: s.src, defer: s.defer, id: s.id}));
})
```
Look for: inline `jQuery(document).ready(...)` appearing BEFORE `jquery-core-js` in DOM order.

### 3. Common patterns
- WordPress exports nav/header scripts as inline `<script>` blocks in `<head>`
- jQuery is included with `id="jquery-core-js"` but placed AFTER those inline scripts
- Cloudflare Rocket Loader adds `defer=""` to unprotected scripts

## The Two Bugs

### Bug 1: Early jQuery() calls (main issue)
WordPress places `jQuery(document).ready(...)` inline scripts in `<head>` before jQuery loads.

**Fix:** Move the `jquery-core-js` `<script>` tag to BEFORE the first `jQuery()` call in the file.

### Bug 2: Cloudflare Rocket Loader adding `defer=""` (secondary issue)
Cloudflare's Rocket Loader intercepts scripts without `data-cfasync="false"` and adds `defer`, causing async timing issues.

**Fix:** Add `data-cfasync="false"` to the jQuery script tag:
```html
<script data-cfasync="false" src="/wp-includes/js/jquery/jquery.min.js?ver=3.7.1" id="jquery-core-js"></script>
```

## Python Fix Script

```python
#!/usr/bin/env python3
import re, subprocess

WORKTREE = '/path/to/active-oahu-tours-mirror'

result = subprocess.run(
    ['grep', '-rl', 'jquery-core-js', f'{WORKTREE}/site/', '--include=*.html'],
    capture_output=True, text=True
)
files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]

fixed = []
for path in files:
    with open(path) as f:
        content = f.read()
    
    jq_match = re.search(r'<script[^>]+id=["\']jquery-core-js["\'][^>]*>.*?</script>', content, re.DOTALL)
    if not jq_match:
        continue
    
    jq_tag = jq_match.group(0)
    jq_start = jq_match.start()
    jq_end = jq_match.end()
    
    # Check for early jQuery() calls
    early_jq_pos = None
    for m in re.finditer(r'jQuery\s*\(', content):
        if m.start() < jq_start:
            early_jq_pos = m.start()
        else:
            break
    
    if early_jq_pos is None:
        continue  # Normal file
    
    # Find the <script> tag before the jQuery call
    before = content[:early_jq_pos]
    script_match = re.search(r'<script[^>]*>\s*$', before, re.DOTALL)
    if not script_match:
        continue
    
    inject_pos = script_match.start()
    
    # Remove old jq tag, inject before the inline script
    new_content = content[:jq_start] + content[jq_end:]
    jq_fixed = jq_tag.replace('src="', 'data-cfasync="false" src="')
    new_content = new_content[:inject_pos] + jq_fixed + '\n' + new_content[inject_pos:]
    
    with open(path, 'w') as f:
        f.write(new_content)
    fixed.append(path)

print(f"Fixed: {len(fixed)} files")
```

## Verification

```js
const { chromium } = require('playwright');
const browser = await chromium.launch({ 
  executablePath: '/usr/bin/chromium-browser',
  args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'] 
});
const page = await browser.newPage();
page.on('pageerror', err => console.error('ERROR:', err.message));
await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 15000 });
await page.waitForTimeout(5000);
const jqLoaded = await page.evaluate(() => typeof window.jQuery !== 'undefined');
console.log({jqLoaded, jsErrors});
await browser.close();
```

## Lighthouse Context

This bug often causes "Best Practices" failures because Lighthouse detects JS errors on the page. The fix resolves these errors and can improve the Best Practices score (though the ceiling is often Cloudflare's own scripts at 81/100).

## Related Tasks

- **GRO-4346:** jQuery missing on 197 pages (magnificPopup + lazyload without jQuery)
- **GRO-4347:** jQuery errors on 4 pages (early jQuery() calls — this skill's main focus)
- **GRO-4348:** target="_blank" on FareHarbor links — harmless due to `return false` in onclick
- **GRO-4349:** H5 heading tags — verified 0 exist in current committed HTML
- **GRO-4350:** Lighthouse BP ceiling at 81 — Cloudflare deprecation errors, not fixable in repo
