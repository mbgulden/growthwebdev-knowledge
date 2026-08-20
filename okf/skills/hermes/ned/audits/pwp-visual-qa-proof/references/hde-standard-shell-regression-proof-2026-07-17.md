# HDE standard shell regression proof — 2026-07-17

## Why this exists

A prior HDE standard-header/footer pass reported success while missing the actual user-visible regression:

- Astro pages had duplicate standard headers/footers because the shared layout injected `Nav`/`Footer` while pages also rendered them directly.
- Legacy/static docs had a temporary `.hde-standard-*` shell that was structurally present but was not the real homepage shell.
- Mobile menu state toggled, but CSS kept the drawer visually hidden.
- The first verification checked too much for presence and not enough for exact shape/behavior.

## Durable verification pattern

For HDE header/footer or shell work, the proof must assert all of these on desktop and mobile:

1. HTTP 200 for every named route and representative sub-route.
2. Exactly one `body > header`.
3. Exactly one `body > footer`.
4. Header nav link text exactly: `Free Reading|Reports|Sanctuary|API|Learn|Coaching`.
5. Footer group headings exactly: `Start|Products|Learn`.
6. No temporary/legacy shell classes such as `.hde-standard-header` or `.hde-standard-footer`.
7. Mobile menu button exists.
8. Clicking mobile menu sets `aria-expanded="true"`, adds `drawer-open` to `body`, and makes the `body > header nav` computed `visibility` equal `visible` with non-zero opacity.
9. Use a cache-busting query string on live Cloudflare/staging checks so old edge content does not masquerade as the deployed fix.

## Representative routes used

- `/`
- `/human-design/gates/`
- `/human-design/channels/`
- `/human-design/centers/`
- `/human-design/authorities/`
- `/human-design/types/`
- `/human-design/gates/gate-1.html`
- `/human-design/channels/1-8-inspiration.html`
- `/human-design/centers/sacral.html`
- `/human-design/authorities/emotional.html`
- `/human-design/types/generator.html`
- `/free-human-design-reading-generator/`

## Implementation notes

- Do not make `Layout.astro` globally inject `Nav`/`Footer` if pages already own their shell. Use explicit page ownership to avoid duplicate chrome.
- For legacy/static pages, inject the same homepage shell markup rather than a simplified placeholder shell.
- If mobile drawer CSS hides nav with `visibility:hidden`/`opacity:0`, the click handler may need `style.setProperty(..., 'important')` or an equivalent CSS class with higher specificity.
- PWP visual smoke should fail the exact regression, not just confirm cream/sage colors or link presence.
