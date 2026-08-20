# Gallery Lightbox Modal + Full-Size Image Derivation (2026-07-31)

> **Session source:** Active Oahu footer/lightbox work. Built a click-to-open gallery lightbox over existing 115×115 thumbnails.
>
> **Use this when:** implementing any "click thumbnail → full-size modal" pattern, especially for image galleries on a WordPress-export-derived static site where thumbnail and full-size URLs share a directory structure.

## The Pattern

Three pieces:

1. **HTML markup** — Wrap each thumbnail in `<a data-lightbox="group-name" data-title="alt text">` so JS can find them.
2. **Vanilla JS controller** — ~120 lines, no framework dependency. Handles click, keyboard, touch, focus trap, ARIA.
3. **CSS** — Full-viewport overlay (`position: fixed; inset: 0;`), close + prev/next buttons, responsive sizing.

## HTML Markup (in the gallery component)

```astro
<a
  href={fallbackUrl}
  data-lightbox="aot-gallery"
  data-title={img.alt}
  aria-label={`View larger image: ${img.alt}`}
>
  <img src={img.src} alt={img.alt} width="115" height="115" loading="lazy" />
</a>
```

The `href` is the no-JS fallback (link to the full gallery page). The `data-lightbox` groups all related thumbnails so the modal can navigate between them.

## JS Pattern

Drop into `public/js/gallery-lightbox.js`:

```javascript
(function () {
  'use strict';
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  function init() {
    const triggers = document.querySelectorAll('[data-lightbox]');
    if (!triggers.length) return;

    let currentGroup = null;
    let currentIndex = 0;
    let touchStartX = 0;
    let lastFocused = null;

    // Inject lightbox DOM
    const overlay = document.createElement('div');
    overlay.id = 'aot-lightbox';
    overlay.className = 'aot-lightbox';
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.setAttribute('aria-label', 'Image gallery viewer');
    overlay.setAttribute('hidden', '');
    overlay.innerHTML = `
      <button class="aot-lightbox-close" type="button" aria-label="Close gallery">×</button>
      <button class="aot-lightbox-prev" type="button" aria-label="Previous image">❮</button>
      <button class="aot-lightbox-next" type="button" aria-label="Next image">❯</button>
      <div class="aot-lightbox-content">
        <img class="aot-lightbox-img" alt="" />
        <div class="aot-lightbox-caption">
          <span class="aot-lightbox-title"></span>
          <span class="aot-lightbox-counter"></span>
        </div>
      </div>
    `;
    document.body.appendChild(overlay);

    const lightboxImg = overlay.querySelector('.aot-lightbox-img');
    const lightboxTitle = overlay.querySelector('.aot-lightbox-title');
    const lightboxCounter = overlay.querySelector('.aot-lightbox-counter');
    const closeBtn = overlay.querySelector('.aot-lightbox-close');
    const prevBtn = overlay.querySelector('.aot-lightbox-prev');
    const nextBtn = overlay.querySelector('.aot-lightbox-next');

    function getGroup(name) {
      return Array.from(document.querySelectorAll(`[data-lightbox="${name}"]`));
    }

    function show() {
      const trigger = currentGroup[currentIndex];
      const img = trigger.querySelector('img');
      let fullSrc = trigger.getAttribute('data-full');
      if (!fullSrc) {
        // Derive: thumbnail -115x115 suffix → full-size in _lightbox/ subdir
        const thumbSrc = img.getAttribute('src') || img.src;
        const derived = thumbSrc.replace(/-\d+x\d+(?=\.\w+$)/, '');
        fullSrc = derived.replace('/wp-content/uploads/', '/wp-content/uploads/_lightbox/');
      }
      const title = trigger.getAttribute('data-title') || img.alt || '';
      lightboxImg.src = fullSrc;
      lightboxImg.alt = title;
      lightboxTitle.textContent = title;
      lightboxCounter.textContent = `Image ${currentIndex + 1} of ${currentGroup.length}`;
    }

    function open(name, index) {
      currentGroup = getGroup(name);
      currentIndex = index;
      lastFocused = document.activeElement;
      show();
      overlay.removeAttribute('hidden');
      overlay.classList.add('open');
      document.body.style.overflow = 'hidden';
      setTimeout(() => closeBtn.focus(), 50);
    }

    function close() {
      overlay.classList.remove('open');
      overlay.setAttribute('hidden', '');
      document.body.style.overflow = '';
      if (lastFocused) lastFocused.focus();
    }

    function next() { if (currentGroup) { currentIndex = (currentIndex + 1) % currentGroup.length; show(); } }
    function prev() { if (currentGroup) { currentIndex = (currentIndex - 1 + currentGroup.length) % currentGroup.length; show(); } }

    triggers.forEach((trigger) => {
      const groupName = trigger.getAttribute('data-lightbox');
      const group = getGroup(groupName);
      const groupIndex = group.indexOf(trigger);
      trigger.addEventListener('click', (e) => { e.preventDefault(); open(groupName, groupIndex); });
    });

    // Image error fallback — if full-size 404s, fall back to the thumbnail URL
    lightboxImg.addEventListener('error', () => {
      const trigger = currentGroup && currentGroup[currentIndex];
      if (trigger) {
        const img = trigger.querySelector('img');
        if (img && img.src && lightboxImg.src !== img.src) lightboxImg.src = img.src;
      }
    });

    closeBtn.addEventListener('click', close);
    prevBtn.addEventListener('click', (e) => { e.stopPropagation(); prev(); });
    nextBtn.addEventListener('click', (e) => { e.stopPropagation(); next(); });
    overlay.addEventListener('click', (e) => { if (e.target === overlay) close(); });

    document.addEventListener('keydown', (e) => {
      if (!overlay.classList.contains('open')) return;
      if (e.key === 'Escape') close();
      else if (e.key === 'ArrowRight') next();
      else if (e.key === 'ArrowLeft') prev();
    });

    // Touch swipe for mobile
    overlay.addEventListener('touchstart', (e) => { touchStartX = e.changedTouches[0].screenX; }, { passive: true });
    overlay.addEventListener('touchend', (e) => {
      const dx = e.changedTouches[0].screenX - touchStartX;
      if (Math.abs(dx) > 50) { if (dx < 0) next(); else prev(); }
    }, { passive: true });
  }
})();
```

Load it via `<script src="/js/gallery-lightbox.js" defer></script>` in BaseLayout.

## Full-Size Image URL Derivation (the reusable trick)

WordPress-derived static sites use the `image-name-115x115.ext` convention for thumbnails. The full-size URL strips the `-WxH` suffix and lives in a different directory (production uses `_lightbox/`):

| Thumbnail URL | Full-size URL |
|---|---|
| `/wp-content/uploads/2018/11/DSC5447_2000-115x115.jpg` | `/wp-content/uploads/_lightbox/DSC5447_2000.jpg` |
| `/wp-content/uploads/2016/11/Oahu-Kayaking-Tours_31-2-115x115.jpg` | `/wp-content/uploads/_lightbox/Oahu-Kayaking-Tours_31-2.jpg` |

The derivation rules:

```javascript
// 1. Strip the -WxH suffix (only when followed by .ext)
thumbSrc.replace(/-\d+x\d+(?=\.\w+$)/, '')
//   /uploads/2018/11/DSC5447_2000-115x115.jpg
//   ↓
//   /uploads/2018/11/DSC5447_2000.jpg

// 2. Route to the full-size directory
derived.replace('/wp-content/uploads/', '/wp-content/uploads/_lightbox/')
//   /wp-content/uploads/2018/11/DSC5447_2000.jpg
//   ↓
//   /wp-content/uploads/_lightbox/DSC5447_2000.jpg
```

The thumbnail URL might also use other sizes (`-480x240`, `-650x433`, etc.) — the regex handles any `\d+x\d+` suffix.

## Bundling Strategy

The full-size images are typically NOT bundled with the Astro site. Two strategies:

1. **Download and bundle** — `mkdir -p public/wp-content/uploads/_lightbox/ && curl -O <each full-size image from production>`. Adds weight to the bundle (~2.7MB for 8 images at AOT) but works offline.
2. **Link to production directly** — use the absolute URL `https://activeoahutours.com/wp-content/uploads/_lightbox/...` in the JS. Lower bundle weight but creates cross-origin dependencies and breaks if production URLs change.

For an AOT-style site, strategy 1 is preferred because the site must be deployable independently of production. For a hosted gallery or CDN-backed site, strategy 2 is fine.

## CSS Skeleton (~130 lines)

```css
.aot-lightbox {
  position: fixed;
  inset: 0;
  z-index: 100000;
  background: rgba(0, 0, 0, 0.92);
  display: none;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}
.aot-lightbox.open { display: flex; opacity: 1; }
.aot-lightbox[hidden] { display: none !important; }

.aot-lightbox-content {
  position: relative;
  max-width: 95vw;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}
.aot-lightbox-img {
  max-width: 95vw;
  max-height: 80vh;
  object-fit: contain;
  border-radius: 4px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
}
.aot-lightbox-caption {
  color: #fff;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.aot-lightbox-close, .aot-lightbox-prev, .aot-lightbox-next {
  position: absolute;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-radius: 50%;
  cursor: pointer;
  z-index: 2;
  display: flex; align-items: center; justify-content: center;
  padding: 0;
}
.aot-lightbox-close { top: 1rem; right: 1rem; width: 44px; height: 44px; font-size: 1.5rem; }
.aot-lightbox-prev { left: 1rem; top: 50%; transform: translateY(-50%); width: 50px; height: 50px; font-size: 1.25rem; }
.aot-lightbox-next { right: 1rem; top: 50%; transform: translateY(-50%); width: 50px; height: 50px; font-size: 1.25rem; }

@media (max-width: 640px) {
  .aot-lightbox-close, .aot-lightbox-prev, .aot-lightbox-next {
    width: 40px; height: 40px; font-size: 1rem;
  }
}
```

## Verification Recipe

After implementing, verify with:

```bash
# 1. Source HTML has the data-lightbox attributes
grep -c 'data-lightbox' "$WORK/src/components/.../FooterExtras.astro"
# Expected: matches the number of gallery thumbnails

# 2. JS file exists and is non-empty
test -s "$WORK/public/js/gallery-lightbox.js" && echo "OK" || echo "MISSING"

# 3. JS is loaded in BaseLayout
grep -c 'gallery-lightbox.js' "$WORK/src/layouts/BaseLayout.astro"

# 4. Built HTML loads the JS
grep -c 'gallery-lightbox.js' "$WORK/dist/index.html"

# 5. CSS includes lightbox rules
grep -c 'aot-lightbox' "$WORK/dist/_aot_assets/"*.css

# 6. Full-size images bundled
ls "$WORK/dist/wp-content/uploads/_lightbox/" | wc -l

# 7. Browser verification (live preview)
#    - Click any gallery thumbnail
#    - Lightbox opens with full-size image (natural width > 200px)
#    - Counter shows "Image N of 8"
#    - Title shows the alt text
#    - ESC closes
#    - Prev/Next navigate
```

## Browser Verification (using browser_console)

```javascript
// Open lightbox
document.querySelector('[data-lightbox]').click();
const img = document.querySelector('.aot-lightbox-img');
const counter = document.querySelector('.aot-lightbox-counter');
return `src=${img.src.split('/').pop()} natural=${img.naturalWidth}x${img.naturalHeight} counter=${counter.textContent}`;
// Expected: natural >= 480 (full size), counter shows "Image 1 of N"

// Navigate
document.querySelector('.aot-lightbox-next').click();
return document.querySelector('.aot-lightbox-counter').textContent;
// Expected: "Image 2 of N"

// Close
document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape'}));
return document.getElementById('aot-lightbox').classList.contains('open');
// Expected: false
```

## Pitfalls

- **Bundle the full-size images BEFORE shipping.** Otherwise the JS falls back to the thumbnail (115×115 stretched to viewport = pixelated). The fallback exists for safety, not for the happy path.
- **The `defer` script tag must be in `<body>`, not `<head>`, if it's also placed inline.** Astro bundles `<script src="..." defer>` correctly, but inline body scripts need `is:inline`.
- **Don't forget the focus management.** When the lightbox opens, focus must move to the close button. When it closes, focus must return to the element that opened it. Otherwise keyboard and screen reader users are stranded.
- **The thumbnail might be the same URL as the full-size if there's only one variant.** Always include the `_lightbox/` subdirectory so the full-size lives in its own directory and can be selectively served.

## Related Skills

- `aot-cloudflare-spa-fallback-asset-404-2026-07-30.md` — when the full-size image URL returns the SPA HTML fallback instead of a real image.
- `aot-cdn-stale-js-after-deploy-2026-07-31.md` — when the JS appears to be the old version even after deploy.
- `aot-hallucinated-commit-verification-2026-07-31.md` — the verification gate that should run BEFORE claiming the lightbox "deployed".
