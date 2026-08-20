# llama.cpp CUDA build and deploy

Distilled from the 2026-08-15 session that built the `llama-cuda:v2` image
that powers Kai/Ned/Fred on VM 230 (4× RTX 3090, K3s v1.34, nvidia-container-toolkit).

**This file is about the BUILD and IMAGE-TRANSFER path. Runtime gotchas
(load it before wiring a profile) are in `references/llama-server-runtime-gotchas.md`.**

## The two-host build problem

llama.cpp CUDA must link against both **CUDA toolkit headers/libs** (in
`nvidia/cuda:12.2.0-devel`) and **NVIDIA driver stubs** (in `libcuda.so`,
which lives only on a GPU host, not in the docker image).

If you build INSIDE the container naively, you get:

```
undefined reference to 'cuDeviceGetAttribute'
undefined reference to 'cudaMemcpy'
```

at link time. The fix is `-Wl,--allow-shlib-undefined` so the missing
libcuda symbols are deferred to runtime, where the nvidia CDI / containerd
injects the real libcuda from the host's nvidia driver into the container.

**Don't try to make `--allow-shlib-undefined` work for f16 inference** — the
fix is build-with-shlib-undefined; runtime dep comes from the container
runtime, not from install.

## CUDA version must match the target host driver

The host's NVIDIA driver version determines which CUDA toolkits are
forward-compatible. The matrix is roughly:

- Driver 470+: CUDA 11.x
- Driver 525+: CUDA 12.0-12.2
- Driver 535+: CUDA 12.4
- Driver 545+: CUDA 12.5-12.6
- Driver 555+: CUDA 12.7
- Driver 565+: CUDA 12.8
- Driver 580+: CUDA 13.x

`ghcr.io/ggml-org/llama.cpp:server-cuda` (the latest prebuilt as of Aug 2026)
is built with CUDA 13.x. It will **not** run on a host with driver <580
even though `nvidia-smi` works — the binary links against forward-compat
symbols that the older driver can't load. Symptom:

```
ggml_cuda_init: failed to initialize CUDA: forward compatibility was
attempted on non supported HW
no usable GPU found, --gpu-layers option will be ignored
```

followed by either CPU-only inference or refusal to load any model.

**Always run this preflight before pulling a prebuilt:**

```bash
# Host driver version
nvidia-smi --query-gpu=driver_version --format=csv,noheader
# 535.288.01 (our case)

# Prebuilt's CUDA version (check the Dockerfile or labels)
docker inspect --format='{{ index .Config.Labels "org.opencontainers.image.version" }}' \
    <image-name>
# or read the FROM line of the upstream Dockerfile
```

If the prebuilt requires a newer driver than the host has, **rebuild from
source** against a CUDA image that matches the host driver (e.g.
`nvidia/cuda:12.2.0-devel-ubuntu22.04` for 535.x drivers). The fresh-source
recipe below takes ~15-20 min wall time but produces a working binary.

## The two-stage build pattern

Stage 1 (`Dockerfile.build`, just for compiling) builds the binary plus the
ggml shared libraries. Stage 2 (`Dockerfile.final` or similar) assembles a
slim runtime image with the binary and libs, but uses
`nvidia/cuda:12.2.0-runtime` as the base (not the empty `base` which lacks
libcublas).

**Verified final image composition** (this is what's in `llama-cuda:v2`):

- Base: `nvidia/cuda:12.2.0-runtime` (provides `libcublas.so.12`,
  `libcudart.so.12`)
- The llama-server binary at `/usr/local/bin/llama-server`
- All `libggml*.so` and `libmtmd.so` siblings in `/usr/local/lib/llama/`
- LD_LIBRARY_PATH set to `/usr/local/lib/llama:/usr/local/cuda/lib64`

**Don't use `nvidia/cuda:12.2.0-base`** — it's missing `libcublas.so.12`
and the model will fail to load (`cublas not found` errors).

## The CPU-instruction portability trap

When you build llama.cpp on webtop-hermes (or any modern build host),
the build may silently use `-march=native`, which embeds AVX/AVX-512
instructions native to the build host's CPU. When you move the binary
to VM 230 inside PVE1, the VM's virtual CPU may only expose SSE/SSE2
(especially if the VM CPU type defaults to `kvm64`).

**Symptoms:**
```
Illegal instruction (core dumped)
```

inside the llama-server process, even though the binary runs fine
under `nvidia-smi` and `ldd`.

**Two fixes:**

1. **Set the target VM CPU to `host`** so it exposes all of PVE1's CPU
   instructions:
   ```bash
   qm set <vmid> --cpu host
   qm stop <vmid>     # required: cpu change does NOT take effect on running VM
   qm start <vmid>    # full reboot needed for CPU type change
   ```
   This is the **correct** fix for production. `host` CPU type gives the
   guest access to all CPU features the host actually has.

2. **Build with portable CPU instructions**: pass
   `-DCMAKE_C_FLAGS="-march=x86-64"` (or similar) at llama.cpp build time.
   This produces a binary that runs anywhere but may be slower (no SIMD
   optimizations).

**Always do (1) for production deployments.** Don't ship a portable
llama.cpp binary to fix a host CPU issue — fix the host.

**Mandatory preflight before building llama.cpp for any new VM:**
```bash
# Inside the target VM (via qm guest exec)
grep -m1 ^flags /proc/cpuinfo
# If you see only "sse sse2" → VM is kvm64; MUST change to host.
# If you see "avx avx2 ..." → VM is already host or has the right CPU type.
```

If the target VM was restored from an older backup, the CPU type may
default to `kvm64` regardless of what the host has. The
`grep -m1 ^flags /proc/cpuinfo` check is the fastest way to catch this
before spending 15-20 min on a CUDA build.

**For GGUF metadata verification** of `n_ctx_train`, you can read the GGUF
header from the running pod via `libggml-base.so`. There's no public
`llama-gguf-info` binary; the simplest way to verify model metadata is
to look at the `/props` endpoint after startup.

## Image transfer to VM 230

VM 230 cannot pull images from Docker Hub (no outbound connectivity to
`registry-1.docker.io` for authentication reasons in some configs), so
images have to be **transferred manually**:

1. **Save the image** on the build host:
   ```bash
   docker save -o /tmp/llama-cuda-v2.tar llama-cuda:v2
   ```
   Final image is ~4.2 GB.

2. **Serve over HTTP** with `python3 -m http.server`:
   ```bash
   cd /tmp && python3 -m http.server 8766 --bind 0.0.0.0
   ```

3. **Pull + import in VM 230**:
   ```bash
   qm guest exec <vmid> -- bash -c "
     wget http://<host-lan-ip>:8766/llama-cuda-v2.tar
     ctr -n k8s.io images import llama-cuda-v2.tar
     ctr -n k8s.io images ls | grep llama-cuda
   "
   ```
   The `ctr` import takes 3-10 minutes for a 4 GB image — start it
   backgrounded with `nohup setsid` and poll.

## Pod startup crashes (empty log + CrashLoopBackOff)

If the pod starts and crashes with **zero useful logs**, the issue is
usually:

1. **CPU instruction mismatch** (see above) — pod crashes before
   the model loads, logs are empty or show only `Illegal instruction`.

2. **CPU didn't take effect without a reboot**: changing `qm set
   <vmid> --cpu host` requires a full VM reboot, not just a restart. The
   `qm start <vmid>` after the change is the reboot trigger.

3. **`qwen35` / `qwen35moe` architecture not in vendored llama.cpp**: only
   relevant if you're using Ollama (which vendors a fork). Upstream
   `ggml-org/llama.cpp` from `b5368` onwards supports these architectures.

**Diagnostic recipe** when a pod is in CrashLoopBackOff with no logs:

```bash
# 1. Get the pod's last-known termination reason
kubectl describe pod -n llm-inference <pod-name> | tail -30

# 2. Run llama-server manually inside a debug pod (or via kubectl exec
#    if the image has bash) with the same args and watch for crash output
kubectl exec -n llm-inference -it <pod-name> -- /usr/local/bin/llama-server <args>
```

## Container readiness probe timing

`readinessProbe.initialDelaySeconds` should be at least **60s** for large
models. Loading 17-19 GB of weights + KV cache + mmproj can take 30-50s,
then CUDA initialization adds another 5-10s. 60s gives headroom.

`failureThreshold: 30` is needed: 30 × 10s period = 300s (5 min) of grace
for warm load. Drop it to 10 (100s) once you've confirmed the pod stays up.
