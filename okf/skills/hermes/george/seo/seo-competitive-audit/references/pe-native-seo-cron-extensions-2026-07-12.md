# PE-native SEO cron extensions (2026-07-12)

Use this reference when adding or auditing Prismatic Engine native crons for SEO automation, especially when migrating work out of Hermes/OpenClaw/profile-local scripts.

## Completed extension set

PR #225 added the remaining AOT SEO jobs as PE-native cron definitions and repo-owned scripts. PR #226 added an explicit contract marker to the GSC export script.

| Native cron ID | Schedule / trigger | Command | Notes |
|---|---:|---|---|
| `seo.gsc-query-page-export` | `30 5 * * *` | `python3 scripts/seo/gsc_query_page_export.py` | Daily GSC `query,page` export for `sc-domain:activeoahutours.com`; live smoke returned 8,960 rows. |
| `seo.aot-counter-content-briefs` | `30 7 * * 0` | `python3 scripts/seo/gsc_ubersuggest_countercontent.py` | Weekly after competitor velocity; consumes GSC export plus `state/seo/competitor_baseline.json`. |
| `seo.aot-internal-link-orphan-audit` | `15 8 * * 1` | `python3 scripts/seo/internal_link_orphan_audit.py` | Static site link graph, orphan pages, missing H1/meta/schema, broken internal links. |
| `seo.aot-structured-data-drift-audit` | `45 8 * * 1` | `python3 scripts/seo/structured_data_drift_audit.py` | JSON-LD parser/type inventory; exits non-zero on parse errors so drift alerts rather than staying silent. |
| `seo.aot-sitemap-gsc-verification` | manual / deactivated | `python3 scripts/seo/sitemap_gsc_verification.py` | Manual/post-deploy gated; live smoke returned GSC 403 and wrote an error artifact, so leave deactivated until sitemap API access is fixed. |
| `seo.aot-lighthouse-seo-a11y-monitor` | `30 9 * * 1` | `python3 scripts/seo/lighthouse_seo_a11y_monitor.py` | Weekly Lighthouse SEO/A11y/Best Practices monitor with static fallback artifacts when Lighthouse/Chrome are unavailable. |

The installed PE crontab block should include the five active new jobs and omit the two manual/deactivated jobs (`seo.aot-full-sweep`, `seo.aot-sitemap-gsc-verification`).

## Durable implementation lessons

1. **Merge repo defaults into existing stores.** Existing hosts may already have `$PRISMATIC_STATE_DIR/native_crons.json`; `NativeCronStore.ensure_seeded()` must merge missing repo-defined cron IDs without overwriting locally customized state.
2. **Keep path compatibility with migrated scripts.** `competitor_velocity.py` writes `state/seo/competitor_baseline.json`, not `state/seo/competitor-velocity/competitor_baseline.json`; counter-content generation should check the real migrated output path.
3. **Deactivated/manual jobs still need scripts and tests.** Sitemap/GSC verification is a real native job even though it should not be in active crontab until GSC sitemap API permissions are healthy.
4. **Static monitors should always write artifacts.** Internal link, schema, and Lighthouse fallback jobs should produce JSON/Markdown output even when they return non-zero to signal drift.
5. **Verification guard pattern.** For Hermes “unverified changed paths” prompts, create a fresh `/tmp/hermes-verify-*` exact-path script, compile changed Python paths, run focused tests, check native registry IDs, check installed crontab active/manual behavior, run temp-state live smokes where credentials permit, remove the verifier, and label the result ad-hoc verification, not canonical suite green.

## Focused verification commands

```bash
python3 -m py_compile prismatic/native_crons.py scripts/seo/*.py
python3 -m pytest tests/test_native_crons.py tests/test_install_native_crons.py tests/test_seo_cron_extensions.py -q
python3 -m prismatic.native_crons list
python3 -m prismatic.native_crons export-crontab --include-header
python3 scripts/install_native_crons.py --dry-run
```

Live chain smoke with temporary state:

```bash
TMP=$(mktemp -d /tmp/pe-counter-live-XXXXXX)
PRISMATIC_STATE_DIR="$TMP/state" python3 scripts/seo/gsc_query_page_export.py
PRISMATIC_STATE_DIR="$TMP/state" python3 scripts/seo/competitor_velocity.py
PRISMATIC_STATE_DIR="$TMP/state" python3 scripts/seo/gsc_ubersuggest_countercontent.py
```

Static AOT smoke:

```bash
TMP=$(mktemp -d /tmp/pe-static-live-XXXXXX)
AOT_SITE_DIR=/home/ubuntu/work/active-oahu-tours-mirror/site \
  PRISMATIC_STATE_DIR="$TMP/state" python3 scripts/seo/internal_link_orphan_audit.py
AOT_SITE_DIR=/home/ubuntu/work/active-oahu-tours-mirror/site \
  PRISMATIC_STATE_DIR="$TMP/state" python3 scripts/seo/structured_data_drift_audit.py
```
