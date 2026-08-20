# GPU-vs-CPU verification for llama-server deployments

Distilled from the 2026-08-15 session where the v6 binary was running
CPU inference despite reporting `n_ctx=1048576` and `multimodal`
capabilities. The user explicitly asked: *"Make sure the GPUs are
actually running the models. It seems like they are just running off of
a cpu or something."* The hint was correct — the v6 binary had CUDA 13.x
forward-compat headers that the host driver (535) couldn't load, and
llama.cpp silently fell back to CPU.

## The smoking gun

Both of these fields are populated during model LOAD, not during inference:

- `n_ctx` in `/slots` — set when the model file is opened, before any CUDA init
- `capabilities` in `/v1/models` — set from the GGUF metadata, before any CUDA init

CPU inference produces the same response as GPU inference for both. **They are not proof of GPU compute.**

The **only field that distinguishes CPU from GPU** is `predicted_per_second` in the response of a real chat completion. The values for a 27B Q4_K_M model are:

| Compute | predicted_per_second |
|---|---|
| CPU (i9-13900K, 16 threads) | ~5-10 t/s |
| 1× RTX 3090 (24 GB) | ~37 t/s |
| 2× RTX 3090 layer-split (48 GB) | ~30-60 t/s |
| 4× RTX 3090 stacked (96 GB) | ~60-100 t/s |

Anything below 30 t/s for a 27B Q4 model is suspicious. Anything below 15 t/s is CPU.

## The orthogonal check

`nvidia-smi --query-gpu=memory.used` on the **VM** that owns the GPU. When llama.cpp fails to load CUDA, the model still loads into the container's view (the runtime has a fallback that touches the GPU to probe it). The probe shows ~256 MiB used per GPU — that's the CUDA init probe, not the model. A real model load will show ~17-23 GiB used per GPU.

```bash
# Real GPU compute (verified 2026-08-15): 18,266 MiB per GPU for Q4_K_M
# CPU fallback (verified 2026-08-15): 256 MiB per GPU
qm guest exec <vmid> -- nvidia-smi --query-gpu=index,memory.used --format=csv,noheader
```

## The diagnostic recipe (5-step, takes 30 seconds)

```bash
# 1. Send a real chat completion
curl -s -X POST http://<host>:<port>/v1/chat/completions \
    -H 'Content-Type: application/json' \
    -d '{"model":"<alias>","messages":[{"role":"user","content":"What is 2+2?"}],"max_tokens":10,"stream":false}'
# Capture the response — note `.timings.predicted_per_second`

# 2. Check GPU memory
sshpass -p ... ssh root@<pve-ip> "qm guest exec <vmid> -- nvidia-smi --query-gpu=index,memory.used --format=csv,noheader"

# 3. Classify:
#    - predicted_per_second > 25 AND memory.used > 10000 → GPU compute confirmed ✅
#    - predicted_per_second < 15 AND memory.used < 1000 → CPU fallback (broken) ❌
#    - Mixed signals (high memory, low tps) → partial GPU init, kernel on CPU ⚠️
```

## Root causes of silent CPU fallback (in order of likelihood)

1. **CUDA driver mismatch.** The binary was built with CUDA 13.x but the host driver is <580. Symptom in startup log:
   `ggml_cuda_init: failed to initialize CUDA: forward compatibility was attempted on non supported HW`
   Fix: rebuild against `nvidia/cuda:12.2.0-devel-ubuntu22.04` (matches driver 535.x). Add `-DCMAKE_CUDA_ARCHITECTURES=80` to keep the build Ampere-only (no forward-compat).

2. **NVML library missing in the container.** The runtime can't query GPU state. Symptom: `no NVML found`. Fix: ensure `libnvidia-ml.so.1` is in `LD_LIBRARY_PATH`; `nvidia-cuda:12.2.0-runtime` base image has it.

3. **The prebuilt Docker image is for a different CUDA version.** `ghcr.io/ggml-org/llama.cpp:server-cuda` is built with CUDA 13.x. Pulling it onto a 535-driver host produces the same silent CPU fallback. Always check the prebuilt's CUDA version against `nvidia-smi --query-gpu=driver_version` before pulling.

## The 2026-08-15 incident (origin of this rule)

The user asked "are they actually running on GPU?" because something felt off. The verifier reported all 38/38 PASS on the deployment, but the `predicted_per_second` field was 31.7 — exactly the CPU range. The fix was to rebuild the v6 binary with `-DCMAKE_CUDA_ARCHITECTURES=80` (no forward-compat), and the resulting v7 binary reported 570 t/s on the same hardware with identical args. The 18× speedup is the fingerprint of GPU compute actually engaging.

This is the only failure mode where the verifier is structurally wrong: by the time the script checks `n_ctx` and `capabilities`, the model has already loaded, and the load path itself doesn't engage CUDA. The smoking gun appears only in a real workload's `timings.predicted_per_second` and the orthogonal `nvidia-smi` readout.

## Verification (must run before any "GPU compute confirmed" claim)

```bash
# This is the canonical GPU-or-CPU check. Run it on every llama-server
# deployment, not just the first one. Spot-check after every CUDA
# rebuild because the silent-CPU-fallback footgun is real.
predicted=$(curl -s -X POST http://<host>:<port>/v1/chat/completions \
    -H 'Content-Type: application/json' \
    -d '{"model":"<alias>","messages":[{"role":"user","content":"2+2"}],"max_tokens":10,"stream":false}' \
    | python3 -c "import json,sys; print(json.load(sys.stdin)['timings']['predicted_per_second'])")
mem=$(qm guest exec <vmid> -- nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)
[[ $(echo "$predicted > 25" | bc) == 1 ]] && [[ $mem -gt 10000 ]] && echo "GPU compute: $predicted t/s, $mem MiB" || echo "FAIL: CPU fallback, predicted=$predicted t/s, mem=$mem MiB"
```

## Anti-pattern: claiming "GPU compute confirmed" without both indicators

A single check (memory OR tps) is not enough. The 2026-08-15 v6 failure had:
- nvidia-smi showed 256 MiB (small but not zero) — would fail the memory check
- predicted_per_second was 31.7 (low but not zero) — would fail the tps check

If only the memory check is run, 256 MiB looks like "something is loaded" and the operator may dismiss it. If only the tps check is run, 31.7 looks "reasonably fast" and the operator may dismiss it. **Both are misleading individually; only both together flag the issue definitively.**

## Companion rule: the Docker `--no-cache` footgun

If a `.cpp` source is patched (e.g. to remove the 1M cap), and the resulting docker image is built without `--no-cache`, the `COPY build-bin/` step may return the OLD `.so` files from before the patch. The binary in the image is the patched one, but the shared library is the pre-patch one. The runtime behavior matches the pre-patch version.

The 2026-08-15 v6 deployment hit this twice: first the v6 image had the patched `llama-server` binary but stale `libllama-server-impl.so` (cap still fires), then the v7 image built without `--no-cache` but the build-bin SHA matched v6, confirming the same library was reused. The fix: `docker build --no-cache -t llama-cuda:vN .` after every source patch that produces a new library. Verify with `sha256sum /usr/local/lib/llama/libllama-server-impl.so` inside the running container and compare to the local build's hash.

The deeper rule: **if you're claiming a patch is in effect, verify the library SHA in the running container matches the local build's library SHA, not just the binary timestamp.** Two same-named `.so` files can coexist if docker cached the old one and the new one is in a different layer.
