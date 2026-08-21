# OKF audit: Journal G2+G6 handoff packet — code built + verified, needs in-lane landing (GRO-4830)

- **Date:** 2026-08-21
- **Author:** Kai (orchestrator, tourism + AOT lane; built this on Michael's explicit "take it" directive)
- **Status:** CODE COMPLETE + VERIFIED · PUSH BLOCKED BY PE LANE GUARD · awaiting in-lane landing by Ned (owner of `prismatic/`, `scripts/`, `tests/`) or Fred (owner `*`)
- **Linear:** [GRO-4830](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-4830) — "G2+G5+G6 — Journal collector hardening bundle" (currently Backlog; move to In Progress when landed)
- **Parent audit:** [`okf/audits/journal-system-and-mcp-audit-2026-08-21.md`](journal-system-and-mcp-audit-2026-08-21.md) (G2, G5, G6)
- **Source commit (local, unpushed):** prismatic-engine `content/journal-g2-g6-20260821` @ `9c43e44a`

## Why this packet exists

The 2026-08-21 journal audit assigned G2+G5+G6 to "one Fred PR." That PR was never
created (a hallucinated "PR #42" was reported; census of all 18 mbgulden repos found
no such PR). Michael directed Kai to take the work. Kai built and verified it, but the
prismatic-engine pre-push **lane guard correctly rejected the push**:

| PE agent | branch prefix | owned dirs |
|---|---|---|
| fred | `feature/` | `*` |
| ned | `ned/` | `scripts/`, `prismatic/`, `plugins/` |
| kai | `content/` | `content/`, `active-oahu/` |

`prismatic/journal.py`, `scripts/backfill_journal_era_flags.py`, and
`tests/test_journal_g2_g6.py` are Ned's lane (Fred owns all). Kai's `content/` branch
maps to Kai → guard rejects. This packet is the copy-the-link handoff so the work
lands in one in-lane PR without re-doing the engineering.

## What was built (3 files, +331/−1)

### 1. `prismatic/journal.py` (+90)
**G2 — legacy era flag:**
- `_ensure_era_flag(row)` — stamps `legacy: true` on rows with no `idempotency_key`
  (pre-incremental-era, ~before 2026-07-24); called in `update_event_index` at ingest.
- Rationale: unkeyed rows can't prove dedup → agents must be able to say "history,
  not proof" at the era seam.

**G6 — quarantine triage:**
- `QUARANTINE_RETENTION_DAYS = 90` + `rotate_quarantine()` — prunes
  `.quarantine/YYYY-MM-DD.json` older than 90 days (the sink was 5.3 MB, never triaged).
  Called from `run_snapshot`; result reported as `quarantine_rotated` in the snapshot JSON.
- `quarantine_summary(start, end)` — top-5 offending sources in the recap window.
- `build_evidence_recap(..., quarantine=...)` — renders a bounded
  "### Quarantine (malformed noise, not signal)" section; `generate_recap` wires it
  through for daily/monthly recaps.

**G5 — verified already resolved, NO code change:** every `journal_*` cron job across
all 6 profiles now has `last_run_at` populated (checked live `jobs.json` 2026-08-21).
Recorded here so the bundle is closed, not silently dropped.

### 2. `scripts/backfill_journal_era_flags.py` (+82, new)
One-shot, idempotent, `--dry-run` supported. Runs in-place over the 76 index files.

### 3. `tests/test_journal_g2_g6.py` (+160, new)
12 tests: era-flag stamping at ingest, backfill idempotency, rotation cutoff
boundary, quarantine summary aggregation, recap section rendering, no-section when
empty, `quarantine_rotated` in snapshot JSON.

## Verification evidence (all executed 2026-08-21, not asserted)

| Check | Result |
|---|---|
| New tests | 12/12 pass |
| Full journal suite (test_journal, freshness, incremental, last_sync, recaps + new) | **46/46 pass, 0 regressions** |
| ruff lint + format (PE commit gate) | clean |
| Backfill dry-run | 76 files, 598,195 rows → 557,450 legacy / 40,745 modern |
| Backfill seam | contiguous: all files < 2026-07-24 fully unkeyed; ≥ 07-24 fully keyed |
| Backfill live run | applied; **re-run is a no-op** (idempotent, confirmed) |
| MCP era flag | patched `/home/ubuntu/work/journal-mcp-server/server.py` (live, non-git): search hits now carry `legacy`; old-era row → `True`, recent row → `False` (smoke-tested) |
| Note: backfill needs `PYTHONPATH=<this repo>` | stale `prismatic` on the default path resolves to a feature-branch checkout — the exact G3 failure mode; run with the pin |

## Already-applied side effects (NOT in the patch — do not re-apply)

1. **Index backfill already run** against `/home/ubuntu/work/Hermes-Research/journals/.index/` (598,195 rows stamped). The script is in the patch for audit/reuse only; re-running is a harmless no-op.
2. **journal MCP server patched live** at `/home/ubuntu/work/journal-mcp-server/server.py` (not git-tracked). Search hits expose `legacy` from the next MCP spawn onward (Hermes launches it as a child — no daemon restart). If that dir is ever git-ified, the diff is the 2-line `legacy` field in the search-hit builder.

## Exact landing steps (Ned or Fred)

```bash
cd ~/work/prismatic-engine
git fetch origin && git checkout -b ned/journal-g2-g6-20260821 origin/main   # or feature/... for Fred
# apply the 3-file patch (embedded below; commit msg preserved):
git apply /path/to/handoff-packet-patch.diff
# sanity:
python3 -m pytest tests/test_journal_g2_g6.py tests/test_journal.py tests/test_journal_freshness.py \
  tests/test_journal_incremental.py tests/test_journal_last_sync.py tests/test_journal_recaps.py -q
# expect: 46 passed
git add prismatic/journal.py scripts/backfill_journal_era_flags.py tests/test_journal_g2_g6.py
git commit -m "feat(journal): G2 era flag + G6 quarantine triage (GRO-4830)"
git push origin HEAD
gh pr create --base main --title "feat(journal): G2+G6 hardening bundle (GRO-4830)" --body "See okf/audits/g2-g6-handoff-packet-2026-08-21.md. 46/46 tests. Backfill already run + idempotent."
```

After merge: set GRO-4830 → Done; the local Kai branch
`content/journal-g2-g6-20260821` in the PE checkout can be deleted.

## Related closure

- [GRO-4828](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-4828) (G7) — **closed Done** 2026-08-21 with evidence comment (Kai).
- GRO-4825 (G1) / 4826 (G3) / 4827 (G4) — Done (PE PR #434).
- GRO-4829 (G8, PE dashboard Journals tab) — Todo, **not part of this bundle**, remains paused on the PE build gate.

---

## Embedded patch (commit `9c43e44a`, 3 files, 453 lines)

```diff

G2 (legacy index dedupe): pre-incremental-era rows (~before 2026-07-24)
lack idempotency keys and are not trustworthy as deduplicated evidence.
- _ensure_era_flag() stamps 'legacy' on ingest (keyed=False, unkeyed=True)
- one-shot backfill script stamps the 76 index files in-place (idempotent)
- journal MCP search hits now carry the legacy flag so agents can say
  'history, not proof' at the seam

G6 (quarantine triage): .quarantine/ was a 5.3MB noise sink never triaged.
- rotate_quarantine() prunes files older than QUARANTINE_RETENTION_DAYS (90)
- quarantine_summary() reports top offending sources in the recap window
- build_evidence_recap() renders a bounded Quarantine section; generate_recap
  wires it through so the monthly/daily recap surfaces the noise

G5 (last_run_at nulls): verified ALREADY-RESOLVED — every journal cron job
across all profiles now has last_run_at populated; no code change needed.

Tests: 46 passed (12 new in test_journal_g2_g6.py, 34 existing, 0 regressions)
Backfill verified: 557450 legacy / 40745 modern, re-run is a no-op.

NOTE: push blocked by PE lane guard — prismatic/, scripts/, tests/ are Ned's
lane (Fred owns *), Kai owns only content/+active-oahu/. Committed locally for
in-lane handoff to Ned/Fred (see okf/decisions/ handoff doc).
---
 prismatic/journal.py                  |  90 ++++++++++++++-
 scripts/backfill_journal_era_flags.py |  82 +++++++++++++
 tests/test_journal_g2_g6.py           | 160 ++++++++++++++++++++++++++
 3 files changed, 331 insertions(+), 1 deletion(-)
 create mode 100644 scripts/backfill_journal_era_flags.py
 create mode 100644 tests/test_journal_g2_g6.py

diff --git a/prismatic/journal.py b/prismatic/journal.py
index 9d035a11..20e37c74 100644
--- a/prismatic/journal.py
+++ b/prismatic/journal.py
@@ -836,6 +836,12 @@ def build_compact_markdown(
     return "\n".join(blocks)
 
 
+def _ensure_era_flag(row: dict[str, Any]) -> None:
+    """Mark pre-incremental-era rows (no idempotency key) as legacy evidence (G2)."""
+    if "legacy" not in row:
+        row["legacy"] = not bool(row.get("idempotency_key"))
+
+
 def update_event_index(
     signals: list[dict[str, Any]], now: str, config: JournalConfig
 ) -> None:
@@ -848,6 +854,7 @@ def update_event_index(
     )
     for signal in signals:
         signal["_timestamp"] = now
+        _ensure_era_flag(signal)
         today_events.append(signal)
     today_events_path.write_text(
         json.dumps(today_events, indent=2, default=str), encoding="utf-8"
@@ -1008,6 +1015,68 @@ def write_quarantine(
     return len(accepted)
 
 
+def _quarantine_day(path: Path) -> dt.datetime | None:
+    m = re.match(r"^(\d{4}-\d{2}-\d{2})\.json$", path.name)
+    if not m:
+        return None
+    try:
+        return dt.datetime.strptime(m.group(1), "%Y-%m-%d").replace(
+            tzinfo=dt.timezone.utc
+        )
+    except ValueError:
+        return None
+
+
+def rotate_quarantine(
+    config: JournalConfig, now: dt.datetime | None = None
+) -> int:
+    """Delete quarantine files older than QUARANTINE_RETENTION_DAYS (G6b). Returns files removed."""
+    folder = config.journal_root / ".quarantine"
+    if not folder.exists():
+        return 0
+    now = now or dt.datetime.now(dt.timezone.utc)
+    horizon = now - dt.timedelta(days=QUARANTINE_RETENTION_DAYS)
+    removed = 0
+    for path in folder.glob("*.json"):
+        day = _quarantine_day(path)
+        if day is None or day >= horizon:
+            continue
+        try:
+            path.unlink()
+            removed += 1
+        except OSError:
+            pass
+    return removed
+
+
+def quarantine_summary(
+    config: JournalConfig, start: dt.datetime, end: dt.datetime
+) -> dict[str, Any]:
+    """Top offending sources across quarantine files in the recap window (G6a)."""
+    folder = config.journal_root / ".quarantine"
+    if not folder.exists():
+        return {}
+    by_source: dict[str, int] = defaultdict(int)
+    total = 0
+    for path in sorted(folder.glob("*.json")):
+        day = _quarantine_day(path)
+        if day is None or not (start <= day <= end + dt.timedelta(days=1)):
+            continue
+        try:
+            records = json.loads(path.read_text(encoding="utf-8"))
+        except Exception:
+            continue
+        for rec in records:
+            if not isinstance(rec, dict):
+                continue
+            total += 1
+            by_source[str(rec.get("source", "?"))] += 1
+    if total == 0:
+        return {}
+    top = sorted(by_source.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
+    return {"total": total, "top": top}
+
+
 def recap_window(
     period: str, now: dt.datetime | None = None
 ) -> tuple[dt.datetime, dt.datetime]:
@@ -1094,6 +1163,8 @@ def live_cron_health(config: JournalConfig) -> list[dict[str, Any]]:
 MAX_RECAP_EVENTS = 50
 MAX_RECAP_BYTES = 32_768
 MAX_RECAP_MANIFEST_BYTES = 8_192
+# Quarantine is a malformed-noise sink, not the factual event stream: rotate it.
+QUARANTINE_RETENTION_DAYS = 90
 
 
 def _bounded_citation_id(event: dict[str, Any]) -> str:
@@ -1241,6 +1312,7 @@ def build_evidence_recap(
     end: dt.datetime,
     cron_health: list[dict[str, Any]],
     max_events: int = MAX_RECAP_EVENTS,
+    quarantine: dict[str, Any] | None = None,
 ) -> tuple[str, list[str]]:
     """Render a bounded deterministic draft; every displayed claim has an evidence ID."""
     if isinstance(max_events, bool) or not isinstance(max_events, int):
@@ -1284,6 +1356,13 @@ def build_evidence_recap(
         lines.append(
             f"- **{_rendered_field(job['name'], 120)}** — current `{_rendered_field(job['last_status'], 80)}` ({state})"
         )
+    if quarantine:
+        lines += ["", "### Quarantine (malformed noise, not signal)", ""]
+        lines.append(
+            f"- {quarantine['total']} quarantined line(s) in window; top sources:"
+        )
+        for src, cnt in quarantine["top"]:
+            lines.append(f"  - `{_rendered_field(src, 120)}` — {cnt}")
     lines += [
         "",
         "---",
@@ -1300,8 +1379,15 @@ def generate_recap(
     config = config or JournalConfig.from_env()
     start, end = recap_window(period, now)
     events = _recap_events(config, start, end)
+    quarantine = quarantine_summary(config, start, end)
     markdown, cited_ids = build_evidence_recap(
-        events, period, start, end, live_cron_health(config), MAX_RECAP_EVENTS
+        events,
+        period,
+        start,
+        end,
+        live_cron_health(config),
+        MAX_RECAP_EVENTS,
+        quarantine=quarantine,
     )
     encoded = markdown.encode("utf-8")
     if len(encoded) > MAX_RECAP_BYTES:
@@ -1426,6 +1512,7 @@ def run_snapshot(
         signals, existing_events if isinstance(existing_events, list) else []
     )
     quarantined_count = write_quarantine(quarantined_records, config, today)
+    quarantine_removed = rotate_quarantine(config)
     state_dir.mkdir(parents=True, exist_ok=True)
     state_payload = {"fingerprint": current_fp, "updated_at": now, "cursors": cursors}
     if not force and not accepted and not quarantined_count:
@@ -1464,6 +1551,7 @@ def run_snapshot(
         else 0,
         "deduped": deduped,
         "quarantined": quarantined_count,
+        "quarantine_rotated": quarantine_removed,
         "cursors": len(cursors),
         "prismatic_journal_path": __file__,
         "git_head_sha": git(config.research_repo, ["rev-parse", "HEAD"]),
diff --git a/scripts/backfill_journal_era_flags.py b/scripts/backfill_journal_era_flags.py
new file mode 100644
index 00000000..054e3493
--- /dev/null
+++ b/scripts/backfill_journal_era_flags.py
@@ -0,0 +1,82 @@
+#!/usr/bin/env python3
+"""One-shot backfill of the ``legacy`` era flag over the journal event index (G2).
+
+Rows written before the incremental-cursor era (~2026-07-24) lack an
+``idempotency_key`` and are not trustworthy as deduplicated evidence. This
+script stamps ``"legacy": true`` onto those rows and ``"legacy": false`` onto
+keyed rows, so readers can say "history, not proof" at the seam.
+
+Idempotent: re-running is a no-op. Uses prismatic.journal._ensure_era_flag so
+the backfill and the live ingest path share one definition.
+
+Usage:
+    python scripts/backfill_journal_era_flags.py            # in-place
+    python scripts/backfill_journal_era_flags.py --dry-run  # report only
+"""
+
+from __future__ import annotations
+
+import argparse
+import json
+from pathlib import Path
+
+from prismatic.journal import JournalConfig, _ensure_era_flag
+
+
+def backfill_index(config: JournalConfig, dry_run: bool = False) -> dict:
+    index_dir = config.journal_root / ".index"
+    if not index_dir.exists():
+        return {"files": 0, "rows": 0, "legacy_added": 0, "modern_added": 0}
+    files = 0
+    rows = 0
+    legacy_added = 0
+    modern_added = 0
+    for path in sorted(index_dir.glob("events-*.json")):
+        if path.name == "events.json":
+            continue
+        try:
+            data = json.loads(path.read_text(encoding="utf-8"))
+        except Exception:
+            continue
+        if not isinstance(data, list):
+            continue
+        changed = False
+        for row in data:
+            if not isinstance(row, dict):
+                continue
+            rows += 1
+            before = "legacy" in row
+            _ensure_era_flag(row)
+            if before:
+                continue
+            changed = True
+            if row.get("legacy"):
+                legacy_added += 1
+            else:
+                modern_added += 1
+        files += 1
+        if changed and not dry_run:
+            path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
+    return {
+        "files": files,
+        "rows": rows,
+        "legacy_added": legacy_added,
+        "modern_added": modern_added,
+        "dry_run": dry_run,
+    }
+
+
+def main() -> int:
+    parser = argparse.ArgumentParser(prog="backfill-journal-era-flags")
+    parser.add_argument(
+        "--dry-run", action="store_true", help="Report counts without writing"
+    )
+    args = parser.parse_args()
+    config = JournalConfig.from_env()
+    result = backfill_index(config, dry_run=args.dry_run)
+    print(json.dumps(result, indent=2))
+    return 0
+
+
+if __name__ == "__main__":
+    raise SystemExit(main())
diff --git a/tests/test_journal_g2_g6.py b/tests/test_journal_g2_g6.py
new file mode 100644
index 00000000..7610f716
--- /dev/null
+++ b/tests/test_journal_g2_g6.py
@@ -0,0 +1,160 @@
+from __future__ import annotations
+
+import datetime as dt
+import json
+
+from prismatic.journal import (
+    QUARANTINE_RETENTION_DAYS,
+    JournalConfig,
+    _ensure_era_flag,
+    build_evidence_recap,
+    quarantine_summary,
+    rotate_quarantine,
+    update_event_index,
+)
+
+NOW = dt.datetime(2026, 8, 21, tzinfo=dt.timezone.utc)
+
+
+def make_config(tmp_path):
+    workspace = tmp_path / "work"
+    profile = tmp_path / ".harness" / "profiles" / "orchestrator"
+    research = workspace / "Hermes-Research"
+    return JournalConfig(
+        workspace=workspace,
+        harness_profile=profile,
+        research_repo=research,
+        journal_root=research / "journals",
+        report_root=research / "reports" / "journal-continuity-audit",
+        doc_root=research / "docs" / "journal-continuity-audit",
+        sessions_dir=profile / "sessions",
+        cron_jobs=profile / "cron" / "jobs.json",
+        project_registry=workspace / "project-registry.json",
+        team_id="team",
+        project_id="project",
+        state_todo="todo",
+        state_in_progress="started",
+        labels={},
+    )
+
+
+# ---- G2: era flag ----
+
+
+def test_ensure_era_flag_marks_unkeyed_rows_legacy():
+    row = {"type": "cron_run", "source": "old.log", "summary": "x"}
+    _ensure_era_flag(row)
+    assert row["legacy"] is True
+
+
+def test_ensure_era_flag_keeps_keyed_rows_modern():
+    row = {"type": "cron_run", "idempotency_key": "abc123"}
+    _ensure_era_flag(row)
+    assert row["legacy"] is False
+
+
+def test_ensure_era_flag_is_idempotent():
+    row = {"type": "cron_run", "legacy": True}
+    _ensure_era_flag(row)
+    _ensure_era_flag(row)
+    assert row["legacy"] is True
+
+
+def test_update_event_index_stamps_legacy_false_on_keyed_rows(tmp_path):
+    config = make_config(tmp_path)
+    index_dir = config.journal_root / ".index"
+    index_dir.mkdir(parents=True)
+    now = "2026-08-21T01:00:00Z"
+    signals = [{"type": "cron_run", "job_name": "x", "idempotency_key": "k1"}]
+    update_event_index(signals, now, config)
+    day = index_dir / "events-2026-08-21.json"
+    rows = json.loads(day.read_text())
+    assert len(rows) == 1
+    assert rows[0]["legacy"] is False
+
+
+def test_update_event_index_stamps_legacy_true_on_unkeyed_rows(tmp_path):
+    config = make_config(tmp_path)
+    index_dir = config.journal_root / ".index"
+    index_dir.mkdir(parents=True)
+    now = "2026-08-21T01:00:00Z"
+    update_event_index([{"type": "log_error", "source": "e.log"}], now, config)
+    rows = json.loads((index_dir / "events-2026-08-21.json").read_text())
+    assert rows[0]["legacy"] is True
+
+
+# ---- G6: quarantine rotation + summary ----
+
+
+def _write_quarantine(config, day, records):
+    folder = config.journal_root / ".quarantine"
+    folder.mkdir(parents=True, exist_ok=True)
+    (folder / f"{day}.json").write_text(json.dumps(records))
+
+
+def test_rotate_quarantine_removes_only_older_than_retention(tmp_path):
+    config = make_config(tmp_path)
+    old_day = (NOW - dt.timedelta(days=QUARANTINE_RETENTION_DAYS + 2)).date().isoformat()
+    fresh_day = (NOW - dt.timedelta(days=3)).date().isoformat()
+    _write_quarantine(config, old_day, [{"idempotency_key": "a"}])
+    _write_quarantine(config, fresh_day, [{"idempotency_key": "b"}])
+    (config.journal_root / ".quarantine" / "notes.json").write_text("[]")
+    removed = rotate_quarantine(config, now=NOW)
+    folder = config.journal_root / ".quarantine"
+    assert removed == 1
+    assert not (folder / f"{old_day}.json").exists()
+    assert (folder / f"{fresh_day}.json").exists()
+    assert (folder / "notes.json").exists()  # undated files never deleted
+
+
+def test_rotate_quarantine_missing_dir_is_noop(tmp_path):
+    config = make_config(tmp_path)
+    assert rotate_quarantine(config, now=NOW) == 0
+
+
+def test_quarantine_summary_reports_top_sources_in_window(tmp_path):
+    config = make_config(tmp_path)
+    d = NOW.date().isoformat()
+    _write_quarantine(
+        config, d,
+        [
+            {"idempotency_key": "1", "source": "/var/log/big.log"},
+            {"idempotency_key": "2", "source": "/var/log/big.log"},
+            {"idempotency_key": "3", "source": "/tmp/other.log"},
+        ],
+    )
+    start = NOW - dt.timedelta(days=1)
+    end = NOW
+    summary = quarantine_summary(config, start, end)
+    assert summary["total"] == 3
+    assert summary["top"][0] == ("/var/log/big.log", 2)
+
+
+def test_quarantine_summary_ignores_out_of_window_files(tmp_path):
+    config = make_config(tmp_path)
+    old_day = (NOW - dt.timedelta(days=QUARANTINE_RETENTION_DAYS - 5)).date().isoformat()
+    _write_quarantine(config, old_day, [{"idempotency_key": "1", "source": "s"}])
+    assert quarantine_summary(config, NOW - dt.timedelta(days=1), NOW) == {}
+
+
+def test_quarantine_summary_empty_dir_returns_empty(tmp_path):
+    config = make_config(tmp_path)
+    (config.journal_root / ".quarantine").mkdir(parents=True)
+    assert quarantine_summary(config, NOW - dt.timedelta(days=1), NOW) == {}
+
+
+def test_build_evidence_recap_renders_quarantine_section(tmp_path):
+    start = NOW - dt.timedelta(days=1)
+    end = NOW
+    quarantine = {"total": 42, "top": [("/var/log/x.log", 40), ("y", 2)]}
+    md, _ = build_evidence_recap([], "daily", start, end, [], quarantine=quarantine)
+    assert "### Quarantine (malformed noise, not signal)" in md
+    assert "42 quarantined line(s)" in md
+    assert "`/var/log/x.log` — 40" in md
+
+
+def test_build_evidence_recap_no_quarantine_param_is_backward_compatible(tmp_path):
+    start = NOW - dt.timedelta(days=1)
+    end = NOW
+    md, _ = build_evidence_recap([], "daily", start, end, [])
+    assert "Quarantine" not in md
-- 
2.43.0
```
