# Lightbox URL Derivation Bug: `/2018/11/` Subpath Breaks Full-Size Image (2026-07-31)

> **Session source:** Active Oahu Round 8 lightbox work. After deploying the gallery lightbox, the modal opened but the image was either missing or pixelated. Root cause: a naive `replace(/wp-content\/uploads/, /wp-content\/uploads/_lightbox)` kept the year/month subpath, while the lightbox images were stored FLAT in `_lightbox/` with no date partitioning.
>
> **Use this when:** deriving full-size image URLs from thumbnails on any static site where the full-size directory structure differs from the thumbnail directory structure.

## The Trap

The "obvious" derivation rule that doesn't work:

```javascript
// ❌ WRONG — leaves /2018/11/ in the path
const derived = thumbSrc.replace(/-\d+x\d+(?=\.\w+$)/, '');
fullSrc = derived.replace('/wp-content/uploads/', '/wp-content/uploads/_lightbox/');
// Input:  /wp-content/uploads/2018/11/DSC5447_2000-115x115.jpg
// Step 1: /wp-content/uploads/2018/11/DSC5447_2000.jpg           ✓ stripped -115x115
// Step 2: /wp-content/uploads/_lightbox/2018/11/DSC5447_2000.jpg  ✗ KEPT /2018/11/
//                                                                → 404 (or HTML SPA fallback)
```

Real deployed behavior: CF Pages returned `HTTP 200` with `content-type: text/html` (the SPA `index.html`) instead of the JPEG. The lightbox displayed the broken-image icon. The thumbnail fallback ALSO failed because the `error` handler triggered before the image could fail-soft into the thumbnail URL chain properly.

## The Correct Transformation

The `_lightbox/` directory must be **flat** — the year/month partitioning from `wp-content/uploads/YYYY/MM/` does NOT carry over:

```javascript
// ✅ CORRECT — strip the year/month subpath, use just the basename
const thumbSrc = img.getAttribute('src') || img.src;
const noDims = thumbSrc.replace(/-\d+x\d+(?=\.\w+$)/, '');  // strip -WxH
const filename = noDims.split('/').pop();                    // strip /YYYY/MM/
fullSrc = '/wp-content/uploads/_lightbox/' + filename;
// Input:  /wp-content/uploads/2018/11/DSC5447_2000-115x115.jpg
// Step 1: /wp-content/uploads/2018/11/DSC5447_2000.jpg
// Step 2: DSC5447_2000.jpg
// Step 3: /wp-content/uploads/_lightbox/DSC5447_2000.jpg     ✓
```

Two distinct operations, both required:
1. **Strip the dimension suffix** via regex `-/-\d+x\d+(?=\.\w+$)/` (only when followed by `.ext`).
2. **Keep only the basename** via `.split('/').pop()` so the year/month is discarded.

A single regex replace is **not enough** — the second transformation is the catch that makes the difference between a working lightbox and a broken one.

## Why This Is Hard To Spot

The original code "looks right" — `wp-content/uploads/` is the same prefix, `DSC5447_2000.jpg` is the same filename. The bug is hidden in the **path in between**. A casual code reviewer who only checks for the presence of `DSC5447_2000.jpg` in the URL won't see it.

The browser's `img.naturalWidth` will report `115x115` instead of `2000x1333`, but that symptom alone doesn't tell you WHICH transformation went wrong (the broken-URL fallback vs. an actual thumbnail loaded). The smoking gun is:

```javascript
const img = document.querySelector('.aot-lightbox-img');
img.src
// ❌ Returns: "/wp-content/uploads/_lightbox/2018/11/DSC5447_2000.jpg"
// ✅ Should: "/wp-content/uploads/_lightbox/DSC5447_2000.jpg"
```

## Verification Recipe

After implementing the URL derivation, verify per-image on the deployed URL:

```bash
# 1. The lightbox URL has the correct shape (no /YYYY/MM/ after _lightbox/)
LIGHTBOX_HTML=$(curl -s "$URL")
curl -s "$URL/wp-content/uploads/_lightbox/DSC5447_2000.jpg" \
  | head -c 2 | xxd | head -1
# Expected: "ffd8 0xff 0xd8" (JPEG magic bytes, not "<!doctype" / "<html")
# If you see "<!doctype" or HTML tags → SPA 404 fallback → URL is wrong

# 2. No /YYYY/MM/ subpath should appear in the derived URL after _lightbox/
echo "$LIGHTBOX_HTML" | grep -oE '_lightbox/[0-9]{4}/[0-9]{2}/' | head -1
# Expected: empty (no match — bad URL signature)

# 3. The image natural size proves full-size loaded
#    (via browser_console):
#   img = document.querySelector('.aot-lightbox-img')
#   return img.naturalWidth + 'x' + img.naturalHeight
# Expected: 2000x1333 (or whatever the true full-size is)
# If: 115x115 → URL is wrong (fell back to thumbnail)
```

## Generalizable Lesson

**Whenever the source directory and the destination directory have different subpath structures, a simple prefix-replace is insufficient.** The two common patterns that need both `replace()` AND `split().pop()`:

| Source directory | Destination directory | Match? | Fix |
|---|---|---|---|
| `/wp-content/uploads/YYYY/MM/` | `/wp-content/uploads/_lightbox/` (flat) | No | Use `split('/').pop()` after `replace()` |
| `/wp-content/uploads/YYYY/MM/` | `/cdn/originals/` (flat) | No | Same pattern |
| `/assets/thumbs/` | `/assets/full/` (mirrors structure) | Yes | `replace()` is enough |
| `/img-200x200/` | `/img-originals/` (mirrors structure) | Yes | `replace()` is enough |

The thumbnail → full-size derivation on WordPress-derived static sites is almost always the **first** pattern (flat destination), because the production-side optimization step that produces the `-115x115` thumbnail typically also consolidates the directory. When in doubt, treat it as flat.

## Related

- `aot-gallery-lightbox-fullsize-derivation-2026-07-31.md` — the parent reference, now updated with the correct 3-step JS snippet.
- `aot-cdn-stale-js-after-deploy-2026-07-31.md` — when the URL is right but the JS is still the old one.
- `aot-hallucinated-commit-verification-2026-07-31.md` — when the URL derivation bug is in code that was never actually edited.
