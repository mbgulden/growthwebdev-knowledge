#!/usr/bin/env python3
"""Baseline / comparison benchmark for the Qwen3.8-27B local inference servers.

Usage:
  python3 bench_qwen.py --label before-llama-cpp --stack llama.cpp [--endpoints kai,ned]

Streams each request and reports:
  - ttft            time to first token (thinking OR content)
  - total_tok_s     all output tokens (thinking + content) / gen time — the stable metric
  - wall_s          end-to-end
  - think_chars / out_chars

Writes <label>.json + <label>.report.md next to this script (or in CWD if not writable).
Prompts and settings are FIXED across runs so before/after are comparable.

Pitfalls baked in:
  - max_tokens high enough that thinking can't starve content (6000 for hard case)
  - NO "content speed after thinking" metric (denominator ~0 -> explodes)
  - idle-probe the endpoints before running (see SKILL.md)
"""
import json, time, urllib.request, sys, os, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
ENDPOINTS = {
    "kai": ("http://192.168.1.230:31002/v1/chat/completions", "local-qwen-27b-q4-kai"),
    "ned": ("http://192.168.1.230:31003/v1/chat/completions", "local-qwen-27b-q4-ned"),
}
# Fred's :31001 is a different model (Q5) — excluded from the comparison by default.

CHAT_PROMPT = ("In one or two sentences, explain the main risk when a local tourism business "
               "depends on a single booking platform, and what a low-cost mitigation looks like.")
HARD_PROMPT = """A Python function is supposed to dedupe a list of dicts by 'id' while keeping first
occurrence, preserving original order, and not mutating the input. Current version:
def dedupe(items):
    seen = {}
    for i in items:
        if i['id'] not in seen:
            seen[i['id']] = i
    return list(seen.values())
A user reports: (a) dict values are shared with the original list and cross-mutate, (b) it crashes
when 'id' is missing on some items. Identify the bugs, explain WHY each happens, and write the
corrected function with a brief docstring. Be thorough but concise."""

# (label, prompt, max_tokens, reps)
CASES = [("chat", CHAT_PROMPT, 500, 1), ("hard", HARD_PROMPT, 6000, 2)]


def stream_once(url, model, prompt, max_tokens):
    body = {"model": model, "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens, "stream": True}
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    ttft = None
    content = ""
    think = ""
    n_content = 0
    n_think = 0
    with urllib.request.urlopen(req, timeout=600) as r:
        for raw in r:
            line = raw.decode("utf-8", "replace").strip()
            if not line.startswith("data:"):
                continue
            payload = line[5:].strip()
            if payload == "[DONE]":
                break
            try:
                d = json.loads(payload)
            except Exception:
                continue
            ch = d.get("choices") or []
            if not ch:
                continue
            delta = ch[0].get("delta", {})
            tc = delta.get("content") or ""
            tr = delta.get("reasoning_content") or ""
            if tc:
                if ttft is None:
                    ttft = time.time() - t0
                content += tc
                n_content += 1
            if tr:
                if ttft is None:
                    ttft = time.time() - t0
                think += tr
                n_think += 1
    wall = time.time() - t0
    return {
        "ttft_s": round(ttft, 2) if ttft else None,
        "think_chars": len(think),
        "out_chars": len(content),
        "total_tok_s": round((n_content + n_think) / max(wall - (ttft or 0), 0.001), 1),
        "wall_s": round(wall, 2),
    }


def bench(name):
    url, model = ENDPOINTS[name]
    print(f"\n=== {name} ({model}) ===", flush=True)
    print("  warmup...", flush=True)
    try:
        stream_once(url, model, HARD_PROMPT, 3000)
    except Exception as e:
        print(f"  warmup failed: {e}", flush=True)
    out = {}
    for label, prompt, mt, reps in CASES:
        runs = []
        for i in range(reps):
            try:
                r = stream_once(url, model, prompt, mt)
                runs.append(r)
                print(f"  {label}#{i+1}: ttft={r['ttft_s']}s wall={r['wall_s']}s "
                      f"total={r['total_tok_s']} tok/s "
                      f"think={r['think_chars']}c out={r['out_chars']}c", flush=True)
            except Exception as e:
                print(f"  {label}#{i+1}: ERROR {e}", flush=True)
        if runs:
            out[label] = {
                "runs": runs,
                "avg_ttft_s": round(sum(x['ttft_s'] or 0 for x in runs) / len(runs), 2),
                "avg_wall_s": round(sum(x['wall_s'] for x in runs) / len(runs), 2),
                "avg_total_tok_s": round(sum(x['total_tok_s'] or 0 for x in runs) / len(runs), 1),
                "avg_think_chars": round(sum(x['think_chars'] for x in runs) / len(runs), 0),
            }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True, help="e.g. before-llama-cpp / after-vllm")
    ap.add_argument("--stack", default="unknown", help="serving stack name, e.g. llama.cpp / vLLM")
    ap.add_argument("--endpoints", default="kai,ned", help="comma list: kai,ned")
    args = ap.parse_args()

    names = [n.strip() for n in args.endpoints.split(",") if n.strip() in ENDPOINTS]
    results = {
        "label": args.label,
        "stack": args.stack,
        "run_at_utc": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
        "host": "k3s-node-230 (192.168.1.230), 4x RTX 3090 24GB",
        "model": "Qwen3.8-27B Q4_K_M (+mmproj vision)",
        "endpoints": {},
    }
    for name in names:
        results["endpoints"][name] = bench(name)

    # Write to CWD (canonical: work/benchmarks/); fall back to script dir if not writable.
    outdir = os.getcwd() if os.access(os.getcwd(), os.W_OK) else HERE
    jpath = os.path.join(outdir, f"{args.label}.json")
    with open(jpath, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSAVED JSON -> {jpath}")

    # Markdown report
    lines = [f"# Qwen3.8-27B local inference benchmark — {args.label}",
             "",
             f"- **Stack:** {args.stack}",
             f"- **Run at:** {results['run_at_utc']} UTC",
             f"- **Host:** {results['host']}", f"- **Model:** {results['model']}",
             "- **Method:** streaming chat completions, 1 warmup + fixed cases; "
             "total tok/s = all output tokens (thinking + answer) / gen time",
             "- **Caveats:** thinking length varies run-to-run (temperature 1.0); tok/s is the stable metric. "
             "TTFT on first case includes prompt-prefill + KV cache warm.",
             "", "| endpoint | case | ttft (s) | wall (s) | total tok/s | think (chars) |",
             "|---|---|---|---|---|---|"]
    for name, d in results["endpoints"].items():
        for label in ("chat", "hard"):
            if label in d:
                s = d[label]
                lines.append(f"| {name} | {label} | {s['avg_ttft_s']} | {s['avg_wall_s']} "
                             f"| {s['avg_total_tok_s']} | {int(s['avg_think_chars'])} |")
    mpath = os.path.join(outdir, f"{args.label}.report.md")
    with open(mpath, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"SAVED REPORT -> {mpath}")


if __name__ == "__main__":
    main()
