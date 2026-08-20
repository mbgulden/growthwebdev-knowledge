# HDE legacy CSS permissions + computed-style proof — 2026-07-17

## Trigger
Use this reference when a legacy/static HDE page appears to include the theme bridge but still visually shows old navy/gold/purple styling.

## Lesson
A link tag is not proof the CSS is applied. In this session `/hde-light-theme.css` was present in the built HTML, but staging served the CSS as `403 Forbidden` because the copied file mode was `600`. Browser/PWP checks that only looked for the link or token absence missed the visible header/title regression.

## Durable fix pattern

1. Verify the stylesheet request itself, not only the HTML:

```bash
curl -sSIL -A 'Mozilla/5.0' https://staging.humandesignengine.com/hde-light-theme.css | sed -n '1,10p'
```

Expected: `HTTP/2 200`, `content-type: text/css`.

2. Make copied legacy assets web-readable in the build/sync path:

```js
fs.copyFileSync(src, dest);
fs.chmodSync(dest, 0o644);
```

For staging dist syncs, prefer:

```bash
rsync -a --delete --chmod=F644,D755 dist/ /home/ubuntu/work/hd-platform-staging/dist/
```

3. Verify visual styling through computed browser styles on representative pages, not grep alone. For the gates page, check at least:

- `nav` background should be cream/translucent, not navy.
- `nav .nav-logo` and nav links should be `rgb(47, 54, 49)` or equivalent sage/ink, not white/gold.
- `h1` should have no old white/gray gradient background and should use the cream/sage title color.
- The page should list `/hde-light-theme.css` in `document.styleSheets`.

4. Scope representative live checks beyond the one complained-about page:

- `/human-design/gates/`
- `/human-design/gates/gate-1.html`
- `/human-design/channels/1-8-inspiration.html`
- `/human-design/types/generator.html`
- `/human-design/authorities/emotional.html`
- `/human-design/profiles/1-3.html`
- plus current funnel pages like `/free-human-design-reading-generator/` and `/buy-report/`.

## Pitfall
Do not report “old tokens gone” as equivalent to visual correctness. CSS cascade, forbidden stylesheets, inline style priority, and stale host roots can still leave the live page visibly wrong. Final proof must include a live browser/computed-style probe or screenshot-level review for the exact URL the user named.
