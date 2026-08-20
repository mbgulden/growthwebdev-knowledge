# AOT SEO cron parking after PE-native migration (2026-07-12)

Use this when parking or auditing AOT SEO automation after migrating recurring jobs out of Hermes.

## Current shape

The canonical scheduler for recurring AOT SEO automation is Prismatic Engine native crons, not Hermes profile crons.

PE-native jobs:

- `seo.ubersuggest-token-refresh` — daily token rotation via PWP credential provider.
- `seo.aot-weekly-rankings` — weekly rankings/KPI snapshot.
- `seo.aot-competitor-velocity` — weekly competitor content velocity monitor.
- `seo.aot-full-sweep` — saved manual/deactivated competitive sweep.

Installed crontab block is managed by `scripts/install_native_crons.py` in `prismatic-engine` and bounded by:

```text
# BEGIN PRISMATIC_NATIVE_CRONS
# END PRISMATIC_NATIVE_CRONS
```

Hermes duplicates for the migrated jobs should remain paused to avoid double execution:

- `4356ea55909b` — old Ubersuggest refresh.
- `ce817dba90d3` — old weekly rankings.
- `f9e8d6319b72` — old competitor velocity.

## Parking/audit checklist

1. Verify PE repo `main` contains `prismatic/native_crons.py`, `scripts/install_native_crons.py`, and `scripts/seo/*.py`.
2. Check the managed crontab block includes the three active PE jobs.
3. Check Hermes duplicates are paused, not running in parallel.
4. Run a live PE-native Ubersuggest refresh smoke using temp state; success should be silent.
5. Run a live PE-native KPI smoke using temp `PRISMATIC_STATE_DIR`; verify `latest_keywords.json` and expected keyword counts.
6. If the dashboard changed, extract inline scripts from `dashboard.html` and run `node --check`.
7. Use a fresh `/tmp/hermes-verify-*` exact-path verifier for any post-edit guard and report it as ad-hoc verification.

## Remaining AOT SEO automation candidates

When Michael asks what SEO tools still need wiring, prioritize:

1. GSC own-site query/page export.
2. GSC + Ubersuggest counter-content brief generator.
3. Internal link graph/orphan page audit.
4. Structured data/schema drift audit.
5. Sitemap/GSC submission verification.
6. Lighthouse SEO/A11y monitor as a PE-native monitor if it should outlive Hermes.