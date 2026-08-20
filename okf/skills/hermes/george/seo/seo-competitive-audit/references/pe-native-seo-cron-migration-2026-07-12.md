# PE-native SEO cron migration pattern (2026-07-12)

Use this when moving SEO automation out of Hermes/OpenClaw/profile-local schedulers into Prismatic Engine so the jobs are portable on any PE host.

## What was migrated

Core Active Oahu SEO jobs were moved into Prismatic Engine native cron state:

| Native cron ID | Previous source | Schedule | Command |
|---|---|---:|---|
| `seo.ubersuggest-token-refresh` | Hermes `4356ea55909b` / `pwp_ubersuggest_refresh.py` | `0 3 * * *` | `python3 scripts/pwp credentials refresh ubersuggest` |
| `seo.aot-weekly-rankings` | Hermes `ce817dba90d3` / `kpi_tracker.py` | `0 4 * * 1` | `python3 scripts/seo/aot_kpi_tracker.py` |
| `seo.aot-competitor-velocity` | Hermes `f9e8d6319b72` / `competitor_velocity.py` | `0 6 * * 0` | `python3 scripts/seo/competitor_velocity.py` |
| `seo.aot-full-sweep` | profile-local `seo_full_sweep.py` | `manual` | `python3 scripts/seo/seo_full_sweep.py` |

The full sweep is intentionally saved as deactivated/manual by default: available for overnight work, not sitting in the active queue.

## PE-native model

Implementation files in `prismatic-engine`:

- `prismatic/native_crons.py` — portable cron registry/state/actions/export.
- `prismatic/gateway/server.py` — `/native-crons` and `/native-crons/{cron_id}/action` endpoints.
- `prismatic/gateway/templates/dashboard.html` — Dashboard “Native Crons” tab.
- `scripts/install_native_crons.py` — managed user-crontab installer.
- `scripts/seo/*.py` — repo-owned SEO jobs, no dependency on `~/.hermes/profiles/.../scripts`.
- `docs/seo-cron-migration.md` — inventory and next SEO cron candidates.

State defaults to `$PRISMATIC_STATE_DIR/native_crons.json` and can be overridden with `PRISMATIC_NATIVE_CRON_STORE`.

## Lifecycle semantics

- **Pause**: stays in the active queue but is disabled temporarily.
- **Deactivate**: moves out of the queue and is saved for later.
- **Delete**: tombstones/hides the job from the default list.

Dashboard delete UX should include a secondary modal with: `Deactivate`, `Delete — I’m sure`, `Cancel`, and an X close control.

## Install/export commands

Export active queued jobs:

```bash
python3 -m prismatic.native_crons export-crontab --include-header
```

Install/update the managed crontab block:

```bash
python3 scripts/install_native_crons.py
```

Preview without writing:

```bash
python3 scripts/install_native_crons.py --dry-run
```

After installing PE-native cron lines, pause duplicate Hermes jobs to prevent double execution.

## Verification pattern

Focused verification for this class of work should include:

1. `py_compile` for `prismatic/native_crons.py`, gateway server, installer, and migrated SEO scripts.
2. Focused tests for native cron store/action semantics, installer managed-block replacement, and existing schedule endpoints.
3. Dashboard inline JS extraction + `node --check`.
4. `python3 -m prismatic.native_crons export-crontab --include-header` contains active jobs and omits deactivated/manual jobs.
5. `python3 scripts/install_native_crons.py --dry-run` emits exactly one managed `BEGIN/END PRISMATIC_NATIVE_CRONS` block.
6. Live smoke for token refresh with temp state: `python3 -m prismatic.native_crons run seo.ubersuggest-token-refresh`; success should be silent.
7. Live smoke for KPI script with temp `PRISMATIC_STATE_DIR`; verify `latest_keywords.json` exists and has expected keyword counts.
8. If Hermes raises an unverified-code guard, run a fresh `/tmp/hermes-verify-*` exact-path verifier and label it ad-hoc, not canonical suite green.

## Import-shadowing pitfall

CI or agent venvs may have installed packages named `prismatic`, `plugins`, etc. For repo-local scripts/tests that must import the checkout, force `REPO_ROOT` to the front of `sys.path`; if an already-loaded module points outside the checkout, evict that package and its submodules before importing local modules. Do this carefully in a central test `conftest.py` where possible to avoid polluting unrelated tests.

## Extended SEO jobs now wired

These follow-up jobs were added in PR #225 and should be treated as PE-native, not “still to wire”:

| Native cron ID | Schedule / trigger | Command | Notes |
|---|---:|---|---|
| `seo.gsc-query-page-export` | `30 5 * * *` | `python3 scripts/seo/gsc_query_page_export.py` | Daily GSC own-site `query,page` export for `sc-domain:activeoahutours.com`; verified live pull returned 8,960 rows on 2026-07-12. |
| `seo.aot-counter-content-briefs` | `30 7 * * 0` | `python3 scripts/seo/gsc_ubersuggest_countercontent.py` | Weekly after competitor velocity; consumes GSC export plus `state/seo/competitor_baseline.json` from `competitor_velocity.py`. |
| `seo.aot-internal-link-orphan-audit` | `15 8 * * 1` | `python3 scripts/seo/internal_link_orphan_audit.py` | Static site link graph/orphan/broken internal link audit. |
| `seo.aot-structured-data-drift-audit` | `45 8 * * 1` | `python3 scripts/seo/structured_data_drift_audit.py` | Static JSON-LD parser/type inventory; exits non-zero on parse errors so drift alerts instead of staying silent. |
| `seo.aot-sitemap-gsc-verification` | `manual` / deactivated | `python3 scripts/seo/sitemap_gsc_verification.py` | Manual/post-deploy gated. Live smoke on 2026-07-12 returned GSC 403 and wrote an error artifact, so do not activate until sitemap API access is fixed. |
| `seo.aot-lighthouse-seo-a11y-monitor` | `30 9 * * 1` | `python3 scripts/seo/lighthouse_seo_a11y_monitor.py` | Weekly Lighthouse SEO/A11y/Best Practices monitor with static fallback artifacts when Lighthouse/Chrome are unavailable. |

Detailed session-specific commands, verification snippets, and pitfalls live in `references/pe-native-seo-cron-extensions-2026-07-12.md`.

The native cron store now merges newly shipped repo defaults into an existing `native_crons.json` without overwriting locally customized job state. After merging new cron definitions, rerun `python3 scripts/install_native_crons.py` from `main` so the managed crontab block picks up active additions.

## Remaining future enhancements

1. Link latest report artifacts directly from the Dashboard Native Crons tab.
2. Trigger sitemap verification and Lighthouse monitor from post-deploy hooks.
3. Turn counter-content briefs/audit deltas into Linear issue drafts when Linear quota is available.
4. Mirror sensitive competitor reports into the private `active-oahu-business` repo rather than only local PE state.