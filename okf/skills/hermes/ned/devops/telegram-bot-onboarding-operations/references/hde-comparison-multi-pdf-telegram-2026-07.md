# HDE comparison Telegram multi-PDF wiring — 2026-07

## Trigger

George/HDE progressive comparison worked through Telegram and generated both Person 1 and Person 2 chart artifacts, but Telegram uploaded only one PDF.

## Root cause

The guest API returned a single `pdf_path`, and `hde_tenant_router.enqueue_media_upload()` only knew how to enqueue one `pdf_path`/`image_path`. Comparison flows generate multiple chart documents, so the router needed list support.

## Durable fix pattern

1. In `guest_agent_server.py`, keep progressive deterministic comparison intake:
   - `I want to compare two charts` → ask Person 1 birth date only.
   - collect Person 1 date/time/location, generate chart.
   - collect Person 2 date/time/location, generate chart.
2. Add a helper like `list_chart_pdfs(relationship_type, "person_1", "person_2")` to return the latest PDF for each comparison subject.
3. Return both the legacy `pdf_path` and the list form `pdf_paths` from `/api/message`; keep single-chart compatibility.
4. In `hde_tenant_router.py`, make `enqueue_media_upload()` accept both singular and plural fields:
   - `image_path`
   - `image_paths`
   - `pdf_path`
   - `pdf_paths`
5. De-duplicate `(kind, host_path)` before enqueueing media so singular + plural compatibility does not double-send the same file.
6. Verify through both layers:
   - direct guest API returns two `/workspace/charts/friends/person_*/...pdf` paths;
   - router logs show Telegram `sendDocument 200 OK` for each queued PDF during a live Telegram canary.

## Focused verification recipe

Use a `/tmp/hermes-verify-*` script that:

- compiles `guest_agent_server.py` and `hde_tenant_router.py`;
- confirms services are active (`hde-reports`, orchestrator, router);
- runs a direct guest comparison canary against a non-primary guest container if possible;
- asserts final response includes Person 1/Person 2 and practical experiment language;
- asserts `pdf_paths` length is 2;
- asserts 2 PDFs, 2 `coach_manifest.json`, and 2 `chart_generated` events exist;
- cleans `conversation_state.json`, fake chart folders, and `coach_view` canary files afterward.

## Pitfall

A live Telegram canary that sends a summary plus one document is not complete for comparison flows. It proves text routing and one media upload, not multi-artifact delivery. Check for both queued/uploaded PDFs.