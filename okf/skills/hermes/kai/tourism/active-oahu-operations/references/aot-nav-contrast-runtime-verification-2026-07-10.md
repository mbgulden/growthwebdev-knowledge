# AOT nav contrast + runtime verification notes (2026-07-10)

## Context
Desktop nav contrast fixes must include all dropdown depths, not only the top-level hover and second-level submenu. The missed case in this run was:

`Rentals → Kayak Rentals → Mokolii Kayak Rentals / Kailua Kayak Rentals`

The third-level submenu needed explicit CSS because broad second-level rules are easy to verify while nested panels inherit/override differently.

## Durable workflow

1. **Verify every nav depth before shipping.** For desktop dropdown work, hover through each parent path and measure contrast for:
   - top-level hovered parent
   - second-level submenu links
   - third-level submenu links
   - hovered/focused states inside third-level menus
2. **Use rendered Playwright, not screenshots alone.** Programmatically hover the real path and read `getComputedStyle()` plus element bounds.
3. **Require nonzero geometry.** A contrast value on a hidden element is not enough. Assert `display != none`, `visibility == visible`, and `rect.width/height > 0` for each target.
4. **Cache bust nav CSS.** When `nav-fix.css` changes, bump the query key (`v=12`, `v=13`, etc.) across pages that load it.
5. **Purge Cloudflare after merge.** Exact URL purge may not refresh `/` reliably; if clean `/` still serves stale HTML after exact purge, use a bounded `purge_everything` and then re-check clean production `/` for the new stylesheet version.
6. **Use a fresh `/tmp/hermes-verify-*` script when Hermes asks for verification.** The verifier should check local source markers, production HTML markers, rendered hover path, contrast ratios, visibility/geometry, and page errors; clean up the temporary verifier after it runs.

## Example rendered checks

Production verified targets after the fix:

| Item | State | Expected |
|---|---|---:|
| Kayak Rentals | hovered parent | contrast ≥ 4.5:1 and visible |
| Mokolii Kayak Rentals | third-level default | contrast ≥ 4.5:1 and visible |
| Kailua Kayak Rentals | third-level default | contrast ≥ 4.5:1 and visible |
| Mokolii Kayak Rentals | third-level hover | contrast ≥ 4.5:1 and visible |

In the verified run these measured 11.21:1, 8.84:1, 8.84:1, and 11.21:1 respectively.

## Pitfalls

- Do not stop after verifying `Activities & Tours` or a second-level submenu. The `Kayak Rentals` nested panel is the regression-prone third-level path.
- Do not claim cache purge succeeded from the API response alone. Fetch the clean production URL and confirm it loads the new `nav-fix.css?v=N`.
- Do not treat browser screenshot attachment as verification if the user asked for contrast. Include computed contrast numbers.
- Do not ignore Hermes' post-edit verification guard. Run a new ad-hoc verifier with the required `hermes-verify-` prefix and summarize it as ad-hoc verification, not suite green.
