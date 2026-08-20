# Local custom provider wiring — Kai/Ned on VM 230 (worked example)

Session: 2026-08-15. Worked end-to-end on webtop-hermes driving a K3s cluster running on PVE1 VM 230 (`192.168.1.230`). Qwen 3.8 27B Q4_K_M served by two `llama-server` pods, one per GPU (Kai=GPU 2, Ned=GPU 3), exposed via NodePort 31002 / 31003.

## Topology

```
webtop-hermes (orchestrator)
  └─ HermeS profile: kai  ────► http://192.168.1.230:31002/v1  (kai pod, GPU 2)
  └─ HermeS profile: ned  ────► http://192.168.1.230:31003/v1  (ned pod, GPU 3)
                                    │
                                    ▼
                              VM 230 (k3s-node-230)
                                ├─ kai-llama pod  (nvidia.com/gpu: 1, NVIDIA_VISIBLE_DEVICES=2)
                                └─ ned-llama pod  (nvidia.com/gpu: 1, NVIDIA_VISIBLE_DEVICES=3)
                                      │
                                      ▼
                              PVE1 hostpci0/1/2/3 → 4x RTX 3090
```

## K8s side — what already had to be true before this skill applies

The `llama-server` pods must already be:
- 1/1 Running (verify via `kubectl get pods -n llm-inference`)
- GPU actually allocated (verify via `nvidia-smi` inside the VM: ~18 GiB on the assigned GPU)
- Service reachable from the orchestrator host (`curl http://<node-ip>:<nodeport>/v1/models` returns the alias)

If any of those are false, this skill is the wrong layer. Fix the K8s deployment first (see `proxmox-k3s-gpu-cluster-ops`).

## Per-profile `config.yaml` patch

Edit `~/.hermes/profiles/<profile>/config.yaml`. Two changes:

### 1. Set the model block to the local provider

```yaml
model:
  default: local-qwen-27b-q4-kai
  provider: custom:qwen27b-kai-local
```

### 2. Define the provider in the `providers:` block

```yaml
providers:
  qwen27b-kai-local:
    name: Qwen 27B Q4_K_M on VM 230 (GPU 2)
    api: http://192.168.1.230:31002/v1
    api_key: local                      # required; any non-empty string
    default_model: local-qwen-27b-q4-kai
    models:
      local-qwen-27b-q4-kai:
        context_length: 32768
    context_length: 32768
    request_timeout_seconds: 600
```

### 3. Keep the previous provider as fallback

```yaml
fallback_providers:
- provider: openai-codex
  model: gpt-5.6-terra
```

For Ned, substitute `ned` everywhere above and use port 31003.

## Verification sequence (no shortcuts)

```bash
# 1. Endpoint reachable
curl -s http://192.168.1.230:31002/v1/models | jq '.data[].id'
# expected: "local-qwen-27b-q4-kai"

# 2. Chat completion works
curl -s -X POST http://192.168.1.230:31002/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"local-qwen-27b-q4-kai","messages":[{"role":"user","content":"Reply with only OK"}],"max_tokens":10,"temperature":0}' \
  | jq -r '.choices[0].message.content'
# expected: "OK"

# 3. Profile config takes the new provider
python3 -c "import yaml; print(yaml.safe_load(open('/home/ubuntu/.hermes/profiles/kai/config.yaml'))['model'])"
# expected: {'default': 'local-qwen-27b-q4-kai', 'provider': 'custom:qwen27b-kai-local'}

# 4. Restart the gateway (config changes are not hot-reloaded)
# Follow the per-profile restart procedure in operations/hermes-model-provider-ops.

# 5. Send a real Telegram message to the profile's bot and verify the response
# went via the local endpoint. Watch for the inference latency (should be ~37 tok/s)
# matching the local model speed, not the upstream API latency.
```

A `/tmp/hermes-verify-local-provider.py` script that exercises steps 1–4 (plus reads back the model block) is the standard deliverable. Exit 0 only if every check passes.

## Pitfalls hit this session (and how to avoid them)

- **Container hostname vs LAN IP**: `localhost` in the provider `api` URL points at the gateway container, not the GPU host. Use the LAN IP of the VM that owns the GPU.
- **Missing `api_key`**: schema rejects it. Pass any non-empty string when the upstream is unauthenticated.
- **`model.default` mismatch**: the `default_model` in the provider block must match a key under `models:`. If they don't, the picker shows the previous model and the default is silently unreachable.
- **`request_timeout_seconds` too low**: defaults leave the gateway timing out on long completions. Bump to 600+ for local LLMs.
- **Forgetting the gateway restart**: the per-profile gateway caches the model at startup. The config edit is not picked up until restart. The wrong-default failure mode is silent (the gateway uses the previous model and you don't see an error).
- **`api: ...` must end in `/v1`**: Hermes appends `/chat/completions` itself. If the URL ends in `/v1/`, the request becomes `/v1/chat/completions/chat/completions` and 404s.

## Cross-references

- `proxmox-k3s-gpu-cluster-ops` — getting the K3s/GPU pods up in the first place
- `hermes-model-provider-ops` — the parent skill (this reference lives under it)
