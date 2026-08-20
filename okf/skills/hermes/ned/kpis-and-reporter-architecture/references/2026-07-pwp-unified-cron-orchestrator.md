# 2026-07-29: Unified cron orchestration, env-var-only GA4, str/Path coercion

This is a session-specific reference captured during an audit that
shipped three gap fixes on top of the existing PWP publish-kpi-tracker
architecture:

- **GAP-#5 — env-var-only GA4 resolution.** The static
  `config/seo_sites.json` had drifted (`hd-engine` had a static
  `G-PRRRLMBR8Z` literal that didn't match the live deployed
  `G-Q6TPL08VM7`). The fix: any literal `ga4_measurement_id` in the
  v1 registry is forced to `None` by the v1→v2 adapter, and the
  loader's `_resolve_tracking_property()` resolves the GA4 ID **only**
  from the `ga4_measurement_env` env-var. Static config can lie;
  runtime always wins.
- **GAP-#7 — unified cron orchestrator.** A single Prismatic Engine
  cron entry (`python3 .../cron_orchestrator.py daily`) now walks the
  registry and dispatches the per-site launcher (`cron_launcher.py`)
  per site, loading each site's share-targets env vars from its
  `<slug>.kpi.json`. Adding a new site = one registry entry +
  one curated file. The orchestrator handles the rest.
- **`Path`-vs-`str` coercion at function entry.** When argparse passes
  strings and a function expects `Path`, coerce at the entry — not at
  every call site. The `cron_orchestrator.run()` regression test
  passes a string to lock this in.

## GAP-#5: env-var-only GA4 resolution

### The drift

The shipped `config/seo_sites.json` had a static
`ga4_measurement_id: G-PRRRLMBR8Z` for `hd-engine`, but the live
deployed loader was using `HDE_GA4_MEASUREMENT_ID=G-Q6TPL08VM7`. The
static config **lied**; the env-var held the truth. The drift was
masked at runtime because the original `_resolve_tracking_property()`
preferred the literal over the env-var, so most reads got the wrong
ID — but the dashboard still rendered because the operator had
also set the env-var to the real value, and the literal-fallback was
rarely exercised in production.

### The two-part fix

1. **Adapter layer**: `legacy_seo_registry._adapt_v1_site` now forces
   any `ga4_measurement_id` literal to `None` after adaptation. The
   drift in the static config is stripped at the seam.

   ```python
   # legacy_seo_registry.py
   def _adapt_v1_site(site: dict) -> dict:
       out = dict(site)  # full passthrough
       # ...
       # GAP-#5: force env-var-only resolution. Any literal GA4 ID
       # in the registry is ignored; the live GA4 property always
       # comes from the `ga4_measurement_env` env-var at runtime.
       if "ga4_measurement_id" in out:
           out["ga4_measurement_id"] = None
       # ...
       return out
   ```

2. **Loader layer**: `pwp_kpi_site_registry._resolve_tracking_property`
   resolves GA4 **only** from the env-var. The literal-fallback branch
   is removed.

   ```python
   def _resolve_tracking_property(site: dict) -> Tuple[Optional[str], Optional[str]]:
       """GAP-#5 FIX — env-var-only:
       The static `ga4_measurement_id` literal is intentionally ignored.
       The live GA4 property always comes from the env-var named in
       `ga4_measurement_env`. This eliminates the tracking-property drift
       between the shipped config and the deployed loader."""
       env_name = site.get("ga4_measurement_env")
       if env_name:
           v = os.environ.get(env_name)
           if v and GA4_MEAS_RE.match(v):
               return v, "env"
       return None, "none"
   ```

### Why this is general

Anywhere a config file carries both a static literal AND an env-var
name for the same secret, the static literal is a foot-gun: it drifts
out of sync with the deployment. The pattern:

- The **adapter** strips the literal at the registry boundary.
- The **resolver** reads only the env-var.
- The **adapter test** asserts both behaviors.

Same shape works for any "config-secret-drift" class: API keys,
webhook URLs, sheet IDs, anything that's both static and env-driven.

### Test coverage

- `test_iter_sites_resolves_tracking_property_from_env` — uses
  `monkeypatch.setenv` for both sites (literal fallback is gone).
- `test_adapt_v1_forces_ga4_measurement_id_to_null_gap5` — new
  regression test asserting the literal is forced to `None`.
- `test_registry.json` — disabled-site switched from literal to
  env-var (`TEST_DISABLED_MEAS_ID`).

Live verified: `active-oahu → G-PRRRLMBR8Z` via
`AOT_GA4_MEASUREMENT_ID`; `hd-engine → G-Q6TPL08VM7` via
`HDE_GA4_MEASUREMENT_ID`. Env-var-only contract holds.

## GAP-#7: unified cron orchestrator

### Before

`hd-platform-staging` had a per-site `cron_launcher.py` that knew
only about HDE. Adding a new site meant:

- Wiring a new Prismatic Engine cron entry.
- Hard-coding the site's env-var names in `registry.json`.
- Keeping two `share_targets` declarations in sync (one in the
  site's `*.kpi.json`, one in `registry.json`).

Three places to keep in sync per site. Adding a new site was a
mini-integration.

### After

A single Prismatic Engine cron entry drives daily/weekly/monthly
runs across every registered site. The orchestrator walks the
registry, reads each site's `delivery_cadence`, and dispatches the
per-site launcher with the right env vars loaded from each site's
`share_targets` block. One cron entry, one registry declaration
per site, zero per-site cron wiring.

### The orchestrator (`cron_orchestrator.py`)

```python
def run(
    *,
    kind: str,                  # daily | weekly | monthly
    registry_path: Optional[PathLike] = None,
    publish_root: Optional[PathLike] = None,
    launcher: Optional[PathLike] = None,
    timeout: int = 120,
) -> Dict[str, Any]:
    registry = load_registry(Path(registry_path) if registry_path else None)
    if publish_root is None or publish_root == "":
        publish_root_path = Path("/tmp/pwp-kpi-runs") / kind
    else:
        publish_root_path = Path(publish_root)
    publish_root_path.mkdir(parents=True, exist_ok=True)
    launcher_path = Path(launcher) if launcher else _resolve_launcher()
    # ...
    for site in iter_sites(registry):
        slug = site["slug"]
        if not site_override_enabled(registry, site):
            manifest["sites"].append(
                {"slug": slug, "status": "skipped (disabled)",
                 "cadence_matched": False})
            continue
        flat = kpi.resolve_collection(slug)
        if not _cadence_matches(flat, kind):
            manifest["sites"].append(
                {"slug": slug, "status": "skipped (cadence)",
                 "cadence_matched": False})
            continue
        env = _resolve_share_targets_env(slug, flat)
        result = dispatch_one_site(
            slug, kind=kind, launcher=launcher_path,
            env_overrides=env, publish_root=publish_root_path,
            timeout=timeout,
        )
        # ...
```

Three contract points:

1. **`_cadence_matches(flat, kind)`** — see below for the three
   shape variants.
2. **`_resolve_share_targets_env(slug, flat)`** — loads each env var
   named in the site's `share_targets` block; missing env vars are
   silently skipped (the launcher falls back to its own defaults).
3. **`_resolve_launcher()`** — never assumes a default; explicit
   `--launcher`, `PWP_KPI_CRON_LAUNCHER`, or `HDE_KPI_REPO_ROOT`.

### `delivery_cadence` shape — three variants

The canonical `active-oahu.kpi.json` and `hd-engine.kpi.json` use
the dict shape:

```json
"delivery_cadence": {
  "daily":   {"kind": "daily"},
  "weekly":  {"kind": "weekly"},
  "monthly": {"kind": "monthly"}
}
```

But `_cadence_matches` accepts three shapes:

| Shape | Example | When used |
|---|---|---|
| String | `"delivery_cadence": "daily"` | Single-cadence sites |
| List | `"delivery_cadence": ["daily", "weekly"]` | Multi-cadence, no extra metadata |
| Dict | `"delivery_cadence": {"daily": {...}, "monthly": {...}}` | Multi-cadence with metadata per kind |

The orchestrator must accept all three. Smoke-test against the
canonical real-world data, not just synthetic fixtures — the dict
shape only surfaced during live orchestrator dispatch, not in the
test suite.

### CLI wiring

```bash
pwp-kpi-tracker cron daily \
  --publish-root /tmp/pwp-kpi-runs/daily \
  --launcher /path/to/cron_launcher.py
```

`cmd_cron(args)` delegates to `cron_orchestrator.run()` and emits
the manifest as JSON. Failure modes (timeout, non-zero return code,
resolve_collection errors) are recorded per-site; the orchestrator
never crashes on a single-site failure.

### Live verification

```
$ pwp-kpi-tracker cron daily --publish-root /tmp/pwp-kpi-runs-test
{
  "kind": "daily",
  "launcher": "/home/ubuntu/work/hd-platform-staging/.../cron_launcher.py",
  "publish_root": "/tmp/pwp-kpi-runs-test",
  "sites": [
    {
      "slug": "active-oahu",
      "status": "dispatched",
      "cadence_matched": true,
      "elapsed_seconds": 0.05,
      "env_overrides": [],
      "stdout_tail": "wrote /tmp/kpi-report-daily.json, ..."
    }
  ]
}
```

The launcher ran in 0.05s and emitted the daily report to `/tmp/`.
`prismatic.core_crons` can fire the orchestrator once a day and get
all sites' daily reports in a single manifest.

## `Path`-vs-`str` coercion at function entry

### The trap

The orchestrator's `run()` had `publish_root: Optional[Path] = None`,
but `argparse` passes strings. The line:

```python
publish_root = publish_root or Path("/tmp/pwp-kpi-runs") / kind
publish_root.mkdir(parents=True, exist_ok=True)
```

crashed with `AttributeError: 'str' object has no attribute 'mkdir'`
when `publish_root` was a non-empty string (the `or` short-circuits,
leaving the string in place).

The canonical pytest suite missed this because every test passed a
`Path` directly. The string path was only reachable through `argparse`,
which the tests did not exercise. The verifier surfaced the bug.

### The fix (three parts)

1. **Widen the type signature** to accept both:

   ```python
   PathLike = Union[Path, str]
   def run(*, ..., publish_root: Optional[PathLike] = None, ...):
       ...
   ```

2. **Coerce at the function entry**, not at every call site:

   ```python
   if publish_root is None or publish_root == "":
       publish_root_path = Path("/tmp/pwp-kpi-runs") / kind
   else:
       publish_root_path = Path(publish_root)
   publish_root_path.mkdir(parents=True, exist_ok=True)
   ```

3. **Add a regression test that passes a string**, not a `Path`:

   ```python
   def test_run_coerces_string_publish_root(tmp_path, monkeypatch):
       publish_root_str = str(tmp_path / "string-publish-root")
       manifest = orch.run(
           kind="daily",
           publish_root=publish_root_str,  # str, not Path
           launcher=tmp_path / "stub_launcher.py",
       )
       assert manifest["publish_root"] == publish_root_str
       assert (tmp_path / "string-publish-root").is_dir()
   ```

### Why this matters

Unit tests typically call functions with `Path` instances directly.
The CLI passes strings. The boundary between argparse and the
function is rarely exercised in tests. The verifier is the durable
place to catch this class of bug.

Three places where this matters in the KPI Hub:

- `cron_orchestrator.run(publish_root=...)` — fixed in this session.
- `cron_orchestrator.run(launcher=...)` — same fix applied.
- `cron_orchestrator.run(registry_path=...)` — same fix applied.

Any function that accepts a path-like arg from `argparse` should
either (a) widen its signature to `Optional[PathLike]` and coerce
at the entry, or (b) wrap the entry-point to coerce before calling
the inner function. The first option is cleaner when the function
is the public API; the second is cleaner when the function is
internal but exposed through a CLI.

## Ad-hoc verifier that surfaced all three

`/tmp/hermes-verify-gap5-gap7.py` was the post-push verifier for
this turn. It had two self-bugs (missing `from pathlib import Path`
in embedded `subprocess.run([python3, "-c", ...])` code, and a
tautological `all(... and "env" in str(value) ...)` check) that
false-failed first. After fixing those, the verifier surfaced the
real `publish_root` str/Path bug in production code. The
`ad-hoc-verification-contracts` skill's
`references/2026-07-cron-orchestrator-str-path-and-tautological-checks.md`
documents those three patterns.

## Net state after this turn

- 106/106 pytest pass.
- 5 commits ahead of `origin/ned/pwp-publish-kpi-tracker`:
  - `3d841694` — site-registry migration + per-site rows
  - `55767f4f` — runtime values pipeline + percent fix
  - `44e466c7` — `migrate --merge` semantic equivalence
  - `0e87b403` — GAP-#5 env-var-only GA4 resolution
  - `a78e9f44` — GAP-#7 unified cron orchestration
- Live dashboard: 7 cards show real values (booking click 47,
  bookings completed 3, leads 12, conversion 6.38%, charts 184,
  sanctuary 7, reports 21).
- Live `pwp-kpi-tracker cron daily` dispatch: active-oahu → launcher
  ran in 0.05s, wrote the daily report.

The KPI Hub is fully wired for "more sites": a single cron entry
drives every site, env-vars handle all secrets, the registry
adapter handles v1→v2, the runtime pipeline populates dashboard
cards from snapshots, and `migrate --merge` lets the registry grow
without clobbering curated metrics.