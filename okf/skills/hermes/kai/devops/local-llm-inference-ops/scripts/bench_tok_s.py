#!/usr/bin/env python3
"""Live tok/s probe for a local OpenAI-compatible endpoint (llama.cpp / vLLM).

Usage:
  python3 bench_tok_s.py [base_url] [model] [max_tokens]
  python3 bench_tok_s.py http://192.168.1.232:8080 qwen3.8-27b 2048

Defaults: Kai endpoint, 2048 tokens. Non-streaming; wall time INCLUDES prefill,
so gen_speed = completion_tokens / wall is a slightly conservative proxy.

Prints: wall time, prompt/completion tokens, think-chars, answer-chars, tok/s.
Warns loudly on the reasoning-only failure mode (content empty, all budget
spent on thinking) — never report a speed from a run that has no answer.
"""
import json
import sys
import time
import urllib.request

base = sys.argv[1] if len(sys.argv) > 1 else "http://192.168.1.232:8080"
model = sys.argv[2] if len(sys.argv) > 2 else "qwen3.8-27b"
max_tokens = int(sys.argv[3]) if len(sys.argv) > 3 else 2048

url = base.rstrip("/") + "/v1/chat/completions"
payload = {
    "model": model,
    "messages": [{"role": "user", "content":
        "Write a detailed technical guide on how to commission and troubleshoot "
        "a residential heat pump system. Cover pre-commissioning checks, "
        "refrigerant pressure verification, airflow, electrical checks, common "
        "failure modes with diagnostic steps, and seasonal differences. Use "
        "numbered sections."}],
    "max_tokens": max_tokens,
    "stream": False,
}
req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                             headers={"Content-Type": "application/json"})
t0 = time.time()
with urllib.request.urlopen(req, timeout=580) as r:
    data = json.loads(r.read())
wall = time.time() - t0
usage = data.get("usage", {})
msg = data["choices"][0]["message"]
content = msg.get("content", "") or ""
reasoning = msg.get("reasoning_content", "") or ""
out = usage.get("completion_tokens", 0)
prompt = usage.get("prompt_tokens", 0)

print(f"wall_time_s: {wall:.2f}")
print(f"prompt_tokens: {prompt}")
print(f"completion_tokens: {out}")
print(f"think_chars: {len(reasoning)}")
print(f"answer_chars: {len(content)}")
if out and wall:
    print(f"gen_speed_tok_s: {out / wall:.1f}")
if out and not content:
    print("WARNING: REASONING-ONLY RESPONSE - max_tokens budget exhausted by "
          "thinking, no answer produced. Raise max_tokens (>=2048) and re-run; "
          "do not report this run's speed.")
elif out:
    print(f"answer_tail_80: {content[-80:]!r}")
