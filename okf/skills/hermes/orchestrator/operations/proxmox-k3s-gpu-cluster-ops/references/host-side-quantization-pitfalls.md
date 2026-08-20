# Host-side LLM quantization pitfalls (the things that break after the recipe is right)

The class of work: running `llmcompressor` quantization on a GPU-VM host (VM 230 on PVE1, 4× RTX 3090) where the quantization recipe is correct but the runtime environment breaks. Built from the 2026-08-15 and 2026-08-16 Qwen3.8-27B → W4A16 sessions where this exact failure chain ran ~30 minutes of wall-clock before being diagnosed on each attempt.

## What "everything is correct but it doesn't work" looks like

The seven symptoms, in order of appearance:

1. **`flash-attn` build fails with "ModuleNotFoundError: No module named 'torch'"** — pip install of `flash-attn` requires `torch` already installed (it's a build-time dep). Fix: install `torch` first, then everything else.
2. **`pip install llmcompressor` succeeds but `python -c 'import llmcompressor'` fails with `AttributeError: module 'torch' has no attribute 'accelerator'`** — `accelerate` 1.10+ requires `torch>=2.10`. With older torch you need `accelerate<1.10`.
3. **`pip install llmcompressor` warns "llmcompressor 0.13.0 requires torch>=2.10, but you have torch 2.5.1"** — version constraint conflict. Pick a side: either torch 2.10+ (which needs newer driver, 580+) or `llmcompressor<0.7` (which works on torch 2.5.1).
4. **`AutoConfig.from_pretrained()` raises `ValueError: ... model type 'qwen3_5' but Transformers does not recognize this architecture`** — Qwen3.5/Qwen3.8 architectures require `transformers>=5.4`. The tokenizer may still load (`Qwen2Tokenizer` is the same code path) so the failure surfaces at Step 3 of the recipe, not Step 1. See `references/llm-compression-repos-2026-08-15.md` for the full symptom chain.
5. **`pip install transformers` warns "llmcompressor X.Y.Z requires transformers<=4.52.4, but you have transformers 5.x which is incompatible"** — the reverse of symptom 3. After upgrading transformers for qwen3_5, you must also upgrade llmcompressor. The two upgrades are coupled.
6. **`python -c 'import torch; print(torch.cuda.is_available())'` returns False even though `nvidia-smi` works** — torch built with CUDA 13 binaries (`+cu130` suffix) on a 535 driver. Silent failure: no error, just no CUDA.
7. **`nvidia-smi` itself prints `Failed to initialize NVML: Driver/library version mismatch`** — kernel driver 535, userspace NVML 580. Most likely cause: `unattended-upgrade` pulled `libnvidia-compute-580-server` as part of a system update.

## The correct install sequence for VM 230 (driver 580, current, 4× RTX 3090)

After an unattended-upgrade has moved the driver to 580 (CUDA 13.0), the install sequence is:

```bash
# Step 1: torch matching the new driver (cu130 for driver 580+)
pip install --quiet --upgrade torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/cu130

# Verify GPU compute (real matrix multiply, not just is_available())
wget -q http://<orchestrator-ip>:8766/gpu_test.py -O /tmp/gpu_test.py
python3 /tmp/gpu_test.py
# Expected: torch 2.13.0+cu130, CUDA available, all 4 GPUs return non-zero sums

# Step 2: transformers 5.x (required for qwen3_5 / Qwen3.8 architecture)
pip install --quiet --upgrade transformers

# Step 3: jinja2 >= 3.1.0 (transformers 5.x chat template requires this)
pip install --quiet --upgrade jinja2

# Step 4: llmcompressor 0.13+ + compressed-tensors (compatible with transformers 5.x)
pip install --quiet --upgrade llmcompressor compressed-tensors

# Step 5: accelerate + datasets (compatible with everything above)
pip install --quiet --upgrade accelerate datasets

# Verify the recipe imports cleanly (the live API-shape check)
wget -q http://<orchestrator-ip>:8766/verify_quantize_fix.py -O /tmp/verify_quantize_fix.py
python3 /tmp/verify_quantize_fix.py
# Expected: "ALL_RECIPE_FIXES_OK"
```

**Why this exact order:**

- **Step 1 FIRST** because every downstream `pip install` for the ML packages will pull a torch wheel as a transitive dep, and we want the cu130 wheel. Install before any llmcompressor/transformers work.
- **Step 2 BEFORE Step 4** because transformers and llmcompressor have a version constraint conflict (transformers 4.x vs llmcompressor 0.13+, or transformers 5.x vs llmcompressor <0.7). If you install llmcompressor first, the version solver will pick the wrong pair. Pin transformers first, then install llmcompressor last.
- **Step 3** because transformers 5.x uses jinja2 features (`apply_chat_template`) that 3.0.x doesn't have. Without upgrading, the recipe crashes at Step 2 with `ImportError: apply_chat_template requires jinja2>=3.1.0`.
- **Step 4** because the API shape (`config_groups` + `QuantizationArgs`) requires llmcompressor 0.13+. Older versions accept the old kwarg form, but transformers 5.x is incompatible with them, so you can't have both old llmcompressor and new transformers.
- **Step 5 LAST** because `accelerate` and `datasets` are looser on version constraints and work with whichever combo you end up with.

The live-import check at the end is non-negotiable: do not assume the install worked. Run `verify_quantize_fix.py` (or equivalent: instantiate a `GPTQModifier(config_groups=..., targets="Linear", ignore=[...], actorder=None)` and a `QuantizationModifier(config_groups=..., kv_cache_scheme=QuantizationArgs(...))`) and confirm both print `OK` before launching the long-running recipe.

## The legacy install sequence for VM 230 (driver 535, still useful for fresh VMs from older backups)

```bash
# Step 1: ensure nvidia user libs are 535 (not 580)
apt-get install -y --allow-downgrades libnvidia-compute-535 libnvidia-cfg1-535
# If libnvidia-ml.so.1 symlink points to .580, re-link it:
# ls -l /usr/lib/x86_64-linux-gnu/libnvidia-ml.so.1
# (manually re-link if needed)

# Step 2: torch 2.5.1 with cu121 (matches 535 driver)
pip install --no-cache-dir torch==2.5.1 torchvision==0.20.1 \
    --index-url https://download.pytorch.org/whl/cu121

# Verify
python3 -c "import torch; print('cuda:', torch.cuda.is_available(), 'v:', torch.__version__)"
# Expected: cuda: True v: 2.5.1+cu121

# Step 3: transformers pinned to 4.52.4 (the last 4.x release that works with Qwen2Tokenizer + qwen3 is gated behind 5.x, so 535 hosts cannot quantize qwen3_5 models at all)
pip install --quiet 'transformers==4.52.4' 'jinja2<3.1'

# Step 4: quantization deps (older llmcompressor for torch 2.5 compatibility)
pip install --quiet 'llmcompressor<0.7' 'accelerate<1.10' compressed-tensors datasets
```

**When to use the legacy sequence:** the cluster was just restored from a 535-era backup, or the kernel driver rolled back, or you intentionally disabled unattended-upgrades and want to stay on 535 long-term.

**When NOT to use it:** you have a 580 driver already loaded and want to use qwen3_5 / Qwen3.8. The legacy sequence uses transformers 4.52.4 which cannot load the model.

## The unattended-upgrade trap (the 30-minute session-killer)

What happens on 2026-08-15:

```
T0:  nvidia-smi works, K8s pods running
T+1: unattended-upgrade runs, pulls libnvidia-compute-580-server
T+5: K8s pods still running (they bundle their CUDA libs)
T+10: host-side torch.cuda.is_available() returns False
T+15: user notices model isn't quantizing, asks why
T+20: agent runs `nvidia-smi` — fails with "Driver/library version mismatch"
T+25: agent tries `apt-get install -y --allow-downgrades libnvidia-compute-535` — blocked
T+27: agent discovers unattended-upgrade is still holding the dpkg lock
T+30: agent kills unattended-upgrade, retries downgrade, succeeds
```

The two-minute fix to detect this:
```bash
# Are the user libs and kernel driver in sync?
cat /proc/driver/nvidia/version | head -1   # NVRM version: 535.288.01
ls -la /usr/lib/x86_64-linux-gnu/libnvidia-ml.so.1
# If the .so.1 symlink target ends in .580.x.x but NVRM is 535.*, this is your problem
```

**Pre-emptive mitigation:** disable `unattended-upgrades` before any GPU-host work:
```bash
dpkg-reconfigure -plow unattended-upgrades
# Select "No" to disable
```

## The "upgrade-accepted" branch (when unattended-upgrade completes successfully)

On 2026-08-16 a different unattended-upgrade cycle ran successfully end-to-end (instead of getting stuck mid-flight): the kernel module got rebuilt under 580, `dkms` reported `nvidia/580.173.02, 5.15.0-174-generic, x86_64: installed`, and a reboot made `nvidia-smi` work again — at driver **580.173.02** with **CUDA 13.0**. The trap then became the reverse: the torch-2.5.1+cu121 pin from the 535 era no longer matches the new driver.

Symptoms that confirm you're in this branch (not the 535 branch above):
- `nvidia-smi` reports `Driver Version: 580.173.02` and `CUDA Version: 13.0`
- `dkms status` shows `nvidia/580.173.02, ... installed`
- `cat /proc/driver/nvidia/version` shows `NVRM version: NVIDIA UNIX Open Kernel Modules ... 580.173.02`
- But `torch.cuda.is_available()` is still `False` because the pinned `torch==2.5.1+cu121` has CUDA 12.1 binaries that forward-compat-fail against the 580 driver

The fix is to **upgrade PyTorch to cu130** to match the new driver:
```bash
pip install --quiet --upgrade torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/cu130
python3 -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.device_count())"
# Expected: 2.13.0+cu130 True 4
```

Then re-verify with the actual matrix-multiply recipe (real `torch.randn(512,512,device='cuda:0'); b=torch.randn(...); c=a@b; print(c.sum())` against each of the 4 GPUs). If `device_count == 4` and every matrix multiply returns a non-zero sum, the cu130 build is correctly engaging the 580 driver. Skip the rest of the 535-era sequence (no need for `libnvidia-compute-535` downgrade).

**Why this is not a 535 problem any more:** after a successful unattended-upgrade of the kernel driver, fighting apt to downgrade user-space NVML libraries is a losing battle — apt will keep re-pulling the 580 libs on the next update cycle. The healthy move is to accept the upgrade and track PyTorch to the new driver. If the cluster later drops back to 535 (driver rollback, kernel downgrade, fresh VM restore from a 535-era backup), this skill's legacy 535 sequence applies again.

## The `flash_attention_2` → `sdpa` switch (don't compile flash-attn unless you have to)

The legacy `templates/quantize.py` hardcoded `attn_implementation="flash_attention_2"`. That requires `pip install flash-attn`, which compiles a CUDA kernel against your exact torch+CUDA combo (cu121 wheel ≠ cu130 wheel). If `flash-attn` isn't installed for the current combo, model load crashes with:

```
ImportError: FlashAttention2 has been toggled on, but it cannot be used due
to the following error: the package for FlashAttention2 doesn't seem to be
installed.
```

**Fix:** default to `attn_implementation="sdpa"` (PyTorch's built-in `torch.nn.functional.scaled_dot_product_attention`, which is fast-path on Ampere and zero extra deps). The current `templates/quantize.py` template has this fallback in place via `--attn-impl` flag. Only pass `--attn-impl flash_attention_2` after `pip install flash-attn` for the matching wheel.

**Fast path note for Qwen3.5:** the model's hybrid architecture uses Gated DeltaNet (linear attention) on some layers and full gated attention elsewhere. The fast-path library for the linear layers is `flash-linear-attention` (`fla-org/flash-linear-attention`), not flash-attn. If the warning "The fast path is not available because one of the required library is not installed. Falling back to torch implementation" appears during model load, install `flash-linear-attention` + `causal-conv1d` for the linear-attention fast path. The W4A16 quantization itself runs fine on the torch fallback; the warning is informational.

## K3s pods reclaiming GPUs during host-side work

Every time the nvidia driver is reloaded (driver upgrade, `modprobe nvidia`, K3s restart after `nvidia-device-plugin` DaemonSet recreation), K3s pods that had requested `nvidia.com/gpu` will be rescheduled and start pulling VRAM. A `kai-llama` + `ned-llama` + `newfred-llama` triad that was scaled to 0 will quietly come back up to 1 replica each as soon as the device plugin re-advertises `nvidia.com/gpu: 4`, leaving the host with ~23 GiB per GPU occupied before any host-side work begins.

**Before any host-side GPU work** (quantization, training, large model load), do this and re-verify:
```bash
# Inside the VM
kubectl scale deploy kai-llama ned-llama newfred-llama -n llm-inference --replicas=0
kubectl delete pods -n llm-inference --all --force --grace-period=0
# Wait 5-10s for VRAM to be released
nvidia-smi --query-gpu=index,memory.used --format=csv
# Expected: every GPU shows ~1 MiB used
```

If `nvidia-smi` still shows ~23 GiB used after 10s, the LLM pods are still scheduled. Inspect with `kubectl get pods -n llm-inference` — any replica set with an unscheduled pod will pick up the freshly-available GPU and start loading weights. Repeat the scale + delete until `nvidia-smi` is clean.

**Why this matters for quantization specifically:** a W4A16 GPTQ job needs ~80-100 GB of total VRAM headroom (BF16 model load + intermediate activations + output checkpoint). If the LLM pods have already claimed ~92 GiB across 4 GPUs, the quantization will OOM even though the math says it should fit.

## When this skill applies

- The user asks to run a quantization job on a GPU VM (vs in a container)
- The user reports "the quantization isn't working" but the recipe is right
- `nvidia-smi` fails but K3s pods are running
- `torch.cuda.is_available()` returns False on a host with working GPUs
- The driver auto-upgraded past 535 and now torch can't see CUDA
- The recipe script fails at Step 1/3 with `qwen3_5` architecture error
- The recipe script fails at Step 3 with `flash_attention_2` ImportError

## When NOT to use this skill

- The quantization is running inside a K8s container (it has its own CUDA libs) — go to `templates/llama-cuda-on-k3s-deploy.yaml` instead
- The user is on a different GPU host (not VM 230 / driver 535) — the patterns transfer but the exact pin versions don't
- The user is serving a quantized model (not quantizing) — go to `references/vllm-via-lued-int8.md`
- The user wants to fix K3s pod GPU visibility (not host-side CUDA) — go to `references/nvidia-device-plugin-k3s-v134.md`

## Companion skills

- `references/llm-compression-repos-2026-08-15.md` — the W4A16 recipe itself (this skill is about the runtime, not the recipe). Covers the llmcompressor 0.13 API change (`config_groups` + `QuantizationArgs`) and the qwen3_5 architecture requirement.
- `references/llama-cuda-build-and-deploy.md` — the parallel gotchas for llama.cpp builds (CPU flags, CUDA 13 forward-compat)
- `references/llama-server-gpu-vs-cpu-verification.md` — the GPU-vs-CPU verification recipe, must run before claiming "GPU compute confirmed"