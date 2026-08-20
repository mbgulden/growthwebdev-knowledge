#!/usr/bin/env python3
"""Probe an OpenAI-compatible local LLM server for reasoning-effort support.

Usage:
    python3 probe_reasoning_effort.py <base_url> [model_name] [--levels low medium high]

- base_url: e.g. http://192.168.1.230:31002/v1 (or without /v1 — it is appended)
- model_name: optional; defaults to the first model from GET /models
- --levels: which effort levels to test (default: low medium high)

Prints, per level, wall time and thinking-token proxy (reasoning_content
char count, falling back to completion_tokens). The no-field run reveals the
SERVER DEFAULT effort — always read that row first.

Exit codes: 0 = ran (even if some levels errored), 2 = server unreachable.
Stdlib only.
"""
import json
import sys
import time
import urllib.error
import urllib.request

HARD_PROMPT = (
    "A Python function is supposed to dedupe a list of dicts by 'id' while "
    "keeping first occurrence, preserving order, and not mutating the input. "
    "Current version:\n"
    "def dedupe(items):\n"
    "    seen = {}\n"
    "    for i in items:\n"
    "        if i['id'] not in seen:\n"
    "            seen[i['id']] = i\n"
    "    return list(seen.values())\n"
    "Bugs reported: (a) values shared with original list cross-mutate, "
    "(b) crashes when 'id' is missing. Identify the bugs, explain why, and "
    "write the corrected function with a docstring."
)


def post(base: str, model: str, body_extra: dict, timeout: int = 300) -> dict:
    url = base.rstrip("/") + "/chat/completions"
    body = {
        "model": model,
        "messages": [{"role": "user", "content": HARD_PROMPT}],
        "max_tokens": 2500,
        "stream": False,
    }
    body.update(body_extra)
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.load(r)
    return {"wall": time.time() - t0, "data": d}


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--levels"]
    levels = []
    if "--levels" in sys.argv:
        i = sys.argv.index("--levels")
        levels = sys.argv[i + 1 : i + 3]
        for j in reversed(range(i, len(sys.argv))):
            if sys.argv[j] in levels:
                del sys.argv[j]
    if not levels:
        levels = ["low", "medium", "high"]

    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    base = sys.argv[1]
    if not base.endswith("/v1"):
        base = base.rstrip("/") + "/v1"
    model = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        with urllib.request.urlopen(base + "/models", timeout=30) as r:
            models = json.load(r)
    except Exception as e:
        print(f"SERVER UNREACHABLE at {base}: {e}")
        return 2
    if model is None:
        data = models.get("data") or models.get("models") or []
        if not data:
            print("No models listed by server.")
            return 2
        model = (data[0].get("id") or data[0].get("name"))
    print(f"Probing model '{model}' at {base}")
    print(f"{'level':<14} {'wall(s)':>8} {'think_chars':>12} {'completion_tokens':>18}")

    runs = [(None, {})] + [(lvl, {"reasoning_effort": lvl}) for lvl in levels]
    for label, extra in runs:
        try:
            res = post(base, model, extra)
            msg = res["data"]["choices"][0]["message"]
            rc = msg.get("reasoning_content") or ""
            ct = res["data"].get("usage", {}).get("completion_tokens", "?")
            print(f"{(label or 'DEFAULT(<none>)'):<14} {res['wall']:>8.1f} {len(rc):>12} {ct:>18}")
        except Exception as e:
            err = str(e)
            if isinstance(e, urllib.error.HTTPError):
                err = f"HTTP {e.code}: {e.read()[:200]!r}"
            print(f"{(label or 'DEFAULT(<none>)'):<14}  ERROR: {err}")
    print("\nNote: think_chars is a proxy (len of reasoning_content). "
          "Compare rows with the SAME prompt to judge whether the level is honored.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
