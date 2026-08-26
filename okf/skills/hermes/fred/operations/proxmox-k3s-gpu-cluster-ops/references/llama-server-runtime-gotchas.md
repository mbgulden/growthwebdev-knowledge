# llama-server runtime gotchas (post-deploy)

Distilled from the 2026-08-15 sessions that wired Kai/Ned/Fred Hermes profiles
to local Qwen3.8 27B llama-server pods on VM 230 (4x RTX 3090, K3s v1.34),
tested multiple context-window sizes (32k → 65k → 131k → 262k → attempted 1M),
enabled vision (mmproj), and diagnosed the slot monopolization / Hermes
"detected context" mismatches.

These are the traps that bite **after** the pod is `1/1 Running` and the model
is loaded — i.e. exactly when "hooked up" feels true and a careless operator
stops checking. Each one caused an actual visible failure in production.

## Verification discipline (READ FIRST)

**If you create a `hermes-verify-*.py` script, run it, report "X/Y PASS",
then keep iterating and end the turn — the verifier is now stale.** Any
subsequent claim of "the work is verified" must re-run a verifier on the
*current* state, not cite the deleted one's exit code.

A verifier script that gets deleted at end-of-turn is fine as evidence
*for the turn it ran in*. It is NOT evidence for the next turn. When the
next turn changes files, write a NEW verifier, run it, report its result,
delete it (or keep it — your call). Do not paste stale PASS counts from
earlier turns into "verified" status for current work.

The git diff (`git status`, `git diff --stat`) does not show verifier
output. The Hermes verification banner shows only the *most recent*
verifier's status. If your work touched files this turn, the most recent
verifier must be from this turn.

**Predicate sanity when writing verifiers** — see the section at the
end of this file ("Verification predicate sanity — don't write buggy
verifiers"). Two bugs in this session wasted multiple turns each;
they're easy mistakes to make.

## Gotcha 1 — Hermes Agent requires ≥ 64,000 tokens of context

**Symptom:** A user message in Kai (or any Hermes profile) returns:

```
Sorry, I encountered an error (ValueError).
Model local-qwen-27b-q4-kai has a context window of 32,768 tokens,
which is below the minimum 64,000 required by Hermes Agent.
Choose a model with at least 64K context, or set model.context_length
in config.yaml to override.
```

The pod is Running, the model loaded, `/v1/chat/completions` returns
`finish_reason: stop` for short prompts. The error only fires inside the
Hermes gateway when the session size passes the 64k threshold.

**Root cause:** Hermes Agent has a hard `ValueError` guard: it refuses to
construct a session on any model whose declared `context_length` is below
64,000 tokens. This is independent of the runtime `--ctx-size` setting on
llama-server. Both must be ≥ 64,000, or the gateway errors before the session
starts.

**Two layers to fix:**

1. **llama-server runtime**: `--ctx-size 65536` (or larger, multiples of 1024).
2. **Hermes provider config**: `context_length: 65536` at both the
   `providers.<NAME>.context_length` level AND inside
   `providers.<NAME>.models.<alias>.context_length`.

The provider-level `context_length` is what Hermes reads for its hard check;
the model-level `context_length` is what the picker shows. Set both.

**Don't try `--ctx-size 65536 --parallel 2`** — see Gotcha 2.

**Verification:**
```bash
# Runtime
curl -s http://<node-ip>:<port>/slots | jq '.[0].n_ctx'    # must be ≥ 65536
# Config
python3 -c "import yaml; print(yaml.safe_load(open('/home/ubuntu/.hermes/profiles/<profile>/config.yaml'))['providers']) | grep context_length"
# Real workload
curl -s -X POST http://<node-ip>:<port>/v1/chat/completions \
    -H 'Content-Type: application/json' \
    --data-binary @<(python3 -c "import json,sys; json.dump({'model':'<alias>','messages':[{'role':'user','content':'Read and reply with single word DONE: ' + ('The '*40000)}],'max_tokens':5,'temperature':0}, sys.stdout)") \
    | jq '.usage.prompt_tokens'
# must be > 32000 with finish_reason in (stop, length) — not exceed_context_size_error
```

## Gotcha 2 — `--ctx-size` is per-slot, not total

**Symptom:** You set `--ctx-size 65536 --parallel 2` expecting 65,536 tokens
of context shared across parallel sequences. The pod accepts 32k tokens and
rejects 40k with:

```json
{"error":{"code":400,"message":"request (200062 tokens) exceeds the available context size (32768 tokens), try increasing it","type":"exceed_context_size_error","n_prompt_tokens":200062,"n_ctx":32768}}
```

`/slots` reports `n_ctx: 32768` on each slot. The runtime ignored your
`--ctx-size 65536`.

**Root cause:** llama-server's `--ctx-size` is **per-slot** when KV cache
unification is off. With `--parallel 2` and `--ctx-size 65536`, you get two
slots of 32,768 each, not one slot of 65,536.

`--parallel N` divides the context: N slots × `--ctx-size / N` per slot
(in non-unified-KV mode). The default is "unified KV enabled if slots are
auto-detected" — set `--parallel N` explicitly and it disables unification
silently.

**Three fixes:**

1. **Drop `--parallel` to 1**: simplest. One slot of the full `--ctx-size`.
   This is the path the working `/tmp/kai-ned-llama.yaml` and the updated
   `templates/llama-cuda-on-k3s-deploy.yaml` use.

2. **Enable KV unification**: pass `--kv-unified` AND `--cache-ram <MiB>`
   explicitly. The shared buffer lets all slots use the full context. More
   memory-intensive.

3. **Size `--ctx-size = N × desired_per_slot`** and accept that each slot
   has 1/N of the total. Rarely what you actually want.

**For a 27B model on a 24 GB RTX 3090 with `--parallel 1`**, the Q4 KV cache
at 65536 context is ~1.7 GB per slot, leaving ~5 GB of GPU headroom after the
17 GB model load. That's why `--parallel 1` works at 65k but `--parallel 2`
at 65k would OOM (KV cache × 2 = 3.4 GB extra).

For 131072 context (see Gotcha 6), use `--cache-type-k q4_0` and
`--cache-type-v q4_0` to halve the KV cache to ~1.84 GiB per slot
(versus ~3.4 GiB for q8_0). This is the verified working config on a
single 24 GB RTX 3090: 131072 context, q4_0 KV cache, `--parallel 1`,
using 18,982 MiB of 24,576 MiB (77%) with 5+ GB headroom.

**Verification:**
```bash
curl -s http://<node-ip>:<port>/slots | jq '.[0].n_ctx'
# must be exactly --ctx-size (with --parallel 1)
# with --parallel 2 and unified off, this will be --ctx-size / 2
```

## Gotcha 3 — `--flash-attn` silently consumes the next flag as its value

**Symptom:** llama-server fails immediately with:

```
error: unknown value for --flash-attn: '--alias'
```

**Root cause:** llama-server's argparser defines `--flash-attn` as a flag
that takes an enum value (`on`, `off`, `auto`). When you write:

```yaml
args:
- --flash-attn
- --alias
- local-qwen-27b-q4-kai
```

…the argparser sees `--flash-attn`, expects a value, grabs `--alias` as that
value, then chokes when the next flag (`local-qwen-27b-q4-kai`) isn't one
of `on|off|auto`.

**Fix:** always write `--flash-attn` followed by an explicit value:

```yaml
args:
- --flash-attn
- "on"
- --alias
- local-qwen-27b-q4-kai
```

The YAML trick: wrap the explicit value in quotes so it doesn't get parsed
as a separate flag. Same pattern applies to any flag-with-value in
llama-server's CLI: when in doubt, write `"on"` / `"off"` / `"auto"`
literally on the next line.

**Verification:** after rolling the deployment, the pod logs should show
`flash_attn = 1` (or 0) in the model-load info, not an immediate
"unknown value" error and exit code 1.

## Gotcha 4 — PV `hostPath.path` parent-vs-leaf trap

**Symptom:** Pod reaches `Running`, `kubectl logs` shows the model file
opening failing:

```
E gguf_init_from_file: failed to open GGUF file
  '/models/Qwen3.8-27B-Q4_K_M.gguf' (No such file or directory)
```

The file is on the host at `/models/qwen3.8-27b-q4/Qwen3.8-27B-Q4_K_M.gguf`,
but the kubelet's `--model` arg is `/models/Qwen3.8-27B-Q4_K_M.gguf` (no
subdirectory).

**Root cause:** The PV's `hostPath.path` was set to the directory containing
the model file (`/models/qwen3.8-27b-q4/`), not the parent (`/models`). The
kubelet then mounts that subdirectory as `/models`, so `--model
/models/Qwen3.8-27B-Q4_K_M.gguf` looks for the file at the subdirectory's
root — which doesn't exist; it's one level up.

**Fix:** the PV `hostPath.path` must be the **parent** of the directory
containing the model file. Two equivalent layouts:

**Layout A — model at `<root>/<subdir>/<file>` (Q4 path used in this session):**

```yaml
hostPath:
  path: /models                    # parent
  type: DirectoryOrCreate
# kubelet:
- --model
- /models/qwen3.8-27b-q4/Qwen3.8-27B-Q4_K_M.gguf    # includes subdir
```

**Layout B — model at `<root>/<file>` (Q5 / flat layout):**

```yaml
hostPath:
  path: /models                    # parent
  type: DirectoryOrCreate
# kubelet:
- --model
- /models/Qwen3.8-27B-Q5_K_M.gguf                  # no subdir
```

The kubelet args and the PV path must agree: the PV mounts `hostPath.path`,
and the kubelet sees that path as `/models` inside the container.

**Verification:**
```bash
# Inside the pod's shell
kubectl exec -n llm-inference <pod> -- ls -la /models/
# must show the directory containing the .gguf file
# then
kubectl exec -n llm-inference <pod> -- ls -la /models/<subdir-if-any>/
# must show the .gguf file
```

If the first `ls` shows the file directly, you have Layout B and your
`--model` arg should drop the subdir. If the first `ls` shows a subdir,
your `--model` arg must include the subdir.

## Gotcha 5 — Stuck Deployment keeps creating CrashLoopBackOff pods

**Symptom:** You force-delete a stuck CrashLoopBackOff pod. Five seconds later,
another pod is in `ContainerCreating`. Ten seconds later, it's in
`CrashLoopBackOff`. Repeat. The Deployment reports `1/1 UP-TO-DATE` but
`AVAILABLE` shows the old pod still there.

**Root cause:** Default `strategy.rollingUpdate.maxSurge: 25%` lets the
controller spin up a new ReplicaSet alongside the old one. With the old pod
still holding the GPU, the new pod can't get scheduled and crashes. The
controller keeps trying.

**Fix:** patch the Deployment to `maxSurge: 0` and `maxUnavailable: 1`:

```bash
kubectl patch deployment -n llm-inference <name> --type=json -p='[
  {"op":"replace","path":"/spec/strategy/rollingUpdate/maxSurge","value":0},
  {"op":"replace","path":"/spec/strategy/rollingUpdate/maxUnavailable","value":1}
]'
```

This forces the controller to take the old pod down before bringing the new
one up. Combined with `kubectl scale deployment ... --replicas=1`, you get
one clean pod per Deployment with no extra CrashLoopBackOff clutter.

For the deep cleanup (delete the orphaned ReplicaSet that the controller
created during the chaos), identify it with:

```bash
kubectl get rs -n llm-inference
# Look for ReplicaSets with DESIRED > 0 and CURRENT > READY (and READY < 1)
```

…and `kubectl delete rs -n llm-inference <name>` to remove them. The
controller will create a fresh RS for the next rollout cycle.

**Verify a clean state:** exactly two pods total in the namespace (one per
agent), each `1/1 Running`, each with `RESTARTS: 0`. Anything else means
there's still an orphaned ReplicaSet or a stuck rollout.

## Gotcha 6 — KV cache sizing math and q4_0 vs q8_0 tradeoff

**When to use this:** you want to bump context past 65k but need to know
how high you can go before OOMing the GPU.

**Qwen3-30B-A3B (and similar 27B) architecture constants:**
- 28 transformer layers
- 4 KV heads (GQA — not 40; heads share 4 KV projections)
- head_dim = 128
- n_embd = 5120
- Per-token KV cache size = `2 × n_layer × n_kv_heads × head_dim × bytes_per_elem`
  - q8_0 (1 byte/elem): `2 × 28 × 4 × 128 × 1 = 28,672 bytes/token ≈ 28 KiB/tok`
  - q4_0 (0.5 byte/elem): `2 × 28 × 4 × 128 × 0.5 = 14,336 bytes/token ≈ 14 KiB/tok`
  - f16 (2 bytes/elem): 56 KiB/tok — only fits with very small ctx

**For Q4_K_M weights (~17.1 GiB) on a 24 GiB RTX 3090 with 1.5 GiB CUDA
overhead and 5 MiB output buffer, the per-card VRAM budget for KV cache
is ~5.4 GiB. With that budget:**

| Context | q8_0 KV | q4_0 KV |
|---------|---------|---------|
| 65,536 | ~1.79 GiB | ~0.90 GiB |
| 131,072 | ~3.58 GiB | **~1.79 GiB** ← verified working |
| 196,608 | ~5.38 GiB | ~2.69 GiB |
| 262,144 (model's n_ctx_train) | ~7.17 GiB | ~3.58 GiB |

**The verified sweet spot: 131072 ctx with `--cache-type-k q4_0
--cache-type-v q4_0`** on a single 24 GiB card. 77% VRAM utilization
(18,982 MiB used, 5,276 MiB free) with healthy headroom for long
generations.

**The 262k sweet spot on a layer-split pair** (Fred's pod): Weights 18.5 GiB
split across 2 cards (~9.25 GiB each) + KV cache q4_0 at 262k
(~3.58 GiB split across 2 cards = ~1.8 GiB per card) + mmproj ~1 GiB per
card + overhead ~2 GiB per card = ~14-15 GiB per card used, ~9-10 GiB free,
~60% utilization with healthy headroom.

**Don't push to 262k with q8_0 KV cache on a single card** — 262k at q8_0
needs ~7 GiB of KV cache, which only leaves ~2 GB headroom on a 24 GB card.
Long generations will OOM.

**Don't push to 196k+ with single-card unless you switch to `--kv-unified
--cache-ram` mode AND verify it actually unifies.** The flag is a known
easy-to-miss pitfall (see Gotcha 2).

**VRAM utilization rule of thumb:**
- <60% utilization: under-using the card; consider a bigger model
  (Q5_K_M for one card, Q8 for split across two)
- 60-85%: sweet spot — room for long outputs without OOM risk
- >90%: risky — long generations may OOM as the output buffer grows

**Verification:**
```bash
# KV cache type took effect
kubectl logs -n llm-inference <pod> | grep -E "cache_type|kv_size"
# Total VRAM usage after a long prompt
qm guest exec <vmid> -- nvidia-smi --query-gpu=memory.used --format=csv,noheader
# Under-load prompt processed without error
curl -s -X POST http://<node-ip>:<port>/v1/chat/completions \
    -H 'Content-Type: application/json' \
    -d '{"model":"<alias>","messages":[{"role":"user","content":"DONE: " + ("The "*80000)}],"max_tokens":5,"temperature":0}' \
    | jq '.usage.prompt_tokens'    # must be > 80000, no exceed_context_size_error
```

## Quick-check checklist (after wiring a profile to a local llama-server)

The proven target: **131,072 ctx with `--cache-type-k q4_0
--cache-type-v q4_0`** on a single 24 GiB card. Adjust context size down
to 65k only if you need to share a card with another workload.

```bash
# 1. llama-server reachable, model listed
curl -s http://<node-ip>:<port>/v1/models | jq '.data[].id'
# 2. Slot context ≥ 131072
curl -s http://<node-ip>:<port>/slots | jq '.[0].n_ctx'
# 3. KV cache is q4_0 (check pod logs)
kubectl logs -n llm-inference <pod> | grep -i cache_type
# 4. Hermes provider config declares ≥ 131072
python3 -c "import yaml; d=yaml.safe_load(open('/home/ubuntu/.hermes/profiles/<profile>/config.yaml')); p=d['providers'][d['model']['provider'].split(':')[1]]; print(p['context_length'])"
# 5. 80k-token real prompt succeeds
curl -s -X POST http://<node-ip>:<port>/v1/chat/completions \
    -H 'Content-Type: application/json' \
    --data-binary @<(python3 -c "import json,sys; json.dump({'model':'<alias>','messages':[{'role':'user','content':'Reply with the word DONE: ' + ('The '*80000)}],'max_tokens':5,'temperature':0}, sys.stdout)")
# 6. GPU actually allocated (and VRAM usage healthy: 15-22 GiB used)
sshpass -p ... ssh root@<pve-ip> "qm guest exec <vmid> -- nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits"
```

A `/tmp/hermes-verify-ctx-131072-q4.py` script that runs all six checks
is the standard deliverable. Exit 0 only if every check passes; fix the
failed layer first (gotcha 1–6 maps to layers 3, 2, deployment, deployment,
runtime, sizing-math).

## Gotcha 7 — `--ctx-size` capped at `n_ctx_train` even with YARN

**Symptom:** you set `--ctx-size 524288 --rope-scaling yarn --yarn-orig-ctx 262144 --yarn-ext-factor 2.0` to get 2× the training length, but the runtime caps the slot ctx at 262144 and a 300k-token request returns:

```json
{"error":{"code":400,"message":"request (300052 tokens) exceeds the available context size (262144 tokens), try increasing it","type":"exceed_context_size_error","n_prompt_tokens":300052,"n_ctx":262144}}
```

The pod's startup log shows:
```
n_ctx_seq (524288) > n_ctx_train (262144) -- possible training context overflow
the slot context (524288) exceeds the training context of the model (262144) - capping
```

**Root cause:** As of llama.cpp b5368 (early 2026 builds), `llama-server`'s startup-time cap on `--ctx-size` is `n_ctx_train`, and the YARN flags (`--rope-scaling yarn --yarn-orig-ctx ... --yarn-ext-factor ...`) do **not** override that cap. The model is loaded with the extended RoPE frequency, but the context-size validation runs before the rope-scaling extension is applied, so the cap stays at `n_ctx_train`.

In practice this means:
- **You can stay at or below `n_ctx_train` (262144 for Qwen3-30B-A3B).** This is the safe, supported path; no quality loss because the model was trained on this length.
- **You cannot exceed `n_ctx_train` via YARN with this build.** Going to 524k or 1M requires either (a) a llama.cpp build that processes the YARN extension before the cap check, (b) patching the cap line directly in `tools/server/server-context.cpp:1202`, or (c) hand-editing the GGUF's `qwen3.context_length` metadata to a higher value. See Gotcha 16 for the actual location of the hard cap.

**Fix paths (in order of preference):**

1. **Accept the training length.** Set `--ctx-size 262144` for Qwen3-30B-A3B / Qwen3.8-27B. On 2× 24 GiB cards with `--split-mode layer --tensor-split 1,1`, this still gives you 4× the previous 65k ceiling and uses ~14 GiB per card.

2. **Patch the hard cap in source and rebuild.** The literal location is `tools/server/server-context.cpp:1202`. Comment out the `n_ctx_slot = n_ctx_train;` line, rebuild (full CUDA compile ~15 min), and the cap no longer fires. This is a one-line change with full understanding of the consequence (model quality degrades past training length, but the user has explicitly asked for it).

3. **Build fresh from master + `--fit-params off` (does NOT bypass the hard cap).** Confirmed Aug 15 2026: latest master still has the cap line. The `--fit-params off` flag bypasses the auto-shrink heuristic introduced in master, but the hard cap at line 1202 is a separate code path. Build succeeds, image imports, pod starts — but `--ctx-size 1048576` is silently capped to 262144 in `/slots`. See Gotcha 16.

4. **Edit the GGUF metadata.** The `qwen3.context_length` and `qwen3.rope.scaling.type` fields can be hand-edited with a `gguf` script (Python `gguf` library, but use `--break-system-packages` on managed Python environments). Risky and unverified — the RoPE tables would not match the extended context, leading to garbage outputs at extended positions.

**For Qwen3-27B specifically, the tested working config is `--ctx-size 262144 --split-mode layer --tensor-split 1,1`.** No YARN args needed. The model was trained at 262144, so you get full native quality for the whole context. Quality at 524k via YARN would be degraded even if you could enable it.

**Verification:**
```bash
# /slots should show n_ctx = 262144 (or your n_ctx_train)
curl -s http://<node-ip>:<port>/slots | jq '.[0].n_ctx'

# a 100k-token prompt should succeed
curl -s -X POST http://<node-ip>:<port>/v1/chat/completions \
    -H 'Content-Type: application/json' \
    -d "$(python3 -c "
import json
print(json.dumps({'model':'<alias>','messages':[{'role':'user','content':'The '*22000}],'max_tokens':3}))
")" | jq '.usage.prompt_tokens'
# must be > 90000, no exceed_context_size_error
```

**The YARN test recipe** (don't ship this; just for diagnostics):

```bash
# Spin up a fresh pod with these args and watch the start-of-init log:
args:
- --ctx-size
- "524288"
- --rope-scaling
- yarn
- --yarn-orig-ctx
- "262144"
- --yarn-ext-factor
- "2.0"
- --yarn-attn-factor
- "1.0"
# If you see "exceeds the training context of the model (262144) - capping",
# YARN didn't override the cap. Revert to --ctx-size 262144.
```

## Gotcha 8 — 2× GPU layer-split with `--split-mode layer --tensor-split 1,1`

**When to use this:** you want a model too large for one 24 GiB card (Q5_K_M of a 27B+ model, or Q8 of a 30B+ model), or you want maximum context capability across two cards.

**The working pattern for 2× RTX 3090 with Qwen3.8-27B-Q5_K_M (18.5 GiB) at 262k ctx:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fred-llama
  namespace: llm-inference
spec:
  replicas: 1
  strategy:
    type: Recreate   # layer-split can't run two pods at once on the same model
  selector:
    matchLabels: {app: fred-llama}
  template:
    metadata:
      labels: {app: fred-llama}
    spec:
      runtimeClassName: nvidia
      nodeSelector: {kubernetes.io/hostname: <k3s-node-name>}
      containers:
      - name: llama-server
        image: llama-cuda:v2
        imagePullPolicy: Never
        env:
        - name: NVIDIA_VISIBLE_DEVICES
          value: "0,1"           # both GPUs
        - name: NVIDIA_DRIVER_CAPABILITIES
          value: "compute,utility"
        resources:
          requests:
            nvidia.com/gpu: 2    # ask for both
          limits:
            nvidia.com/gpu: 2
        ports:
        - containerPort: 8001
        args:
        - --model
        - /models/qwen3.8-27b-q5/Qwen3.8-27B-Q5_K_M.gguf
        - --mmproj
        - /models/qwen3.8-27b-q5/mmproj-F16.gguf
        - --alias
        - local-qwen-27b-q5-fred
        - --ctx-size
        - "262144"
        - --parallel
        - "1"
        - --cache-type-k
        - q4_0
        - --cache-type-v
        - q4_0
        - --flash-attn
        - "on"
        - --split-mode
        - layer                 # split by transformer layer
        - --tensor-split
        - "1,1"                 # equal split across 2 GPUs
        - --host
        - 0.0.0.0
        - --port
        - "8001"
        readinessProbe:
          httpGet: {path: /health, port: 8001}
          initialDelaySeconds: 60
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 30
```

**VRAM math for 2× 24 GiB cards with Qwen3.27B-Q5_K_M at 262k ctx:**
- Weights layer-split: 18.5 GiB / 2 = ~9.25 GiB per card
- KV cache at 262k ctx with q4_0: 3.58 GiB / 2 = ~1.79 GiB per card (split across slots, but unified → both cards share)
- mmproj: ~1 GiB per card when vision is enabled
- CUDA overhead: ~1.5 GiB total per card
- **Total per card: ~14 GiB** (60% utilization) — comfortable headroom

**Three things to verify before declaring it deployed:**

1. **Both GPUs show ~equal memory usage.** `nvidia-smi --query-gpu=index,memory.used --format=csv,noheader` should show both cards in the same range. A 2× or 3× asymmetry means `--tensor-split 1,1` wasn't applied.

2. **Health endpoint responds within 60 seconds.** `--split-mode layer` requires the model to be loaded across both cards, which can take 30-60s on large models. The `initialDelaySeconds: 60` is critical.

3. **`/slots` reports the full `n_ctx`**, not the per-slot value. With `--parallel 1`, this is the total. With `--parallel N`, see Gotcha 2.

**Anti-patterns:**

- **Don't use `--parallel 2` with layer-split.** Each slot needs its own KV cache space; with layer-split, the KV cache lives on both cards but the slot allocation is still per-slot. The math gets complicated; stick with `--parallel 1` for first-try deployments.
- **Don't use `replicas: 2` with `--split-mode layer`.** The second pod would need its own GPU reservation, which would conflict with the first pod's reservation. Use `strategy: {type: Recreate}` if you want idempotent restarts.
- **Don't forget that `nvidia.com/gpu: 2` is a single resource request, not 2 separate GPUs.** The device plugin schedules it as a unit.

**The model file size for Qwen3.27B-Q5_K_M is 19.83 GiB (not 19.07 GiB).** Earlier research cited 19.07 GiB; HuggingFace's actual `X-Linked-Size` is `content-length: 19834055648` = 19.83 GiB. This matters when checking disk space before download.

## Gotcha 9 — `qm guest exec` syntax trap (no `-c` flag)

**Symptom:** you try to run a command inside a VM and get:
```
Unknown option: c
400 unable to parse option
```

**Root cause:** `qm guest exec` does NOT take a `-c <cmd>` flag. The command goes after `--` (positional):

```bash
# WRONG
qm guest exec 230 -c "bash -c 'something'"

# CORRECT
qm guest exec 230 -- bash -c "some command"
qm guest exec 230 -- python3 -c "print(1+1)"
qm guest exec 230 -- ls /models
```

The user inside the VM is `root` (qemu-guest-agent runs as root); no sudo needed. You don't need to log in first.

For long-running commands inside the VM (>30 seconds), the `--` separator hands the command to qemu-guest-agent, which has a timeout. Use the `nohup setsid` pattern from `proxmox-orchestrator-remote-ops` (write a script to disk first, then detach).

## Gotcha 10 — Hermes security gate blocks direct edits to `~/.hermes/profiles/<orchestrator>/config.yaml` ONLY

**Symptom:** you try `patch` or `write_file` on `~/.hermes/profiles/orchestrator/config.yaml` and get:

```
Refusing to write to Hermes config file: /home/ubuntu/.hermes/profiles/orchestrator/config.yaml
Agent cannot modify security-sensitive configuration. Edit ~/.hermes/config.yaml directly or use 'hermes config' instead.
```

**Root cause:** the **orchestrator** profile's config is gated from direct
agent mutation. Other profiles (`kai`, `ned`, etc.) are NOT gated and can
be patched directly. Verified 2026-08-15: the agent successfully patched
both `kai/config.yaml` and `ned/config.yaml` to update `context_length` and
add `max_tokens`.

**Recipe when you need an orchestrator change:**

1. **Surface the proposed change to the user** as a clear, copy-paste-ready prompt. Include:
   - The exact `providers:` block to add (or edit)
   - The `model:` block changes
   - The expected runtime behavior (curl health/model endpoint)
   - The live endpoint URL and the model alias
2. **Wait for the user to do the edit** (or confirm they've done it before you verify).
3. **Verify the wiring** by issuing a chat completion through the Hermes profile (not just hitting the endpoint directly). The user can run a quick test from their chatbot.

**Don't try:**
- `hermes config set <key> <value>` for nested paths (the CLI doesn't handle them; see `hermes-agent` skill).
- Patching the security gate (it will refuse again).
- Adding a new provider to a separate file under `~/.hermes/profiles/orchestrator/`. The config is one file.

**For non-orchestrator profiles (kai, ned, etc.)** — just `patch` or
`write_file` directly. The gate does not apply. Verify with:

```bash
python3 -c "
import yaml
d = yaml.safe_load(open('/home/ubuntu/.hermes/profiles/<profile>/config.yaml'))
print('declared ctx:', d['providers'][...].context_length)
"
```

## Gotcha 11 — `max_tokens=-1` server default causes slot monopolization (looks like vision/chat failures)

**Symptom:** a model agent (Kai, Ned, anything wired to a local llama-server)
reports "the vision API is throwing errors" or "I'll fall back to OCR" /
"connection timed out" — even though the pod is healthy, `/health` returns
200 OK, `/v1/models` shows the right alias, and the model itself is
multimodal-capable.

The slot stays `is_processing: true` for minutes per request. Other clients
submitting image_url requests queue up, time out waiting for the slot, and
report "vision API error" — but the vision API is fine; it's just held
behind a runaway generation.

`/slots` shows `params.max_tokens: -1` and `n_remain` in the tens of thousands
mid-generation.

**Root cause:** llama.cpp b5368+ defaults `max_tokens` (the per-request
output budget) to **-1 = unlimited** when the client omits it. With an
unlimited cap, a single chat request can spin the model for tens of thousands
of tokens of `<think>` reasoning (Qwen3.8 is a thinking model by default)
before producing visible content. On reasoning-heavy prompts that "thinking"
can run 30k+ tokens — taking 15+ minutes at ~33 t/s.

Hermes Agent (and most chat clients) does **NOT** set `max_tokens` explicitly
unless told to. Default-Unlimited is a **server-level footgun** — every
Hermes profile wired to a local llama-server is exposed.

**The misleading-failure cascade:** slot monopolization → subsequent
requests time out → model agent blames "API error" / "vision error" →
operator debugs the wrong subsystem.

**Fix on the server side: add `--n-predict 4096` to the llama-server args.**

```yaml
args:
- --model
- /models/qwen3.8-27b-q4/Qwen3.8-27B-Q4_K_M.gguf
- --n-predict
- "4096"          # NEW: cap output budget, prevent slot monopolization
- --ctx-size
- "262144"
# ... rest unchanged
```

With Qwen3.8 at 37 t/s on a layer-split pair, 4096 tokens max ≈ 110 seconds
worst-case generation — comfortably under any reasonable Telegram or web
timeout.

**Verification (mandatory after wiring any local llama-server):**

```bash
# Send a request with NO max_tokens and observe the slot mid-flight
curl -s -X POST http://<host>:<port>/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"<alias>","messages":[{"role":"user","content":"Say OK."}],"temperature":0.1}' \
  >/dev/null &

sleep 0.5
curl -s http://<host>:<port>/slots | jq '.[0].params.max_tokens'
# must be a positive finite value (4096 if --n-predict was passed).
# If it shows -1, the server default kicked in — fix the manifest.
```

**Diagnostic recipe when a user reports "vision API error" / "model stuck":**

1. **Check `/slots` first.** If `is_processing: true` with high `n_remain`,
   the slot is the problem, not the API.
2. **Send a direct quick test** (`max_tokens: 100`) to the same endpoint.
   If it succeeds, the API is fine.
3. **If the slot is the problem:** restart the pod with
   `kubectl delete pod -n llm-inference <pod-name>` and patch the manifest
   to add `--n-predict 4096`.

**Anti-pattern:** when the user says "vision API is throwing errors," **do
not** immediately assume vision is broken. The vision API has been
verified working in isolation (see section 1 of
`references/llama-server-vision-and-multi-pod.md`). Check `/slots` first.
If a direct quick vision test succeeds while the agent's path fails, the
agent's *request pipeline* is broken (likely slot contention from a
runaway prior request), not the model or vision.

## Gotcha 12 — `provider.max_tokens` on the Hermes side does work (don't rely on server `--n-predict` alone)

**Symptom:** Gotcha 11 says to add `--n-predict 4096` to the llama-server
manifest to cap output. The agent does this, deploys, and the slot still
shows `max_tokens: -1` on requests that don't include `max_tokens` in the
JSON body — because Hermes itself is asking for unlimited.

**Root cause (verified on 2026-08-15 against Hermes gateway):** Hermes
Agent reads `providers.<NAME>.max_tokens` from the YAML and applies it
as the request's `max_tokens` field when calling the local llama-server.
This is a **separate fix layer** from `--n-predict` on the server:

- `--n-predict <N>` on llama-server: hard server-side cap on every
  completion. Even if a client (Hermes or anything else) sends
  `max_tokens: 100000` in the JSON, the server enforces `--n-predict`.
- `provider.max_tokens: <N>` on Hermes: causes Hermes to **send** that
  value in the request body. The server may or may not cap further
  depending on `--n-predict`.

**Both layers should be set:**

```yaml
# In ~/.hermes/profiles/<profile>/config.yaml (Hermes side)
providers:
  qwen27b-kai-local:
    api: http://192.168.1.230:31002/v1
    api_key: llama-local
    default_model: local-qwen-27b-q4-kai
    models:
      local-qwen-27b-q4-kai:
        context_length: 262144
    context_length: 262144
    max_tokens: 4096            # NEW: Hermes sends this in every request
    request_timeout_seconds: 600
```

```yaml
# In the K8s Deployment args (llama-server side)
args:
- --n-predict
- "4096"                       # NEW: server-side hard cap, defense in depth
```

The Hermes-side value is what unblocks a profile wired today without
re-deploying the pod. The server-side value is the long-term guarantee.

**Verification:**

```bash
# After Hermes gateway reloads with the new config, send a request with
# NO max_tokens in the body and inspect the slot mid-flight:
curl -s -X POST http://<host>:<port>/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"<alias>","messages":[{"role":"user","content":"Say OK."}]}' \
  >/dev/null &
sleep 0.8
curl -s http://<host>:<port>/slots | jq '.[0].params.max_tokens'
# must show 4096 if provider.max_tokens was honored,
# -1 if neither layer fixed it.
```

**Why this matters:** a profile wired without `provider.max_tokens` will
**persistently** hit the slot monopolization bug even if the server has
`--n-predict` set, IF the user (or another client) sends requests
through a different path. The two layers are independent.

## Gotcha 13 — Hermes "Context: 131K tokens (detected)" is the declared value, not detected

**Symptom:** user runs `/restart` on a Hermes profile and sees:
```
◆ Context: 131K tokens (detected)
```
The actual server has `n_ctx: 262144` (verified via `/slots`). The header
is lying.

**Root cause:** Hermes reads the **declared** `context_length` from the
provider YAML, not the `n_ctx` value from the server's `/v1/models` or
`/slots` endpoint. The "detected" label is misleading — it means
"detected from the config file the agent loaded", not "detected from a
live query to the inference engine".

**Fix:** keep `providers.<NAME>.context_length` and the inner
`providers.<NAME>.models.<alias>.context_length` in sync with the actual
server's `--ctx-size`. Two values to set per profile:

```yaml
providers:
  qwen27b-kai-local:
    context_length: 262144        # provider-level (Hermes reads this)
    models:
      local-qwen-27b-q4-kai:
        context_length: 262144    # model-level (picker shows this)
```

After editing, restart Hermes (`/restart` in the chat, or restart the
gateway). The session header will then show "262K tokens" matching the
real server config.

**Verification:**

```bash
python3 -c "
import yaml
d = yaml.safe_load(open('/home/ubuntu/.hermes/profiles/kai/config.yaml'))
p = d['providers'][d['model']['provider'].split(':')[1]]
print('declared ctx:', p['context_length'])
print('model ctx:', p['models'][d['model']['default']]['context_length'])
"
# both must match the server's /slots n_ctx

sshpass -p ... ssh root@<pve-ip> "qm guest exec <vmid> -- curl -s http://localhost:31002/slots | jq '.[0].n_ctx'"
# server n_ctx
```

If the two diverge, the session header will display whichever value is
in the YAML, regardless of the actual server capability.

## Gotcha 14 — Pushing past `n_ctx_train`: build fresh from master + `--fit-params off`

**Context:** Gotcha 7 documents that `--ctx-size > n_ctx_train` is hard-capped by llama.cpp b5368 regardless of YARN flags. **As of August 2026, the cap-after-extension fix is in latest master, AND a new auto-cap heuristic (`fit_params`) replaces it.** The fresh-source build path now reaches 1M on 2× 24 GiB RTX 3090s without needing Ollama. The Ollama Modelfile path is still valid as a fallback.

**CORRECTION (verified Aug 15 2026 — same session):** the assertion above is wrong on both counts. Latest master still has the hard cap at `tools/server/server-context.cpp:1202` (see Gotcha 16), AND the `--fit-params off` flag bypasses only the auto-shrink heuristic, not the hard cap. Build the binary successfully, image imports cleanly, pod starts — but `/slots` still reports `n_ctx: 262144` after `--ctx-size 1048576`. The fresh-source build is wasted effort if 1M is the goal; the actual unlock requires patching the cap line in source and rebuilding.

**Why b5368 caps:** the b5368 validation runs the `--ctx-size > n_ctx_train` check **before** RoPE extension is applied, so even with correct YARN flags the requested ctx gets capped. Newer builds run the YARN extension first, then check.

**The fresh-source build recipe (verified Aug 15, 2026, but only gets you to 262k):**

```bash
# 1. Get source
git clone --depth 1 https://github.com/ggml-org/llama.cpp.git llama-master

# 2. Build inside nvidia/cuda:12.2.0-devel container (matches driver 535.x)
docker run --rm -v $(pwd)/llama-master:/src -v /tmp/build-out:/out \
    nvidia/cuda:12.2.0-devel-ubuntu22.04 bash -c '
    apt-get install -y cmake && cd /src && rm -rf build
    cmake -B build -DGGML_CUDA=ON -DCMAKE_BUILD_TYPE=Release \
          -DGGML_NATIVE=OFF -DGGML_CPU_ALL_VARIANTS=OFF
    cmake --build build --config Release --target llama-server -- -j24
    cp /src/build/bin/llama-server /out/llama-server-new
    '
# ~15-20 min wall time. The CUDA kernel compilation is the slow part.
# IMPORTANT: every fresh container requires apt-get install cmake again;
# container state does not persist between `docker run` invocations.

# 3. Package as a Docker image per references/llama-cuda-build-and-deploy.md
#    (the two-stage pattern with nvidia/cuda:12.2.0-runtime is unchanged).

# 4. In the K8s deployment args, also pass --fit-params off:
#    --fit-params
#    "off"
#    (This bypasses the auto-shrink heuristic, NOT the hard cap.)
```

**The math at 1M tokens on 2× 24 GB GPUs (verifies the constraint is memory-bound but solvable if the cap is removed):**

- Q5_K_M weights: 18.5 GiB
- KV cache q4_0: 28 layers × 2 × 4 heads × 128 dim × 0.5 byte × 1,048,576 tokens = **14.7 GiB**
- Flash-attn workspace: 3 GiB
- mmproj: 1 GiB
- CUDA overhead: 2 GiB
- **Peak: ~38 GiB** — fits in 48 GiB with ~10 GiB headroom

So the only blocker is the hard cap, not memory.

**Three-layer tradeoff for going to 1M:**

| Approach | Build needed | Result | Compatibility |
|---|---|---|---|
| Stay on llama.cpp b5368, accept 262k | None | Works today | Current K8s deployment |
| Build fresh from master + `--fit-params off` | ~15-20 min rebuild + image transfer | **Does NOT unlock 1M** — cap still fires | Current K8s deployment (image swap only) |
| Patch the cap line in source + rebuild | ~15-20 min rebuild + image transfer | Actually unlocks 1M (with quality caveats) | Current K8s deployment (image swap only) |
| Switch that deployment to Ollama, use Modelfile-1M | Install Ollama, write Modelfile | Same cap exists; no win | New containerized runtime, not K8s-managed |

**Anti-pattern: do NOT pull `ghcr.io/ggml-org/llama.cpp:server-cuda` as a prebuilt replacement for the custom `llama-cuda:v2` image.** The prebuilt is built with CUDA 13.x and requires driver ≥580. Our PVE1 GPUs run driver 535.288.01 (CUDA 12.x max). Result: `ggml_cuda_init: failed to initialize CUDA: forward compatibility was attempted on non supported HW` followed by `no usable GPU found` and every request runs on CPU (or refuses to load the model). Always build from source against a CUDA version that matches the target host driver, OR verify the prebuilt's CUDA version against `nvidia-smi --query-gpu=driver_version` on the target host before pulling. The fix is the same fresh-source build recipe above — `nvidia/cuda:12.2.0-devel-ubuntu22.04` matches the 535.x driver.

**Anti-pattern:** Do not edit the GGUF metadata by hand (`qwen3.context_length` → 1048576) to "trick" llama.cpp. The GGUF's `n_ctx_train` is what the RoPE tables are computed against; setting a higher `qwen3.context_length` without re-generating the RoPE frequency table produces garbage outputs at extended positions.

**Diagnostic when you see "1M context" requests:**

1. **First try:** confirm `n_ctx_train` of the GGUF (it's in `/props` from a working llama-server, or read directly with `gguf-py`). If it's `262144`, the b5368 build will cap and YARN won't help — proceed to step 2.
2. **Recommended path if 1M is a hard requirement:** patch `tools/server/server-context.cpp:1202` to remove the hard cap, rebuild (~15-20 min CUDA compile). After the image swap, `--ctx-size 1048576` will work. Quality at extended positions will be degraded (model wasn't trained there); document this in the user-facing deployment notes.
3. **Rebuilding fresh from master + `--fit-params off` does NOT unlock 1M.** Don't waste the 15-20 min rebuild unless you also patch the cap line.
4. **If you tried pulling a prebuilt and it fails to use GPU:** check the prebuilt's CUDA version against `nvidia-smi --query-gpu=driver_version` on the target host. Mismatch = CUDA 13 forward-compat trap; rebuild from source.

## Gotcha 15 — `--no-flash-attn` is not a flag in llama.cpp b5368 (use `--flash-attn off`)

**Symptom:** pod starts and immediately exits with:
```
error: invalid argument: --no-flash-attn
```

**Root cause:** b5368 only supports `--flash-attn` with values `on|off|auto`. There is no `--no-flash-attn` boolean flag. The "off" state is `--flash-attn off`.

**Fix:**
```yaml
args:
- --flash-attn
- "off"     # not --no-flash-attn
```

**Compounding constraint:** if you set `--cache-type-k q4_0` (or any quantized KV cache) AND `--flash-attn off`, llama-server refuses to start with:
```
quantized V cache requires flash_attn to be enabled
```

This is a hard constraint — quantized KV caches require flash-attn. So you cannot combine q4_0 KV cache with flash-attn off. The "disable flash-attn to save VRAM" path is closed for quantized KV; you can only disable flash-attn when keeping f16 KV cache (and only f16 KV at small ctx fits on 24 GB anyway).

**Implication for 1M context attempts:** the YARN test in Gotcha 14 hits this exact constraint. You need q4_0 KV cache to fit 14.7 GiB in the budget, but q4_0 KV requires flash-attn on, and flash-attn on adds ~3 GiB of workspace that pushes the peak above available memory. The 1M path requires either:
- The Ollama workaround (different runtime, doesn't hit this constraint)
- A llama.cpp build where `--flash-attn off` is decoupled from the q4_0 KV requirement (none known yet)
- Hand-tuning CUDA memory pool settings (fragile, unverified)

## Gotcha 16 — Hardcoded cap at `server-context.cpp:1202` is the actual 1M blocker

**Symptom:** you built fresh from llama.cpp master (verified all the
flags), imported the image, ran the trial with `--ctx-size 1048576
--rope-scaling yarn --yarn-orig-ctx 262144 --yarn-ext-factor 4.0
--fit-params off`. The pod started, the model loaded, but `/slots`
reports `n_ctx: 262144` (capped) and the startup log says:

```
n_ctx_seq (1048576) > n_ctx_train (262144) -- possible training context overflow
the slot context (1048576) exceeds the training context of the model (262144) - capping
```

**Root cause:** the cap is in the server's startup code, not in any
heuristic. In latest master (Aug 15 2026), the literal source is
`tools/server/server-context.cpp:1202`:

```cpp
const int n_ctx_train = llama_model_n_ctx_train(model_tgt);
int n_ctx_slot = llama_n_ctx_seq(ctx_tgt);
if (n_ctx_slot > n_ctx_train) {
    SRV_WRN("the slot context (%d) exceeds the training context of the model (%d) - capping\n",
            n_ctx_slot, n_ctx_train);
    n_ctx_slot = n_ctx_train;   // ← unconditional cap, no flag to bypass
}
```

The `--fit-params off` flag (introduced in master) controls the
auto-shrink heuristic only — it's a **different code path** from this
hard cap. Disabling `--fit-params` does NOT bypass line 1202.

**No flag in any llama.cpp version bypasses this cap.** I checked the
code: there is no `--no-cap`, `--allow-context-extension`,
`--override-n-ctx-train`, or similar flag. The cap is unconditional.

**Three real paths to 1M context:**

1. **Patch the source line AND add `--kv-unified` to args.** Change
   line 1202 to remove the cap (e.g. set `n_ctx_slot = n_ctx_slot`
   instead of `n_ctx_slot = n_ctx_train`, or comment out the if-block).
   Rebuild takes ~15-20 min. **Also add `--kv-unified` to the K8s
   deployment args** — see "Companion gotcha — `--kv-unified` is the
   second unlock" below for why. After the image swap, `--ctx-size 1048576`
   will actually take effect. Quality caveat: the model wasn't trained
   at 1M, so outputs at far positions degrade (RoPE extrapolation).

2. **Edit the GGUF metadata.** The `qwen3.context_length` and
   `qwen3.rope.scaling.type` fields can be modified with `gguf-py`.
   Risky — RoPE tables won't match the extended positions, so outputs
   at extended positions are likely garbage.

3. **Don't go to 1M.** Qwen3.8-27B was trained at 262k; that IS the
   native ceiling. Any context beyond that is extrapolation. Quality
   at 524k via YARN would be degraded; at 1M via YARN it would be much
   worse. 262k already gives 4× the previous 65k ceiling and fits
   comfortably on 2× 24 GiB cards.

**Companion gotcha — `--kv-unified` is the second unlock you need.** The
patch above removes the *server-side* cap, but there's a second
allocation-time division at `src/llama-context.cpp:293`:

```cpp
if (cparams.kv_unified) {
    cparams.n_ctx_seq = cparams.n_ctx;
} else {
    cparams.n_ctx_seq = cparams.n_ctx / cparams.n_seq_max;
    cparams.n_ctx_seq = GGML_PAD(cparams.n_ctx_seq, 256);
    ...
}
```

With `n_ctx = 1048576` and `n_seq_max` set by `--parallel` (default
from `n_parallel`, often 4), `n_ctx_seq = 262144` — a silent
division-by-parallel that hides the cap. Without `--kv-unified`,
the patched server still reports `n_ctx_slot: 262144` because this
code path divides the allocated ctx before the slot sees it. Wasted
a full rebuild iteration on this before the lesson stuck.

**The fix:** add `--kv-unified` to the deployment args alongside the
patched binary. With `--kv-unified`, `n_ctx_seq = n_ctx` directly — no
division. Verification:

```bash
# Start log must show kv_unified = 'true', NOT 'false'
kubectl logs -n llm-inference <pod> | grep "kv_unified"
# /slots must report n_ctx = --ctx-size (e.g. 1048576), NOT n_ctx_train
curl -s http://<host>:<port>/slots | jq '.[0].n_ctx'
```

If the pod's init log shows `kv_unified = 'false'`, the flag was not
honored — verify it's spelled `--kv-unified` (with double-dash) and not
`--kv_unified` or similar. With `--parallel 1`, the unified-vs-divided
distinction is moot for memory but the flag still controls how
`n_ctx_seq` is computed; set it explicitly to avoid the silent
division-by-parallel behavior on future bumps to `--parallel`.

**Verification:**
```bash
# /slots shows the cap
curl -s http://<node-ip>:<port>/slots | jq '.[0].n_ctx'
# must equal --ctx-size if the cap is bypassed (e.g. 1048576)
# must equal n_ctx_train if the cap fires (262144 for Qwen3.8-27B)

# The startup log proves the cap line fired
kubectl logs -n llm-inference <pod> | grep -i "capping"
```

**Anti-pattern:** Don't waste 15-20 min rebuilding llama.cpp from
master with `--fit-params off` if 1M is the goal — the rebuild succeeds,
the binary runs, the cap still fires. The path forward requires a
source patch.

**Anti-pattern: `docker build` without `--no-cache` after patching shared libraries.** When you
patch a `.cpp` source file and run `docker build` to bake the new binary into a
container image, the `COPY build-bin/` step (or any `COPY` of pre-built
artifacts) is cached based on the source path's hash, NOT the file contents.
If the patched `.cpp` produces a new binary but the `build-bin/` directory
was populated before the patch, the cache returns the OLD `.so` files even
though the source was rebuilt. The resulting image has the patched
executable but stale shared libraries. Symptom: the binary works but
runtime behavior matches the pre-patch version (e.g. cap still fires even
though source has the cap removed). Fix: `docker build --no-cache -t
llama-cuda:vN .` after every source patch that produces a new library.
Verify the in-image library is fresh with `sha256sum
/usr/local/lib/llama/libllama-server-impl.so` inside the running container
and compare to the local build's hash.

**Diagnostic when a user asks "can we go past 262k?":**

1. **Confirm the math.** 2× 24 GiB cards + q4_0 KV + Q5_K_M weights = ~38 GiB peak. Fits. Memory is not the blocker.
2. **Confirm the cap location.** `grep -n "exceeds the training context" tools/server/server-context.cpp` in the source. If the line is there, the cap is there.
3. **Confirm the user's intent.** Is the goal "more context than 262k" or "any specific capability that requires more"? If it's "more because it's there," point them at Gotcha 7 and explain that 262k is the model's trained limit. If it's a specific workload, estimate the actual prompt size needed.
4. **Verify the patched binary is actually deployed.** If the source was patched but the running pod still shows the cap behavior, check the image SHA in `ctr -n k8s.io images ls` against the local build's `docker images` SHA — they must differ across versions to confirm a new image was built. If they're the same, the build was cached.

## Gotcha 17 — `-c/--ctx-size` is TOTAL context across all slots, not per-slot (VRAM math breaks if you assume per-slot)

**Symptom:** you plan "2 agents × 64k context" and launch with
`-c 65536 -np 2`, but the startup log says
`initializing, n_slots = 2, n_ctx_slot = 32768, kv_unified = 'false'`.
Each agent silently gets **half** what you intended.

**Root cause:** `-c` sets the total context pool; without `--kv-unified`,
the server divides by `--parallel` (`n_ctx_slot = n_ctx / n_seq_max`,
padded to 256 — see the `llama-context.cpp:293` companion in Gotcha 16).
So:

- 2 slots × 65,536 per agent → **`-c 131072 -np 2`** (NOT `-c 65536`)
- 1 slot × 131,072 → `-c 131072 -np 1`

**VRAM math consequence (measured 2026-08-21, VM 232, 1× RTX 3090,
Qwen3.8-27B UD-Q4_K_M + mmproj-BF16, MTP spec decode, flash-attn on):**

| Config | KV cache type | Idle VRAM | Result |
|---|---|---|---|
| `-c 65536 -np 2` (32k/slot) | q8_0 | 21,042 MiB | boots, ~3.5 GB headroom |
| `-c 131072 -np 2` (64k/slot) | q8_0 | **23,764 MiB** | boots, **~780 MiB headroom** |
| `-c 65536 -np 4` (any) | q8_0 | — | **OOM** — runbook-grade mistake |
| `-c 131072 -np 2` | q4_0 | ~17.8 GB (est. from old config) | boots, ~6 GB headroom |

Rules of thumb:

1. **Always read `n_ctx_slot` from the startup log before declaring
   context size.** It is the only number that matters; your `-c` value is
   a plan, not a fact.
2. **KV cache type is the big VRAM knob.** q8_0 ≈ 2× the bytes of q4_0 at
   the same context. On a single 24 GB card running a 15–16 GB Q4 model
   with MTP + mmproj, q8_0 at 128k total is the **ceiling** — it fits, but
   with <1 GiB headroom. Heavy concurrent requests or bigger image
   payloads eat into that; q4_0 is the "comfortable" operating point.
3. **`--cache-reuse` silently auto-disables with `--mmproj`** (log line:
   "cache_reuse is not supported by multimodal, it will be disabled").
   Don't rely on it for prompt-prefix caching on a vision server.
4. **Newer builds log `consider enabling --reasoning-preserve`** when the
   chat template preserves reasoning; with `--jinja` + `--reasoning-effort`,
   add `--reasoning-preserve` so reasoning tokens survive into
   `reasoning_content` cleanly. (Observed 2026-08-21.)
5. **`--alias` + a single loaded model = model-id is cosmetic.** With one
   model loaded, requests succeed for ANY `model` string (alias, old path,
   garbage) and the response echoes the alias back. Verify with the
   specific id the client actually sends, but don't be surprised if the
   "wrong" id works too — it's the same weights.

**The test-boot pattern that makes this safe:** never swap the production
launcher blind. Boot the new config as a detached one-shot
(`nohup setsid llama-server ... > /var/log/kai-test-boot.log 2>&1 &`),
wait for `listening on http`, read `n_ctx_slot` + `nvidia-smi`, run the
health curls, kill it, THEN install the launcher and restart the systemd
unit. On VM 232 the first test boot caught the 32k/slot surprise before
Kai lost service. Slow-disk VMs: first cold model load is I/O-bound
(~17 min for 16.5 GB on VM 232's NAS-backed disk); second load is
page-cached (~16 s). Budget for the cold one.

## Gotcha 18 — HuggingFace download: no `huggingface-cli` on the VM, verify with sha256 from the API

`huggingface-cli` is usually NOT installed on these GPU VMs (no pip
toolchain). The reliable download path:

1. **Get exact sizes + sha256 from the HF API first:**
   ```bash
   curl -s "https://huggingface.co/api/models/<org>/<repo>?blobs=true" \
     | python3 -c "
   import sys,json
   d=json.load(sys.stdin)
   for f in d.get('siblings',[]):
       lfs=f.get('lfs',{})
       if lfs: print(f['rfilename'], lfs['size'], lfs['sha256'])"
   ```
2. **`wget -q -c` the resolve URL** (resume-capable, survives the slow
   link): `wget -c "https://huggingface.co/<org>/<repo>/resolve/main/<file>" -O /models/<file>`
3. **sha256-verify against the API value before touching the running
   server.** On VM 232 the 16.5 GB checksum took ~25 min on the
   NAS-backed disk — it's real work, not a hang. Measure progress via
   `grep rchar /proc/$(pgrep -x sha256sum)/io` instead of guessing.
4. **Delete the old weights only AFTER the new service is confirmed
   serving** (systemd unit active + `/v1/models` responds). Keep the old
   subdir's other files (mmproj, MTP heads) for rollback unless disk is
   critical.

Also: **third-party (e.g. Gemini) runbooks for these boxes routinely get
the basics wrong** — wrong PVE host, wrong service name, wrong model
path, wrong binary name, VRAM-infeasible parallelism. Always run a
recon pass (`systemctl list-unit-files | grep llama`, `cat` the real
launcher, `ls` the real model dir, `df -h`, `qm list` on each PVE node)
before executing a pasted plan. Treat the runbook as a hint set, the
live box as truth.

## Verification predicate sanity — don't write buggy verifiers

This is about the verifier itself, not the deployment. Two failures from
the 2026-08-15 session that wasted ~3 turns each:

**Bug A — Predicate with sentinel value that doesn't satisfy magnitude checks:**

```python
# WRONG — returns False for the value that should trigger the alert
is_dangerous = (max_tokens in (-1, 65536, 32768, 16384)) and (max_tokens > 4096)
# For max_tokens = -1: (-1 in (-1, ...)) = True AND (-1 > 4096) = False
# Result: is_dangerous = False, alert missed
```

```python
# RIGHT — explicitly handle sentinel as "unlimited"
is_dangerous = (max_tokens == -1) or (max_tokens > 4096)
```

When verifying an "is dangerous" condition for a numeric sentinel like
-1 (unlimited) or 0 (unset), write the predicate as a disjunction
(`==` for sentinels, OR `>` for magnitudes), not a conjunction with
magnitude checks that the sentinel will never satisfy.

**Bug B — Multi-response endpoint field selection ambiguity:**

```python
# WRONG — /v1/models response has TWO fields, only one has capabilities
r = json.loads(urllib.request.urlopen("http://host/v1/models").read())
models = r.get('data', r.get('models', []))   # prefers 'data' which has NO capabilities
caps = models[0].get('capabilities', [])  # returns [], missing "multimodal"
```

```python
# RIGHT — explicitly prefer the schema field that has the data you need
r = json.loads(urllib.request.urlopen("http://host/v1/models").read())
models_list = r.get('models', []) or r.get('data', [])
caps = models_list[0].get('capabilities', []) if models_list else []
# 'models' is the legacy/llama.cpp field with capabilities;
# 'data' is the OpenAI-style field without.
```

When verifying any endpoint that has multiple response shapes (legacy +
modern), probe both fields explicitly, don't assume one.