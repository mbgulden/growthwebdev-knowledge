#!/usr/bin/env python3
"""
Hermes Projector-Aware Communication Discipline — reply-shape verifier.

Heuristic checker that flags anti-patterns in agent replies:
  - Replies longer than N lines when the user asked a status question
  - Replies ending with "Want me to ... ?" / "Should I ... ?" / "Choose A or B"
    without an explicit user ask
  - Replies that contain a 1-row markdown table
  - Replies that end with a numbered list of 3+ options where the first option
    is also the obvious next step

Best-effort. The verifier is a surface for re-reading candidates, not a
policy enforcer. False positives are possible and should be reviewed by
human judgment, not blindly acted on.

Usage:
  python3 verify_reply_shape.py --text "..." [--save-to /path/of/reply.md]
  python3 verify_reply_shape.py --from-stdin [--save-to /path/of/reply.md]
  cat reply.md | python3 verify_reply_shape.py --from-stdin

When --save-to is used, the reply is appended to that file's bottom in a
verifiable format and a machine-legible report is emitted to stdout.

Exit codes:
  0 = no anti-patterns detected (CLEAN)
  1 = one or more anti-patterns detected (NEEDS REVIEW)
  2 = usage error
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any


ANTIPATTERNS_USER_ASK = [
    "want me to",
    "shall i ",
    "should i ",
    "do you want me to",
    "let me know if you",
    "here are your options",
    "which would you prefer",
    "what would you like to do",
    "what do you want me to do",
]

CHOICE_PROMPTS = [
    r"choose a or b",
    r"choose between",
    r"pick a or b",
    r"your call",
    r"would you like to pick",
    r"which option",
]


def _ends_with_ask(text: str) -> list[str]:
    """Returns list of anti-pattern matches found in the last 5 lines."""
    lines = [l for l in text.rstrip().split("\n") if l.strip()]
    tail = "\n".join(lines[-5:])
    findings = []
    for ap in ANTIPATTERNS_USER_ASK:
        if ap in tail.lower():
            findings.append(f"ends-with-ask: '{ap}' in last 5 lines")
    return findings


def _has_one_row_table(text: str) -> list[str]:
    """Returns list of 'table-of-one-item' findings."""
    findings = []
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        if not lines[i].strip().startswith("|"):
            i += 1
            continue
        # Collect the contiguous table block
        block = []
        while i < len(lines) and lines[i].strip().startswith("|"):
            block.append(lines[i])
            i += 1
        # A markdown table needs at least 3 lines: header, separator, data
        if len(block) < 3:
            continue
        # Check if the header has only 1-2 columns (table of one item)
        header_cols = [c for c in block[0].split("|") if c.strip()]
        if len(header_cols) <= 2:
            findings.append(f"table-of-one-item: {len(header_cols)} cols at line {i - len(block)}")
    return findings


def _ends_with_numbered_options(text: str, threshold: int = 3) -> list[str]:
    """Returns list of 'ends-with-numbered-options' findings (>= N numbered items in last 10 lines)."""
    lines = [l for l in text.rstrip().split("\n") if l.strip()]
    last_10 = lines[-10:]
    numbered = sum(1 for l in last_10 if re.match(r"^\s*\d+[.)]\s+", l))
    if numbered >= threshold:
        return [f"ends-with-numbered-options: {numbered} numbered items in last 10 lines (threshold={threshold})"]
    return []


def _length_check(text: str, max_lines: int) -> list[str]:
    """Returns list of 'too-long' findings if reply exceeds max_lines (excluding code blocks)."""
    in_code = False
    body_lines = 0
    for line in text.split("\n"):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if not in_code and line.strip():
            body_lines += 1
    if body_lines > max_lines:
        return [f"length: {body_lines} body lines (max {max_lines})"]
    return []


def _status_question_in_input(user_text: str) -> bool:
    """Heuristic: did the user ask a status/next/where question?"""
    user_lower = user_text.lower()
    status_patterns = [
        r"\bwhat'?s next\b",
        r"\bwhere are we\b",
        r"\bwhere were we\b",
        r"\bwhat shipped\b",
        r"\bwhat'?s the status\b",
        r"\bwhat did you do\b",
        r"\bwhat'?s pending\b",
        r"\bany progress\b",
    ]
    for pat in status_patterns:
        if re.search(pat, user_lower):
            return True
    return False


def _is_genuine_tradeoff_ask(user_text: str, agent_text: str) -> bool:
    """Heuristic: did the user EXPLICITLY ask for a choice between options?"""
    user_lower = user_text.lower()
    explicit_asks = [
        r"pick (a|b|one|two|the)",
        r"choose (a|b|one|two|the|between)",
        r"which (one|do you prefer|option)",
        r"what do you think",
        r"your (call|choice|decision)",
        r"a or b",
    ]
    for pat in explicit_asks:
        if re.search(pat, user_lower):
            return True
    # Also: if the agent is using the genuine-tradeoff shape
    if any(re.search(p, agent_text.lower()) for p in CHOICE_PROMPTS):
        return True
    return False


def verify(reply_text: str, user_text: str = "") -> dict[str, Any]:
    """Run all checks on a reply. Returns a structured report."""
    findings: list[dict[str, str]] = []

    # Always-on checks
    for f in _ends_with_ask(reply_text):
        findings.append({"check": f, "severity": "high", "fix": "remove the ask; do the bounded work first or state the pick"})
    for f in _has_one_row_table(reply_text):
        findings.append({"check": f, "severity": "medium", "fix": "convert single-row table to 'Status: ... / Evidence: ...' lines"})
    for f in _ends_with_numbered_options(reply_text):
        # Only flag if the user didn't explicitly ask for choices
        if not _is_genuine_tradeoff_ask(user_text, reply_text):
            findings.append({"check": f, "severity": "medium", "fix": "pick one option; state it; do it"})
        else:
            findings.append({"check": f + " (but user explicitly asked for choices — OK)", "severity": "info", "fix": "none"})

    # Conditional checks
    if _status_question_in_input(user_text):
        for f in _length_check(reply_text, max_lines=20):
            findings.append({"check": f, "severity": "high", "fix": "filter aggressively; answer the status question; cut everything else"})

    return {
        "verdict": "CLEAN" if not findings or all(f["severity"] in ("info",) for f in findings) else "NEEDS_REVIEW",
        "findings_count": len(findings),
        "findings": findings,
        "context": {
            "user_text_provided": bool(user_text),
            "user_was_status_question": _status_question_in_input(user_text) if user_text else None,
            "user_explicitly_asked_for_choices": _is_genuine_tradeoff_ask(user_text, reply_text) if user_text else None,
        },
    }


def save_to_path(reply_text: str, path: str, verdict_report: dict[str, Any]) -> None:
    """Append the reply + its verdict to a file for later audit."""
    import datetime
    with open(path, "a") as f:
        f.write("\n\n---\n")
        f.write(f"## Verifier run at {datetime.datetime.now(datetime.timezone.utc).isoformat()}\n")
        f.write(f"verdict: {verdict_report['verdict']}\n")
        f.write(f"findings: {verdict_report['findings_count']}\n\n")
        f.write("```\n")
        f.write(reply_text)
        f.write("\n```\n")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="verify_reply_shape.py")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--text", help="The reply text to check")
    src.add_argument("--from-stdin", action="store_true", help="Read reply from stdin")
    p.add_argument("--user-text", default="", help="The user prompt that prompted the reply (for context)")
    p.add_argument("--save-to", default=None, help="Append the reply + verdict to this file (audit log)")
    args = p.parse_args(argv)

    if args.from_stdin:
        reply = sys.stdin.read()
    else:
        reply = args.text

    report = verify(reply, args.user_text)
    print(json.dumps(report, indent=2))

    if args.save_to:
        save_to_path(reply, args.save_to, report)

    return 0 if report["verdict"] == "CLEAN" else 1


if __name__ == "__main__":
    raise SystemExit(main())