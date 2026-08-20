# Cloudflare Pages SPA Fallback Returns HTML for Missing Assets

> **Session source:** Active Oahu 2026-07-30 — Round 4 visual gap audit. Michael reported "missing lots of images and broken images." Pixel-diff showed 8 of 10 page slices with significant visual gaps. Root cause was NOT content/structure — it was that **16 of 25 image URLs on the deployed staging site returned 65,413 bytes of HTML** (the `index.html`) instead of actual JPEGs. Cloudflare Pages treats unknown routes as SPA fallback.
>
> **Use this when:** CF Pages preview URL serves images/CSS/JS that look broken, but `curl -I` returns HTTP 200 with the right Content-Type for HTML. Specifically, when `file downloaded.bin` shows `HTML document` instead of the expected `JPEG image data` for a request to `/wp-content/...` or any non-existent static asset.

## The trap: HTTP 200 ≠ image served

Cloudflare Pages by default serves `index.html` for any unknown route (this is the standard SPA pattern — the JS then handles client-side routing). The catch: **this fallback applies to ALL routes, including asset paths** like `/wp-content/uploads/2025/03/foo.jpg`. If that file doesn't exist in the deployed `dist/`, CF Pages returns `index.html` with HTTP 200, the browser tries to decode it as an image, and the `<img>` tag silently shows a broken icon or empty box.

The pixel diff was the diagnostic that surfaced this: production has 78% mid-tone content in the Feature Block area (real photos), staging has 5% (essentially white). HTML structural diff said all 25 image URLs were present in the HTML. Image-load verification said 16 of 25 returned 65,413 bytes of HTML.

## Why HTTP code check alone misses this

```bash
# This returns HTTP 200 — looks fine
curl -sI https://content-astro-homepage.active-oahu-tours-mirror.pages.dev/wp-content/uploads/2018/11/DSC5281_2000-650x433.jpg
# HTTP/2 200
# content-type: text/html; charset=utf-8    ← THE TELL

# This catches it:
curl -s -o /tmp/test.jpg https://content-astro-homepage.active-oahu-tours-mirror.pages.dev/wp-content/uploads/2018/11/DSC5281_2000-650x433.jpg
file /tmp/test.jpg
# /tmp/test.jpg: HTML document, Unicode text, UTF-8 text, with very long lines (27750)
```

The 65,413-byte response size is identical to the homepage `dist/index.html` — that's not a coincidence. CF Pages is serving the SPA shell for any unknown route.

## The right verification recipe

**Never trust HTTP 200 alone for asset verification on CF Pages. Always check the file type:**

```python
# /tmp/aot-check-images.py
import re, subprocess, tempfile, json
from pathlib import Path

with open('/tmp/staging-homepage.html') as f:
    html = f.read()

# Collect every image URL (img src, srcset, background-image)
urls = set()
for m in re.finditer(r'<img[^>]+src="([^"]+)"', html):
    u = m.group(1)
    if 'wp-content' in u or 'active-oahu' in u: urls.add(u)
for srcset in re.findall(r'srcset="([^"]+)"', html):
    for part in srcset.split(','):
        u = part.strip().split()[0]
        if 'wp-content' in u or 'active-oahu' in u: urls.add(u)
for m in re.finditer(r'background-image:\s*url\([\'"]?([^\'")\s,]+)', html):
    u = m.group(1)
    if 'wp-content' in u or 'active-oahu' in u: urls.add(u)

results = []
for url in sorted(urls):
    full = f"https://your-preview.pages.dev{url}" if url.startswith('/') else url
    with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as f:
        tmp = f.name
    try:
        r = subprocess.run(['curl', '-s', '-L', '--max-time', '15', '-o', tmp, '-w', '%{http_code}', full],
                          capture_output=True, text=True)
        http_code = r.stdout.strip()
        ft = subprocess.run(['file', tmp], capture_output=True, text=True)
        file_type = ft.stdout.split(':', 1)[1].strip()
        is_real_image = ('image data' in file_type or 'PNG image' in file_type
                         or 'JPEG' in file_type)
        size = Path(tmp).stat().st_size
        results.append({'url': url, 'http': http_code, 'size': size,
                        'file_type': file_type, 'is_real_image': is_real_image})
    finally:
        Path(tmp).unlink(missing_ok=True)

real = sum(1 for r in results if r['is_real_image'])
fake = len(results) - real
print(f"Real: {real}/{len(results)}, HTML fallback: {fake}")
# Real: 9/25, HTML fallback: 16   ← in this session
```

This pattern catches the gap immediately and produces machine-readable JSON for downstream tooling.

## The root-cause architectural fix

**Astro's static build only bundles assets placed in `public/` or imported via relative paths.** When the Astro homepage references legacy WordPress `/wp-content/uploads/...` paths, those images are NOT bundled into `dist/` unless they're physically placed in `astro/public/`.

```bash
$ ls dist/
_aot_assets  _routes.json  _worker.js  index.html

$ find dist -type f \( -name "*.jpg" -o -name "*.png" \)
# (0 results)
```

The fix is to mirror the production WP directory structure into `astro/public/`:

```bash
# Download all production images referenced by staging HTML
mkdir -p astro/public/wp-content/uploads/{2016,2018,2019,2021,2022,2023,2025,2026}/{01..12} 2>/dev/null
for url in $(grep -oE 'wp-content/uploads/[^"'"'"' )]+\.(jpg|jpeg|png|svg)' \
             astro/dist/index.html | sort -u); do
  curl -s -L "https://activeoahutours.com/$url" -o "astro/public/$url"
done

# Rebuild — Astro copies public/ into dist/ verbatim
cd astro && npm run build
ls dist/wp-content/uploads/2018/11/  # now has the actual JPEGs
```

After this, CF Pages serves the bundled images directly from `dist/wp-content/...` — no HTML fallback, no SPA shell confusion. `aot-check-images.py` should then report `Real: 25/25, HTML fallback: 0`.

## Why some images "work" anyway (CDN cache survivors)

In this session, 9 of 25 image URLs returned real JPEGs even though the build had no images bundled. These are **CDN edge cache survivors** from a prior deployment that DID have the images at the same paths. Once the cache TTL expires (Cloudflare's default is ~4 hours for HTML, longer for static assets), those 9 will also start returning HTML.

**Implication for verification:** the "working" image count is a moving target. A deployment that looks healthy at 14:00 might look broken at 19:00 once cache entries expire. The fix must address the source — bundle the images — not just rely on cache.

## Diagnostic ladder when an AOT PR is "missing images"

1. **HTML structural diff** (`scripts/aot-staging-vs-prod-diff.py`) — confirms image URLs are present in HTML
2. **HTTP status check** — `curl -sI URL` for each image. Fast but misleading (returns 200 for HTML fallback)
3. **File-type check** (`aot-check-images.py`) — definitive. Always run this on CF Pages preview URLs
4. **Pixel diff** (`/tmp/aot-pixel-diff.py`) — visual confirmation of where staging actually looks empty

If step 1 says "all present" but step 4 says "lots of empty sections," step 3 is the smoking gun. Skip step 2.

## When this recipe applies

- CF Pages preview URL returns 200 for asset paths but images/CSS/JS look broken in browser
- HTML structural diff says all references are present, but pixel diff shows blank sections
- Any project that migrated from a CMS/static-export and references legacy absolute paths (`/wp-content/...`, `/static/...`, etc.) in the Astro build

## When it does NOT apply

- The asset paths are correctly bundled in `dist/` and HTTP 200 returns real image bytes — that's a different bug (broken URL, wrong path, etc.)
- The image returns a real 404 status (not the SPA fallback) — that's a missing-file issue you fix by bundling
- The CF Pages project has explicit `not_found_handling` set to `404_page` instead of the default SPA fallback — check with `GET /accounts/{id}/pages/projects/{name}` and look at `build_config` and `deployment_configs`
