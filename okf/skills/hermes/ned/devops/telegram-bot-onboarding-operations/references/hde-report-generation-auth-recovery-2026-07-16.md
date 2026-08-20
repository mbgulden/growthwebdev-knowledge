# HDE report-generation auth recovery — 2026-07-16

## Durable lesson

A user-facing “report server authorization error” from the HDE guest bot is not always a bad API key. In this session the report server key path was valid, but the short follow-up `Yes pdf report` fell through to the LLM path instead of the deterministic chart/report tool. The LLM then described an auth failure even though `/api/compute` accepted the guest container key.

## Diagnostic pattern

1. Check report-server key parity without printing values:
   - staging `.env` `HDE_API_KEY` hash/length
   - production/reports service `HDE_API_KEY` hash/length
   - guest container runtime `HDE_API_KEY` hash/length
2. Probe from inside the affected guest container:
   - POST to `http://host.docker.internal:8081/api/compute`
   - Header: `X-API-Key: $HDE_API_KEY`
   - Expect `200` and `success: true` with `pdf_path`.
3. Inspect guest logs for whether the request actually called the deterministic chart/report path or simply asked the LLM to respond.
4. If direct report auth succeeds but the bot reports auth failure, treat it as routing/fallback confusion, not credentials.

## Fix pattern

Add a deterministic PDF/report follow-up handler before LLM fallback:

- Match short follow-ups like `pdf report`, `yes pdf report`, `report please`.
- If a stored profile has birth details, rebuild/generate from that profile and return `pdf_path`/`pdf_paths` metadata.
- If no profile exists yet, scan recent user turns for a complete birth-detail sentence and persist/generate from that.
- Keep API keys in env only; never print or embed them.

## Verification recipe

Use focused ad-hoc verification, not suite-green language:

1. Compile the guest runtime.
2. From `guest-hermes-<id>`, POST directly to reports `/api/compute`; expect `200`, `success: true`, `pdf_path` present.
3. POST to the guest `/api/message` with `Yes pdf report`; expect response `200`, `pdf_path` true, `pdf_paths >= 1`, and a successful chart-generation marker.
4. Check that router media upload can see the returned PDF path.
5. Secret-scan changed docs/runtime for token/API-key-shaped values.

## Pitfalls

- Do not rotate or rewrite report API keys until direct guest-to-report auth fails.
- Do not trust the LLM’s “auth error” text as the source of truth. Verify the transport path.
- Do not let short follow-ups after a chart request fall through to generic LLM handling; they are operational commands.
- When copying patched guest runtime into containers, update the path actually imported by the running service. In this stack `/workspace/guest_agent_server.py` can shadow `/app/guest_agent_server.py`.