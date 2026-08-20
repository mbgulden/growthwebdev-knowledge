---
name: vision-and-auxiliary-routing-2026-08.md
---

# Vision and auxiliary routing: 2026-08 lesson bundle

Session-specific detail for the Qwen3.8-27B vision enablement + auxiliary.vision re-routing that happened in the August 2026 GPU cluster ops burst. **Read `../../proxmox-k3s-gpu-cluster-ops/SKILL.md` first; this file adds three concrete pitfalls to those anti-patterns.**

## Pitfall: A "local llama-server with vision" is NOT the same as "vision routed through local llama-server"

The local server can be fully multimodal-capable (running with `--mmproj .../mmproj-F16.gguf`, advertising `capabilities: ["completion", "multimodal"]`, accepting `image_url` content and producing accurate image descriptions) **and** Hermes can still send every Telegram image to GPT/OpenRouter because Hermes has its **own** routing block that the local server doesn't know about.

**Three-layer wiring required:**

1. **Local server running with multimodal support:** `--mmproj <path>` flag on `llama-server`, mmproj file present at the path, model loads cleanly. Verify with `curl -s http://<host>:<port>/v1/models | jq '.data[0].capabilities'` showing `multimodal`.

2. **Main model routed to local in Hermes:** `model.default` and `model.provider` in `~/.hermes/profiles/<profile>/config.yaml` pointing at the custom local provider. This routes **chat** to local.

3. **Auxiliary vision routed to local in Hermes:** `auxiliary.vision.provider` / `model` / `base_url` in the same config, pointing at the same custom local provider. This routes **Telegram image attachments, document screenshots, etc.** to local.

Without step 3, the local multimodal capability is invisible to Hermes, and the agent reports "vision API failed" the moment cloud auth drifts (rates, OAuth expiry).

## Pitfall: Three caps to prevent slot monopolization

**Layer 1 — Server-side (`--n-predict`):** `--n-predict 4096` on the `llama-server` command line. Caps the maximum generated tokens per request when the client doesn't specify `max_tokens`.

**Layer 2 — Client request (`max_tokens`):** Set per request. Hermes configures this via `provider.max_tokens` in the profile.

**Layer 3 — Server-side runtime cap via llm-server params:** Some newer llama.cpp builds treat `max_tokens = -1` as unlimited; you may also need `--n-predict 4096` even when the client sends `max_tokens`.

Without all three layers set, a single reasoning-mode Qwen3 request can run for several minutes (`n_remain = 64705` observed in a real session) and monopolize the only available slot, blocking all subsequent requests.

**Verify all three layers are set:**

```bash
# Layer 1: server flag
sshpass -p proxmox123 ssh root@192.168.1.2 "qm guest exec 230 -- bash -c 'ps -ef | grep llama-server'"
# Look for: --n-predict 4096 OR equivalent cap mechanism

# Layer 2: Hermes provider config
python3 -c "import yaml; cfg = yaml.safe_load(open('/home/ubuntu/.hermes/profiles/kai/config.yaml')); print(cfg['providers']['qwen27b-kai-local'].get('max_tokens', 'MISSING'))"
# Expect: 4096

# Layer 3: observed at runtime
sshpass -p proxmox123 ssh root@192.168.1.2 "qm guest exec 230 -- bash -c 'curl -s http://localhost:31002/slots | python3 -c \"import json,sys; d=json.load(sys.stdin); print(d[0].get(\\\"params\\\",{}).get(\\\"max_tokens\\\",\\\"-1\\\"))\"'"
# Expect: 4096 (NOT -1)
```

If layer 3 returns `-1`, the gate is open and a runaway reasoning pass is one bad prompt away.

## Pitfall: Pushing vision through Hermes, not just through the local server

When a Hermes agent says "the vision API is throwing errors", the data flow is:
- Telegram attaches an image to a message.
- Hermes extracts the image and routes it through `auxiliary.vision`.
- If `auxiliary.vision.provider` is `openai-codex`, the image goes to chatgpt.com via OAuth.
- If OAuth is rate-limited or stale, the request fails, agent reports "vision failed".

**The fix is in `~/.hermes/profiles/<profile>/config.yaml`** under `auxiliary.vision`, not in the local server. Point all three (`provider`, `model`, `base_url`) at the local custom provider. Verify with:

```bash
python3 -c "
import yaml
cfg = yaml.safe_load(open('/home/ubuntu/.hermes/profiles/kai/config.yaml'))
v = cfg.get('auxiliary', {}).get('vision', {})
print('provider:', v.get('provider'))
print('model:', v.get('model'))
print('base_url:', v.get('base_url'))
"
# Expect: provider='custom:qwen27b-kai-local', model='local-qwen-27b-q4-kai',
#         base_url='http://192.168.1.230:31002/v1'
```

A correct setup shows all three pointing at the local custom provider. A broken setup shows `provider='openai-codex'` or similar cloud provider.

## Qwen3.8-27B specifics (for context)

The Qwen3.8-27B model from `unsloth/Qwen3.8-27B-GGUF` is multimodal-capable (the model card on Hugging Face reports `pipeline_tag: image-text-to-text` and the architecture description includes "vision-language model"). A multimodal projector (`mmproj-F16.gguf`, ~927 MB) is required alongside the language weights.

**Required serving stack:**
- Language model: `Qwen3.8-27B-Q4_K_M.gguf` (~17 GB) or `Qwen3.8-27B-Q5_K_M.gguf` (~19 GB)
- Vision adapter: `mmproj-F16.gguf` (~927 MB)
- llama.cpp build with `qwen35` architecture support (commit `6b4344e` / build `b5368` confirmed working)
- `--mmproj` CLI flag pointing at the vision adapter

**Download commands (run once per VM):**
```bash
mkdir -p /models/qwen3.8-27b-q4
cd /models/qwen3.8-27b-q4
wget -q https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/resolve/main/Qwen3.8-27B-Q4_K_M.gguf
wget -q https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/resolve/main/mmproj-F16.gguf
```

## Verification recipe: vision end-to-end

After enabling vision at all three layers, run a real test that exercises:
1. Synthetic image generation (PIL or ImageMagick)
2. base64-encode → data URL in the request
3. Live prompt to the local endpoint
4. Check content for accurate description of the synthetic image

```python
import base64, json, urllib.request
from PIL import Image, ImageDraw

# Generate a recognizable synthetic image
img = Image.new('RGB', (256, 256), (128, 0, 128))
ImageDraw.Draw(img).ellipse([40, 40, 216, 216], fill=(0, 255, 255))
img.save('/tmp/test-image.jpg', 'JPEG', quality=85)

# Send with image_url content type
with open('/tmp/test-image.jpg', 'rb') as f:
    b64 = base64.b64encode(f.read()).decode()
data = json.dumps({
    "model": "local-qwen-27b-q4-kai",
    "messages": [{"role": "user", "content": [
        {"type": "text", "text": "Describe this image. What colors and shapes do you see?"},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
    ]}],
    "max_tokens": 1500,
    "temperature": 0.1
}).encode()
req = urllib.request.Request(
    "http://localhost:31002/v1/chat/completions",
    data=data, headers={"Content-Type": "application/json"}
)
import time
t0 = time.time()
resp = urllib.request.urlopen(req, timeout=60)
d = json.loads(resp.read())
print(f"OK {time.time()-t0:.1f}s content={d['choices'][0]['message']['content']}")
```

**Pass criteria:**
- HTTP 200 in 4-8 seconds
- Content describes the purple background and cyan circle accurately
- `timings.prompt_ms` is 400-1000ms (vision preprocessing)
- `usage.completion_tokens` is non-zero (model actually produced output)

A failure here despite the local server being multimodal-capable means one of the three wiring layers (server flag, main model routing, auxiliary vision routing) is missing.

## Aug-2026 specific model + driver + llama.cpp notes

- **Qwen3.8-27B size:** Q5_K_M = 19.83 GB (CF: HF X-Linked-Size); Q4_K_M = 17.10 GB
- **MMProj size:** F16 = 927 MB; BF16 = 931 MB. Same content in practice; F16 is the canonical llama.cpp default.
- **VRAM budget for vision + ctx = 262144 with kv q4_0:**
  - Weights: 17-19 GB
  - KV cache: 3.4 GB
  - mmproj on GPU: ~1 GB
  - Total: ~22-24 GB per card
  - Plan for 96% VRAM utilization on a single 24 GB card.
- **llama.cpp build:** upstream `ggml-org/llama.cpp` post-b5368 supports `qwen35` architecture. Older Ollama-forked builds (e.g. the one vendored at the time of writing in 2026-04 Ollama releases) do NOT support `qwen35moe` for vision. Use upstream.
- **YARN scaling:** `--ctx-size 524288` with `--rope-scaling yarn --yarn-orig-ctx 262144 --yarn-ext-factor 2.0` is **silently capped at 262144** in llama.cpp b5368. The YARN validation in older builds does NOT extend `n_ctx_train`. Fix: stay at 262144. (Math: ~40 GB KV+weights for 1M ctx — physically won't fit on 4×24 GB anyway.)

## Layered verification script template

When a future session has to verify that local vision routing is fully wired, the script should hit these in order:

1. Server reaches multimodal: `curl -s .../v1/models | jq '.data[0].capabilities'`
2. Server actually does vision: synthetic image + vision test request (above)
3. Hermes main model is local: `python3 -c "..."` reads `model.provider` from config
4. Hermes auxiliary vision is local: same for `auxiliary.vision.provider`
5. Three caps are set: server `--n-predict`, provider `max_tokens`, observed `slots.params.max_tokens`
6. Vision preprocessing is fast: `timings.prompt_ms` is sub-second

A `hermes-verify-vision-262k-*.py` (with versioned suffix to avoid filename collisions across sessions) should land in `/tmp/` and exit 0/1 with clear evidence for all six checks. The non-obvious failure mode is 5: even when all configs are right, a request without `max_tokens` from Hermes falls back to the server's `-1` default until `provider.max_tokens` is set.
