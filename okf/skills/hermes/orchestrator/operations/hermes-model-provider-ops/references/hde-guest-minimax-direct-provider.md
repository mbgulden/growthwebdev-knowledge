# HDE guest bot direct MiniMax provider pattern

Use this when Human Design Engine guest/deconditioning bot containers should run on Michael's direct MiniMax API rather than MiniMax via OpenRouter.

## Durable lesson

MiniMax model slugs differ by route:

- OpenRouter route: `provider: openrouter`, model like `minimax/minimax-m3`.
- Direct MiniMax route in Hermes: `provider: minimax`, model `MiniMax-M3`.

If Michael says “use our MiniMax API, not OpenRouter,” do **not** use OpenRouter model IDs even if they smoke-test successfully.

## Guest container wiring checklist

1. Hermes guest config should contain:

```yaml
model:
  provider: minimax
  default: MiniMax-M3
```

2. Container env should pass the direct MiniMax key:

```yaml
environment:
  - MINIMAX_API_KEY=${GUEST_MINIMAX_API_KEY}
```

3. The orchestrator/env generator should derive:

```python
GUEST_MINIMAX_API_KEY={os.getenv("GUEST_MINIMAX_API_KEY") or os.getenv("MINIMAX_API_KEY", "mock_minimax_api_key")}
```

4. Do not keep `OPENROUTER_API_KEY` in the guest env for this route.

## Dependency pitfall

Hermes' direct MiniMax provider uses the Anthropic-compatible route. Guest images need the Anthropic SDK installed, e.g. in the Dockerfile:

```dockerfile
RUN pip install --no-cache-dir \
    "hermes-agent[web,pty]" \
    ... \
    "anthropic>=0.39.0"
```

If explicit direct MiniMax fails with:

```text
The 'anthropic' package is required for the Anthropic provider
```

install/add `anthropic>=0.39.0` and rebuild/reprovision the guest container.

## Verification shape

Use an ad-hoc `/tmp/hermes-verify-*` script and label it ad-hoc, not full suite green. Check:

- Dockerfile declares `anthropic>=0.39.0`.
- Guest container has `anthropic` importable.
- Guest has `MINIMAX_API_KEY` and lacks `OPENROUTER_API_KEY`.
- Guest config shows `provider: minimax` and `default: MiniMax-M3`.
- Explicit guest smoke passes:

```bash
sudo docker exec guest-hermes-3 sh -lc 'timeout 150 hermes --provider minimax --model MiniMax-M3 -z "Reply with only: ok"'
```

- Routed guest endpoint returns a non-error response:

```bash
ip=$(sudo docker inspect --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' guest-hermes-3)
curl -sS --max-time 180 -X POST "http://${ip}:8000/api/message" \
  -H 'Content-Type: application/json' \
  -d '{"text":"For a staging smoke test, reply with one short grounding cue and nothing else."}'
```

Treat this as a reusable pattern, not proof for every future deployment; rerun against the current guest/container before claiming fixed.
