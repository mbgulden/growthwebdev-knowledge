"""
Live quantize.py recipe verifier for hybrid-attention LLMs.

AD-HOC VERIFICATION SCRIPT (not hermes suite green).
Use this as the template for any recipe verifier that runs against the
quantize.py on the VM. Pre-baked with the SSH/qm shell-escape workarounds.

Usage:
    python3 verify-recipe-live.py
    # Or import and customize the checks list for a new recipe

Returns 0 on PASS, 1 on FAIL. Prints section-by-section results with PASS/FAIL.
"""

import json
import re
import subprocess
import sys

SSH = "sshpass -p '[REDACTED]' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null root@192.168.1.2"


def direct_qm_grep(pattern, file="/tmp/qwen-quantize/quantize.py"):
    """Run grep via qm guest exec and extract count from JSON output.

    Uses fixed-string (-F) so regex metachars don't need escaping.
    Single quotes around the inner command survive the SSH wrapper.
    """
    inner = f"grep -cF '{pattern}' {file} 2>/dev/null || echo 0"
    inner_for_bash = "'" + inner.replace("'", "'\"'\"'") + "'"
    cmd = f"qm guest exec 230 -- bash -c {inner_for_bash}"
    full = f'{SSH} "{cmd}"'
    r = subprocess.run(full, shell=True, capture_output=True, text=True, timeout=20)
    text = r.stdout
    if '"out-data"' in text:
        try:
            start = text.find('{')
            end = text.rfind('}') + 1
            obj = json.loads(text[start:end])
            out_data = obj.get("out-data", "")
            m = re.search(r'\d+', out_data)
            return int(m.group()) if m else 0
        except Exception:
            pass
    m = re.search(r'\d+', text)
    return int(m.group()) if m else 0


def direct_qm_command(cmd_in_vm):
    """Run arbitrary command inside VM 230, return raw stdout from out-data."""
    inner_for_bash = "'" + cmd_in_vm.replace("'", "'\"'\"'") + "'"
    full_cmd = f"qm guest exec 230 -- bash -c {inner_for_bash}"
    full = f'{SSH} "{full_cmd}"'
    r = subprocess.run(full, shell=True, capture_output=True, text=True, timeout=30)
    text = r.stdout
    if '"out-data"' in text:
        try:
            start = text.find('{')
            end = text.rfind('}') + 1
            obj = json.loads(text[start:end])
            return obj.get("out-data", "")
        except Exception:
            m = re.search(r'"out-data"\s*:\s*"([^"]*)"', text)
            if m:
                return m.group(1).replace('\\n', '\n').replace('\\"', '"')
    return text


def ssh_run(cmd, timeout=30):
    full = f'{SSH} "{cmd}"'
    try:
        r = subprocess.run(full, shell=True, capture_output=True, text=True, timeout=timeout)
        text = r.stdout
        if '"out-data"' in text:
            try:
                start = text.find('{')
                end = text.rfind('}') + 1
                obj = json.loads(text[start:end])
                return obj.get("out-data", "")
            except Exception:
                m = re.search(r'"out-data"\s*:\s*"([^"]*)"', text)
                if m:
                    return m.group(1).replace('\\n', '\n').replace('\\"', '"')
                return text
        return text
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    except Exception as e:
        return f"ERROR: {e}"


def check(name, condition, note=""):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {name}{(' — ' + note) if note else ''}")
    return condition


print("=" * 70)
print("Quantize Recipe Live Verification (ad-hoc)")
print("=" * 70)
print()

passed = 0
total = 0

# [1] Process running
print("[1] Quantization process running")
out = ssh_run('qm guest exec 230 -- bash -c \'ps aux | grep -E "python3.*quantize" | grep -v grep | head -1\'')
total += 1
if check("Process running with --seq-len 4096", "python3" in out and "seq-len 4096" in out):
    passed += 1

# [2] "re:" prefix count (THE CRITICAL FIX)
print()
print("[2] 're:' prefix on ignore patterns")
n_re = direct_qm_grep("re:")
total += 1
if check("'re:' prefix on patterns (>=6)", n_re >= 6, f"{n_re} occurrences"):
    passed += 1

# [3] All 7 BF16 exclusion patterns
print()
print("[3] All 7 BF16 exclusion patterns")
for pattern, label in [
    ("visual", "Vision tower (visual)"),
    ("merger", "Vision merger (merger)"),
    ("linear_attn", "DeltaNet projections (linear_attn)"),
    ("in_proj", "DeltaNet sub-projections (in_proj)"),
    (".*mtp.*", "MTP heads"),
    ("embed_tokens", "Input embeddings"),
    ("lm_head", "lm_head (exact)"),
]:
    n = direct_qm_grep(pattern)
    total += 1
    if check(f"{label}", n >= 1, f"{n} occurrences"):
        passed += 1

# [4] Hessian dampening
print()
print("[4] Hessian dampening")
for pattern, label in [
    ("dampening_frac=0.05", "dampening_frac=0.05"),
    ("offload_hessians=True", "offload_hessians=True"),
]:
    n = direct_qm_grep(pattern)
    total += 1
    if check(f"{label}", n >= 1, f"{n} occurrences"):
        passed += 1

# [5] Calibration data loaded
print()
print("[5] Calibration data loaded")
out = direct_qm_command("grep -E 'Loaded.*samples' /tmp/quantize_main.log")
for dataset, label in [
    ("Bespoke-Stratos", "Bespoke-Stratos-17k (reasoning)"),
    ("iamtarun", "iamtarun/python_code (code)"),
    ("ultrachat", "ultrachat_200k (dialogue)"),
]:
    total += 1
    if check(label, dataset in out):
        passed += 1

# [6] Marlin W4A16 scheme
print()
print("[6] W4A16 Marlin scheme")
for pattern, label in [
    ("group_size=128", "group_size=128"),
    ("symmetric=True", "symmetric=True"),
    ("num_bits=4", "num_bits=4 (INT4)"),
]:
    n = direct_qm_grep(pattern)
    total += 1
    if check(f"{label}", n >= 1, f"{n} occurrences"):
        passed += 1

# [7] FP8 KV cache
print()
print("[7] FP8 KV cache")
n = direct_qm_grep("fp8_e4m3")
total += 1
if check("fp8_e4m3 KV cache", n >= 1, f"{n} occurrences"):
    passed += 1

# [8] Module count check (the integration test)
print()
print("[8] Module count (DeltaNet correctly excluded — should be ~65, not 768)")
out = direct_qm_command("grep -oE '\\(.*/65\\): Calibrating' /tmp/quantize_main.log | tail -1")
total += 1
if check("Currently calibrating within 1-65 (NOT 768)", "/65" in out):
    passed += 1

# [9] GPU state
print()
print("[9] GPU state")
out = direct_qm_command("nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader,nounits | head -4")
mem_values = []
util_values = []
for line in out.strip().split('\n'):
    if ',' in line:
        parts = line.strip().split(',')
        if len(parts) >= 3:
            try:
                mem_values.append(int(parts[1].strip()))
                util_values.append(int(parts[2].strip()))
            except ValueError:
                pass
gpus_loaded = sum(1 for m in mem_values if m > 1000)
gpus_active = sum(1 for u in util_values if u > 0)
total += 1
if check("All 4 GPUs have model loaded", gpus_loaded >= 4, f"{gpus_loaded} GPUs with >1GB"):
    passed += 1
total += 1
if check("At least 1 GPU active (GPTQ compute)", gpus_active >= 1, f"{gpus_active} GPUs active"):
    passed += 1

print()
print("=" * 70)
print(f"RESULT: {passed}/{total} PASS")
print("=" * 70)

sys.exit(0 if passed == total else 1)