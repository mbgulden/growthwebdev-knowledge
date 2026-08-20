# KPI Tracking Workflow — Weekly Rankings Monitor

## What It Does

The KPI tracker (`scripts/kpi_tracker.py`) checks rankings for your site + top competitors every Monday 4AM, compares against the previous week, and reports gains/losses/improvements/declines.

## Setup

1. Ensure `kpi_tracker.py` exists at `$HOME/.hermes/profiles/kai/scripts/kpi_tracker.py`
2. Ensure `/tmp/ubs_token` has a valid Ubersuggest Bearer token
3. Verify cron is registered: `cronjob action=list`

## Cron Schedule

- **Schedule:** `0 4 * * 1` (Mondays 4AM)
- **First run:** Must be triggered manually with `cronjob action=run job_id=<id>` to establish a baseline
- **Subsequent runs:** Compare against the `latest_keywords.json` snapshot from the previous run

## Known Pitfall — `domain_keywords` Response Format

**Critical:** `domain_keywords` returns a **raw list** of keyword objects, NOT a dict with a `keywords` key.

```python
# WRONG — crashes because data is a list, not a dict:
if "keywords" in data:
    for k in data["keywords"]: ...

# RIGHT — check isinstance:
if isinstance(data, list):
    for k in data:
        kw = k.get("keyword", "").lower()
```

Each item in the list has these keys:
- `keyword` (str)
- `position` (int)
- `volume` (int)
- `traffic` (int)
- `cpc` (float)
- `search_intent` (str, e.g. "Transactional")
- `pd` (int — paid difficulty)
- `sd` (int — seo difficulty)

## How to Debug

If the KPI report is empty or shows "0 keywords" despite having data:

1. Check the snapshot file: `cat cron/output/seo-audit/kpi-tracking/latest_keywords.json`
2. If `our_keywords` is `{}`, the `isinstance(data, list)` check is failing
3. Run a manual test with execute_code to inspect the raw response type
4. Fix the script, delete `latest_keywords.json`, re-run the script manually

## Interpreting the Report

Each Monday cron delivers:

- **Traffic Snapshot** — current keyword count, DA, backlinks for us + KBA + SurfnSea
- **Rankings Changes**:
  - **Gained**: keywords we now rank for that weren't tracked before
  - **Lost**: keywords dropped from our rankings
  - **Improved**: keywords that moved up in position
  - **Declined**: keywords that slipped down
- **Top items** — top 5 by volume for each category

## Important

The first run always reports "No previous data for comparison — baseline established." The real value starts with run #2.

If the KPI cron fails (e.g., Ubersuggest MCP connection issue), it tries again the next Monday. The report is a point-in-time snapshot, not a cumulative metric — a single missed week doesn't cascade.
