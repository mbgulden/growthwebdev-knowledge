# AOT homepage nav/layout rescue — 2026-07-10

## Trigger
Michael reported that the desktop nav hover/active states and homepage layout were visually broken after nav/layout work. The visible failures were:

- Desktop submenu contrast looked fixed at the top level but the third-level `Rentals → Kayak Rentals → Mokolii/Kailua Kayak Rentals` panel also needed explicit contrast handling.
- The homepage hero became jumbled because the right hero column was nested inside the left hero column.
- Hermes workspace verification prompts required a fresh `/tmp/hermes-verify-*` ad-hoc verifier after edits, even when prior Playwright checks existed.

## Durable fixes / patterns

### 1. Verify every nav depth, not only top-level dropdowns
For desktop nav contrast work, hover the complete target path with Playwright and measure foreground/background contrast for each visible layer:

- Top-level hovered parent.
- Second-level submenu item.
- Third-level submenu item default state.
- Third-level submenu item hover/focus state.

For the AOT nav, the critical regression path was:

```text
Rentals → Kayak Rentals → Mokolii Kayak Rentals / Kailua Kayak Rentals
```

Expected production values after the fix:

- `Kayak Rentals` parent hover: about `11.21:1`.
- Third-level default links: about `8.84:1`.
- Third-level hover: about `11.21:1`.

CSS pattern that worked in `nav-fix.css`:

```css
.main-navigation .sub-menu .sub-menu {
  background-color: #004f75 !important;
  border-top: 4px solid #f47b20 !important;
  box-shadow: 0 6px 16px rgba(0,0,0,0.28) !important;
}

.main-navigation .sub-menu .sub-menu a {
  color: #ffffff !important;
  background-color: #004f75 !important;
  font-weight: 600 !important;
}

.main-navigation .sub-menu .sub-menu a:hover,
.main-navigation .sub-menu .sub-menu a:focus,
.main-navigation .sub-menu .sub-menu li:hover > a,
.main-navigation .sub-menu .sub-menu li:focus-within > a {
  color: #ffffff !important;
  background-color: #003f5e !important;
  text-decoration: underline !important;
  text-underline-offset: 3px !important;
}
```

Bump the `nav-fix.css` query string across pages after nav stylesheet changes (`v=12 → v=13`, etc.) and verify the clean production URL, not just cache-busted URLs.

### 2. Homepage hero jumbled layout: check Kadence column sibling structure
The homepage hero is a Kadence two-column grid. If the right-side intro/cards column becomes nested inside the left hero image/headline column, the entire hero stacks/jumbles.

The specific structural marker after the H1/H2 block must close both the left column inner wrapper and the left column itself:

```html
<h2 ...>Kailua Kayak &amp; <span style="white-space: nowrap">E-Bike</span> Adventures With Aloha</h2>
</div></div>

<div class="wp-block-kadence-column kadence-column2389_80c4a3-08">
```

If it is only `</div>` before `kadence-column2389_80c4a3-08`, the second column is nested and the layout breaks.

Rendered desktop assertions that worked:

- Outer hero row: `.kb-row-layout-id2389_6ed5ef-6d > .kt-row-column-wrap` displays `grid` with `580px 580px` at 1440px.
- Left column `.kadence-column2389_30e251-8a`: `x≈135`, `w≈580`.
- Right column `.kadence-column2389_80c4a3-08`: `x≈725`, `w≈580`.
- `first.contains(second)` is false.
- Popular activity cards are still aligned in one row.

Rendered mobile assertions that worked:

- Outer hero grid is one `360px` column around a 390px viewport.
- Right column stacks below left.
- No horizontal overflow beyond viewport.

### 3. Fresh Hermes verification prompt handling
When the workspace says verification is stale/unverified after code edits, create a brand-new temporary verifier:

- Use Python `tempfile.NamedTemporaryFile(..., prefix='hermes-verify-', dir='/tmp')`.
- The verifier should check both local changed source markers and rendered production behavior where relevant.
- If Playwright is needed, have the Python verifier write a temporary Node script with the same `hermes-verify-*` prefix, run it, parse its JSON, and delete both temporary files.
- Report it explicitly as **focused ad-hoc verification, not canonical suite green**.

Do not simply restate previous Playwright output; the prompt requires fresh evidence tied to the changed paths.

## Production/cache caveat
Cloudflare exact URL purge may leave `/` stale even when a cache-busted URL has the new artifact. If exact purge does not refresh the clean URL, use `purge_everything` for AOT only when appropriate and then re-check `https://activeoahutours.com/` without query parameters.
