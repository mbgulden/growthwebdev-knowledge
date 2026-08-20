# Direct MiniMax guest bot wiring — 2026-07

Use this when wiring Hermes guest/container bots to Michael's direct MiniMax API rather than MiniMax through OpenRouter.

## Desired route

For guest Hermes config:

```yaml
model:
  provider: minimax
  default: MiniMax-M3
```

Do **not** use OpenRouter slugs such as `minimax/minimax-m3` when the user asks for “our MiniMax API”. That means the direct Hermes `minimax` provider.

## Required environment

Container/runtime env should include:

```bash
MINIMAX_API_KEY=...
```

and should not need:

```bash
OPENROUTER_API_KEY=...
```

If provisioning is generated from a host orchestrator, propagate either `GUEST_MINIMAX_API_KEY` or `MINIMAX_API_KEY` into the guest `.env`, then expose it in compose as `MINIMAX_API_KEY`.

## Dependency pitfall

Hermes' direct MiniMax provider can use the Anthropic-compatible API path. Minimal guest images may need the Anthropic SDK installed even though the model is MiniMax:

```dockerfile
RUN pip install --no-cache-dir \
    "hermes-agent[web,pty]" \
    ... \
    "anthropic>=0.39.0"
```

Verify this in the rebuilt container:

```bash
python3 -c "import importlib.util, os; print(importlib.util.find_spec('anthropic') is not None); print(bool(os.environ.get('MINIMAX_API_KEY'))); print(bool(os.environ.get('OPENROUTER_API_KEY')))"
```

Expected:

```text
anthropic installed: True
MINIMAX_API_KEY present: True
OPENROUTER_API_KEY present: False
```

## Verification pattern

Use both explicit provider smoke and the real routed bot path:

```bash
hermes --provider minimax --model MiniMax-M3 -z "Reply with only: ok"
```

Expected:

```text
ok
```

Then call the guest service path that the router uses, for example:

```bash
curl -sS -X POST "http://$GUEST_IP:8000/api/message" \
  -H 'Content-Type: application/json' \
  -d '{"text":"For a staging smoke test, reply with one short grounding cue and nothing else."}'
```

Expected: non-empty model response without `HTTP 401` and without `No models provided`.

## Reporting

Say “direct MiniMax API” only when both are true:

1. guest config says `provider: minimax` / `MiniMax-M3`;
2. guest env has `MINIMAX_API_KEY` and lacks OpenRouter dependency for that route.

If checkout/Telegram/provisioning is also in scope, keep those as separate verification lanes; a direct MiniMax model smoke is not proof of the whole product flow.