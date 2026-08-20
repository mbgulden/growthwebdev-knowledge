# Shared API Budget / Cooldown Remediation Pattern — 2026-07-08

## When this applies

Use this for recurring cron/supervisor/daemon failures where an external shared API quota is exhausted even though a budget system supposedly exists.

## Root-cause pattern

The durable lesson is not "Linear is broken." The failure mode was architectural:

- The system had a budget DB and an event-driven path.
- Live scripts still had direct `urllib` GraphQL calls and polling fallback paths.
- Those direct calls bypassed the budget DB, so local budget telemetry looked quiet while the real tenant quota burned down.

## Remediation workflow

1. **Inventory active callers, not just source files**
   - Search for raw API URL, API key env names, and mutation/query names.
   - Check active processes and cron scripts to find which copies are live.
   - Identify whether each caller is canonical provider, compatibility wrapper, one-shot migration, live daemon, test, or archival.

2. **Find the lowest shared execution path**
   - Patch the canonical provider/client if one exists.
   - If live profile scripts still bypass it, add a temporary compatibility wrapper that fails closed rather than making unmetered calls.

3. **Use one shared tenant bucket**
   - Per-agent buckets can still overrun a provider-level tenant quota if each starts with a full quota.
   - For tenant-scoped APIs, use a shared `global` bucket or equivalent before network.

4. **Add cooldown on real provider 429**
   - On HTTP 429, write a local cooldown marker with retry time.
   - All follow-up callers must check the cooldown marker before network.
   - This prevents retry storms from worsening the outage.

5. **Demote polling to a safety net**
   - Event-driven paths may still keep polling fallback, but it must be slow, budget-gated, observable, and configurable.
   - Verify CLI interval flags are actually applied, not merely printed.

6. **Verify with no real API calls**
   - Build `/tmp/hermes-verify-*` fixture tests that monkeypatch the network layer.
   - Assert budget is consumed before network.
   - Assert budget exhaustion blocks before network.
   - Assert 429 writes cooldown.
   - Assert cooldown blocks before network.
   - Assert wrappers share the same global budget.

## Evidence language

```text
Ad hoc targeted verification: PASS — not full-suite green.
- Fixture made 0 real API calls.
- Budget consumed before fake network call.
- Fake 429 wrote cooldown marker.
- Cooldown blocked follow-up without network.
```

## Pitfalls

- Do not record a durable memory that an API/tool is broken; capture the budget/cooldown pattern instead.
- Do not trust budget telemetry until you prove every live caller uses the budget path.
- Do not post evidence to the same exhausted API while the cooldown marker is active; save a local evidence comment.
- Do not call scheduler `last_status=ok` sufficient if the underlying daemon is restarting or bypassing budget.
