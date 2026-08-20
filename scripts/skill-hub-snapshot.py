#!/usr/bin/env python3
"""OKF Skill Hub Snapshot Generator (Phase A).

Imports the fleet's skill stores into okf/skills/ as a versioned,
1:1 mirror, and generates index.json (machine) + index.md (human).

Sources:
  hermes/  <- ~/.hermes/profiles/*/skills/          (per-profile subdirs)
  agy/     <- ~/.antigravity/skills/                (per-category subdirs)
  prismatic/<store>/ <- prismatic-engine/{SKILLS, .agents/skills, portable-skills, prismatic/skills}

Guarantees:
  - Idempotent: re-run wipes generated trees (guarded by marker file) and re-imports.
  - 1:1 mirror: no transforms; per-profile dirs preserve divergence for later reconciliation.
  - Drift detection: same skill name with differing SKILL.md hashes -> flagged in index.

Exit 0 = success; index.json contains full sha256 manifest.
"""
import hashlib
import json
import os
import re
import shutil
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

HUB = Path("/home/ubuntu/work/growthwebdev-knowledge")
DEST = HUB / "okf" / "skills"
MARKER = ".generated-by-skill-hub-snapshot"
SKIP_DIRS = {".archive", ".curator_backups", ".hub", "__pycache__", ".git", "node_modules"}
SKIP_FILES = {".usage.json"}  # runtime usage telemetry — churns on every skill use, not skill content
HERMES_PROFILES = Path("/home/ubuntu/.hermes/profiles")
AGY = Path("/home/ubuntu/.antigravity/skills")
ENGINE = Path("/home/ubuntu/work/prismatic-engine")


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def skill_name(skill_md: Path) -> str:
    """Prefer frontmatter name:, fall back to dir name."""
    try:
        text = skill_md.read_text(errors="replace")
        m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        if m:
            for line in m.group(1).splitlines():
                mm = re.match(r"^name:\s*(.+)", line.strip())
                if mm:
                    return mm.group(1).strip().strip('"').strip("'")
    except Exception:
        pass
    return skill_md.parent.name


def find_skill_dirs(root: Path):
    """Yield dirs containing SKILL.md, skipping hidden/skip dirs (no symlink cycles)."""
    if not root.is_dir():
        return
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        if "SKILL.md" in filenames:
            yield Path(dirpath)


def import_tree(src: Path, dst: Path) -> dict:
    """Mirror src -> dst 1:1. Returns {relpath: sha256}."""
    manifest = {}
    if src.is_dir():
        for dirpath, dirnames, filenames in os.walk(src, followlinks=False):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
            base = Path(dirpath)
            for fn in filenames:
                if fn in SKIP_FILES:
                    continue
                sp = base / fn
                dp = dst / base.relative_to(src) / fn
                dp.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(sp, dp)
                manifest[str(dp.relative_to(DEST))] = sha256_file(dp)
    return manifest


def wipe_generated(subdir: Path):
    """Remove a generated subtree, guarded by marker."""
    marker = subdir / MARKER
    if subdir.is_dir() and marker.is_file():
        shutil.rmtree(subdir)
        print(f"  wiped {subdir.relative_to(HUB)}")


def stable_timestamp() -> str:
    """Deterministic timestamp: last commit date touching real skill files.

    Excludes index.json/index.md so no-op regenerations stay byte-stable and
    the index diff only reflects actual skill changes.
    """
    import subprocess
    try:
        out = subprocess.run(
            ["git", "-C", str(HUB), "log", "-1", "--format=%cd", "--date=short",
             "--", ":(glob)okf/skills/**", ":(exclude)okf/skills/index.json", ":(exclude)okf/skills/index.md"],
            capture_output=True, text=True, timeout=30,
        )
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip() + "T00:00:00Z"
    except Exception:
        pass
    return datetime.now(timezone.utc).strftime("%Y-%m-%d") + "T00:00:00Z"


def main():
    files_copied = 0
    per_source = {}

    # --- wipe previous generated trees (guarded) ---
    wipe_generated(DEST / "agy")
    wipe_generated(DEST / "prismatic")
    # hermes: single marker at hermes/ root; wipe per-profile subdirs under it
    hermes_root = DEST / "hermes"
    if hermes_root.is_dir() and (hermes_root / MARKER).is_file():
        for prof_dir in hermes_root.iterdir():
            if prof_dir.is_dir():
                shutil.rmtree(prof_dir)
                print(f"  wiped {prof_dir.relative_to(HUB)}")
    (DEST).mkdir(parents=True, exist_ok=True)

    # --- import sources ---
    profiles = sorted(
        d.name for d in HERMES_PROFILES.iterdir()
        if d.is_dir() and (d / "skills").is_dir()
    )
    (DEST / "hermes").mkdir(parents=True, exist_ok=True)
    for prof in profiles:
        src = HERMES_PROFILES / prof / "skills"
        dst = DEST / "hermes" / prof
        per_source[f"hermes/{prof}"] = import_tree(src, dst)
    (DEST / "hermes" / MARKER).write_text("generated\n")

    per_source["agy"] = import_tree(AGY, DEST / "agy")
    (DEST / "agy" / MARKER).write_text("generated\n")

    engine_stores = {
        "engine-skills": ENGINE / "SKILLS",
        "agents-skills": ENGINE / ".agents" / "skills",
        "portable-skills": ENGINE / "portable-skills",
        "prismatic-skill-pkg": ENGINE / "prismatic" / "skills",
    }
    for label, src in engine_stores.items():
        if src.is_dir():
            per_source[f"prismatic/{label}"] = import_tree(src, DEST / "prismatic" / label)
    (DEST / "prismatic" / MARKER).write_text("generated\n")

    # --- build inventory over imported tree ---
    entries = {}  # name -> list of {source, category, path, hash}
    # recompute manifest over DEST for a single source of truth (exclude generated indexes)
    manifest = {}
    for p in DEST.rglob("*"):
        if p.is_file() and p.name not in (MARKER, "index.json", "index.md"):
            manifest[str(p.relative_to(DEST))] = sha256_file(p)
    files_copied = len(manifest)

    for p in DEST.rglob("SKILL.md"):
        rel = p.relative_to(DEST)
        parts = rel.parts  # hermes/<prof>/<cat>/<name>/SKILL.md | agy/<cat>/<name>/SKILL.md | prismatic/<store>/<name>/SKILL.md
        top = parts[0]
        if top == "hermes" and len(parts) >= 4:
            source, profile, cat = f"hermes/{parts[1]}", parts[1], parts[2]
        elif top == "prismatic" and len(parts) >= 3:
            source, profile, cat = f"prismatic/{parts[1]}", parts[1], "flat"
        elif top == "agy" and len(parts) >= 3:
            source, profile, cat = "agy", None, parts[1]
        else:
            source, profile, cat = top, None, "uncategorized"
        name = skill_name(p)
        entries.setdefault(name, []).append({
            "source": source,
            "profile_or_store": profile,
            "category": cat,
            "path": str(rel.parent),
            "hash": manifest.get(str(rel), "")[:16],
            "hash_full": manifest.get(str(rel), ""),
        })

    # --- classify ---
    catalog = []
    for name, locs in sorted(entries.items()):
        hashes = {l["hash_full"] for l in locs if l["hash_full"]}
        n = len(locs)
        if n == 1:
            status = "unique"
        elif len(hashes) == 1:
            status = f"shared-{n}-identical"
        else:
            status = f"divergent-{len(hashes)}-variants"
        catalog.append({"name": name, "status": status, "locations": locs})

    # --- index.json ---
    index = {
        "generated_at": stable_timestamp(),
        "generator": "scripts/skill-hub-snapshot.py",
        "sources": {
            "hermes_profiles": profiles,
            "agy_root": str(AGY),
            "engine_stores": list(engine_stores.keys()),
        },
        "files": len(manifest),
        "skills": len(catalog),
        "status_counts": _status_counts(catalog),
        "catalog": catalog,
        "file_manifest": manifest,
    }
    (DEST / "index.json").write_text(json.dumps(index, indent=2) + "\n")

    # --- index.md ---
    lines = [
        "# OKF Skill Hub — Catalog",
        "",
        f"_Generated {index['generated_at']} by `scripts/skill-hub-snapshot.py`. "
        f"{index['skills']} skills / {index['files']} files across {len(profiles)} Hermes profiles, AGY CLI, and the Prismatic engine._",
        "",
        "## Status counts",
        "",
    ]
    for k, v in sorted(index["status_counts"].items()):
        lines.append(f"- **{k}**: {v}")
    lines += ["", "## Legend", "",
              "- `unique` — exists in exactly one store",
              "- `shared-N-identical` — N copies, byte-identical SKILL.md (safe symlinks/mirrors)",
              "- `divergent-K-variants` — ⚠ same name, K different contents — reconciliation needed",
              ""]
    div = [c for c in catalog if c["status"].startswith("divergent")]
    if div:
        lines += ["## ⚠ Divergent skills (reconciliation backlog)", ""]
        for c in div:
            lines.append(f"### {c['name']}")
            lines.append("")
            for l in c["locations"]:
                src = l["source"] + (f"/{l['profile_or_store']}" if l["profile_or_store"] else "")
                lines.append(f"- `{l['path']}` (sha256 {l['hash']})")
            lines.append("")
    lines += ["## Full catalog", "",
              "| Skill | Status | Category | Location(s) | sha256(8) |",
              "|---|---|---|---|---|"]
    for c in catalog:
        locs = "<br>".join(
            l["path"] for l in c["locations"]
        )
        cats = ", ".join(sorted({l["category"] for l in c["locations"]}))
        h = c["locations"][0]["hash"]
        lines.append(f"| {c['name']} | {c['status']} | {cats} | {locs} | {h} |")
    lines.append("")
    (DEST / "index.md").write_text("\n".join(lines))

    print(f"OK: {files_copied} files, {len(catalog)} skills, "
          f"divergent={len(div)} -> {DEST.relative_to(HUB)}/")
    return 0


def _status_counts(catalog):
    counts = defaultdict(int)
    for c in catalog:
        s = c["status"]
        key = s.split("-identical")[0].split("-variants")[0]
        if key == "divergent":
            key = "divergent"
        counts[key] += 1
    return dict(counts)


if __name__ == "__main__":
    sys.exit(main())
