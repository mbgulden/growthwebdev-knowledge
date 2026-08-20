#!/usr/bin/env python3
"""Compare two benchmark runs (before/after) and emit a shareable table.

Usage: python3 compare.py before-llama-cpp after-vllm
Reads <label>.json from CWD (canonical: work/benchmarks/) or from this script's dir,
writes comparison.md next to the JSON files.
Safe to run when the 'after' file doesn't exist yet (prints a reminder).
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
METRICS = [("avg_ttft_s", "TTFT (s)"), ("avg_wall_s", "Wall (s)"),
           ("avg_total_tok_s", "Total tok/s"),
           ("avg_think_chars", "Think (chars)")]
LOWER_IS_BETTER = {"avg_ttft_s": True, "avg_wall_s": True, "avg_total_tok_s": False,
                   "avg_think_chars": False}


def load(label):
    for d in (os.getcwd(), HERE):
        p = os.path.join(d, f"{label}.json")
        if os.path.exists(p):
            with open(p) as f:
                return json.load(f), p
    return None, None


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    before, bp = load(sys.argv[1])
    after, ap = load(sys.argv[2])
    if not before or not after:
        missing = [l for l, d in (("before", before), ("after", after)) if not d]
        print(f"Missing: {', '.join(missing)}. Re-run: python3 bench_qwen.py --label <label> --stack <stack>")
        sys.exit(1)

    outdir = os.path.dirname(bp)
    lines = ["# Qwen3.8-27B local inference — before/after comparison",
             "",
             f"| | before ({before['label']}, {before['run_at_utc']} UTC) | after ({after['label']}, {after['run_at_utc']} UTC) |",
             "---|---|---",
             f"Stack | {before.get('stack', '?')} | {after.get('stack', '?')}",
             "",
             "## Per-endpoint averages",
             ""]
    for name in before["endpoints"]:
        if name not in after["endpoints"]:
            continue
        lines.append(f"### {name}")
        lines.append("")
        for case in ("chat", "hard"):
            b, a = before["endpoints"][name].get(case), after["endpoints"][name].get(case)
            if not b or not a:
                continue
            lines.append(f"**{case}**")
            lines.append("")
            lines.append("| metric | before | after | delta | verdict |")
            lines.append("|---|---|---|---|---|")
            for key, label in METRICS:
                bv, av = b.get(key), a.get(key)
                if bv is None or av is None:
                    continue
                diff = round(av - bv, 2)
                if isinstance(bv, float):
                    pct = f" ({diff/bv*100:+.0f}%)" if bv else ""
                else:
                    pct = f" ({diff:+.0f})"
                better = LOWER_IS_BETTER.get(key)
                verdict = ""
                if better is not None:
                    verdict = "✅ faster/less" if (diff < 0) == better else "❌ slower/more"
                lines.append(f"| {label} | {bv} | {av} | {diff:+}{pct} | {verdict} |")
            lines.append("")
    lines += ["## Caveats",
              "- Same prompts, same harness, same endpoints; different serving stack.",
              "- Hard-case thinking length varies run-to-run (temp 1.0); compare tok/s and wall trends, not single think-char counts.",
              "- Vision (mmproj) support must be re-verified separately — this benchmark is text-only."]
    path = os.path.join(outdir, "comparison.md")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"SAVED -> {path}")
    print("\n".join(lines[:12]))


if __name__ == "__main__":
    main()
