# HDE Fred-era bodygraph renderer recovery — 2026-07

## Trigger

Use this when Michael says an older HDE chart/bodygraph looked better, mentions Fred, or asks to restore Personality/Design channel visualization, red/black channels, or better bodygraph colors.

## Durable finding

The better renderer is the Fred-era professional SVG bodygraph path, not the local Pillow `image_generator.render_bodygraph()` preview.

Likely provenance:

- `hd-platform` / `hd-platform-staging` branch family: `feature/fred-hde-stripe-staging-gro3792`
- Commit family around `[Fred] Build HDE Stripe launch updates into staging (#GRO-3792)`
- Supporting commits/files around public bodygraph work:
  - `api/routes/bodygraph.py`
  - `public/bodygraph-widget.js`
  - `public/bodygraph-widget.css`
  - `docs/hd-engine/interactive-bodygraph-design.md`
  - `/home/ubuntu/work/hd-bodygraph/render-pro.mjs`

The renderer uses the `hd-bodygraph/render-pro.mjs` Node/SVG path and carries:

- black Personality activations,
- red Design activations,
- split/mixed channels,
- professional 820×960 SVG/bodygraph layout,
- better center coloring/geometry than the local Pillow fallback.

## Recovery pattern

1. Search git history for Fred/bodygraph context before rebuilding from scratch:
   - branches: `feature/fred-*`, `origin/feature/fred-*`
   - commits/files containing `bodygraph`, `render-pro.mjs`, `Personality`, `Design`, `Gonzih/hd-bodygraph`.
2. Confirm the reports service already has or can call `/home/ubuntu/work/hd-bodygraph/render-pro.mjs`.
3. In `reports/server.py`, keep `/api/public/bodygraph?format=svg` and add/verify `format=png` conversion through `rsvg-convert` so Telegram can receive a native PNG image.
4. In the HDE guest runtime/template (`scripts/guest_hermes_template/daily_journal_mcp.py`), prefer the reports endpoint for chart preview images:
   - `GET http://host.docker.internal:8081/api/public/bodygraph?format=png&...`
   - write the response to the chart PNG artifact path.
5. Keep the older `render_bodygraph(normalize_defined_channels_for_renderer(...))` Pillow path as fallback only. Do not delete it; it preserves graceful degradation if the Node/SVG renderer is unavailable.
6. Copy the patched guest runtime into the live guest template and any active guest workspaces/containers that need immediate behavior, then restart those containers.
7. Document the policy in the HDE report/chart docs: chart previews should prefer the restored Fred-era professional renderer; local Pillow is fallback only.

## Verification recipe

Use a focused `/tmp/hermes-verify-*` script and label it ad-hoc verification:

1. Assert changed files contain the expected wiring:
   - `reports/server.py` contains `render-pro.mjs`, PNG format dispatch, and `image/png` response path.
   - `daily_journal_mcp.py` requests `/api/public/bodygraph` with `format=png` and still contains the Pillow fallback call.
   - docs mention the Fred-era renderer policy.
2. `py_compile` the changed Python files.
3. Call the live local reports endpoint with a known chart, e.g. Ruth Gulden canonical data:
   - `GET http://127.0.0.1:8081/api/public/bodygraph?format=png&name=Ruth+Gulden&year=1952&month=8&day=2&hour=18&minute=46&location=Glendale+California&lat=34.1425&lon=-118.2551&timezone=America/Los_Angeles`
4. Assert:
   - HTTP 200,
   - `Content-Type: image/png`,
   - PNG signature `89504e470d0a1a0a`,
   - size is substantial (observed ~137 KB),
   - `file` reports `PNG image data, 820 x 960`.
5. Call the same endpoint with `format=svg` and assert SVG contains:
   - `<svg`,
   - `#EB5757` red Design color,
   - `#000000` black Personality color,
   - visible labels/tokens `Personality` and `Design`.
6. Optional pixel sanity with PIL: verify substantial red and black pixel counts in the PNG.

## Pitfalls

- Do not mistake the local Python/Pillow `image_generator.render_bodygraph()` output for the better historical renderer. It is the fallback and can look like a rough beige preview.
- Do not port only the public widget CSS/JS and assume Telegram chart previews improve. Guest Telegram chart previews need the runtime to fetch the professional PNG endpoint.
- Do not remove SVG output while adding PNG. Browser/widget consumers may still depend on SVG; Telegram needs PNG.
- Do not claim visual restoration from file existence alone. Verify SVG red/black Personality/Design semantics and PNG conversion output.
- Do not force chart mechanics to match an old visual. Renderer recovery is presentation; profile/type/gates must still come from real OpenHumanDesignMCP calculation data.
