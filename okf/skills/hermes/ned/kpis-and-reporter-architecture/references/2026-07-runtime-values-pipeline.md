# 2026-07-29 — Runtime values pipeline: closing the `—` placeholder gap

Concrete session artifacts for the runtime values pipeline added to
`plugins/pwp/capabilities/publish_kpi_tracker/runtime_values.py`
and wired into `build_dashboard()` + `operator_cli.py`.

## The problem the pipeline solves

The multi-site dashboard rendered `—` for every card on every site
because `aggregate(runtime_values={})` was the only call path —
nothing populated the runtime_values dict. Operators couldn't tell
whether the cron was broken, the GA4 ID was wrong, or the site had
simply not reported. The pipeline fixes this by providing a
default-mode that pulls values from per-site snapshot files (the
**demo path**) or live API calls (the **production path** when
credentials are configured).

## What landed in `runtime_values.py`

The file (~500 lines) implements:

- `default_sites_dir()` — public accessor for the canonical
  `<PWP_REPO>/plugins/pwp/.../sites/` path. Anchored on
  `config/seo_sites.json` via `_walk_to_pwp_repo()` so it works
  through both the `plugins/` symlink and the
  `prismatic/shipped_plugins/` target. PWP_REPO_ROOT env var
  overrides.
- `_walk_to_pwp_repo()` — the symlink-safe anchor walker (vs the
  parent-N pitfall).
- `ADAPTERS` dict — source → adapter function dispatch table.
  Six adapters: `_query_ga4`, `_query_stripe`, `_query_gsc`,
  `_query_telegram`, `_query_internal`, `_query_verifier`.
- `_compute_derived(metric_key, metric_spec, runtime_values_for_site)`
  — derived-metric arithmetic with bare-id substitution, regex
  gate, and sandboxed `eval()`.
- `_load_snapshot(sites_dir, slug)` — reads
  `<slug>.runtime.json` and coerces values to float.
- `RuntimeValuesBuilder` class with `build_site(slug, sites_dir)`
  and `build_all(sites_dir)`. Per-site flow:
  1. Load canonical snapshot.
  2. Walk non-derived metrics; try live adapter, fall back to
     snapshot.
  3. Compute derived metrics LAST.
  4. Filter out `None`.
- `build_runtime_values(*, sites_dir=None, env=None)` —
  convenience wrapper around `RuntimeValuesBuilder`.

## The `None`-vs-`{}` pitfall (the bug that surfaced the wiring)

`build_dashboard` in `__init__.py` has:

```python
if runtime_values is None:
    from . import runtime_values as rv
    runtime_values = rv.build_runtime_values(sites_dir=sites_dir)
```

The CLI's `cmd_build_dashboard` originally did:

```python
runtime = kpi.read_runtime_values(args.runtime_values_path)
manifest = kpi.build_dashboard(runtime_values=runtime, ...)
```

`kpi.read_runtime_values(None)` returns `{}` (not `None`). The
empty dict passes through to `build_dashboard`, where the `is None`
guard fails — the pipeline never runs, and the dashboard renders
all `—` placeholders forever. The fix was one line:

```python
runtime = None  # default; build_dashboard will trigger the pipeline
if args.runtime_values_path:
    runtime = kpi.read_runtime_values(args.runtime_values_path)
```

This is a class-level invariant for any "use default behavior"
orchestrator pattern: the empty-dict sentinel and the missing-input
sentinel are different. `None` means "auto-discover"; `{}` means
"explicit empty override."

## The percent-format math bug (the "simple math" that slipped through)

The first round-trip audit of the dashboard after pipeline integration
showed `Click → complete conversion: 0.06%` when the snapshot
supplied `0.0638`. The expected output was `6.38%`.

Root cause: `_format_value(fmt="percent")` did NOT multiply by 100:

```python
# WRONG:
if fmt == "percent":
    return f"{float(value):.2f}%"
# 0.0638 → "0.06%"

# CORRECT:
if fmt == "percent":
    return f"{float(value) * 100:.2f}%"
# 0.0638 → "6.38%"
```

The **percent-format contract** (see SKILL.md):
- Storage: fraction (`0 ≤ v ≤ 1`).
- Display: multiplied by 100, 2dp + `%`.

The canonical `active-oahu.kpi.json` formula
`booking_complete / booking_click` produces a fraction. The
renderer multiplies by 100. The data shape stores the raw fraction;
the renderer applies the multiplication. **Self-rendering preserved**
because the formatter is the single source of truth.

The audit also caught **a test that asserted the wrong value**:

```python
# WRONG (passed for the wrong reason):
assert _format_value(0.1234, "percent") == "0.12%"

# CORRECT:
assert _format_value(0.1234, "percent") == "12.34%"
```

A regression test was added:

```python
def test_format_value_percent_is_audit_safe():
    raw = 0.0638
    rendered = _format_value(raw, "percent")
    assert "%" in rendered
    assert "0.06%" not in rendered, f"old bug regressed: {rendered!r}"
    numeric = float(rendered.rstrip("%"))
    assert abs(numeric - raw * 100) < 0.01
```

The round-trip assertion (`rendered → parse → /100 → raw`) catches
the bug in either direction. If a future change accidentally
introduces the off-by-100x bug, this test fails immediately.

**Lesson:** when the user finds a "simple" math bug, the surrounding
tests may also assert the wrong value. Audit test assertions, not
just the production code. Tests that pass for the wrong reason are
worse than no test at all.

## Sibling wiring bugs caught during the audit

Three sibling bugs surfaced during the percent-format audit, all
related to the runtime-values wiring:

1. **`cmd_list_sites` was wired to `build_all_site_summaries()` with
   no `runtime_values` argument**, so `headline_value` was always
   `None` even when snapshots had values for the headline metric.
   Fixed by running the pipeline explicitly in `cmd_list_sites`
   when the caller didn't pass `--runtime-values-path` or
   `--no-runtime-values`. New `--no-runtime-values` flag forces
   `headline_value=None` for callers who want raw output.

2. **`_resolve_schema_path()` in `pwp_kpi_site_registry.py` still
   pointed at `<PWP_REPO>/schemas/pwp-kpi-registry.schema.json`**
   (which doesn't exist after the lane cleanup). Fixed to point at
   the in-plugin location `plugins/.../publish_kpi_tracker/schemas/`.

3. **`cmd_build_dashboard` originally converted `None` to `{}`** —
   the exact pitfall above.

The lesson: **when a bug is found in a wiring layer, audit every
caller of that layer.** `build_dashboard`'s "treat None as auto"
contract was violated by the CLI's "default to empty dict"
pattern; both `cmd_build_dashboard` and `cmd_list_sites` had to be
audited together.

## Bare-id vs metric_key contract (the merge-mode pitfall)

Canonical `*.kpi.json` files key metrics by **dotted names**
(`funnel_booking.booking_click`); the migration operator's
registry-derived `default_metric_specs` key them by **bare ids**
(`booking_click`). When merging registry metrics into a curated
file, comparing full keys creates phantom duplicates:

```python
# WRONG (full-key comparison — creates duplicates):
for mid, spec in registry_metrics.items():
    if mid not in existing_metrics:
        existing_metrics[mid] = spec  # adds "booking_click"
        # But the file already has "funnel_booking.booking_click"!

# CORRECT (bare-id comparison — no duplicates):
def _bare_id(metric_key: str) -> str:
    return metric_key.rsplit(".", 1)[-1]

existing_bare_ids = {_bare_id(k) for k in existing_metrics.keys()}
for mid, spec in registry_metrics.items():
    bare = _bare_id(mid)
    if bare in existing_bare_ids:
        continue  # curated file already has a metric with this bare id
    existing_metrics[mid] = spec
    existing_bare_ids.add(bare)
```

The `_merge_into_existing()` function in `operator_migrate.py`
encodes this contract. The integration test asserts both
directions:

```python
def test_run_merge_does_not_overwrite_curated_metric():
    existing = {"metrics": {"funnel_booking.booking_click": {...}}}
    registry_coll = {"metrics": {"funnel_booking.booking_click": {...},
                                  "funnel_booking.new_event": {...}}}
    merged, added = _merge_into_existing(target, registry_coll)
    assert merged["metrics"]["funnel_booking.booking_click"]["label"] == "Curated Label"
    assert "funnel_booking.new_event" in merged["metrics"]
    assert added == ["funnel_booking.new_event"]
```

Three rules for metric key comparison:

1. **Storage is dotted** — canonical `*.kpi.json` uses
   `<collection>.<metric>` namespacing.
2. **Default metric specs use bare ids** — registry's
   `default_metric_specs` keys are event names without prefix.
3. **Comparison normalizes to bare id** — when comparing metric
   keys across shapes, strip the dotted prefix to detect "same
   metric, different naming".

## Subprocess verifier pitfall: `SITES_DIR` mutation doesn't propagate

When the ad-hoc verifier (`/tmp/hermes-verify-runtime-values.py`)
runs tests via `subprocess.run([python3, "-c", code])`, the child
process mutates `kpi.SITES_DIR = d`, but the mutation lives in the
child process only — the orchestrating Python (or a separate test
process) doesn't see it. `resolve_collection()` reads from the
inner module's `SITES_DIR`, which is a separate module attribute
from the `__init__.py` re-export.

The fix: patch BOTH names:

```python
import plugins.pwp.capabilities.publish_kpi_tracker as kpi
import plugins.pwp.capabilities.publish_kpi_tracker.publish_kpi_tracker as inner

# Patch the __init__.py re-export AND the inner module.
kpi.SITES_DIR = d
inner.SITES_DIR = d
```

The pytest version uses `monkeypatch.setattr(inner, "SITES_DIR", d)`
which handles this correctly because `monkeypatch` patches the
attribute on the actual module object. Inline `kpi.SITES_DIR = d`
only patches the re-export in `__init__.py` because Python copies
the value at import time.

When the same `SITES_DIR` is referenced from multiple places in a
package, audit every import statement for `from .module import
SITES_DIR` and patch each module independently.

## Snapshot files and the demo path

Three kinds of files live at `<sites_dir>/`:

- `<slug>.runtime.json` — canonical `{metric_key: value}` override.
  Wins over every adapter. The demo path for new sites is "drop
  this file next to `<slug>.kpi.json` and call `build-dashboard`."
- `<slug>.internal.json` — values for `source: "internal"`
  metrics. Read by `_query_internal`.
- `<slug>.verifier.json` — values for `source: "verifier"`
  metrics. Read by `_query_verifier`.

`operator_cli snapshot` writes the canonical snapshot template:

```bash
pwp-kpi-tracker snapshot --sites-dir ./sites
# -> writes ./sites/<slug>.runtime.json with null placeholders
#    for every metric_key in the resolved collection
```

Existing files are NOT overwritten unless `--force` is passed.
The operator fills the nulls manually or via a live-mode adapter.

## Live adapter two-stage guard

Each live adapter is gated on credentials AND on package presence:

```python
def _query_ga4(metric_key, metric_spec, site_flat, *, env):
    creds = env.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds:
        return None
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
    except ImportError:
        return None
    # ... real GA4 Data API call ...
```

Missing credentials AND missing package both return `None`. The
pipeline never raises — it gracefully degrades to snapshot values.
The two stages are important:

1. Without this guard, `import google.analytics.data_v1beta` at
   module load time would crash on systems without the package
   installed (e.g. CI without the analytics SDK).
2. The pipeline can run on a developer laptop with only snapshots,
   with no live integration required. That's the demo path.

## Derived metric safety pattern

`_compute_derived` evaluates formulas like
`purchase_total / booking_click`:

```python
def _compute_derived(metric_key, metric_spec, runtime_values_for_site):
    formula = metric_spec.get("formula")
    if not formula:
        return None
    if not _SAFE_EXPR_RE.match(formula):
        return None
    # Build bare-id -> value map.
    by_bare_id = {}
    for k, v in runtime_values_for_site.items():
        bare = k.split(".")[-1]
        if bare:
            by_bare_id[bare] = v
    # Substitute longest-first to avoid click swallowing booking_click.
    keys = sorted(by_bare_id.keys(), key=len, reverse=True)
    expr = formula
    for bare in keys:
        expr = re.sub(rf"\b{re.escape(bare)}\b", repr(by_bare_id[bare]), expr)
    # Reject any remaining identifier (NameError risk).
    if re.search(r"[a-zA-Z_][a-zA-Z0-9_.]*", expr):
        return None
    try:
        return float(eval(expr, {"__builtins__": {}}, {}))
    except Exception:
        return None
```

Three security layers:

1. **Pre-substitution regex gate** — formula must match
   `^[a-zA-Z0-9_./ ()*+%-]+$` before substitution. Rejects anything
   with operators not in the allowlist.
2. **Post-substitution identifier check** — after substituting bare
   ids with literals, scan for remaining identifier-shaped tokens.
   If any remain, the formula referenced an unknown metric.
3. **Sandboxed `eval()`** — runs with `{"__builtins__": {}}` so
   `__import__` / `open` / etc. cannot resolve even if they sneak
   past the regex.

The pre-substitution regex check MUST happen on the raw formula
string with identifier tokens — the post-substitution expression
contains numeric literals, so the same regex would always pass
on the substituted form. Two checks, two stages, both required.

## Test surface

`tests/test_runtime_values.py` added 25 tests. Key coverage:

- `default_sites_dir()` resolves correctly with and without
  `PWP_REPO_ROOT` env override.
- Snapshot reads win over adapter when both have a value.
- Sidecar reads fill values when the canonical snapshot doesn't.
- Unknown source silently skipped (no exception, no entry).
- Derived metric arithmetic: `purchase_total / booking_click`
  evaluates correctly.
- Derived metric longest-first substitution: `booking_click /
  click` doesn't accidentally substitute `click` first.
- Derived metric rejects builtin refs (`__import__("os")` → `None`).
- `build_all` walks every registered site deterministically
  (`out_a == out_b`).
- `snapshot` subcommand writes null templates with no existing
  files.
- `snapshot --force` overwrites; without it, existing files
  preserved.
- Every live adapter returns `None` without credentials.
- `internal` adapter reads from `<slug>.internal.json` sidecar.

Tests use the canonical fixture
`tests/fixtures/hd-engine.kpi.json` (5 metrics covering ga4,
stripe, derived, verifier sources) and monkeypatch
`SITES_DIR` to point at a temp dir so the per-test kpi.json
mutations don't pollute the canonical plugin tree.

## Final tallies

- Canonical pytest: **96/96 PASS** (was 64; +32 new tests:
  25 for runtime values, 4 for percent format + list-sites
  headline pipeline, 3 for `migrate --merge` mode).
- Ad-hoc verifier: **12/12 PASS**
  (`/tmp/hermes-verify-runtime-values.py`) after the
  `SITES_DIR`-propagation fix.
- Live evidence: dashboard renders 7 real numbers (47 booking
  clicks, 3 bookings completed, 12 leads, **6.38%** conversion on
  AOT; 184 charts, 7 sanctuary, 21 report purchases on HDE). The
  6.38% is correctly formatted from 0.0638 via
  `_format_value(0.0638, "percent")`. `cmd_list_sites` populates
  `headline_value` (47.0 / 184.0).

## What this closes vs what's still open

**Closes:**

- Dashboard shows `—` placeholder forever → dashboard shows real
  numbers from snapshots or live API calls.
- Operator can't tell whether cron is broken → empty card grids
  surface the "no values yet" condition explicitly.
- New sites can't be onboarded without credentials → snapshot
  bootstrap makes it one JSON file away.
- Percent metrics displayed correctly (6.38% not 0.06%).
- `cmd_list_sites` headline value populated from pipeline.
- Merge mode adds registry metrics to existing curated files
  without clobbering them.

**Still open (next gap from the same analysis):**

- Cron unification: a single Prismatic Engine cron entry that
  iterates registered sites and calls the launcher per-site with
  the right env vars.
- Move `cron_launcher.py` in-tree (optional consolidation).

Both are smaller scope than the pipeline and ready to tackle when
the user signals.