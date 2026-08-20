# 2026-07-29 — PWP publish-kpi-tracker migration operator + symlink anchor walk + per-site rows

Concrete session artifacts for three patterns added to the SKILL.md body
alongside the existing `parents[N]` cron-launcher fix.

## v1 → v2 schema adapter (legacy_seo_registry)

The real `config/seo_sites.json` is v1 shape (a flat list of sites with
`gsc_property`, `sitemap_url`, `site_dir_candidates`,
`expected_data_layer_events`, and direct GA4 fields). The canonical
`schemas/pwp-kpi-registry.schema.json` is v2 (requires
`pwp_kpi_capability`, `default_metric_specs`, per-site
`pwp_kpi_override` / `pwp_kpi_metric_specs`).

The adapter at `plugins/pwp/capabilities/publish_kpi_tracker/legacy_seo_registry.py`:

- detects v1 by the absence of `pwp_kpi_capability` + the presence of any
  legacy field (`gsc_property`, `expected_data_layer_events`,
  `ga4_measurement_env`, etc.);
- maps v1 fields onto v2 with explicit defaults:
  - `pwp_kpi_capability = {enabled: true, operator: "ned", shares: {…defaults…}}`
  - `default_metric_specs` built from the union of `expected_data_layer_events`
    and `expected_ga4_recommended_events` across all sites, one metric per
    event with `source: "ga4"`, `format: "number"`,
    `front_of_card: false`.
- preserves every v1 site field verbatim (v2 schema's
  `additionalProperties: true` on the site shape allows this);
- sets `pwp_kpi_override.enabled = true` per site by default;
- is **idempotent over v2**: passing a v2 registry returns it with
  defaults filled in.

`pwp_kpi_site_registry.load_registry()` now does:

```python
raw = json.loads(p.read_text(encoding="utf-8"))
from .legacy_seo_registry import adapt_v1_to_v2
return adapt_v1_to_v2(raw)
```

Every downstream consumer (operator, dashboard builder, tests) only sees v2.

15 tests in `tests/test_legacy_seo_registry.py` cover: detection,
v1→v2 adaptation, v2 passthrough, integration with `load_registry()`
(via a tmp v1 file), and integration with the real
`config/seo_sites.json` on disk.

## Symlink-walk anchor pattern (`_walk_to_pwp_repo`)

`prismatic-pwp-ubersuggest-auth` has `plugins/` as a git symlink to
`prismatic/shipped_plugins/`. The two paths give different `parents[N]`
for the same file. The deeper variant of the `parents[N]` bug already
documented at `references/2026-07-python-312-isoformat-and-here-parents-pitfalls.md`
is: `__file__` reports the **symlink path** when modules load through
the symlink, even after `Path(__file__).resolve()` is called.

`HERE.parents[5]` of
`/home/ubuntu/work/prismatic-pwp-ubersuggest-auth/plugins/pwp/capabilities/publish_kpi_tracker/operator_migrate.py`
is `/home/ubuntu/work` (one level too high). The same file resolved
through the symlink target gives the real repo root.

**Fix** (applied to both `pwp_kpi_site_registry.py` and
`operator_migrate.py`):

```python
def _walk_to_pwp_repo(here: Path) -> Path:
    cur = here
    for _ in range(10):
        if (cur / "config" / "seo_sites.json").is_file():
            return cur
        cur = cur.parent
    raise FileNotFoundError(
        f"…no config/seo_sites.json within 10 parent levels. "
        f"Set PWP_REPO_ROOT to override."
    )

REPO_ROOT = Path(os.environ.get("PWP_REPO_ROOT") or _walk_to_pwp_repo())
```

Two invariants to test:

1. The loader's `REPO_ROOT` and the operator's `PWP_REPO` resolve to
   the same path through the symlink-vs-target ambiguity.
2. The resolved path's `config/seo_sites.json` is the file the v1
   adapter is being applied to.

## Migration operator safety guard (`--dry-run`, `--skip-if-exists`, `--force`)

The live `config/seo_sites.json` carries much less metric curation than
the existing canonical `active-oahu.kpi.json` (a hand-curated 3630-byte
file with GSC queries, conversion-rate derivation, and FareHarbor-import
metrics). Running `migrate` without a safety guard would clobber the
curated file with a 5-event default-metric placeholder.

The fix is the class-level contract: a write-side migration operator's
default is **skip-if-exists**, with `--force` as the explicit opt-in
to overwrite. Manifest status values must distinguish:

- `"written"` — file did not exist (or `--force` was set) and was created.
- `"skipped (exists)"` — file existed, no `--force`, bytes unchanged.
- `"skipped (disabled)"` — `pwp_kpi_override.enabled: false`.
- `"error"` — building the collection raised.

This four-state contract lets a cron-driven migrate run idempotently.
The ad-hoc verifier wraps `--force` destructive tests in a backup /
restore so the test itself is idempotent — see the next section.

## Ad-hoc verifier with backup/restore (12-check contract)

`/tmp/hermes-verify-pwp-kpi-live-registry.py` runs 12 checks against
the real `config/seo_sites.json` and the curated
`active-oahu.kpi.json`. The destructive checks (forcing overwrite via
`--force`) are wrapped in `try`/`finally` with `shutil.copy2()` for
backup and restore:

```python
target = REPO / ".../sites/active-oahu.kpi.json"
backup = target.with_suffix(".kpi.json.hermes-verify-backup")
shutil.copy2(target, backup)
try:
    # ... destructive ops (--force overwrite, byte-diff) ...
finally:
    shutil.copy2(backup, target)
    backup.unlink()
```

This makes `--force` testable without leaving the curated file in a
different state. The same pattern generalizes to any destructive
verifier check against a curated production file. See
`ad-hoc-verification-contracts` for the parent skill.

## Per-site rows on the multi-site dashboard

The user has explicitly directed that the multi-site dashboard render
**per-site rows** (the smallest visual unit that closes the loop):

> "per-site row is the smallest, but it's what closes the loop
> visually. It would also fix the multi-site row that currently shows
> Metrics: N — front-of-card: ... with empty cards (no runtime_values)"

The fix: `render_index(agg)` now produces one
`<section class="pwp-kpi-site-row">` per registered site, each
containing a header (name, slug, domain, owner, metric_count, extends,
detail link) and an inline card grid (one card per `front_of_card`
metric, label + value with `—` placeholder for missing values). Every
site that has registered any `front_of_card` metric renders a card
grid even when the cron has not yet populated values; every site that
has not registered any shows the "No front-of-card metrics registered"
note.

The 6-line `_format_value(value, fmt)` helper, defined alongside
`aggregate()` and `render_*()` in `publish_kpi_tracker.py`, renders
runtime values deterministically:

- `None` / missing → `"—"` (placeholder, never silent collapse)
- `percent` → `"12.34%"`
- `currency` → `"$1,234.50"`
- `duration` → `"45s"`
- `number` → `"1,234"` for integer-valued floats, `"1.23"` otherwise

The same helper feeds both `render_index()` and `render_accordion()`
so the empty-card collapse ("None") is gone from every surface in one
fix. CSS for the new layout (`.pwp-kpi-site-row`, `.pwp-kpi-card`,
`.pwp-kpi-card-grid`, `.pwp-kpi-card-label`, `.pwp-kpi-card-value`)
lives in `templates/pwp-publish-kpi.css` and is read at
`build_dashboard()` time.

## Self-rendering dashboard principle

The user has explicitly directed that the rendering function MUST live
next to the data shape, NOT in `__init__.py` separate from the data:

> "the rendering function should live next to the data shape (e.g., in
> `publish_kpi_tracker.py` or `site_builder.py` — NOT in `__init__.py`
> separate from the data)"
>
> "make the dashboard canonical from a single source of truth. The
> dashboard must be self-rendering from a single source of truth —
> same data going in, same HTML out, deterministically."

The current architecture already satisfies this: `aggregate()` (data)
and `render_index/detai/accordion/_format_value` (rendering) all live
in `publish_kpi_tracker.py`. `__init__.py` only has orchestrators
(`build_dashboard`, `publish_publish_kpi_dashboard`, etc.).

The class-level rule for any future KPI / dashboard / report work:

- **One file holds data shape + rendering.** Adding a metric field
  updates the rendering function in the same edit — no drift.
- **`__init__.py` only orchestrates.** No render functions, no
  template strings. Composing data + render is the only job.
- **Same input → same output.** The integration test asserts
  `render_index(agg) == render_index(agg)` byte-identical.
- **CSS in `templates/`.** One-file edit when adding new card styles.

If you find yourself adding a render function to `__init__.py` to
avoid a circular import, that's a smell — extract the data shape
into its own module and render against that instead. Two files
(data + render) is one too many when they could be one.

The complementary architectural directive: **the artifact pair
`dashboard_data.json` + `index.html` should not require manual
reviewing of two separate files**. Both are generated by one
function call from one input. The dashboard data and the HTML are
co-located, and the dashboard is generated by a function that takes
only one input — the dashboard data — and produces deterministic
output.

## Path-portability commit gate (avoid `/home/...` in tests)

The Prismatic commit gate has a path-portability check that aborts
the commit when a `.py` file contains a hardcoded absolute path like
`/home/ubuntu/...`. The check fires at **commit time** (separate
from the lane-ownership check at **push time**). Test fixtures are
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

Two invariants to assert in the test suite:

1. The fixture path resolves to the same file on every developer's
   machine and in CI.
2. The repo-root anchor resolves to a directory that actually contains
   the canonical config (`config/seo_sites.json` for PWP) — see the
   symlink-walk anchor pattern above.

When the gate fires, the error names every offending file path. Fix
all of them in one commit; the gate will pass on retry without
re-running the test suite.

## Push-time lane violation: schemas/ and config/ are outside Ned's lane

The Prismatic Engine enforces per-agent lane ownership at push time
(separate from the path-portability check at commit time). Ned's lane
is `['scripts/', 'prismatic/', 'plugins/']` per `PRISMATIC_ENGINE.yaml`.
Files committed to `schemas/` or `config/` will commit cleanly but
**fail at push** with:

```
❌ [Prismatic Engine] Lane violation by ned:
   - config/seo_sites.json
   - schemas/pwp-kpi-registry.schema.json
   - schemas/pwp-kpi-site.schema.json
   These files are outside ned's lane.
   Owned directories: ['scripts/', 'prismatic/', 'plugins/']
```

The recovery for PWP plugin work:

- **Schemas**: move from `schemas/` (repo root, outside lane) to
  `plugins/<plugin>/capabilities/<capability>/schemas/` (inside
  lane). Update the loader's `_resolve_schema_path()` to look in the
  new location. Both `plugins/` and `prismatic/shipped_plugins/` need
  to be `git mv`-ed in lockstep because of the symlink.
- **Registry files (`config/seo_sites.json`)**: do NOT commit Ned's
  edits to the canonical registry — it's owned by another lane. The
  PWP plugin's adapter reads it but doesn't write; Ned's edits to
  per-site `*.kpi.json` files (in `plugins/.../sites/`) are
  sufficient to make new sites appear on the dashboard via the
  file-system scan in `list_sites()`.
- **`git rm --cached <file>`** removes a file from the index without
  deleting it from disk. Use this to drop a lane-violating file from
  the staged set while keeping the working-tree copy for reference.

The general rule: **commit-time gates catch one class of mistake
(paths, format), push-time gates catch another (lane ownership, secrets
scan). Both must pass before a commit becomes a remote commit.**
Don't conflate them — a clean local commit can still be a blocked
push, and a clean local push can still leave the branch in a broken
state for the next agent.

## Final tallies (across this work)

- Canonical pytest: **64/64 PASS** (39 prior → 57 after migration
  operator → 64 after per-site rows + `_format_value`).
- Ad-hoc verifier: **12/12 PASS** (`/tmp/hermes-verify-pwp-kpi-live-registry.py`).
- Live evidence: `tracking_property: G-PRRRLMBR8Z` resolved through
  the v1 `ga4_measurement_env` field via the v1→v2 adapter; curated
  `active-oahu.kpi.json` preserved unchanged across `--force`
  round-trip; per-site dashboard renders 2 rows (active-oahu +
  hd-engine) with 4 + 3 = 7 cards, each with `—` placeholder before
  runtime values are populated and the corresponding real numbers
  (47, 3, 12, 0.06%, 184, 7, 21) after.
- Two commits ready on `ned/pwp-publish-kpi-tracker`:
  - `4c94aec8` — migration operator + v1→v2 adapter + safety guard.
  - `bb8b398d` — per-site rows + `_format_value` + hd-engine in
    registry.
- **Push blocked** by lane violation on `config/seo_sites.json` and
  `schemas/*.schema.json`. Recovery: move schemas to
  `plugins/.../schemas/` and revert `config/seo_sites.json` from the
  commit; per-site `hd-engine.kpi.json` already in Ned's lane.