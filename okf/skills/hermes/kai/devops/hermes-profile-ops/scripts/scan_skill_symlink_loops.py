#!/usr/bin/env python3
"""Scan every Hermes profile's skills/ tree for self-referential (cyclic) symlinks.

A cyclic symlink makes the skill lister walk the same directory forever and
inject phantom nested <available_skills> entries into the system prompt every
turn (observed: one self-link added ~14 phantom copies = ~500 tokens/turn).

Exit code 0 = no cycles. Exit code 1 = at least one cycle found (offenders printed).

Usage: python3 scan_skill_symlink_loops.py [profiles_root]
  profiles_root defaults to ~/.hermes/profiles
"""
import os
import sys
from pathlib import Path

def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / ".hermes" / "profiles"
    if not root.is_dir():
        print(f"not a dir: {root}", file=sys.stderr)
        return 2

    offenders = []
    for prof in sorted(root.iterdir()):
        skills = prof / "skills"
        if not (prof.is_dir() and skills.is_dir()):
            continue
        for dirpath, dirnames, _files in os.walk(skills):
            for name in list(dirnames):
                link = Path(dirpath) / name
                if not link.is_symlink():
                    continue
                # resolve; an unresolvable (dangling) link is reported separately
                try:
                    resolved = link.resolve()
                except OSError:
                    continue
                # A cycle: the resolved target is the link itself, its parent,
                # or an ancestor of the link's own path.
                if resolved == link or resolved == link.parent:
                    offenders.append((prof.name, link))
                    continue
                link_ancestor = str(link.parent)
                if str(resolved) == link_ancestor or link_ancestor.startswith(str(resolved) + os.sep):
                    # resolved is an ancestor of the link -> walking down re-enters
                    offenders.append((prof.name, link))
                # NOTE: do NOT flag a link that merely RESOLVES to a path whose
                # string starts with the link's own string (e.g. foo -> foo.py).
                # That is a .py script, not a skill dir; the lister ignores it.

    if offenders:
        print(f"FOUND {len(offenders)} cyclic symlink(s):")
        for prof, link in offenders:
            print(f"  [{prof}] {link} -> {os.readlink(link)}")
        return 1
    print("no cyclic symlinks in any profile skills/ tree")
    return 0

if __name__ == "__main__":
    sys.exit(main())
