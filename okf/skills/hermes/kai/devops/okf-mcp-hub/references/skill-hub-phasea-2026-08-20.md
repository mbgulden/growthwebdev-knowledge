# Skill hub Phase A — session record (2026-08-20, PR #33)

## What shipped
`okf/skills/` = first git-versioned registry of **every skill** across the fleet.
PR #33 (`content/kai-skill-hub-snapshot` @ 969ec6a, MERGEABLE/CLEAN, 2,463 files):

| Source | Hub location | SKILL.md |
|---|---|---|
| Hermes (12 profiles) | `okf/skills/hermes/<profile>/<cat>/<skill>/` | 215 |
| AGY CLI (`~/.antigravity/skills/`, was NOT a git repo) | `okf/skills/agy/<cat>/<skill>/` | 24 |
| Engine: `SKILLS/`, `.agents/skills/`, `portable-skills/`, `prismatic/skills/` | `okf/skills/prismatic/<store>/<skill>/` | 44 |

176 unique names: 104 unique, 60 shared-identical, **12 divergent** (same name,
different content across profiles — e.g. `agy-autopilot-governance` 3 variants,
`agent-onboarding-workflow` george≠kai). Divergent list = reconciliation backlog
in the ⚠ section of `okf/skills/index.md`.

## Generator: `scripts/skill-hub-snapshot.py` (in hub repo)
- 1:1 mirror, no transforms. Marker-guarded: wipes only trees containing
  `.generated-by-skill-hub-snapshot`, re-imports. Idempotent — run twice, tree
  hash identical (excludes index files from the manifest; including them broke
  idempotence because they carry a timestamp).
- `okf/skills/index.md`: status counts + divergent backlog + full table (path + sha256(8)).
- `okf/skills/index.json`: per-file sha256 manifest, per-skill status, `generated_at`.
- Status vocabulary: `unique` / `shared-N-identical` / `divergent-K-variants`.
- Re-run after ANY skill change; the index diff IS the change report.

## Design decisions (recorded in `okf/decisions/2026-08-20-okf-skill-hub-phase-a.md`)
- **Sync direction: profiles → hub** (hub = registry/mirror; flip later = one flag).
- **Per-profile folders are mandatory** — they preserve divergence as-is so
  reconciliation is deliberate, never a silent merge.
- **Engine distribution (Phase B)**: extend the EXISTING bootstrapper
  (`prismatic skills sync`, GRO-4362/4363 — `bootstrapper.py` + 4-tier resolution
  `PRISMATIC_SKILLS_PATH` → repo `.agents/skills/` → package → `~/.prismatic/skills/`)
  with `--source <okf-checkout>` + hermes/agy target backends.
  **Engine never calls the OKF MCP** — it reads a plain git checkout, keeping the
  engine portable to any computer (`git clone && prismatic skills sync --source ./okf`).
- Phase C: dashboard "sync from hub" + per-skill drift reconciliation.

## Verification (ad-hoc 12/12 PASS)
`/tmp/hermes-verify-skill-hub-phasea.py`: generator exit, idempotence (tree hash
across runs), index.json↔disk (2,444 files / 176 skills), per-source 1:1 counts,
marker guards, index sections, secrets scan (AKIA/Bearer/ghp/xox, example-tolerant —
the one hit was a documented `AKIA...EXAMPLE` template, not a live key).

## Pitfalls hit
1. **Heredoc `&` tripped the terminal backgrounding guard** — a Python
   `set & set` expression inside a `<<'EOF'` heredoc was parsed as shell
   backgrounding. Write the script to a file with `write_file`, then run it.
2. **Credential scrubber mangles heredoc Linear API calls** — `-H "Authorization:
   Bearer $KEY"` style lines and long python - heredocs get eaten. Use the
   portable `linear_api.py` (prismatic-pwp-ubersuggest-auth portable-skills) or a
   script file.
3. **Inventory count discrepancy**: earlier "159 unique skills" was the
   symlink-resolved count; the generator's 283 SKILL.md files / 176 names counts
   physical copies (divergent variants count once per name). Both are right;
   name the basis when reporting.
