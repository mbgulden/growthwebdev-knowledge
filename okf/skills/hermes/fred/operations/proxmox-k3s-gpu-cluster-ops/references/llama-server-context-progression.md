# llama-server context progression: 32k → 131k → 262k → 1M

Distilled from the 2026-08-15 sessions that progressively unlocked larger
context windows on Qwen3.8-27B + 2× RTX 3090 + patched llama.cpp. Each
step has a known-good recipe, a known failure mode, and a verification
script template. Use this as a walkable procedure when Michael asks
"can we go bigger?" after a successful smaller-context deployment.

## The progression at a glance

| Step | Context | Model | Image | VRAM/card | Throughput | Verified |
|---|---|---|---|---|---|---|
| 0 | 32,768 | Q4_K_M | llama-cuda:v2 | ~17 GiB | 37 t/s | ✅ Aug 15 14:00 |
| 1 | 131,072 | Q4_K_M | llama-cuda:v2 | ~19 GiB | 37 t/s | ✅ Aug 15 16:00 |
| 2 | 262,144 | Q4_K_M | llama-cuda:v2 | ~23 GiB | 37 t/s | ✅ Aug 15 18:00 |
| 3 | 1,048,576 | Q4_K_M + mmproj | llama-cuda:v7 (patched) | ~23 GiB (layer-split) | 31-50 t/s | ✅ Aug 15 22:00 |

Every step is reachable on the same hardware (2× RTX 3090 24 GB) without
upgrading GPUs. The trick is matching the math to the model's KV cache
shape and staying under the llama.cpp caps.

## The math at each step (Qwen3.8-27B, n_embd=5120, 28 layers, 4 KV heads, head_dim=128)

Per-token KV cache size:
- q8_0 (1 byte/elem): 28 × 2 × 4 × 128 × 1 = **28,672 bytes/token ≈ 28 KiB/tok**
- q4_0 (0.5 byte/elem): 28 × 2 × 4 × 128 × 0.5 = **14,336 bytes/token ≈ 14 KiB/tok**

For Q4_K_M weights (~17 GiB) on a single 24 GiB card with 1.5 GiB CUDA
overhead and 5 MiB output buffer, the per-card VRAM budget for KV cache
is ~5.4 GiB:

| Context | q8_0 KV | q4_0 KV |
|---------|---------|---------|
| 65,536 | ~1.79 GiB | ~0.90 GiB |
| 131,072 | ~3.58 GiB | **~1.79 GiB** ← verified working |
| 196,608 | ~5.38 GiB | ~2.69 GiB |
| 262,144 | ~7.17 GiB | ~3.58 GiB |
| 524,288 | ~14.34 GiB | ~7.17 GiB |
| 1,048,576 | ~28.67 GiB | ~14.34 GiB |

For 1M context on a 2× 24 GiB pair (layer-split): Q4_K_M (16 GiB) + q4_0
KV (14.7 GiB) + mmproj (1 GiB) + flash-attn workspace (3 GiB) + overhead
(2 GiB) = ~37 GiB — fits in 48 GiB with ~10 GiB headroom.

## Step 1: 32k → 131k context (single GPU, q4_0 KV)

This is the simplest bump. Just patch `--ctx-size` and add KV cache
compression. No source patch needed.

**Patch (only 3 lines):**
```yaml
# K8s Deployment args
- --ctx-size          # existing: 32768
- "131072"            # NEW: 131072
- --cache-type-k      # NEW
- q4_0                # NEW (q4_0 halves KV cache memory)
- --cache-type-v      # NEW
- q4_0                # NEW
```

**Hermes side:**
```yaml
providers:
  qwen27b-kai-local:
    context_length: 131072          # provider-level
    models:
      local-qwen-27b-q4-kai:
        context_length: 131072      # model-level
```

**Expected VRAM:** ~19 GiB / 24 GiB (77% util, 5 GiB free)
**Expected throughput:** 37 t/s (same as step 0)
**Verification:** `/slots` shows `n_ctx: 131072`, `nvidia-smi` shows GPU 2
at ~19 GiB, `predicted_per_second` ~37 t/s, no `exceed_context_size_error`
on an 80k-token prompt.

## Step 2: 131k → 262k context (single GPU, q4_0 KV)

Same recipe as step 1, just bump `--ctx-size`. 262k is Qwen3.8-27B's
native training length — no extrapolation, full quality.

**Patch:**
```yaml
- --ctx-size
- "262144"            # was 131072
```

**Hermes side:**
```yaml
context_length: 262144          # both levels
```

**Expected VRAM:** ~23 GiB / 24 GiB (96% util, 1 GiB free — VERY TIGHT)
**Expected throughput:** ~37 t/s (same)
**Verification:** `/slots` shows `n_ctx: 262144`, `nvidia-smi` shows GPU
at 23 GiB used, `predicted_per_second` ~37 t/s, real chat completion
with 80k+ tokens succeeds.

## Step 3: 262k → 1M context (2× GPU layer-split, patched source)

This is the unlock that requires BOTH the source patch AND `--kv-unified`
AND `--fit off` AND `--no-cache` Docker build. All four layers are
required; each fails silently if missed.

**The four layers:**

1. **Source patch at `tools/server/server-context.cpp:1202`:** comment out
   `n_ctx_slot = n_ctx_train;` (the line that caps ctx to training length).
2. **`--kv-unified` in K8s args:** bypasses the per-sequence division
   at `src/llama-context.cpp:293` where `n_ctx_seq = n_ctx / n_seq_max`
   silently slices the requested context.
3. **`--fit off` in K8s args:** bypasses the auto-shrink heuristic
   introduced in master (a separate code path from the cap).
4. **`docker build --no-cache`:** the build context can have stale `.so`
   files cached from earlier builds. The patched binary loads but the
   shared library still has the cap line.

**Patch recipe (use Q4_K_M, not Q5 — Q5 OOMs at 1M even with the patch):**

```yaml
# K8s Deployment args
- --model
- /models/qwen3.8-27b-q4/Qwen3.8-27B-Q4_K_M.gguf    # Q4, not Q5
- --mmproj
- /models/qwen3.8-27b-q4/mmproj-F16.gguf            # vision
- --ctx-size
- "1048576"                                         # 1M
- --parallel
- "1"                                               # required
- --cache-type-k
- q4_0
- --cache-type-v
- q4_0
- --flash-attn
- "on"                                              # required by q4_0 KV
- --rope-scaling
- yarn                                              # parsed but optional
- --yarn-orig-ctx
- "262144"
- --yarn-ext-factor
- "4.0"
- --yarn-attn-factor
- "1.0"
- --tensor-split
- "1,1"                                             # 2 GPUs
- --split-mode
- layer
- --alias
- local-qwen-27b-q5-fred-1m
- --kv-unified                                      # CRITICAL
- --fit
- "off"                                             # CRITICAL
```

**Build the patched image:**
```bash
# 1. Apply the source patch
cd /tmp/llama-master
# Edit tools/server/server-context.cpp:1202 — remove the n_ctx_slot = n_ctx_train; line
# (Keep the SRV_WRN for visibility, just don't act on it)

# 2. Build inside nvidia/cuda:12.2.0-devel container
docker run --rm -v $(pwd):/src -v /tmp/build-out:/out \
    nvidia/cuda:12.2.0-devel-ubuntu22.04 bash -c '
    apt-get install -y cmake && cd /src && rm -rf build
    cmake -B build -DGGML_CUDA=ON -DCMAKE_BUILD_TYPE=Release \
          -DGGML_NATIVE=OFF -DGGML_CPU_ALL_VARIANTS=OFF \
          -DCMAKE_CUDA_ARCHITECTURES=80
    cmake --build build --config Release --target llama-server -- -j24
    cp /src/build/bin/llama-server /out/llama-server-new
    '
# ~15-20 min wall time

# 3. Refresh the build-bin libraries (the patch produced new .so files)
cp /tmp/build-out/libllama-server-impl.so* /tmp/llama-fresh/build-bin/
# ... etc for every lib* in build-out

# 4. Build the Docker image with --no-cache (critical!)
docker build --no-cache -t llama-cuda:v7 /tmp/llama-fresh

# 5. Save and push to VM 230
docker save llama-cuda:v7 > /tmp/llama-cuda-v7.tar
# (serve via http.server, wget+ctr import in VM 230)
```

**Hermes side:**
```yaml
providers:
  qwen27b-fred-local:
    context_length: 1048576
    models:
      local-qwen-27b-q5-fred:
        context_length: 1048576
```

**Expected VRAM:** ~23 GiB / 24 GiB per card (95% util, 1 GiB free per
card — with layer-split, both cards share the workload)
**Expected throughput:** 31-50 t/s (vs 570 t/s on single GPU; layer-split
incurs cross-GPU communication overhead)
**Verification:**
- `/slots` shows `n_ctx: 1048576` (NOT 262144)
- Pod log shows `kv_unified = 'true'`
- `predicted_per_second` 31-50 t/s (vs 5-10 t/s for CPU)
- Real chat completion with 35k+ tokens succeeds
- `nvidia-smi` shows ~23 GiB on both GPU 0 and GPU 1

## The four failure modes that look like "AI capabilities aren't ready" but are actually deployment bugs

When Michael asks "is it actually running on GPU?" or "is the vision
broken?", the answer is the diagnostic from
`references/llama-server-gpu-vs-cpu-verification.md`. The four failure
modes that PRESENT as "AI limitations" but are actually deployment bugs:

1. **CUDA 13 forward-compat (operator pulled a prebuilt):** binary
   loads, model loads, but `predicted_per_second < 15` and `nvidia-smi`
   shows ~256 MiB (CUDA init probe, not model load). Fix: rebuild
   against CUDA 12.x dev image with `-DCMAKE_CUDA_ARCHITECTURES=80`.

2. **Shared library cache (operator's patch in source but build artifacts
   unchanged):** `docker build` without `--no-cache` returns the old
   `.so` files. Patched binary loads but stale library still has the
   cap. Fix: `docker build --no-cache`.

3. **CPU instruction mismatch (target VM is `kvm64`):** the binary
   crashes with `Illegal instruction` before any inference. The pod
   is in CrashLoopBackOff with empty logs. Fix: `qm set <vmid> --cpu
   host` + full VM restart.

4. **`--kv-unified` forgotten (the kv-split gotcha):** even with the
   source patch, the per-sequence division at
   `src/llama-context.cpp:293` silently hides the cap. The startup
   log shows `kv_unified = 'false'`. Fix: add `--kv-unified` to the
   args.

All four present as "the model is slow" or "the model is broken" — but
each has a specific fix that takes 30 seconds to a few minutes. The
diagnostic in `llama-server-gpu-vs-cpu-verification.md` catches all
four.

## When to stop the progression

- **At step 2 (262k):** when the use case is multi-document chat, code
  review, or any typical agent workload. 262k is already 4× the previous
  65k ceiling and uses 96% of one GPU. Most prompts never exceed 100k
  tokens.
- **At step 3 (1M):** when the use case is document RAG over a long
  codebase, repo-level code generation, or long-form analysis. The
  1M context has quality degradation at far positions (RoPE
  extrapolation past `n_ctx_train=262144`).
- **Stop at step 2 if capacity is shared:** if you want to keep Kai/Ned
  on a single GPU each, step 3 requires Fred's full 2-GPU pair. There
  are no idle GPUs left to upgrade step 2 to step 3 without losing other
  agents.

## Verified recipe files

- `templates/llama-cuda-on-k3s-deploy.yaml` — step 2 (262k, single GPU)
- `templates/llama-cuda-1m-trial.yaml` — step 3 (1M, 2× GPU layer-split)
- `templates/llama-cuda-on-k3s-deploy-multi-gpu.yaml` — 2× GPU without
  context extension (smaller models, more throughput)

## Companion references

- `references/llama-server-runtime-gotchas.md` — the gotchas at each step
  (the `--ctx-size` × `--parallel` interaction, the `--flash-attn`
  argparser, the PV hostPath trap, the YARN cap, the kv-unified gotcha)
- `references/llama-cuda-build-and-deploy.md` — the build side (CUDA
  toolkit matching driver, the linker flag, the CPU instruction trap)
- `references/llama-server-gpu-vs-cpu-verification.md` — the GPU-vs-CPU
  diagnostic (predicted_per_second + nvidia-smi memory)
- `references/llama-server-vision-and-multi-pod.md` — vision (mmproj)
  enabling and multi-pod layout
