# HuggingFace research patterns — rate-limit false positives and the `-L` workaround

Patterns that recur when pulling model files (`GGUF`, `safetensors`, etc.) from HuggingFace during GPU cluster operations. The HF API returns misleading headers that look like rate-limit blocks but are actually normal redirects that need `-L` to follow.

## The misleading 401 / 307 on `HEAD` requests

When you test reachability of a HuggingFace model repo with `curl -I` (HEAD), you'll see:

```
HTTP/2 401
ratelimit: "resolvers";r=2999;t=300
ratelimit-policy: "fixed window";"resolvers";q=3000;w=300
```

This **looks** like a rate-limit block. It is not. The 401 is the response to the HEAD on a `resolve/main/<file>` URL — HF returns 401 on HEAD for the `resolve` endpoint because the bucket resolver doesn't support HEAD. The `ratelimit` headers are also misleading: the `r=2999` and `t=300` are the *current state* of the rate limit window, not a rejection of this request.

**Actual GET works fine with `-L`:**

```bash
# This returns 401 (HEAD fails on resolve endpoint)
curl -s -m 10 -I 'https://huggingface.co/Qwen/Qwen3.8-27B/resolve/main/config.json' | grep HTTP

# This returns 200 (GET follows redirects to the actual file)
curl -s -L -m 10 -o /dev/null -w 'HTTP=%{http_code}\n' \
  'https://huggingface.co/Qwen/Qwen3.8-27B/resolve/main/config.json'

# For multiple files, ALWAYS use -L to follow the CDN redirect
curl -s -L -o /models/qwen3.8-27b-q4/Qwen3.8-27B-Q4_K_M.gguf \
  'https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/resolve/main/Qwen3.8-27B-Q4_K_M.gguf'
```

## The `model.safetensors.index.json` is the canonical entry point

For multi-shard safetensors repos (which is almost all modern models), the canonical way to enumerate the files is:

```bash
# Get the index — this gives you the per-file shards
curl -s -L -m 15 'https://huggingface.co/Qwen/Qwen3.8-27B/resolve/main/model.safetensors.index.json' \
  | python3 -c "import json, sys; d = json.load(sys.stdin); print(d['metadata']['total_size']); print('\n'.join(sorted(set(d['weight_map'].values()))))"
```

Output:
```
55562855904
model-00001-of-00018.safetensors
model-00002-of-00018.safetensors
...
model-00018-of-00018.safetensors
```

Then download each shard individually. The `weight_map` JSON field has the full mapping of tensor → shard file.

## The repo-existence check (clean way)

When verifying a HF repo exists before doing real work, **don't trust** HEAD or the unauthenticated API. Use a GET on the README — if 200, the repo is public and accessible:

```bash
# Does the repo exist?
curl -s -L -m 10 -o /dev/null -w "%{http_code}\n" \
  "https://huggingface.co/<repo>"

# Is the README accessible?
curl -s -L -m 10 -o /dev/null -w "%{http_code}\n" \
  "https://huggingface.co/<repo>/resolve/main/README.md"

# Is the model actually downloadable (token-gated vs public)?
curl -s -L -m 10 -o /dev/null -w "%{http_code}\n" \
  "https://huggingface.co/<repo>/resolve/main/config.json"
```

A 200 on the first + 200 on the second + 200 on the third = repo is public, accessible, and has a config file (i.e. it loads). A 401 on the third = token-gated, even if the README is public.

## The "auth required" misdirection

The HF API endpoint (`/api/models/Qwen/Qwen3.8-27B`) returns `{"error": "Invalid username or password."}` for any unauthenticated request, even for public models. This is **not** the same as the file resolver. To test repo existence, use the file URLs above, not the API.

## The `-L` is mandatory for all HF downloads

The CDN path for HF files is:
```
https://huggingface.co/<repo>/resolve/main/<file>
  → 302 redirect to
https://us.aws.cdn.hf.co/xet-bridge-us/<hash>...
```

Without `-L`, the 302 is returned as the final response and you get 0 bytes. Always include `-L` for any HF download.

## The HEAD-vs-GET pattern for verification scripts

When writing verifiers that check whether a file exists on HF, use this pattern:

```python
import subprocess

def hf_file_exists(repo, file):
    """Returns True if the file exists and is downloadable."""
    url = f"https://huggingface.co/{repo}/resolve/main/{file}"
    # HEAD doesn't work on resolve endpoints. Use GET with -L and check size.
    r = subprocess.run(
        ["curl", "-s", "-L", "-m", "10", "-o", "/dev/null", "-w", "%{http_code}|%{size_download}", url],
        capture_output=True, text=True, timeout=15
    )
    code, size = r.stdout.strip().split("|")
    return code == "200" and int(size) > 100
```

The `size_download` check is critical — the 200 response with size 0 is a real failure mode (HF's redirect requires `-L` to actually fetch the file).

## When to give up and use a different source

If HF download is repeatedly failing (not just 401-on-HEAD), check:

1. **Disk space** — `df -h` on the target host. HF safetensors for 27B-class models are 15-55 GB.
2. **Network** — `curl -s -L -m 10 -o /dev/null -w "%{http_code}|%{time_total}\n" https://huggingface.co/Qwen/Qwen3.8-27B/resolve/main/config.json`. If `time_total > 5s`, the connection is slow but working.
3. **Mirror** — `hf-mirror.com` is a Chinese HF mirror; routes requests to actual HF. Useful when HF directly is rate-limited from your IP.
4. **Local cache** — `~/.cache/huggingface/hub/` has prior downloads if the same model was pulled before. `huggingface-cli download --local-dir` reuses the cache when the same SHA is requested.

## The "phantom 401" cautionary tale

The 2026-08-15 vLLM research turn wasted ~30 minutes chasing a "rate-limit block" that wasn't there. The actual sequence:

1. `curl -I https://huggingface.co/Qwen/Qwen3.8-27B/resolve/main/config.json` → 401 with rate-limit headers
2. Tried multiple variations of the URL, all 401
3. Tried the mirror, got 308 redirect (also explained by the GET path)
4. Finally just ran `curl -L -m 10 -o /tmp/config.json https://huggingface.co/Qwen/Qwen3.8-27B/resolve/main/config.json` → 200, 4312 bytes, downloaded in 0.14 seconds
5. By the time we found this, the model files had been downloadable all along

The lesson: HF's HEAD behavior is not a download-readiness signal. Always try the actual GET first before chasing a phantom rate-limit story.

## The HF mirror (`hf-mirror.com`) — useful but partial

```bash
# Check it works
curl -s -L -m 10 -o /dev/null -w "%{http_code}\n" "https://hf-mirror.com"
# → 200

# Try a model through it
curl -s -L -m 10 -o /tmp/test.json -w "%{http_code}|%{size_download}\n" \
  "https://hf-mirror.com/Qwen/Qwen3.8-27B/resolve/main/config.json"
# → 302 → 200 (the -L follows the redirect)
```

The mirror just routes to actual HF. It does NOT bypass rate limits. It IS useful when:
- HF is blocked by your environment's firewall
- You're in a Geo where HF is slow
- You want a fallback URL for a script that runs from multiple regions

For the rate-limit case specifically, the mirror gives the same 401 on HEAD with the same rate-limit headers — the bucket resolver is the same.

## The Tailscale-vs-LAN IP gotcha (related but separate)

When downloading from HF inside a VM that has Tailscale installed and `tailscale` is configured to be the preferred egress, HF downloads from the VM's `--hostname` IP may count against the Tailscale IP's rate limit instead of the LAN IP's. Use `curl --interface eth0` (or whatever the LAN interface is) to force the LAN IP egress for HF downloads.

## The persistent blocker pattern

When the user reports "I can't download X from HF," the diagnostic sequence is:

1. `curl -s -L -m 10 -o /dev/null -w "%{http_code}|%{size_download}\n" https://huggingface.co/<repo>/resolve/main/config.json` — does HEAD work as GET?
2. If size_download > 100, the file IS reachable. The "failure" is downstream.
3. Check disk space (target host where the file is being saved).
4. Check network path (LAN vs Tailscale vs VPN).
5. Check for HF token (some repos are gated).
6. If the model itself is the size of the repo, consider streaming download with `wget -c` (resume on interrupt).

Don't chase the "rate limit" story until the basic GET has been confirmed to work.
