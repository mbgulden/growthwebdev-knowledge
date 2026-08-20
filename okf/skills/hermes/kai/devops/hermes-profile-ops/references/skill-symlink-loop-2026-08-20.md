# Skill symlink loop in `<available_skills>` — diagnosis + fix (2026-08-20)

## Symptom
Kai's injected `<available_skills>` block listed `projector-aware-communication-discipline`
at ~14 nested depth levels (`agent-operations/x/x/x/...`). The skill only exists ONCE on disk.
Every session of kai + any profile symlinking orchestrator's tree paid ~500 extra tokens/turn.

## Root cause
```
orchestrator/skills/agent-operations/projector-aware-communication-discipline/
  ├── SKILL.md                          (the one real copy)
  └── projector-aware-communication-discipline -> (its own parent dir)   ← CYCLE
```
A self-referential symlink created when the skill was adopted across profiles
(`_adopt_shared_skills` pattern). The lister follows symlinks while walking,
so each descent re-entered the same directory, emitting a phantom nested entry
at each depth.

## Diagnosis (what actually worked)
1. `find <skills> -name SKILL.md | wc -l` → 28 real files.
2. Reconstructed lister payload: ~3.8K chars, ~28 entries — but the LIVE system
   prompt showed ~50 entries with 14-deep nesting. List ≠ disk → lister is
   following something.
3. `find <skills> -type l` → 12 symlinks (all into orchestrator's profile,
   legitimate cross-profile sharing). `readlink` each.
4. One link: `.../projector-aware-communication-discipline/projector-aware-communication-discipline
   -> .../agent-operations/projector-aware-communication-discipline` (its own parent).
   **That's the loop.**
5. Bounded follow-walk confirmed: 16 phantom SKILL.md copies reachable pre-fix,
   1 post-fix.

## Fix
```bash
LOOP=~/.hermes/profiles/orchestrator/skills/agent-operations/projector-aware-communication-discipline/projector-aware-communication-discipline
cp -P "$LOOP" /tmp/skill-loop-backup-2026-08-20/projector-aware.symlink   # back up
rm "$LOOP"
```
Then re-scan ALL profiles with `scripts/scan_skill_symlink_loops.py` (0 cycles),
and verify with the LIVE lister (`skills_list category=agent-operations` →
exactly 3 clean skills, no phantoms).

## False positive encountered
`orchestrator/skills/agent-operations/_adopt_shared_skills -> .../_adopt_shared_skills.py`
— a symlink to a `.py` SCRIPT. A naive path-prefix cycle check flags it
(target string contains the link path as prefix), but it has no SKILL.md and
the lister ignores it. The scanner in `scripts/` deliberately does NOT flag
this shape (exact-parent/self resolution only).

## Verification (ad-hoc, 9/9)
- lister count (159 unique canonical skills across 12 profiles) matched an
  independent `os.walk(followlinks=True)` recomputation
- zero cycles across all 12 profiles post-fix
- real SKILL.md intact (9,415 bytes)
- loop link removed

## Key numbers
- 12 profiles with skills/ dirs: active-oahu, ai-consulting, autobot, fred,
  george, google-ai-toolkit, hdengine, jules, kai, ned, next-step, orchestrator
- 159 unique canonical skills (symlinks resolved); 215 profile-skill entries
- 56 skills shared across >1 profile via symlinks
- canonical homes: orchestrator 56, ned 39, george 26, kai 22, others ≤5

## Related: OKF skills hub (planned, not yet built)
Michael wants `okf/skills/<category>/<skill>/` as a versioned (git) mirror of
all profile skills, with a daily no-agent cron (scan → diff sha256 vs
`okf/skills/index.json` → sync + PR). Design decisions pending: sync direction
(recommended: profiles → hub) and scope (recommended: all skills, owner-tagged).
