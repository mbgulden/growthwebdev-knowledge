#!/usr/bin/env python3
"""Targeted OKF Markdown verifier.

Usage:
    python3 verify_okf_markdown.py FILE [FILE ...] --require "phrase" --require "another phrase"

Checks:
- files exist and are non-empty
- frontmatter delimiter pair exists when file starts with YAML frontmatter
- relative Markdown links to .md files resolve
- required phrases are present across the combined file contents

This is ad-hoc doc verification, not a replacement for a canonical project suite.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", help="Markdown files to verify")
    parser.add_argument("--require", action="append", default=[], help="Phrase required somewhere in the combined content")
    args = parser.parse_args()

    errors: list[str] = []
    combined: list[str] = []

    for raw in args.files:
        path = Path(raw).expanduser().resolve()
        if not path.exists():
            errors.append(f"missing file: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        combined.append(text)
        if not text.strip():
            errors.append(f"empty file: {path}")
        if text.startswith("---\n") and text.splitlines().count("---") < 2:
            errors.append(f"frontmatter closer missing: {path}")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+\.md)\)", text):
            if target.startswith(("http://", "https://", "file://", "/")):
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                errors.append(f"broken relative link in {path}: {target} -> {resolved}")

    all_text = "\n".join(combined)
    for phrase in args.require:
        if phrase not in all_text:
            errors.append(f"missing required phrase: {phrase}")

    if errors:
        print("AD-HOC VERIFY FAILED")
        for err in errors:
            print(f"- {err}")
        return 1

    print("AD-HOC VERIFY PASSED")
    print(f"checked_files={len(args.files)}")
    print("validated: non-empty files, frontmatter delimiters, relative markdown links, required phrases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
