# Canonical evidence-cited recap pattern

Use this for Prismatic journal event indexes rather than treating raw inbox prose as the source of truth.

## Contract

- Load only normalized event index files that fall within a UTC daily or ISO-week window.
- Each rendered historical claim must cite a stable event key: `E:<idempotency-key-prefix>`.
- Redact the rendered detail before output.
- Render a deterministic draft first. Any later LLM synthesis may use **only** the cited event IDs; do not let it introduce unsupported claims.
- Quiet windows produce an explicit “no accepted normalized events” statement.

## Scheduler truth separation

Historical `cron_run` events describe what happened then. They do **not** define present service health. Read current scheduler records separately (`enabled`, `last_status`, job name) and label that section “Live scheduler health.” A historical failure followed by a current `ok` must render as current `ok`, not a persistent current failure.

## Verification

Test at least:

1. Daily citation and redaction.
2. Historical cron failure + current live `ok` separation.
3. Quiet-day output.
4. UTC weekly boundary (Monday start) with an injected clock.
5. CLI/API output points to the persisted recap artifact.

When CI dependency drift is involved, reproduce the release install surface in a clean venv before accepting a PR; do not rely only on ambient tool versions.
