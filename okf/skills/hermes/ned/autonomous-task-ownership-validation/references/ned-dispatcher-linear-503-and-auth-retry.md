# Ned dispatcher Linear 503 + auth retry pattern

Use when a cron wakeup reports:

```text
[ERROR] Ned dispatcher wakeup failed: Linear API error 503: upstream connect error or disconnect/reset before headers. reset reason: connection termination
```

## Durable lesson

A Linear 503 during Ned's data-collection script is not proof the queue is blocked or that credentials are missing. Treat it as a transient upstream failure first, then manually re-query Linear before deciding whether any task is executable.

## Recovery sequence

1. Load Linear credentials from Ned's profile backup when needed:
   ```bash
   set -a
   source /home/ubuntu/.hermes/profiles/ned/.env.bak
   set +a
   echo ${#LINEAR_API_KEY}   # expected: 48
   ```
2. For manual Linear GraphQL calls with `LINEAR_API_KEY`, send the key directly in `Authorization`; do **not** prefix `Bearer`.
   - `Authorization: $LINEAR_API_KEY` works for API keys.
   - `Authorization: Bearer $LINEAR_API_KEY` returns Linear `400`: "trying to use an API key as a Bearer token".
3. Re-query the current `agent:ned*` queue and apply ownership validation before acting.
4. If all returned issues carry `agent:needs-human-review` and/or `requires:human-approval`, report `0 autonomous-executable` and do not run `finalize_task.sh`.
5. Report the original script failure as a transient dispatcher wakeup failure plus the manual verification result. Do not create fake progress just to satisfy the cron skeleton.

## Why this matters

The dispatcher script may internally expect an OAuth token, while the profile backup contains a Linear API key. Manual recovery should use the credential's native auth shape rather than forcing it into the script's Bearer-token path. That lets Ned distinguish a transient Linear outage from a real executable task queue.