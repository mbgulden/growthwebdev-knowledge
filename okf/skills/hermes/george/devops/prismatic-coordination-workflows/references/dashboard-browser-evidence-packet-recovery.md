# Dashboard browser evidence packet recovery

Use when a Prismatic dashboard/dashboard-adapter candidate is source-clean but independent review rejects the browser/evidence packet.

## Durable lesson

Do not treat a screenshot, tab count, or route smoke as a sufficient dashboard evidence packet. For dashboard acceptance/review, the packet must be reviewable without trusting the producer's browser session.

## Required evidence when repairing a rejected packet

1. Bind to exact candidate head/tree and prove source unchanged since the rejected review.
2. Start the exact installed artifact or exact candidate server from the intended import/runtime path.
3. If the dashboard deep link previews repository/workspace files, configure the server with the intended allowed read-only workspace root before capture; a 404 caused by wrong root is evidence setup failure, not candidate proof.
4. Capture full, untruncated DOM/status text for every canonical dashboard tab. Do not use `.slice()`, byte caps, or summarized DOM for authoritative review evidence.
5. For each tab, record:
   - tab name/label/heading;
   - visible text byte count;
   - API request URLs;
   - network records;
   - actual JSON source fields extracted from response bodies;
   - classification constrained to `REAL_SOURCE`, `CLEARLY_LABELLED_INTERIM/SAMPLE/NO-OP`, or `UNLABELLED/UNPROVEN`.
6. For every API request, record both `request_url` and originating `pageUrl`, plus a structured initiator (`type`, document URL, frame URL, navigation flag). Require this even when there are zero non-2xx failures in the corrected capture.
7. Prove adapter parity from the dashboard page, not just direct curl: repaired gateway/adapter requests should be HTTP 200 and attributed to `/dashboard` page activity.
8. For Telemetry or similar tabs, require distinct actual response sources for each subsystem being represented; do not accept a generic tab label as source proof.
9. For workspace deep links, prove selected-file text and rendered preview body are both present and simultaneously visible in the mobile viewport; also capture preview endpoint HTTP 200 records.
10. Record mobile viewport, DPR, and physical PNG dimensions. If horizontal overflow remains, compare to current production and disclose it as a boundary/non-regression rather than claiming full overflow elimination.
11. Freeze a stable packet directory with ledger excluding itself; include screenshots, JSON proof, verifier log, receipt, carried canonical/focused/wheel logs, and explicit nonclaims.
12. Run a focused post-packet verifier that reads the frozen packet back, checks the ledger, validates schema/classifications/initiators/deep-link/mobile dimensions, and removes temporary verifier scripts.

## Review boundary language

```text
PRODUCER_STATUS=<failed|completed>
SOURCE_CHANGED_AFTER_REVIEW=false
EVIDENCE_PACKET=<path>
LEDGER_SHA256=<sha>
AD_HOC_OR_CANONICAL=ad-hoc focused evidence packet
NOT_CLAIMING=independent review, merge, deploy, live acceptance, canonical rerun unless actually rerun
```

If a previous packet was rejected, say so directly: `V<N>_REVIEW=BLOCKED evidence only`; do not overwrite history or call the old packet authoritative.
