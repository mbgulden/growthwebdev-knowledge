---
name: kpis-and-reporter-architecture
description: Define, build, and operate a multi-surface KPI/reporter system for a public product site (GA4 + Stripe + Telegram + internal). Patterns the canonical KPI definition as a single JSON file, renders it to a Google Sheet + email reports (daily / weekly / monthly) + a PWP dashboard tab, and treats Stripe as the source of truth for revenue. Use when asked to define KPIs, ship a daily/weekly/monthly report, wire a PWP dashboard section, or build a Google Sheet-backed funnel dashboard.
triggers:
  - user asks to define or refine KPIs for a public product site
  - user asks for daily / weekly / monthly KPI reports
  - user asks to ship a Google Sheet-backed funnel dashboard
  - user asks to add a PWP dashboard section with tracked KPIs
  - user asks to integrate Stripe + GA4 + Telegram into a single reporting surface
  - user asks to make conversion funnel events visible across email + sheet + dashboard
  - user asks to standardize KPI tracking across multiple sites
  - user asks to register a new site (e.g. active-oahu) in an existing KPI tracker
  - user asks to unify a Node CLI and a Python cron that both produce KPI reports
  - user asks to migrate config/seo_sites.json into per-site *.kpi.json files
  - user asks "is this KPI JSON actually wired into the live site?"
---

# KPI / Reporter architecture

## Goal

Build a single, code-tracked KPI definition that renders to multiple surfaces
(Google Sheet, email reports, PWP dashboard) without duplicating the metric
shape. Treat Stripe as the canonical source for revenue and the GA4 Data
API as the source for funnel events. This is a class-level pattern; it does
not depend on a specific product.

## Working register for KPI / reporter work

When the user says "do X" / "create Y" / "fix Z" / "rewrite at the right path",
produce the artifact and one line of summary. Don't pre-narrate; don't
post-narrate the corrected failure mode unless the user asked. The
"Procurement discipline" + "Front_of_card is site-local" + "Forget the
{kind}" + "Ruff MUST be scoped" sections below are the durable lessons
that matter; the response is the artifact.

Three things have come up as named preferences in this register, all
captured as durable rules below, not as style directives on every turn:

- Ground metric JSON against the live site **before** writing it
  ("Procurement discipline" — the user has corrected this twice).
- `front_of_card` is site-local: an inherited metric's flag does NOT
  surface on the child unless the child re-declares it.
- The Claude-side response ends after the artifact summary; don't keep
  apologizing for a follow-up turn unless the user asks.

What this register is **not**: it is not a request to suppress diagnostics
when the user explicitly asked for them, and it is not a request to
skip explanation when the user asked a real question. Use the rule "if
the user asked a follow-up question, answer it; if they sent a directive,
produce the artifact and stop."

## Procurement discipline: ground metric JSON against the live site BEFORE writing

The structural validator (`validate()`) catches: bad source, missing required field, inner-id mismatch, dotted-key pattern. It does **not** catch: a metric event that the live site never emits, a `tracking_property` that doesn't match the GA4 ID actually configured, or a `source_urls[0]` that doesn't reference a real page. Separating procurement from validation is required:

1. **Pick the canonical mirror.** Multi-mirror repos (e.g. `active-oahu-tours-mirror`, `active-oahu-tours-mirror-2529`) advertise the right one via `config/seo_sites.json` `site_dir_candidates[0]` or the most recent PWP publish log. Don't guess from memory.
2. **Pull the live GA4 ID:** `grep -rhE "gtag\(\s*['\"]config['\"]" <REPO>/site/`. Quote the captured ID verbatim in `globally_required.tracking_property`.
3. **Pull the live event names:** `grep -rhE "gtag\(\s*['\"]event['\"],?\s*['\"]([A-Za-z0-9_]+)['\"]" <REPO>/site/`. The grep output is the only source of truth. **There is no second source.** If the user tells you "the site emits X, Y, Z", that's a passing ground for saying so, but the emitting code is the actual source.
4. **Hit `source_urls[0]` over HTTPS** and confirm the response body includes the GA4 loader snippet (`googletagmanager` or `gtag/js`).
5. **Write the JSON.** Every metric `event` field is a subset of the live event names. `expected_data_layer_events` equals the live event names exactly.
6. **Save and verify.** Run the live-mirror-anchored verifier. All assertions must pass.

Cherry-picked grep invocations live in the references table below; the full checklist and a verifier template are in `references/2026-07-ground-against-live-site-before-writing.md`. The lesson encoded here came from a real session in which a freshly-authored `kpi-collections.json` passed `validate()` cleanly but listed four event names (`booking_start`, `begin_checkout`, `purchase`, `generate_lead`) that the live site never emitted — the file would have worked as a schema, but produced empty dashboards. The next session must grep the live mirror **before** writing, not after, so a wrong file is never produced.

## Single source of truth: `scripts/kpis/kpi-collections.json`

Every metric lives in one JSON file. The shape:

```jsonc
{
  "schema_version": "1.0",
  "owner": "ned",
  "site": "site-slug-or-name",            // optional, for sites that aren't "hde"
  "site_slug": "lowercase-hyphenated",    // optional; required per the multi-site schema
  "domain": "example.com",                // optional; required per the multi-site schema
  "globally_required": {
    "tracking_property": "G-XXXXXXXXXX",          // GA4 measurement ID
    "expected_loader_on_every_page": true,
    "expected_dataLayer_event_set": ["..."],     // all custom event names
    "ga4_recommended_events": ["select_item", "begin_checkout", "purchase", ...]
  },
  "collections": [
    {
      "id": "funnel_buy_report",
      "title": "Report purchase funnel",
      "owner": "ned",
      "lane": "scripts/",
      "source_urls": ["https://example.com/buy-report/"],
      "metrics": [
        {"id": "report_selected_total", "label": "Report selected", "source": "ga4", "event": "checkout_report_selected"},
        {"id": "revenue_usd",          "label": "Gross revenue",   "source": "stripe", "event": "checkout.session.completed",
         "filter": "metadata.funnel == report_checkout", "field": "amount_total"},
        {"id": "conversion_rate",      "label": "Conversion rate", "source": "derived", "formula": "buy_report_purchase_total / buy_report_page_view", "format": "percent"}
      ]
    }
  ],
  "share_targets": {"google_sheet": {...}, "email": {...}},
  "delivery_cadence": {"daily": {...}, "weekly": {...}, "monthly": {...}},
  "pwp_dashboard_surface": {"path": "...", "renders": ["..."]}
}
```

The renderer (`scripts/kpis/build-report.mjs`) reads this file and yields
both a structured JSON (for the Sheet and dashboard) and a styled HTML (for
the email). Every script reads from the same file — there is no metric
duplication across surfaces.

## Sourcing rule

| Source | Used for | Where it lives |
|---|---|---|
| **GA4 Data API** | funnel events, page views, engagement | `collections[*].metrics[source=="ga4"]` |
| **Stripe API** | `*purchase_total`, `*revenue_usd`, refunds, churn | `collections[*].metrics[source=="stripe"]` |
| **Telegram / bot** | `deep_link_clicked_total`, post-purchase activation | `collections[*].metrics[source=="telegram"]` |
| **Internal** | PDF delivery, webhook smoke | `collections[*].metrics[source=="internal"]` |
| **Derived** | ratios, ARR, conversion rates | `collections[*].metrics[source=="derived"]` |

Stripe is the canonical source for revenue. The GA4 Data API is the source for
funnel events. Do not compute revenue from GA4 — it is approximate; Stripe is
truth. Do not compute conversion events from Stripe — the GA4 event is
authoritative for funnel timings.

### `front_of_card` is **site-local**, not inherited

A child site's `front_of_card` flag is **not** inherited from the parent.
The reasoning: a parent's headline list is a parent-level editorial
choice (e.g. "headline 3 funnel_top metrics for HDE"), and a child site
that extends the parent shouldn't have its own multi-site index
defaulted to whatever the parent chose. The contract is:

- The child site must **explicitly** set `front_of_card: true` on each
  metric it wants on the multi-site index.
- The parent's inherited metrics land in the resolved collection with
  `front_of_card` *stripped* (the `resolve_collection()` walker pops
  `front_of_card` from parent metrics that the child doesn't override).
- The test fixture is: for every metric in the resolved collection that
  came from the parent, `front_of_card` must NOT be present unless the
  child re-declared the metric with `front_of_card: true`.

This was discovered twice in this session — the bug presents as "the
multi-site index shows the parent's headline metrics for every child,
even though the child didn't ask for them." The contract is enforced
inside `resolve_collection()` so consumers don't have to know about it.
The integration test that catches the regression is:

```python
def test_front_of_card_is_site_local():
    flat = resolve_collection("active-oahu")
    own = flat["metrics"].get("funnel_booking.booking_click", {})
    inherited = flat["metrics"].get("funnel_top.free_chart_generated_total", {})
    assert own.get("front_of_card") is True
    assert "front_of_card" not in inherited
```

### Cross-domain booking flows ≠ Stripe

When a booking flow lives on a third-party provider and the site only
embeds it (`<iframe src="fareharbor.com/...">`), Stripe is **not** the
source of truth for revenue — the third-party provider is. The canonical
pattern in this case is:

- Capture **click events** (`booking_click`) on the embed via `postMessage` or a wrapper script.
- Capture **completion events** (`booking_complete`) via the provider's webhook → a server endpoint that fires a GA4 event through the Measurement Protocol.
- Treat the provider's *exported* CSVs as the eventual revenue source; the GA4 events capture funnel attribution only.

The site file for an AOT-style booking site is:

```json
{
  "site_slug": "active-oahu",
  "domain": "activeoahutours.com",
  "extends": "hd-engine",
  "metrics": {
    "funnel_booking.booking_click_total":      {"id": "booking_click_total",      "label": "Booking-click events", "source": "ga4", "event": "booking_click"},
    "funnel_booking.booking_complete_total":    {"id": "booking_complete_total",    "label": "Booking-complete events", "source": "ga4", "event": "booking_complete"},
    "funnel_booking.booking_conversion_rate":   {"id": "booking_conversion_rate",   "label": "Click → complete conversion", "source": "derived", "formula": "booking_complete_total / booking_click_total", "format": "percent"}
  }
}
```

Documentation comment (in the file or in `notes/gro-XXXX-...md`): "GA4 revenue requires purchase/generate_lead/booking events to be emitted from the booking flow or imported from FareHarbor. If booking completes off-site, configure cross-domain tracking and/or server-side Measurement Protocol/imports."

The skill's "Stripe is truth" rule is correct for direct-payment flows; it is **explicitly relaxed** for cross-domain booking flows. Do not invent a `*revenue_usd` metric for an AOT-style site — the provider's export is the only reliable source.

### Sourcing rule implementation note for cross-domain flows

The capture+forward pattern above means the AOT KPI authority document must contain at least one comment of the form:

> "GA4 revenue requires purchase/generate_lead/booking events to be emitted from the booking flow or imported from FareHarbor. If booking completes off-site, configure cross-domain tracking and/or server-side Measurement Protocol/imports."

without which the team will always be tempted to add a `*revenue_usd` metric that does not exist on the live site. Add the comment to the file, to `config/seo_sites.json.booking_revenue_notes`, and to the relevant `notes/gro-XXXX-...md` paper trail.

## Derived metrics

Only allow four operators over `metric_id` references: `+ - * /` and parens.
Tiny safe evaluator:

```js
function derive({ formula, metrics, priorMetrics }) {
  const expr = formula.replace(/[A-Za-z_][A-Za-z0-9_]*/g, (id) => {
    if (id === 'true' || id === 'false') return id;
    if (metrics[id] !== undefined) return String(metrics[id] || 0);
    if (priorMetrics && priorMetrics[id] !== undefined) return String(priorMetrics[id] || 0);
    return '0';
  });
  if (!/^[\d\s+\-*/().]+$/.test(expr)) return { error: `formula ${formula} could not be evaluated safely` };
  try { return { value: Function(`"use strict";return (${expr})`)() }; }
  catch (err) { return { error: String(err.message) }; }
}
```

This guard is critical — formulas are user-defined in JSON and must not
be a JS injection vector. The regex `^[\d\s+\-*/().]+$` is the security gate.

**Important ordering.** The regex runs **after** identifier substitution. A
verifier that applies the regex against the raw formula string `a / b` will
reject it because `a` and `b` are not in the digit/operator allowlist. The
correct pre-substitution step is:

```python
def safe_substitute(expr):
    return re.sub(r"[A-Za-z_][A-Za-z0-9_]*", lambda m: "0", expr)

assert re.match(r"^[\d\s+\-*/().]+$", safe_substitute("booking_complete_total / booking_click_total"))
```

The substitution **must** happen before the regex. A naive verifier that
applies the regex check against the raw formula string will be a false
negative on every derived metric that uses identifier references.

## Filter DSL for Stripe events

Tiny DSL on the metric filter: `metadata.funnel == sanctuary`, `event !=
checkout.session.completed`. Match with a single regex:

```js
function matchFilter(filter, e) {
  if (!filter) return true;
  const m = filter.match(/^(\w+)\.(\w+)\s*(==|!=)\s*(\w+)$/);
  if (!m) return true;
  const [, group, key, op, val] = m;
  const left = group === 'metadata' ? e.metadata?.[key] : e[`${group}_${key}`];
  return op === '==' ? left === val : left !== val;
}
```

Anything more complex should be a separate `event`/`field` pair, not a
sub-language. Filters are first-class in the JSON so reviewers can audit them.

## Surfaces

### Google Sheet

- One tab per collection type (Daily / Weekly / Monthly) + a Raw events tab
  + a Targets tab.
- Real-time appends for Stripe events via a webhook proxy.
- 6-hourly back-fill for GA4 via `cron`.
- Pulls lineage from the same JSON definitions, so a metric rename in
  `kpi-collections.json` automatically flows to all sheets.

### Email reports

- Plain HTML table per collection, with delta vs prior window inline.
- Subject prefix from the JSON: `[HDE KPI] Daily — 2026-07-28`.
- Archive every rendered HTML + JSON to a `~/.hermes/profiles/<profile>/reports/kpi/<kind>/`
  directory for hand inspection.
- Honestly: skip-emit-when-zero is off by default. Michael wants the heartbeat
  even when nothing moved. Use `skip_if_no_new_events` only for noisy
  sub-cadences, not the daily/weekly/monthly cycle.

### PWP dashboard section

- Rendered as a standalone static page (`/pwp/kpi-dashboard.html`) hosted on
  Cloudflare Pages, generated daily by `scripts/kpis/render-dashboard.mjs`.
- Top section: KPI collection cards (one per collection).
- Body: bump charts sourced from the Google Sheet via `=IMPORTDATA()`.
  Do not call live APIs from the page — it must work on the family-test
  device with no JS bundlers.
- Embedded in the existing PWP dashboard via iframe.

## Per-site row is the smallest visual unit that closes the loop

The multi-site dashboard must NOT be a wide summary table where each
site gets one row with N empty card cells when `runtime_values` is not
yet populated. The user has explicitly said: "per-site row is the
smallest, but it's what closes the loop visually. It would also fix
the multi-site row that currently shows Metrics: N — front-of-card: ...
with empty cards (no runtime_values)."

The fix: **one `<section class="pwp-kpi-site-row">` per registered
site**, with a header (name, slug, domain, owner, metric_count,
extends, detail link) and an inline card grid (one card per
`front_of_card` metric, label + value with `—` placeholder for
missing values). Every site that has registered any `front_of_card`
metric renders a card grid even when the cron has not yet populated
values; every site that has not registered any shows the "No
front-of-card metrics registered" note.

The 6-line `_format_value(value, fmt)` helper (defined alongside
`aggregate()` and `render_*()` in `publish_kpi_tracker.py`) renders
runtime values deterministically:

- `None` / missing → `"—"` (placeholder, never silent collapse)
- `percent` → `"12.34%"` (stored as fraction: `0.0638` → `"6.38%"`)
- `currency` → `"$1,234.50"`
- `duration` → `"45s"`
- `number` → `"1,234"` for integer-valued floats, `"1.23"` otherwise

The same helper feeds both `render_index()` and `render_accordion()`
so the empty-card collapse ("None") is gone from every surface in one
fix. Same input → same output (deterministic; required by the
self-rendering contract below).

**Percent-format contract.** Metrics with `format: "percent"` store
their value as a **fraction** (`0 ≤ v ≤ 1`), NOT as a percentage literal
(`0 ≤ v ≤ 100`). The formatter multiplies by 100 for display:

```python
# CORRECT:
if fmt == "percent":
    return f"{float(value) * 100:.2f}%"
# 0.0638 (fraction) → "6.38%" (display)

# WRONG (the bug that prompted this rule):
if fmt == "percent":
    return f"{float(value):.2f}%"
# 0.0638 (fraction) → "0.06%" (display, off by 100x)
```

The canonical `active-oahu.kpi.json` formula
`booking_complete / booking_click` produces a fraction. The renderer
multiplies by 100. The data shape (in `dashboard_data.json`) stores
the raw fraction `{"value": 0.0638, "format": "percent"}`; the
renderer applies the multiplication. **Self-rendering preserved:**
data shape + rendering live in the same file, so the contract
cannot drift.

Three rules for percent metrics:

1. **Storage is always a fraction** — the metric's `formula`,
   adapter output, or runtime snapshot must produce a value in
   `[0, 1]` for percent metrics.
2. **The renderer multiplies by 100** — `_format_value(fmt="percent")`
   is the single place where the conversion happens. Never multiply
   in the formula or the snapshot.
3. **The audit test catches drift.** A round-trip test
   (`_format_value(0.0638, "percent") == "6.38%"`,
   then `float("6.38%".rstrip("%")) ≈ 0.0638 * 100`) catches the
   bug in either direction. See
   `references/2026-07-runtime-values-pipeline.md` for the canonical
   round-trip assertion.

When the user finds a math contract bug, **audit adjacent code
paths** before declaring the fix complete. The same `_format_value`
function is used by `render_index` and `render_accordion`; the same
percent-format assumption underlies the dashboard, the email
report, and any future surface that reads runtime values. A fix in
one place is a fix in all places only when the helper is the single
source of truth.

CSS for the new layout (`.pwp-kpi-site-row`, `.pwp-kpi-site-header`,
`.pwp-kpi-card-grid`, `.pwp-kpi-card`, `.pwp-kpi-card-label`,
`.pwp-kpi-card-value`, `.pwp-kpi-card-delta`) lives in
`templates/<name>.css` and is read at `build_dashboard()` time. Adding
a new card style is a single-file change.

## Self-rendering dashboard principle

The rendering function MUST live next to the data shape, NOT in
`__init__.py` separate from the data. This is the user's explicit
directive: "the rendering function should live next to the data shape
(e.g., in `publish_kpi_tracker.py` or `site_builder.py` — NOT in
`__init__.py` separate from the data)".

The class-level rule:

- `aggregate()` (data shape) and `render_index()` / `render_detail()` /
  `render_accordion()` / `_format_value()` (rendering) all live in the
  same file. When a metric field is added or renamed, the rendering
  function is updated in the same edit — no drift between data and
  template.
- `__init__.py` only has orchestrators (`build_dashboard`,
  `publish_publish_kpi_dashboard`, `build_all_site_summaries`,
  `read_runtime_values`) that compose the data and rendering — they
  don't render themselves.
- `aggregate(runtime_values)` is the only input any `render_*` takes.
  Same data in → same HTML out, byte-identical. The integration test
  asserts this by calling `render_index(agg)` twice with the same
  `agg` and comparing for equality.
- The CSS lives in `templates/<name>.css` and is read at
  `build_dashboard()` time. Adding a new card style (e.g.
  `.pwp-kpi-card-value`) is a single-file change.

If you find yourself adding a render function to `__init__.py` to
avoid a circular import, that's a smell — extract the data shape
into its own module and render against that instead. Two files
(data + render) is one too many when they could be one.

The complementary architectural directive: **make the dashboard
canonical from a single source of truth**. Same data going in, same
HTML out, deterministically. The dashboard template + data model are
co-located; changes to one can't drift from the other. The artifact
pair `dashboard_data.json` + `index.html` should not require manual
reviewing of two separate files — both are generated by one function
call from one input.

## Env-var-only config drift fix (env-var is single source of truth)

When a config file carries **both** a static literal AND an env-var
name for the same secret, the static literal is a foot-gun: it drifts
out of sync with the deployed loader. The class-level pattern is:

1. **The adapter** strips the literal at the registry boundary.
   `legacy_seo_registry._adapt_v1_site` (or any v1→v2 adapter) forces
   the literal to `None` so the runtime never sees it.
2. **The resolver** reads only the env-var.
   `pwp_kpi_site_registry._resolve_tracking_property` (or any
   similar "secret / config-secret" resolver) reads from
   `os.environ.get(<env_var_name>)` and ignores the static literal.
3. **The regression tests** assert both behaviors:
   - `test_iter_sites_resolves_tracking_property_from_env` uses
     `monkeypatch.setenv` for every site (literal fallback is gone).
   - `test_adapt_v1_forces_ga4_measurement_id_to_null_gap5` asserts
     the literal is forced to `None`.
4. **Test fixtures** use env-vars, not literals — change
   `test_registry.json` so every site sets `ga4_measurement_env`,
   never `ga4_measurement_id`.

The result: the static config can lie without breaking runtime; the
deployed env-var always wins. Same shape works for any
"config-secret-drift" class — API keys, webhook URLs, sheet IDs,
anything that's both static and env-driven.

The fix shipped as GAP-#5 in 2026-07-29 (env-var-only GA4 resolution).
Live verified: `active-oahu → G-PRRRLMBR8Z` via
`AOT_GA4_MEASUREMENT_ID`; `hd-engine → G-Q6TPL08VM7` via
`HDE_GA4_MEASUREMENT_ID`. See
`references/2026-07-pwp-unified-cron-orchestrator.md` for the
full diff and rationale.

## Unified cron orchestrator pattern (one cron entry, all sites)

When the same KPI cron has both a Python launcher (`cron_launcher.py`)
and a Node shim (`kpi.mjs`) — typically because `prismatic.core_crons`
runs Python and the dev experience already runs Node — the two paths
will eventually diverge on paths, output filenames, kind lists, and
share-target env vars. The class-level fix is a single `registry.json`
that both paths read (see "Dual-path unification" below). When the
launcher is a **per-site** implementation that needs to fire from a
**single cron entry** that walks every registered site, a different
shape applies: a `cron_orchestrator.py` that wraps the per-site
launcher.

The orchestrator pattern:

```python
def run(*, kind, registry_path=None, publish_root=None,
        launcher=None, timeout=120):
    registry = load_registry(...)
    # ... coerce publish_root / launcher to Path ...
    for site in iter_sites(registry):
        if not site_override_enabled(registry, site):
            yield {"slug": ..., "status": "skipped (disabled)"}
            continue
        flat = resolve_collection(site["slug"])
        if not _cadence_matches(flat, kind):
            yield {"slug": ..., "status": "skipped (cadence)"}
            continue
        env = _resolve_share_targets_env(site["slug"], flat)
        result = dispatch_one_site(
            site["slug"], kind=kind, launcher=...,
            env_overrides=env, ...)
        yield {"slug": ..., "status": "dispatched", ...}
```

Three contract points:

1. **`_cadence_matches(flat, kind)`** — accepts three shapes: string,
   list, and dict. The dict shape (canonical active-oahu + hd-engine
   use) carries per-kind metadata:
   ```json
   "delivery_cadence": {
     "daily":   {"kind": "daily"},
     "weekly":  {"kind": "weekly"},
     "monthly": {"kind": "monthly"}
   }
   ```
   The orchestrator checks `kind in cadence.keys()` for dicts,
   `kind in cadence` for lists, and `cadence == kind` for strings.
   Smoke-test against canonical real-world data, not just synthetic
   fixtures — the dict shape only surfaced during live orchestrator
   dispatch, not in the test suite.

2. **`_resolve_share_targets_env(slug, flat)`** — loads each env var
   named in the site's `share_targets` block:
   ```python
   share_targets = flat.get("share_targets") or {}
   env = {}
   for key, env_name in share_targets.items():
       if not isinstance(env_name, str): continue
       v = os.environ.get(env_name)
       if v is not None: env[env_name] = v
   ```
   Missing env vars are silently skipped — the launcher falls back
   to its own defaults.

3. **`_resolve_launcher()`** — never assumes a default. Resolution
   order: explicit `--launcher`, then `PWP_KPI_CRON_LAUNCHER`, then
   `HDE_KPI_REPO_ROOT` + `/scripts/kpis/operators/cron_launcher.py`.

Result: a single Prismatic Engine cron entry
(`python3 .../cron_orchestrator.py daily`) drives every site. Adding
a new site = one registry entry + one curated `*.kpi.json`; the
orchestrator handles dispatch. Live verified end-to-end:
`pwp-kpi-tracker cron daily` dispatches `active-oahu` to
`cron_launcher.py` in 0.05s, writes the daily report to `/tmp/`.

The full reference is `references/2026-07-pwp-unified-cron-orchestrator.md`,
which also documents the `Path`-vs-`str` coercion pitfall (when
argparse passes a string to a function expecting `Path`) and the
two-mode cadence contract.

## `Path`-vs-`str` coercion at function entry

When `argparse` passes a string to a function expecting `Path`, coerce
at the function entry — not at every call site. Unit tests typically
call functions with `Path` directly; the CLI passes strings. The
boundary is rarely exercised in tests; the verifier is the durable
place to catch this class of bug.

Pattern:

```python
PathLike = Union[Path, str]

def run(*, publish_root: Optional[PathLike] = None, ...):
    if publish_root is None or publish_root == "":
        publish_root_path = Path("/tmp/default") / kind
    else:
        publish_root_path = Path(publish_root)
    publish_root_path.mkdir(parents=True, exist_ok=True)
```

Plus a regression test that passes a string, not a `Path`:

```python
def test_run_coerces_string_publish_root(tmp_path, monkeypatch):
    publish_root_str = str(tmp_path / "string-publish-root")
    manifest = run(
        kind="daily",
        publish_root=publish_root_str,  # str, not Path
        launcher=tmp_path / "stub.py",
    )
    assert manifest["publish_root"] == publish_root_str
    assert (tmp_path / "string-publish-root").is_dir()
```

This pattern was needed in `cron_orchestrator.run()` after a verifier
surfaced `AttributeError: 'str' object has no attribute 'mkdir'`.
The canonical pytest suite missed it because every test passed
`Path` directly.

## Path-portability commit gate (avoid `/home/...` in tests)

The Prismatic commit gate has a path-portability check that aborts
the commit when a `.py` file contains a hardcoded absolute path like
`/home/ubuntu/...`. The check is separate from the lane-ownership
check (which fires at push time, not commit time). Test fixtures are
the most common offender because developers paste the absolute path
into `FIXTURES = Path("...")` constants during local exploration.

The fix:

```python
# BAD: hardcoded absolute path → commit gate aborts.
FIXTURES = Path("/home/ubuntu/work/prismatic-pwp-ubersuggest-auth/.../tests/fixtures")

# GOOD: relative to __file__ → portable.
FIXTURES = Path(__file__).resolve().parent / "fixtures"

# GOOD when PWP_REPO_ROOT is needed inside a tests/ subdir:
#   <PWP_REPO>/prismatic/shipped_plugins/pwp/capabilities/publish_kpi_tracker/tests/test_foo.py
# so PWP_REPO = parents[6] (the extra `tests/` adds one level vs the
# same file outside `tests/`).
PWP_REPO = Path(__file__).resolve().parents[6]
```

Two invariants:

1. The fixture path resolves to the same file on every developer's
   machine and in CI.
2. The repo-root anchor resolves to a directory that actually contains
   the canonical config (`config/seo_sites.json` for PWP) — see the
   symlink-walk anchor pattern below for the deeper variant.

When the gate fires, the error names every offending file path. Fix
all of them in one commit; the gate will pass on retry without
re-running the test suite.

## Module-scanner pattern for live coverage verifiers

When verifying that GA4 events actually reach the live site, the page body
**is not enough**: Astro builds page hydration into `/_astro/<name>.js`
modules. The verifier must scan both. The pattern:

```js
function extractAstroModuleUrls(body) {
  return [...new Set([...body.matchAll(/src=[\"\']([^\"\'+?_astro\/[^\"\'+]+\.js)[\"\'](])].map((m) => m[1]))];
}

async function fetchModulesConcat(urls) {
  const texts = await Promise.all(urls.map(async (u) => {
    try {
      const abs = u.startsWith('http') ? u : new URL(u, baseUrl).toString();
      const r = await fetchText(abs);
      return r.body || '';
    } catch (err) { return ''; }
  }));
  return texts.join('\n');
}

async function augmentPageWithModules(page) {
  const modules = extractAstroModuleUrls(page.body);
  const moduleBody = modules.length ? await fetchModulesConcat(modules) : '';
  const moduleEvents = extractGa4EventNames(moduleBody);
  return { ...page, eventNames: [...new Set([...(page.eventNames || []), ...moduleEvents])] };
}
```

CRITICAL: the page record built by `inspectHtml()` does **not** carry `body`
forward. Pass it explicitly when merging:

```js
const pagesInspected = pageFetches.map((p) => ({
  body: p.body,
  ...inspectHtml(p.url, p.status, p.finalUrl, p.body, p.error),
}));
const pages = await mapLimit(pagesInspected, concurrency, augmentPageWithModules);
```

If you omit `body`, every augment returns 0 modules and the verifier stays
broken in a way that is hard to spot. Confirm by logging in dev: a page
without `/_astro/` should still report `bodyLen=N` where N > 0.

## Live deploy race after a merge

Cloudflare Pages does not instantly reflect the new commit. Symptom pattern:
`len(body)` and `'has_ga_id'` oscillate between two values for ~60–180 s
after a merge. Pattern:

```js
let last_state = null;
for (let i = 0; i < 40; i++) {
  const body = fetchOnce(url);
  const state = (has_ga, len(body));
  if (state !== last_state) {
    console.log('tick', i, state);
    last_state = state;
  }
  // Stop only when the new content is stable for >= 3 ticks
  if (state_desired && state_matches(state)) {
    stable_count++;
    if (stable_count >= 3) break;
  }
  sleep(6);
}
```

The first "moved" tick is not a stable green. Three consecutive ticks on
the new content is the threshold.

## Direct push to `main` does NOT trigger CF Pages deploy

Cloudflare Pages only deploys on PR merge to the configured branch, not on
direct push. After a `git push origin main` from a non-PR session, the Live
URL stays stale. If you committed directly to `main`, you must open a PR
backed by the same commit and merge it (or revert + reopen as a PR) to
trigger the deploy. Verification proof requires the Live URL to reflect
the new commit, so plan the work to merge via PR.

## Pitfalls

- **Stripe secrets must never be printed.** Cards created via the test API
  use `cs_test_funnel_123` placeholders in tests, never real `cs_live_*`
  values. The KPI sheet's `Raw` tab should redact the `customer_email`
  field to first-3-chars + `@domain` for non-admin viewers.
- **GA4 fetch races.** The GA4 Data API has up to ~24h of intra-day
  latency. Daily reports that run at 06:30 PT cover "yesterday" in the
  GA4 API, partly-today in Stripe. Surface this in the report footer.
- **Telegram deep-link count is lagged.** The Telegram bot reports
  `/start <token>` activations through the Prismatic Engine, which has its
  own cron. Don't surface a daily KPI for deep-link clicks until the
  upstream has a daily cron; fall back to weekly.
- **PWP dashboard page must not call live APIs.** A static page that uses
  `=IMPORTDATA()` for charts is family-test-safe. A page that calls
  `fetch()` to the GA4 API requires an API key in the page bundle, which
  is a security problem.
- **Don't re-derive already-derived metrics.** Keep formulas short and
  reuse ids. If you find yourself writing `A * 52 / 12` in three places,
  promote it to a named metric with `source: "derived"`.
- **Cross-domain booking flows ≠ Stripe.** When the booking provider lives
  off-site (FareHarbor, Peek, etc.), Stripe is not the truth. Don't add a
  `*revenue_usd` metric. Capture funnel events via GA4 + Measurement
  Protocol, and treat the provider's CSV export as the eventual revenue
  source. See "Sourcing rule exception" above for the canonical pattern.
- **Override `parents[N]` with a canonical anchor walk.** A launcher at
  `scripts/kpis/operators/cron_launcher.py` is fragile when invoked via
  `python3 scripts/kpis/operators/cron_launcher.py` because `__file__`
  resolves as relative and drops a parent. Always use a `_resolve_repo_root()`
  walker that looks for a known anchor file (e.g. `registry.json`).
- **Forget the `{kind}` template substitution.** A
  `Path("/tmp/kpi-report-{kind}.json")` baked at module load returns the
  literal string. Always `replace("{kind}", kind)` immediately before `Path()`.
- **Regex-check derived formulas against raw identifiers.** A naive
  `re.match(r"^[\d\s+\-*/().]+$", "booking_complete_total / booking_click_total")`
  fails because identifier tokens are not in the allowlist. The skill's
  safe-eval `derive()` substitutes identifiers with `String(metrics[id] || 0)`
  *before* applying the regex. Verifiers that port the gate must do the
  same pre-substitution (see "Important ordering" above `derive()` for the
  full pattern).
- **Writing JSON without grepping the live site first.** The structural
  validator catches shape, not facts. The "Procurement discipline" section
  above is the canonical counter-move: grep `gtag('config', 'G-XXX')` and
  `gtag('event', '<name>')` against the live mirror **before** writing the
  JSON, so a wrong file is never produced. The reference file
  `references/2026-07-ground-against-live-site-before-writing.md` captures
  the full checklist and a verifier template.
- **Hardcoded `/home/ubuntu/...` paths in tests abort the commit gate.** The
  path-portability check fires at commit time, separate from the lane
  check at push time. Use `Path(__file__).resolve().parent /
  "fixtures"` and `parents[6]` for tests-dir depths. See
  "Path-portability commit gate" above.
- **Multi-site summary table collapses to empty cards.** A wide
  `<table>` row per site with empty card cells when `runtime_values`
  is not yet populated is the wrong layout. Use one
  `<section class="pwp-kpi-site-row">` per site with an inline card
  grid showing `—` placeholders. See "Per-site row is the smallest
  visual unit that closes the loop" above.
- **Bare-id vs metric_key collision in merge ops.** Canonical
  `*.kpi.json` files key metrics by dotted names like
  `funnel_booking.booking_click`; the migration operator's
  registry-derived `default_metric_specs` key them by bare ids
  (`booking_click`). A merge that compares full keys creates
  phantom duplicates. The fix: normalize by bare id
  (`metric_key.rsplit(".", 1)[-1]`) before comparison. See
  `references/2026-07-runtime-values-pipeline.md` for the canonical
  `_merge_into_existing()` pattern.
- **`build_dashboard(runtime_values={})` silently bypasses the pipeline.**
  `{}` is a valid (empty) `runtime_values` dict, so the `if
  runtime_values is None` guard inside `build_dashboard` skips the
  pipeline and `aggregate(runtime_values={})` is called with no
  values at all. The CLI must pass `None` (not `{}`) when no
  `--runtime-values-path` was given, otherwise the dashboard renders
  all `—` placeholders forever. See "Runtime values pipeline" below
  for the full contract.
- **`Path`-vs-`str` boundary silently crashes argparse paths.** When a
  function signature says `Optional[Path]` but `argparse` passes a
  string, the function crashes with `AttributeError: 'str' object has
  no attribute '<method>'` on first call. The pytest suite missed this
  because every test passed `Path` directly. Widen the signature to
  `Optional[PathLike]` (Union[Path, str]), coerce at the function
  entry, and add a regression test that passes a string. See
  "`Path`-vs-`str` coercion at function entry" above.
- **Per-render random content (CSRF nonces, request IDs) breaks the
  byte-identical determinism test.** `render_index` is contractually
  byte-identical for the same `agg` input — every integration test
  relies on this for cache-key assertions and snapshot diffing.
  Adding a feature that injects a per-render random token (e.g. a
  CSRF nonce via `secrets.token_urlsafe()`) into the modal HTML
  breaks the contract: two consecutive renders of the same `agg`
  produce different bytes. The fix: accept an optional `csrf_token`
  keyword-only argument on `render_index`, pass it through to the
  modal-rendering helper, and have the existing determinism test
  pass `csrf_token="test-csrf-stable"`. Live dashboards generate
  fresh tokens per render (None → fresh `secrets.token_urlsafe(16)`);
  tests pass a stable token to verify the rest of the HTML is
  byte-identical. Same pattern applies to any "self-rendering"
  builder that adds non-deterministic data (timestamps, request IDs,
  fresh hash salts, etc.). See "Dashboard modal flow
  (Phase 4.2)" below for the canonical funnel_config-modal example.
- **Lazy-import with try/except — never let a missing feature break
  the dashboard.** When `render_index` adds an injected block
  (modal, announcement banner, feature flag panel), import the
  producing module via a `try: from .module import ... except
  Exception: ... = ""` guard. If the module is uninstalled, the
  dashboard still renders the rest of the HTML instead of 500ing on
  the operator's terminal. The canonical Phase 4.2 pattern wraps
  `from .funnel_form import render_modal_html` so a partial install
  (e.g., a pinned dashboard-only build) keeps working. The cost is
  one import-time guard, the benefit is no operator-time
  "ImportError: cannot import name 'render_modal_html'" debugging
  detour when a feature module is missing.
- **Per-site CTA buttons depend on prior submission logs — keep the
  helper dumb, the data live.** `site_row_buttons(site)` reads
  `/tmp/pwp-provisioning/funnel-config/<slug>.json` to decide
  whether to render "Configure website KPIs" (no prior) vs.
  "Edit funnel" + "Re-submit refinement" (prior exists). Tests
  `monkeypatch.setattr(module, "SUBMISSION_LOG_DIR", tmp_path)`
  to point at a temp dir; do NOT mock `load_prior_submission`
  itself, or the test stops exercising the production reading
  code. The data stays on disk under `PWP_FUNNEL_CONFIG_DIR`; only
  the directory moves in tests.
- **`delivery_cadence` is a dict, not just a string/list.** The canonical
  active-oahu and hd-engine files use a dict shape keyed by cadence
  kind. An orchestrator that only handles string/list will skip
  every site. Always check the dict shape too. See "Unified cron
  orchestrator pattern" above.
- **Fixture tests that unlink production files destroy data silently.**
  A test that writes a sentinel to a shared production file (e.g.
  `<sites_dir>/<slug>.runtime.json`) and calls `.unlink()` in
  `finally` to "clean up" silently deletes the original file when a
  real one exists. The canonical fix: back up the original content
  before overwriting, and restore in `finally` (only `unlink()` if
  `backup is None`). Restore lives in `finally`, not `try`-pass,
  so a failing assertion still restores the bytes. See "Orchestrator
  patterns: prior_outputs, soft-failure, test hygiene" above for
  the canonical pattern.
- **`getattr(step_module, "STEP_CATEGORIES", {})` is the canonical hook
  for the soft-failure gate.** Read it inside the orchestrator's
  per-step wrapper; default to `"blocking"` when missing so
  capabilities without the dict stay fail-loud. The step category
  is for *credential configuration gaps*, not flaky-step excuses.
  See "Orchestrator patterns: prior_outputs, soft-failure, test
  hygiene" above.
- **`prior_outputs` flows every non-empty output forward.** Filter
  by output emptiness, not by step status. A step that wants
  "did upstream succeed?" checks the output's *content*, not the
  orchestrator's filter. See "Orchestrator patterns: prior_outputs,
  soft-failure, test hygiene" above.

## Runtime values pipeline: closing the `—` placeholder gap

A multi-site dashboard that always renders `—` is operationally
incomplete: an operator looking at it can't tell whether the cron is
broken, the GA4 ID is wrong, or the site simply hasn't reported yet.
The runtime values pipeline (`runtime_values.py`, ~500 lines) closes
this gap with a **two-mode contract** that prefers live API calls
when credentials are present and falls back to on-disk snapshots
otherwise.

### The two-mode contract

For each metric, the pipeline:

1. Reads the canonical snapshot file `<sites_dir>/<slug>.runtime.json`
   and treats its values as the **override** (they always win).
2. For each non-derived metric, dispatches to the source-specific
   adapter (`ga4`, `stripe`, `gsc`, `telegram`, `internal`,
   `verifier`) keyed by `metric.source`. Each adapter has the same
   contract: `query(metric_key, metric_spec, site_flat, *,
   env) -> value | None`. Live mode requires credentials in the
   passed env (e.g. `GOOGLE_APPLICATION_CREDENTIALS`,
   `STRIPE_API_KEY`, `TELEGRAM_COUNTER_URL`); without them, the
   adapter returns `None` and the snapshot value (if any) is the
   final answer.
3. Computes derived metrics LAST, after all sources have filled in.
   The formula is sandboxed (see "Derived metric safety" below) and
   uses bare ids (`purchase_total`) rather than dotted keys
   (`funnel_buy_report.purchase_total`).
4. Drops any metric that ended up with `None` so the dashboard
   renders `—` for it.

### Per-source snapshot files

The pipeline reads three kinds of files at `<sites_dir>/`:

- `<slug>.runtime.json` — canonical `{metric_key: value}`. Wins
  over every other source when present.
- `<slug>.internal.json` — `{metric_key: value}` for `source:
  "internal"` metrics. Read by `_query_internal`.
- `<slug>.verifier.json` — `{metric_key: value}` for `source:
  "verifier"` metrics. Read by `_query_verifier`.

The snapshot path is the **demo path**: a small JSON file carries
curated values that the dashboard renders directly without any
credentials. Adding a new site is "drop a snapshot file next to the
site's `*.kpi.json` and call `build-dashboard`." No live integration
required.

### `build_dashboard(None)` triggers the pipeline

The orchestrator's contract:

```python
def build_dashboard(*, publish_root, runtime_values=None, window="last24h",
                    write_snapshot=True, sites_dir=None):
    publish_root = Path(publish_root)
    publish_root.mkdir(parents=True, exist_ok=True)
    if runtime_values is None:
        from . import runtime_values as rv
        runtime_values = rv.build_runtime_values(sites_dir=sites_dir)
    # ... render from runtime_values ...
```

Two invariants:

1. **`runtime_values is None` is the only signal that triggers the
   pipeline.** A caller passing `{}` is explicitly opting out
   (empty, but no pipeline run). The CLI must pass `None` when
   `--runtime-values-path` was not given — passing `{}` silently
   bypasses the pipeline and renders `—` for every card.
2. **Sites with no data produce no row.** `build_runtime_values()`
   drops empty per-site dicts. The dashboard's `aggregate()` iterates
   `list_sites()` regardless, but each row's `front_of_card` list
   is empty when no runtime values exist, so the per-site row
   renders an empty card grid with "No front-of-card metrics
   registered" copy.

### CLI bootstrap

`operator_cli snapshot` writes a `<slug>.runtime.json` template
with `null` placeholders for every metric key in the resolved
collection. Existing files are NOT overwritten unless `--force` is
passed. The operator fills the placeholders manually or via a
live-mode adapter. Without this subcommand, the only way to
bootstrap a runtime snapshot was hand-editing JSON — error-prone for
a 21-metric collection like AOT.

### Derived metric safety

`_compute_derived(metric_key, metric_spec, runtime_values_for_site)`
evaluates formulas like `purchase_total / booking_click`:

- Identifiers are substituted with `repr(float_value)` LONGEST FIRST
  to avoid `click` swallowing part of `booking_click`.
- After substitution, the expression must match
  `^[a-zA-Z0-9_./ ()*+%-]+$` — anything else returns `None`.
- `eval()` runs with `{"__builtins__": {}}` so builtin references
  like `__import__` cannot resolve even if they sneak past the
  regex.

The two-step gate (substitute-then-regex-then-eval) is the security
boundary. A naive verifier that applies the regex against the raw
formula `purchase_total / booking_click` will false-reject it
because identifier tokens are not in the digit/operator allowlist.
The substitution MUST happen before the regex, in that order, every
time.

### Live adapter pattern

Each live adapter is **gated on credentials**, not on package
presence:

```python
def _query_ga4(metric_key, metric_spec, site_flat, *, env):
    creds = env.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds:
        return None  # snapshot path takes over
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
    except ImportError:
        return None  # package not installed; treat as no creds
    tracking_property = site_flat.get("tracking_property")
    if not (tracking_property and tracking_property.startswith("G-")):
        return None
    # ... real GA4 Data API call ...
```

The two-stage guard is important: missing credentials AND missing
package both return `None`. The pipeline never raises — it
gracefully degrades to snapshot values. This is the difference
between "the dashboard works for the demo right now" and "the
dashboard requires a live GA4 + Stripe + Telegram integration to
even render."

### Test surface

The runtime values pipeline added 25 tests in
`tests/test_runtime_values.py` covering:

- `default_sites_dir()` resolution + `PWP_REPO_ROOT` env override
- Snapshot reading, sidecar reading, snapshot-wins-over-adapter
- Derived metric arithmetic, bare-id substitution, longest-first
- `_compute_derived` rejects unknown operands + builtin refs
- Unknown source silently skipped
- `build_all` walks every site deterministically
- `snapshot` subcommand via operator_cli produces null templates
- `snapshot` safety guard (no `--force` preserves existing)
- Every live adapter returns `None` without credentials

A typical end-to-end run:

```bash
# Bootstrap a snapshot template.
pwp-kpi-tracker snapshot --sites-dir ./sites

# Operator fills values manually, or a live-mode adapter writes them.
cat > ./sites/hd-engine.runtime.json <<EOF
{
  "funnel_top.free_chart_generated_total": 184,
  "funnel_sanctuary.sanctuary_purchase_total": 7
}
EOF

# Build the dashboard. No --runtime-values-path → pipeline runs.
pwp-kpi-tracker --publish-root /tmp/dashboard build-dashboard
```

The dashboard now renders **real numbers** in each card: 184, 7,
etc. The `—` placeholders disappear. This is the missing piece
that makes the multi-site dashboard useful as a daily check,
not just a registry dump.

### Pitfalls

- **Don't pass `{}` to `build_dashboard` when you mean "use the
  pipeline."** Pass `None`. `{}` is "explicit empty override"
  semantics; `None` is "auto-discover values."
- **Don't put credentials in the snapshot file.** The snapshot is
  checked into git (Ned's lane). Live credentials belong in env vars
  passed to the FastAPI gateway or the cron launcher, not in
  `<slug>.runtime.json`.
- **Don't write a `<slug>.runtime.json` with literal nulls and
  expect the pipeline to substitute them.** The pipeline treats
  `null` as missing; the snapshot must have real numbers. Use the
  `snapshot` subcommand to bootstrap a template, then fill the
  values.
- **Don't re-implement the `eval()` step.** The bare-id
  substitution is the security boundary. A naive regex against the
  raw formula is a false-reject (see "Derived metric safety").
- **Don't add new adapter sources without updating the test
  surface.** The "every live adapter returns None without
  credentials" test block guards the snapshot-vs-live contract;
  extending the `ADAPTERS` dict without extending that block means
  the new source ships without a fallback test.
- **Don't call `list_sites()` to discover sites for the runtime
  pipeline.** `list_sites()` reads from `kpi.SITES_DIR` (the
  canonical plugin tree), so a test that puts a fixture in
  `tmp_path/sites/` and expects the pipeline to discover it must
  `monkeypatch.setattr(inner, "SITES_DIR", d)` for the duration of
  the test. The test_runtime_values suite already does this; copy
  the pattern when adding new tests.

## PWP plugin capability pattern (canonical schema → reusable plugin primitive)

When a one-off KPI tracker (e.g. HDE's `scripts/kpis/`) needs to become a
reusable plugin primitive that the rest of the Prismatic engine can
ship, the class-level pattern is to add it under an existing PWP plugin
as a `capabilities/<name>/` sub-package. The KPI standardization is
the trigger; the pattern is general — any capability that takes a
**canonical schema**, an **aggregation**, and **three views from one
data source** fits.

### File layout

```
plugins/pwp/capabilities/<name>/
├── __init__.py                        public API + register_<name>_plugin() + publish_<name>_dashboard()
├── <name>.py                          validate / load / resolve / aggregate / render_index / render_detail / render_accordion
├── schemas/<schema>.schema.json       canonical JSON Schema 2020-12
├── templates/<name>.css               dashboard styles
├── sites/<slug>.json                  per-site files (one per registered site)
└── tests/
    ├── __init__.py
    ├── conftest.py                    prepended ROOT to sys.path
    ├── test_<name>.py
    └── fixtures/<slug>.kpi.json        canonical fixture (under tests, never in production sites/)
```

Place `conftest.py` and `pytest.ini` inside `plugins/pwp/` (or the
plugin's symlink target) — never at the repo root. The lane guard
allowlists `scripts/`, `prismatic/`, `plugins/` for Ned; repo-root
config files appear in the lane-violation push failure.

### Lazy import + register adapter

The host plugin's `plugin.py` must not require the new capability at
install time. Pattern:

```python
try:
    from plugins.pwp.capabilities.<name> import (
        <NAME>_CAPABILITY_ID,
        <NAME>_VERSION,
        publish_<name>_dashboard,
        register_<name>_plugin as _register_<name>_plugin,
    )
except Exception:
    <NAME>_AVAILABLE = False
    def _missing(*_a, **_k): return {"error": "not installed"}
    publish_<name>_dashboard = _missing
    _register_<name>_plugin = None
else:
    <NAME>_AVAILABLE = True
```

Then in `on_init(self, context)`:

```python
if <NAME>_AVAILABLE and _register_<name>_plugin is not None:
    try: _register_<name>_plugin(self)
    except Exception as exc:
        print(f"<name> registration failed: {exc}")
```

Missing capability → graceful degradation; the four new routes return
a clear "not installed" error from the FastAPI gateway.

### Manifest as the source of truth for declared surface area

`plugins/pwp/plugin-manifest.yaml` lists every dashboard surface and
every endpoint. Adding a capability without listing it in the manifest
makes it invisible to the operator even though the routes work. Always
add `dashboard_surfaces` and `endpoints` entries when you add a
capability, and bump the plugin version (e.g. 1.2.0 → 1.3.0).

### FastAPI gateway wiring

The four routes live in `prismatic/gateway/server.py`. They lazy-import
the capability so the gateway can boot even when the capability is
absent:

```python
@app.get("/api/pwp/kpi/sites")
async def pwp_kpi_sites() -> dict[str, Any]:
    try:
        from plugins.pwp.capabilities.publish_kpi_tracker import (
            aggregate as _aggregate,
            list_sites as _sites,
        )
    except Exception as exc:
        return {"ok": False, "error": f"not installed: {exc}"}
    return {"ok": True, "sites": _aggregate(runtime_values={})["sites"]}
```

### Symlink trap: `plugins/` → `prismatic/shipped_plugins/`

In `prismatic-pwp-ubersuggest-auth`, `plugins/` is a git symlink to
`prismatic/shipped_plugins/`. Practical consequences:

- Writing to `plugins/foo/bar.py` writes to `prismatic/shipped_plugins/foo/bar.py`.
- `git add plugins/foo/bar.py` errors with `pathspec ... is beyond a
  symbolic link`. Stage the canonical path instead.
- Tests must use `pythonpath = "."` so `from plugins.pwp.capabilities
  import <name>` resolves via the symlink target.

### Ruff MUST be scoped

A bare `ruff check --fix` in this repo rewrites 200+ files in
unrelated lanes. Always pass an explicit file list:

```bash
OWNED=(prismatic/shipped_plugins/pwp/capabilities/<name>/*.py …)
ruff check --fix "${OWNED[@]}"
ruff format "${OWNED[@]}"
```

`ruff format` mangles YAML files (it expects JSON-ish blocks). Restore
any YAML manifest from `HEAD` after a mistaken `ruff format ... .yaml`.

### What the `kpis-and-reporter-architecture` schema already provides

The "Multi-site standardization" section below defines the canonical
schema, the `extends` inheritance model, and the three views. When
shipping that as a PWP capability, the schema moves to
`schemas/kpi-collection.schema.json` and the example sites move to
`sites/<slug>.kpi.json`. The renderer, the dashboard route, and the
email cron do not change.

The `validate()` function is small (~30 lines, stdlib-only) and lives
in the capability's `__init__.py` or `*.py` module — not in a separate
validation library. It assumes JSON Schema is the upstream source of
truth, but adds three project-specific guards the schema can't express
cheaply: source allowlist, inner-id/key-name match, and the unknown-field
warning. See `references/2026-07-pwp-publish-kpi-tracker-lane-guard.md`
for the lane-guard + symlink specifics surfaced in PR #410.

## Dual-path unification (one canonical registry, multiple runtimes)

When the same KPI cron has both a Node CLI (`scripts/kpis/cli.mjs`) and
a Python CLI (`scripts/kpis/operators/cron_launcher.py`) — typically
because CronsManager already runs Python and the dev experience already
runs Node — the two paths will eventually diverge on paths, output
filenames, kind lists, and share-target env vars. The class-level fix is
a single `registry.json` that both paths read.

### File layout

```text
scripts/kpis/
├── kpi-collections.json             # canonical definitions (single source of truth)
├── fixtures/kpi-fixtures.json
└── operators/
    ├── registry.json                # paths, kinds, outputs, share-targets
    ├── cron_launcher.py             # canonical Python launcher
    ├── kpi.mjs                      # Node shim that spawns the Python launcher
    └── tests/test_dual_path.py      # integration test: assert same metric_index keys
```

### registry.json shape

```jsonc
{
  "canonical_launcher": "scripts/kpis/operators/cron_launcher.py",
  "node_shim":           "scripts/kpis/operators/kpi.mjs",
  "schedule": {
    "daily":   { "kind": "daily"   },
    "weekly":  { "kind": "weekly"  },
    "monthly": { "kind": "monthly" }
  },
  "outputs": {
    "json":      "/tmp/kpi-report-{kind}.json",
    "html":      "/tmp/kpi-report-{kind}.html",
    "sheet_csv": "/tmp/hde-kpi-sheet.csv",
    "email_eml": "/tmp/kpi-email.eml"
  }
}
```

The `{kind}` token is a template placeholder. Both paths must call
`str.replace("{kind}", kind)` **before** constructing `Path()`; do not
let `Path(name)` bake the literal `{kind}` into the final filename.

### Pattern in Python

```python
def output_paths(kind: str) -> tuple[Path, Path, Path, Path]:
    reg = load_registry()
    tmpl = reg.get("outputs") or {}

    def _expand(t: str) -> Path:
        return Path("/tmp/") / Path(t.replace("{kind}", kind)).name

    return (
        _expand(tmpl.get("json",  f"kpi-report-{kind}.json")),
        _expand(tmpl.get("html",  f"kpi-report-{kind}.html")),
        _expand(tmpl.get("sheet_csv", "hde-kpi-sheet.csv")),
        _expand(tmpl.get("email_eml", "kpi-email.eml")),
    )
```

Always run `(Path("/tmp/") / Path(...)).name` instead of `Path("/tmp/")
/ Path(...)`. `Path("/tmp/") / "/tmp/file.json"` with an absolute second
arg silently drops the leading slash on some platforms.

### Pattern in Node shim

```js
// kpi.mjs spawns the Python launcher; both paths emit the same JSON.
import { spawnSync } from "node:child_process";
const res = spawnSync("python3", ["./cron_launcher.py", "daily"], { stdio: "inherit" });
process.exit(res.status ?? 1);
```

The Node shim must not re-implement the metric aggregation. It must
spawn the Python launcher so the schema equivalence is guaranteed at
the OS level.

### Robust path resolution (no `parents[N]`)

For a launcher at `scripts/kpis/operators/cron_launcher.py`, do **not**
rely on `HERE.parents[3]` — `parents[N]` is brittle when the script is
invoked via `python3 scripts/kpis/operators/cron_launcher.py` (which
flips `__file__` to a relative path, dropping a parent during
`.resolve()`). Use a canonical anchor walk:

```python
def _resolve_repo_root(here: Path) -> Path:
    for p in [here, *here.parents]:
        if (p / "scripts" / "kpis" / "operators" / "registry.json").is_file():
            return p
    return here.parents[3]  # fallback only; raise if the registry is missing
```

Add `HDE_KPI_REPO_ROOT` as an env override so CI and isolated verifiers
can pin the repo root without depending on parent-chain resolution.

### Schema-equivalence integration test

```python
def test_both_paths_produce_same_metric_set():
    py_daily = _run_launcher("daily")
    node_daily = _run_shim("daily")
    assert set(py_daily["metric_index"].keys()) == set(node_daily["metric_index"].keys())
    for k, m in py_daily["metric_index"].items():
        for fld in ("id", "label", "value", "format"):
            assert fld in m
```

If the Node shim ever re-implements aggregation (or the Python launcher
adds a new metric without reading the registry), this test fails
immediately. The pair `<kind>.json` is the canonical contract.

### Common pitfalls

- **Forgetting the `{kind}` substitute.** A `Path("/tmp/kpi-report-{kind}.json")` baked at module load returns the literal string `/tmp/kpi-report-{kind}.json` and the file never gets written. Always `replace("{kind}", kind)` immediately before `Path()`.
- **Trusting `parents[N]` to find the repo root.** Use the anchor walk above.
- **Shipping the Node shim as a re-implementation.** It degrades to a spawn wrapper. If the capability is small enough to fork, the registry should still be the source of truth.
- **Skipping the integration test.** Without it, the two paths drift silently over months.

## Migration operator pattern: `--dry-run`, skip-if-exists, `--force`

When a write-side migration derives a curated file from a registry, the
default behavior must protect the curated file from being clobbered. The
class-level contract for any migration operator:

1. **`--dry-run`** — compute the would-be writes, print the manifest, write
   nothing. Every site in the manifest must show `metric_count`,
   `tracking_property`, and the resolved output path.
2. **Skip-if-exists (the default)** — if the target file already exists,
   report `status: "skipped (exists)"` and leave the bytes alone. This
   is the **safety guard**. Curated `*.kpi.json` files carry hours of
   curation (Front-of-card flags, formula overrides, custom event sets)
   that a registry cannot reproduce, so a registry re-run must never
   overwrite them silently.
3. **`--force`** — explicit operator intent to overwrite. Use when
   bootstrapping a new site or after a registry change the curated file
   should inherit. The default-flag asymmetry (skip by default, opt-in
   overwrite) is what makes the operator safe to wire into a cron.

The manifest the operator returns must distinguish four outcomes per
site:

- `"written"` — file did not exist (or `--force` was set) and was created.
- `"skipped (exists)"` — file existed, no `--force`, bytes unchanged.
- `"skipped (disabled)"` — `pwp_kpi_override.enabled: false` for this site.
- `"error"` — building the collection raised; surface the message.

This four-state contract lets the cron-driven use case run idempotently
without supervision, and lets the on-call operator inspect the manifest
without diffing the registry.

**Real PWP publish-kpi-tracker output:**

```json
{
  "dry_run": false,
  "force": false,
  "sites": [
    {"slug": "active-oahu", "status": "skipped (exists)",
     "path": "/home/ubuntu/work/.../publish_kpi_tracker/sites/active-oahu.kpi.json"}
  ],
  "validation_errors": []
}
```

Re-running `migrate --force` flips the status to `"written"` and the
curated bytes are replaced with the freshly-built collection. The
ad-hoc verifier wraps this in a backup/restore so the destructive test
is idempotent — see `ad-hoc-verification-contracts` for that pattern.

## v1 → v2 schema adapter pattern (transparent upgrade)

The PWP publish-kpi-tracker registry evolved from v1 (`config/seo_sites.json`
as it exists today — a flat list of sites with `gsc_property`,
`expected_data_layer_events`, and direct GA4 fields) to v2 (the canonical
`schemas/pwp-kpi-registry.schema.json` with `pwp_kpi_capability`,
`default_metric_specs`, and per-site `pwp_kpi_override` /
`pwp_kpi_metric_specs`).

The class-level pattern for evolving a canonical schema without breaking
existing consumers is a transparent v1→v2 adapter that runs at load time:

```python
# legacy_seo_registry.py
def _is_v1(registry: dict) -> bool:
    """Heuristic: v1 has no `pwp_kpi_capability` block; v1 sites carry
    `gsc_property`/`expected_data_layer_events` directly."""
    sites = registry.get("sites") or []
    return isinstance(registry, dict) \
        and "pwp_kpi_capability" not in registry \
        and any(isinstance(s, dict) and (
            "gsc_property" in s
            or "expected_data_layer_events" in s
            or "ga4_measurement_env" in s
        ) for s in sites)

def adapt_v1_to_v2(registry: dict) -> dict:
    if not _is_v1(registry):
        # Already v2 — fill in explicit defaults and return.
        v2 = dict(registry)
        v2.setdefault("pwp_kpi_capability", {...defaults...})
        for s in v2.get("sites") or []:
            s.setdefault("pwp_kpi_override", {"enabled": True})
        return v2
    # build default_metric_specs from union of expected events
    # preserve every v1 site field, add pwp_kpi_override.enabled=True
    return v2
```

Then in `load_registry`:

```python
def load_registry(path=None):
    p = Path(path) if path else _resolve_registry_path()
    raw = json.loads(p.read_text(encoding="utf-8"))
    from .legacy_seo_registry import adapt_v1_to_v2
    return adapt_v1_to_v2(raw)
```

Three rules:

1. **The adapter is the only seam that knows both shapes.** Downstream
   consumers (registry loader, migration operator, dashboard builder)
   always see v2. New code never has to handle v1.
2. **The adapter is idempotent over v2.** Passing a v2 registry through
   `adapt_v1_to_v2()` is a no-op apart from filling explicit defaults.
   The loader can call it unconditionally on every read.
3. **Tests assert both directions.** Cover the v1→v2 adaptation path AND
   the v2 passthrough path. The integration test loads a v1 file from
   disk and confirms v2 fields appear; the unit tests assert the
   per-site v1 fields are preserved.

When the adapter is in place, a one-shot v1→v2 rewrite of
`config/seo_sites.json` can be deferred to "the next time someone
touches the file." Existing readers keep working; new readers see v2.

## Symlink-walk anchor pattern (plugin layer)

The earlier `parents[N]` pitfall covers the cron-launcher case. The
plugin layer adds a deeper variant: when the same module is reachable
through both a **symlink path** (e.g. `plugins/pwp/...`) and its
**target path** (e.g. `prismatic/shipped_plugins/pwp/...`), Python's
`__file__` reports the symlink path when modules are loaded via the
symlink — even after `Path(__file__).resolve()`, because `.resolve()` is
not always canonicalizing every intermediate symlink on every platform.

**Symptom.** `HERE.parents[5]` of
`/home/ubuntu/work/prismatic-pwp-ubersuggest-auth/plugins/pwp/capabilities/publish_kpi_tracker/operator_migrate.py`
is `/home/ubuntu/work` (one level too high). The same file resolved
through `prismatic/shipped_plugins/pwp/.../operator_migrate.py` gives
the real repo root.

**Fix.** Walk up looking for an anchor file the production code expects
to find at the repo root. The anchor must be unique to the repo (the
canonical config registry is good; `README.md` is not):

```python
def _walk_to_pwp_repo(here: Path) -> Path:
    cur = here
    for _ in range(10):
        if (cur / "config" / "seo_sites.json").is_file():
            return cur
        cur = cur.parent
    raise FileNotFoundError(
        f"operator_migrate: could not locate PWP_REPO from {here}; "
        f"no config/seo_sites.json within 10 parent levels. "
        f"Set PWP_REPO_ROOT to override."
    )

PWP_REPO = Path(os.environ.get("PWP_REPO_ROOT") or _walk_to_pwp_repo(HERE))
```

Two invariants the test must assert:

1. `REPO_ROOT` (loader) and `PWP_REPO` (operator) resolve to the same path.
2. The resolved path's `config/seo_sites.json` is the same file the v1
   adapter is being applied to.

A 3-test block (`tests/test_site_registry.py`) covers both invariants
plus the existing-fixture safety guard without needing live network or
live cron state.

## Migrate `config/seo_sites.json` into per-site `*.kpi.json`

`config/seo_sites.json` is the canonical site registry the Prismatic
engine already maintains (slug, domain, GA4 env-var names, expected
events, optional PWP overrides). It is the natural source for which
sites the PWP publish-kpi-tracker should serve. The migration pattern:

### Add two JSON Schema files

- `schemas/pwp-kpi-site.schema.json` — schema for a single per-site file
  (required: `schema_version`, `name`, `owner`, `site_slug`, `domain`, `metrics`).
- `schemas/pwp-kpi-registry.schema.json` — schema for `config/seo_sites.json`
  extended with `pwp_kpi_capability {enabled, operator, shares}`,
  `default_metric_specs` (registry-level metric templates applied to
  every site), and per-site `pwp_kpi_metric_specs` (overrides).

Both files live inside the plugin's `schemas/` directory
(`plugins/pwp/capabilities/publish_kpi_tracker/schemas/`) so they're
in Ned's lane (`plugins/`). The migration operator loads them via
the canonical anchor walk. Avoid `schemas/` at the repo root — that
path is outside Ned's lane and the push-time lane guard will reject
the commit.

When you accidentally placed schemas at `schemas/` at the repo root
and the commit is rejected at push time, the canonical recovery is the
**soft-reset + relocate + re-commit** workflow (see
`references/2026-07-pwp-lane-cleanup-soft-reset-recommit.md`):

1. `git reset --soft <last_good_commit>` — undoes both commits but
   keeps everything staged.
2. `git rm --cached config/seo_sites.json schemas/*.schema.json` —
   drops lane-violating files from the index without deleting them
   from disk.
3. `git checkout -- config/seo_sites.json` — reverts the working-tree
   changes to those files (the registry owner keeps authority).
4. Move the schema files from `schemas/` (outside lane) to
   `plugins/.../schemas/` (inside lane) via filesystem move, then
   `git add` the new locations and update `_resolve_schema_path()`.
5. `git restore --staged plugins` if the symlink itself got marked
   for deletion in step 1.
6. Re-run pytest + ad-hoc verifier (expecting the same green counts).
7. Single commit + push. The lane gate will report "0 violations".

### The migration operator

```
pwp_kpi_site_registry.py   — load + validate + iter_sites + iter_metric_specs_for_site
operator_migrate.py         — run(dry_run, registry_path, sites_dir) -> manifest
```

`operator_migrate.run(dry_run=True)` is the dry-run / preview path. The
manifest lists per-site `status` (`written` / `dry_run` / `skipped
(disabled)` / `error`), `path`, `metric_count`, `tracking_property`,
plus a top-level `validation_errors` array (always run the canonical
`kpi.validate()` over the in-memory set even on dry_run, so schema drift
surfaces before commit).

The `enabled` flag is read at two levels — `pwp_kpi_capability.enabled`
(default) and per-site `pwp_kpi_override.enabled` (override). A site
with `pwp_kpi_override.enabled: false` is skipped (the integration
test asserts this for `disabled-site`).

### Top-level `expected_data_layer_events` vs `globally_required.expected_data_layer_events`

The canonical `hd-engine.kpi.json` and `active-oahu.kpi.json` keep
`expected_data_layer_events` at the TOP level, not nested in
`globally_required`. The site-builder emits both:

- The **top level** is the public contract — operators, dashboards, and
  ad-hoc tools read this directly.
- `globally_required.expected_data_layer_events` is the redundant
  cross-check — the validator confirms both stay in sync.

A `site_builder` bug (now fixed) emitted only the nested form, which
made the per-site file look structurally valid while failing every
downstream check that read the top-level key. The rule: **always lift
`expected_data_layer_events` and `ga4_recommended_events` to the top
level** in addition to keeping them in `globally_required`.

### Idempotency is a contract, not a goal

`operator_migrate.run()` is byte-stable on re-run. A re-migration of
the same registry produces identical bytes in each `*.kpi.json` (no
header reordering, no whitespace drift, no timestamp). The integration
test asserts this explicitly. The site-builder produces deterministic
output by sorting keys consistently.

### Real-registry dry-run is the gate

Before committing the migration output, always run
`pwp-kpi-tracker migrate --dry-run` against the real
`config/seo_sites.json`. The dry-run path emits the manifest without
writing files, so a faulty registry can't pollute the production sites
directory. If the dry-run shows a site with `validation_errors: [...]`,
the registry is misconfigured and the migration should be blocked at
the cron level — the operator returns rc=1, the cron logs the error,
and the site files are left as they were.

### Example dry-run output

```json
{
  "dry_run": true,
  "registry_path": "/home/ubuntu/work/.../config/seo_sites.json",
  "sites_dir": "/home/ubuntu/work/.../plugins/pwp/capabilities/publish_kpi_tracker/sites",
  "sites": [
    {"slug": "active-oahu", "status": "dry_run", "path": ".../sites/active-oahu.kpi.json",
     "metric_count": 21, "tracking_property": "G-PRRRLMBR8Z"},
    {"slug": "disabled-site", "status": "skipped (disabled)"}
  ],
  "validation_errors": []
}
```

If `validation_errors` is non-empty, the dry-run prints the errors and
the cron should fail. If `sites_dir` already contains a file that the
registry no longer references, the migration leaves it in place (the
migration is additive-only). Manual cleanup of orphaned files is the
operator's responsibility.

## Multi-site standardization (one canonical schema, many sites)

The "standardize this workflow and KPI standard so the KPIs can be viewed
for all websites on one page and then there's a detail page for each
website or an expanded accordion type view for each website/business/row
KPI" requirement breaks into three explicit contracts.

### Contract 1: one canonical schema, one file per site

```json
{
  "schema_version": "1.0.0",
  "name": "hd-engine-funnel",
  "owner": "ned",
  "site_slug": "hd-engine",
  "domain": "humandesignengine.com",
  "tracking_property": "G-XXXXXXXXXX",
  "expected_data_layer_events": ["..."],
  "extends": null,
  "metrics": {
    "funnel_top.free_chart_generated_total": {
      "id": "free_chart_generated_total",
      "label": "Charts generated",
      "source": "ga4",
      "event": "hde_chart_generated",
      "front_of_card": true
    }
  },
  "share_targets": {...},
  "delivery_cadence": {...}
}
```

A site registers its own shape by writing a single `*.kpi.json` file. The
canonical schema validates:

- `schema_version` matches `^\d+\.\d+\.\d+$`.
- Each metric key matches `^[a-z0-9._*]+$` (dots for `collection.metric` namespacing).
- Each metric has `id`, `label`, `source`.
- `source` is in the allowlist: `ga4`, `stripe`, `telegram`, `internal`,
  `derived`, `gsc`, `mcp`, `sheets`, `ci`, `verifier`.
- When `id` is a dotted key like `funnel_top.foo`, the inner `id` must equal
  the trailing segment (`foo`). This catches drift between key and inner id.
- `format` is one of `number`, `percent`, `currency`, `duration`.
- **`front_of_card` is a per-metric boolean.** When `true`, the metric
  shows on the multi-site index. When `false` (or absent), it only
  appears on the per-site detail page. This is the *only* knob that
  controls multi-site visibility; don't invent a per-view filter language.
- `expected_data_layer_events` is an array of custom event names; the
  verifier cross-checks that every metric's `event` key is in this list.
- `site_slug` matches `^[a-z0-9][a-z0-9-]{1,63}$` (used for path
  naming in the dashboard iframe).
- `domain` is a valid hostname (kept as a string for routing, not as a
  regex constraint).

### Contract 2: `extends` for site inheritance

A new site can declare a parent:

```json
{"site_slug": "active-oahu", "extends": "hd-engine", "metrics": {...}}
```

The resolver derives the effective metric set as
`parent.metrics | site.metrics` (override-on-key-collision). The parent's
metric set is the floor; the site only has to declare *overrides and new metrics*.
This is how a PWP plugin that tracks many sites avoids duplicating the
canonical funnel across each site's KPI file.

The `extends` slug is a `*.kpi.json` filename without the extension. The
validator must resolve `active-oahu → hd-engine → (built-in defaults)` and
error if a cycle is detected.

### Contract 3: three views from one aggregation

`aggregate(runtime_values={slug: {metric_key: value}})` produces one
site-row per registered site. The three views are pure render choices over
the same aggregated dict:

- **Multi-site index** (`render_index`) — one `<section
  class="pwp-kpi-site-row">` per site with a header and a card grid (see
  "Per-site row is the smallest visual unit that closes the loop"
  above). The "KPIs for all websites on one page" surface.
- **Per-site detail** (`render_detail`) — a single page enumerating every
  metric for that site with its source, format, event, filter, formula.
  The "detail page for each website" surface.
- **Accordion** (`render_accordion`) — a single page with a `<details>`
  block per site. Default-open when the operator is doing a sweep;
  default-closed when the operator is doing a deep dive. The "expanded
  accordion type view for each website/business/row KPI" surface.

The same `aggregate()` is the source of truth for all three. The render
choices are presentation-only. All three rendering functions live in
the same file as `aggregate()` (see "Self-rendering dashboard
principle" above).

### Per-site canonical metric-id shape

The dotted-key namespace pattern (`funnel_booking.booking_click_total`)
is the canonical `id` shape. The validator accepts both:

- A flat key: `metric_id` (e.g. `booking_click_total`) — allowed for sites
  with a single collection.
- A dotted key: `<collection_id>.<metric_id>` (e.g. `funnel_booking.booking_click_total`) — preferred for multi-collection sites.

When the key is dotted, the inner `id` must equal the trailing segment. This
prevents drift between the placeholder and the inner id.

### When the user asks to register a new site

1. Pick a `site_slug` matching `^[a-z0-9][a-z0-9-]{1,63}$`.
2. Choose whether to extend a parent (most sites do via `extends`).
3. List only the *deltas* — overrides of parent metrics and new metrics.
4. Set `front_of_card: true` only on metrics that should appear on the
   multi-site index.
5. Run `validate()` against the canonical schema (this skill ships
   a 30-line `validate()` that catches: source allowlist, inner-id
   mismatch, dotted-key pattern, missing required fields).
6. Run an integration test that asserts `aggregate()` produces a
   non-zero `metric_index` for the new site.

**Procurement before authorship (re-stated as required step).** Before
any of the above, ground the JSON against the live mirror tree per
"Procurement discipline" above. The most common failure mode in this
flow is shipping a structurally-valid `kpi-collections.json` whose
metric events are never emitted on the live site — the JSON reads
correctly but the dashboard renders empty rows. The fix is to grep
the live mirror **before** writing the JSON so a wrong file is never
produced.

### Implementation checklist

When the user asks to "standardize the KPI workflow across all sites":

1. **Adopt per-site `*.kpi.json` files** with the canonical schema above.
   Keep the schema in the plugin's `schemas/` directory (e.g.
   `plugins/<plugin>/capabilities/<capability>/schemas/`) — never at
   the repo root, where the lane guard would reject the commit.
2. **Stand up the three views** as a single render function (`aggregate` +
   `render_index` + `render_detail` + `render_accordion`). Don't ship one
   without the others — operators expect all three from the same data.
   All four functions live in the same file as `aggregate()` (see
   "Self-rendering dashboard principle" above).
3. **Run `validate()` once per site** in CI. The schema-light check
   catches: bad source, missing required field, inner-id mismatch, and
   dotted-key pattern violations. Add it to the test suite, not just
   runtime.
4. **Wire the publish path** as a single function that takes a `publish_root`
   and writes `index.html`, `accordion.html`, `{slug}.html`, and the CSS
   to that directory. The PWP dashboard iframe-targets into the index;
   the per-site URL pattern `{slug}.html` is stable so external links
   don't break.
5. **Treat Stripe as the source of truth for revenue**, GA4 for funnel
   timings, and the `front_of_card` flag as the only thing that controls
   whether a metric appears on the multi-site index. That's it. Don't
   invent a per-view filter language.
6. **For cross-domain booking flows** (FareHarbor etc.), follow the
   "Sourcing rule exception" pattern above. Capture `booking_click` and
   `booking_complete` via GA4 + Measurement Protocol, and rely on the
   provider's CSV export for revenue. Don't invent a `*revenue_usd` metric
   for these sites.

### AOT-shaped example (booking site, cross-domain)

```json
{
  "schema_version": "1.0.0",
  "name": "active-oahu-funnel",
  "owner": "ned",
  "site_slug": "active-oahu",
  "domain": "activeoahutours.com",
  "extends": "hd-engine",
  "globally_required": {
    "tracking_property": "G-AOT-PLACEHOLDER",
    "expected_data_layer_events": [
      "booking_click",
      "booking_start",
      "begin_checkout",
      "purchase",
      "generate_lead"
    ],
    "ga4_recommended_events": [
      "select_item",
      "begin_checkout",
      "purchase",
      "generate_lead"
    ]
  },
  "metrics": {
    "funnel_booking.booking_click_total":    {"id": "booking_click_total",    "label": "Booking-click events", "source": "ga4", "event": "booking_click"},
    "funnel_booking.booking_complete_total":  {"id": "booking_complete_total",  "label": "Booking-complete events", "source": "ga4", "event": "booking_complete"},
    "funnel_booking.booking_conversion_rate": {"id": "booking_conversion_rate", "label": "Click → complete conversion", "source": "derived", "formula": "booking_complete_total / booking_click_total", "format": "percent"}
  },
  "share_targets": {
    "google_sheet_id_env": "AOT_KPI_SHEET_ID",
    "credential_file_env": "AOT_GOOGLE_SERVICE_ACCOUNT_JSON",
    "email_to_env":        "AOT_KPI_EMAIL_TO",
    "email_to_default":    "mbgulden@gmail.com",
    "dashboard_route":     "/pwp/kpi/"
  },
  "delivery_cadence": {
    "daily":   { "kind": "daily"   },
    "weekly":  { "kind": "weekly"  },
    "monthly": { "kind": "monthly" }
  }
}
```

Notes that belong alongside this file but not in JSON:

- "GA4 revenue requires purchase/generate_lead/booking events to be emitted
  from the booking flow or imported from FareHarbor. If booking completes
  off-site, configure cross-domain tracking and/or server-side Measurement
  Protocol/imports." (also captured in `config/seo_sites.json.booking_revenue_notes`.)
- The FareHarbor import script is presumably elsewhere — do not duplicate
  the import behavior here; the KPI file is read-only.

### Why this is a class-level pattern

The same shape works for any product that has multiple sites / multiple
funnels / multiple revenue streams under one umbrella. The three
contracts (canonical schema, extends inheritance, three views from one
aggregation) are independent of the metric *content* — a new KP for
"checkout funnel" or "newsletter funnel" or "support NPS" is just a new
site file with the same shape. The renderer, the dashboard route, and
the email cron do not change.

## Reference: session-specific detail

- `references/2026-07-ground-against-live-site-before-writing.md` — the
  procurement discipline required from this point forward: grep the
  live mirror for the GA4 ID and event names **before** writing the JSON,
  plus the verifier template that anchors structural validation against the
  live site. Captures the user's explicit workflow correction (verbatim)
  and the five concrete failure modes that this rule prevents.
- `references/2026-07-pwp-migration-operator-and-symlink-anchor.md` —
  v1→v2 schema adapter (legacy_seo_registry), the deeper
  symlink-walk anchor pattern (vs the cron-launcher variant), the
  migration operator safety guard (`--dry-run` /
  `--skip-if-exists` / `--force`), the verifier backup/restore
  pattern around destructive `--force` checks, the per-site-row
  multi-site dashboard layout, and the path-portability commit gate.
- `references/2026-07-pwp-lane-cleanup-soft-reset-recommit.md` — the
  seven-step recovery workflow when local commits already exist
  but the push-time lane gate rejects out-of-lane files. Covers the
  soft-reset, `git rm --cached`, schema relocation, symlink-target
  staging, and the "0 violations" push confirmation.
- `references/2026-07-runtime-values-pipeline.md` — the runtime
  values pipeline (`runtime_values.py`): per-source adapter
  dispatch with live/snapshot two-mode contract, derived metric
  computation with sandboxed eval, the `<slug>.runtime.json`
  canonical snapshot, and the `build_dashboard(None)` vs
  `build_dashboard({})` pitfall that causes the dashboard to render
  `—` forever when the CLI converts a missing path to `{}`.
- `references/2026-07-pwp-unified-cron-orchestrator.md` — the
  unified cron orchestrator (`cron_orchestrator.py`), env-var-only
  GA4 resolution (GAP-#5), the `Path`-vs-`str` coercion at function
  entry pattern, and the `delivery_cadence` dict/list/string shape
  contract.
- `references/2026-07-pwp-provision-site-phase1.md` — the
  provision_site capability (Phase 1 Cloudflare-first MVP): DNS TXT
  domain verification, sites.json appendix for write-restricted
  registry lanes, the orchestrator/step-function pattern with
  resume + status persistence, and the `types.py` extraction
  pattern that breaks the orchestrator↔steps circular import.
- `references/2026-07-pwp-provision-site-phase2.md` — the
  Phase 2 build atop phase 1: real GSC verification via DNS TXT
  through the Cloudflare API, programmatic GA4 property + web
  stream creation and GTM container creation via service-account
  JWT auth (~30 lines of `cryptography`, no PyJWT), `STEP_CATEGORIES`
  for blocking-vs-soft step failures (so missing GOOGLE_SA_JSON
  doesn't abort the run), and the `prior_outputs` complete-vs-failed
  regression fix where downstream steps need to see upstream
  *success* output (cloudflare_zone.zone_id) to make their own
  calls. Includes the EZShare.systems live-test transcript.
- `references/2026-07-pwp-provision-site-phase2.md`'s pitfalls:
  `tests that write <slug>.runtime.json and unlink it in finally
  silently destroy production data — back up + restore, never
  unconditional unlink`, and `getattr(<step_module>,
  "STEP_CATEGORIES", {})` is the canonical orchestrator
  hook for the soft-failure gate.

## Orchestrator patterns: prior_outputs, soft-failure, test hygiene

Three durable orchestration patterns emerged from Phase 2 of the
`provision_site` capability work
(`references/2026-07-pwp-provision-site-phase2.md`). They apply to
any orchestrator that walks a sequence of steps with state
persistence + resume semantics, not just `provision_site`.

### Step category: blocking vs soft

Use `STEP_CATEGORIES` (a module-level dict) to declare whether a
step's failure stops the orchestrator. Use **soft** for steps
gated on credentials or infrastructure the owner configures
LATER (e.g. shared Google service account for GA4/GTM). Use
**blocking** for steps required for forward progress (DNS
verification, canonical registry write, KPI bootstrap). Never
mark a step soft just because it's flaky — the flag is for
credentialed configuration gaps, not transient errors.

The orchestrator's wrapper reads `getattr(step_module,
"STEP_CATEGORIES", {}).get(sname, "blocking")`. On soft failure:
set `output["_soft_failure"] = True` and continue. On blocking
failure: set `overall_status = "failed"` and return.

### `prior_outputs` flows every non-empty step output

The `prior_outputs` dict is the inter-step data bus. The
orchestrator must populate it with **both** `complete` AND
`failed` prior step outputs (never filter by status). A step
that wants "did upstream succeed?" checks the output's
*content*, not the orchestrator's filter. A common bug:
`step_<downstream>` reads `prior["<upstream>"]["zone_id"]` and
the orchestrator only forwards failed outputs, so downstream
loses access to upstream's success state. Fix: include both
statuses in the filter.

### Smoke-test fixtures must not destroy production data

Tests that write a sentinel to a shared production file (e.g.
`<sites_dir>/<slug>.runtime.json`) and `unlink()` it in `finally`
silently destroy production data when a real file already exists.
The fix pattern: backup the original content before writing, and
restore in `finally` (only `unlink()` if `backup is None`). A
failing assertion still restores the file because the restore
lives in `finally`, not `try`-pass.

## Dashboard modal flow (Phase 4.2)

When a dashboard needs an interactive UI (a "Configure website KPIs"
modal, an "Edit funnel" inline form, a per-site action button) without
giving up the static-HTML-deployment model, the shape is a self-contained
HTML+CSS+JS fragment injected before `</body>` of `render_index()`. The
modal is HTML-first, vanilla JS, no framework — every dashboard host can
ship it.

The pattern:

1. **One module: `funnel_form.py`** — owns `render_modal_html()`,
   `render_modal_css()`, `render_button_wiring_js()`,
   `site_row_buttons()`, and `load_prior_submission()`. Each is a
   pure function over its inputs (no global state except the
   `SUBMISSION_LOG_DIR` pointer, which is `monkeypatch.setattr`-able in
   tests).
2. **`render_index(agg, *, csrf_token=None)`** — lazy-imports
   `funnel_form` inside a try/except guard so a missing modal
   doesn't break the dashboard, and so the existing byte-identical
   determinism test still passes (pass `csrf_token="test-stable"`).
3. **`site_row_buttons(site)`** — emits one button per site row;
   switches label and adds a refinement button when a prior
   submission log exists at
   `<SUBMISSION_LOG_DIR>/<site.slug>.json`. Tests use
   `monkeypatch.setattr` to point at a temp dir.
4. **Two-layer safety escape**: the form POSTs to `/pwp/api/funnel-config`.
   If the host has no backend, the JS detects the 404 and falls back to
   downloading the JSON payload as a file the user hands to the
   agent. Static-hosting-friendly by default; backend is a progressive
   enhancement.
5. **CSRF nonce**: per-render via `secrets.token_urlsafe(16)`. Tests
   pass a stable token via the keyword arg; live calls let the helper
   generate one. This is the same fix as the "per-render random
   content" pitfall above.

If the dashboard ever needs a second modal (e.g. "Run registry
validation now", "Mark site stale"), make a sibling module
`announcements.py` or `actions.py` and inject the same way. The
modular approach keeps `render_index()` unchanged for callers who only
care about the data + card grid.

Reference implementation: `funnel_form.py` next to `publish_kpi_tracker.py`
in the `publish_kpi_tracker` capability.

## Provision-site capability: site onboarding end-to-end

The KPI dashboard is only useful when there are sites to track.
The **provision_site capability** is the sibling that takes a
domain + owner email and walks the user through every step needed
to make the site trackable. It lives under the same PWP plugin
as the KPI tracker (`plugins/pwp/capabilities/provision_site/`)
because the **registry**, **migrate operator**, and **KPI
file shape** are shared between them.

### Phase 1 scope: Cloudflare-first MVP

A real onboarding flow has many steps (Cloudflare, GA4, GTM, GSC,
Stripe, emdash site templates, deploy, GitHub backup, AI agents).
Phase 1 covers the smallest end-to-end flow that proves the wiring:

1. **Domain verification** — DNS TXT challenge at `_pwp-verify.<domain>`.
   The provisioner issues a `pwp-verify-<16 hex chars>` token; the owner
   creates the TXT record; a second run verifies it. The same
   mechanism Google uses for `sc-domain:` verification.

2. **Cloudflare zone** — look up an existing zone or create a new one
   via the API. Uses a shared `CF_API_TOKEN` env var (multi-tenant
   auth is a later phase).

3. **GSC verify** — placeholder for Phase 2. Skipped when no service
   account is available. The DNS TXT for GSC is added at the apex,
   so the existing zone setup is enough.

4. **Register in registry** — writes a `<publish_root>/sites.json`
   **appendix** rather than touching `config/seo_sites.json` directly.
   The latter is in a different lane (Ned can't write it). The
   appendix is merged by the registry loader in a later phase.

5. **Migrate** — triggers `operator_migrate.run()` with a minimal
   v2-shaped registry built from the appendix. This is the same
   migrate operator the KPI dashboard uses; no new code path.

### File layout

```text
plugins/pwp/capabilities/provision_site/
├── __init__.py                  public API: CloudflareClient, errors, Zone, DNSRecord
├── cloudflare_client.py         thin CF API v4 wrapper (zone + DNS ops)
├── domain_verifier.py           DNS TXT challenge (DoH lookup, no creds needed)
├── orchestrator.py              step ordering + resume + state persistence
├── types.py                     StepResult / ProvisionRun dataclasses
├── operator_cli.py              provision / provision-status / provision-list
├── steps/
│   ├── __init__.py              step_<name>(domain, owner, run, publish_root) → StepResult
│   ├── register_in_registry.py  writes sites.json appendix
│   └── migrate.py               calls operator_migrate.run() with minimal registry
└── tests/test_provision_site.py
```

Wired into the existing `operator_cli.py` via `attach_subparser(sub)`:

```python
# publish_kpi_tracker/operator_cli.py
from plugins.pwp.capabilities.provision_site import operator_cli as prov_cli
prov_cli.attach_subparser(sub)
```

The provisioner lives next to the KPI tracker because:
- They share `config/seo_sites.json` (eventually)
- The migrate operator is the same one
- The CLI tree is unified (`pwp-kpi-tracker provision ...`)

### Orchestrator pattern with resume + state persistence

The orchestrator's contract:

```python
def run(*, domain, owner, publish_root=None, resume=True,
        step_filter=None) -> ProvisionRun:
    # 1. Load prior state from <publish_root>/<domain>.json if resume=True
    # 2. For each step in STEP_NAMES (in order):
    #    - if already complete in prior state, skip
    #    - if step_filter is set and step not in it, skip
    #    - call step_<name>(domain, owner, run, publish_root)
    #    - append StepResult to run.steps
    #    - persist state to <publish_root>/<domain>.json
    #    - if status == "failed", mark overall_status=failed and return
    # 3. Mark overall_status=complete
```

Three properties make this safe to expose as a CLI:

1. **State after every step.** The UI can poll `<publish_root>/<domain>.json`
   to render progress. A long-running step (real DNS propagation)
   doesn't block the user.

2. **Resume by default.** A re-run skips completed steps. If the owner
   forgot to add the TXT record and the run failed at `verify_domain`,
   they add it and re-run; `verify_domain` succeeds, `cloudflare_zone`
   runs. No restart-from-zero.

3. **Step filter for debugging.** `--step-filter=verify_domain,migrate_kpi`
   runs only the named steps. Used to re-run a failed step in isolation
   without re-touching the others.

### Step functions never raise

Each `step_<name>` returns a `StepResult` and **never raises**.
The orchestrator wraps in try/except as a defensive layer, but the
step's contract is "fail = `StepResult(status="failed", error="...")`."
A raised exception inside a step would leave the orchestrator's state
file half-written and the resume logic unsure whether to retry.

### `types.py` extraction to break circular import

When wiring the orchestrator + steps, the natural shape is:

```python
# orchestrator.py
from . import steps as step_module
@dataclass
class StepResult: ...       # referenced by step_<name>() return types
class ProvisionRun: ...    # referenced by orchestrator state

# steps/__init__.py
from ..orchestrator import StepResult  # <-- circular!
```

Python handles the cycle but `StepResult` is `None` at import time
inside `steps/__init__.py`, breaking the dataclass. Fix:

```python
# types.py  (NEW — owned by no other module)
@dataclass
class StepResult: ...
@dataclass
class ProvisionRun: ...

# orchestrator.py
from .types import ProvisionRun, StepResult  # both directions resolve

# steps/__init__.py
from ..types import StepResult  # also resolves cleanly
```

The rule: **shared dataclasses live in `types.py`.** Orchestrator and
steps import from `types.py`. Never import from each other (the only
orchestrator → step edge is `step_module.step_<name>(...)` via string
lookup, which works fine because the import is lazy).

### sites.json appendix: a write-restricted registry lane

`config/seo_sites.json` is in another lane (Ned can't write it).
The provisioner writes to a **separate file**:

```jsonc
// <publish_root>/sites.json
{
  "<domain>": {
    "slug": "<derived>",
    "name": "<derived>",
    "owner": "<owner-email>",
    "domain": "<domain>",
    "ga4_measurement_env": "<SLUG>_GA4_MEASUREMENT_ID",
    "expected_data_layer_events": [],
    "pwp_kpi_override": {"enabled": true},
    "registered_at": "<iso8601>"
  }
}
```

The migrate step reads this appendix and synthesizes a minimal v2
registry. Phase 2 wires `load_registry()` to merge the appendix
automatically. Until then, the migration is hand-wired:

```python
# steps/migrate.py
appendix = Path(os.environ.get("PWP_PROVISIONING_ROOT", "/tmp/pwp-provisioning")) / "sites.json"
minimal_registry = _build_minimal_registry(slug, appendix)
# ... call operator_migrate.run(registry_path=tmp_registry, ...) ...
```

The appendix file is the **only** place the provisioner writes outside
its own package — that's the seam that respects lane discipline.

### Live verification pattern (Phase 1 smoke)

Without credentials, the smoke flow exercises the failure path:

```bash
$ pwp-kpi-tracker provision --domain test-acme.com --owner founder@acme.com \
    --publish-root /tmp/pwp-provision-smoke

{
  "overall_status": "failed",
  "steps": [{
    "name": "verify_domain",
    "status": "failed",
    "error": "domain verification pending. Create a DNS TXT record
              at _pwp-verify.test-acme.com with value pwp-verify-abc...,
              then re-run provisioning. Observed TXT values: []",
    "output": {"challenge_token": "pwp-verify-abc..."}
  }]
}
```

After the owner creates the TXT record, re-running the same command
skips `verify_domain` (already complete in prior state) and runs
`cloudflare_zone`. The orchestrator's resume is the user-visible
"this is going to take a while, just re-run when you're done" UX.

### Why this is a class-level pattern

Every multi-tenant platform that adds sites/services/endpoints has
the same shape:

1. Owner proves they own the resource (DNS / email / OAuth).
2. The platform calls a remote API to provision.
3. State persists across partial failures.
4. Resume semantics make long flows feel async without async.

The provision_site capability is one instance; the same pattern
applies to new Stripe products, new GSC sites, new Cloudflare Pages
projects, etc. Each gets its own `step_<name>` module and the
orchestrator grows a new entry in `STEP_NAMES`.