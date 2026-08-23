#!/usr/bin/env python3
"""Redact a Hermes config.yaml (or any YAML-ish file) into a shareable file.

Two passes + optional final scan (see skill: operations/redacted-profile-config-export):
  1. Key-name pass  — secret-looking key with a non-empty literal (not env-ref) -> [REDACTED]
  2. Value-shape pass — token-shaped values (sk-, xox, ghp_, xai-, AIza, eyJ, telegram-bot-token) -> [REDACTED]
  3. --scan FILE    — scan an arbitrary finished document for secret-looking strings;
                      exits non-zero if any hit. Always run this on the final .md before delivery.

Usage:
  python3 redact_config.py <config.yaml> <out.yaml>
  python3 redact_config.py --scan <finished.md>
"""
import re
import sys

SECRET_KEY = re.compile(r"(?i)(api[_-]?key|token|secret|password|passwd|credential|authorization|bearer)")
ENV_REF = re.compile(r"^\s*(\$\{|\$[A-Za-z_]|env:)")
SECRET_SHAPE = re.compile(
    r"(?i)^\s*(sk-[A-Za-z0-9]{16,}|xox[baprs]-[A-Za-z0-9-]{10,}|ghp_[A-Za-z0-9]{16,}"
    r"|gho_[A-Za-z0-9]{16,}|xai-[A-Za-z0-9]{16,}|AIza[0-9A-Za-z_-]{20,}|eyJ[A-Za-z0-9_-]{30,}"
    r"|[0-9]{8,10}:[A-Za-z0-9_-]{25,})"
)
KEY_LINE = re.compile(r"^(\s*[\w.-]*?)(:)(\s*)(.*)$")
BENIGN = {"none", "null", "~", "false", "true", ""}


def redact_line(line: str) -> tuple[str, bool]:
    m = KEY_LINE.match(line)
    if not m:
        return line, False
    key, colon, space, val = m.groups()
    v = val.split("#", 1)[0].strip()
    if not v:
        return line, False
    if SECRET_KEY.search(key) and not ENV_REF.match(v) and v.strip("\"'").lower() not in BENIGN and len(v) > 4:
        return f"{key}{colon}{space}[REDACTED]", True
    if SECRET_SHAPE.match(v) and len(v) > 16:
        return f"{key}{colon}{space}[REDACTED]", True
    return line, False


def main() -> int:
    args = sys.argv[1:]
    if args and args[0] == "--scan":
        path = args[1] if len(args) > 1 else sys.stdin
        data = open(path).read() if isinstance(path, str) else sys.stdin.read()
        hits = [l for l in data.splitlines() if SECRET_SHAPE.match(l.split(":", 1)[-1] if ":" in l else l)]
        # also catch bare token-shaped tokens anywhere (multi-word lines)
        hits2 = [l for l in data.splitlines() if re.search(r"(?<![A-Za-z0-9])(sk-[A-Za-z0-9]{20,}|xox[bap]-[A-Za-z0-9-]{15,}|ghp_[A-Za-z0-9]{20,}|eyJ[A-Za-z0-9_-]{40,})", l)]
        allhits = sorted(set(hits + hits2))
        print(f"secret-looking tokens found: {len(allhits)}")
        for h in allhits[:5]:
            print("  ?", h[:120])
        return 1 if allhits else 0
    if len(args) != 2:
        print(__doc__)
        return 2
    src, out = args
    redacted, keys = 0, []
    out_lines = []
    for line in open(src):
        line = line.rstrip("\n")
        new, hit = redact_line(line)
        if hit:
            redacted += 1
            keys.append(KEY_LINE.match(line).group(1).strip())
        out_lines.append(new)
    open(out, "w").write("\n".join(out_lines) + "\n")
    print(f"lines={len(out_lines)} redacted={redacted}")
    print("redacted keys:", sorted(set(keys)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
