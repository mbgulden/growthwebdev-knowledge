# Hollow /tmp scaffold audit (2026-09-05)

Context: four `/tmp` dirs parked since the 08-23→08-26 PR batches (all merged by
then). Question: what is actually in them, and does deleting lose anything?

## Verified findings

| Dir | `du -sh` | Real files (excl. node_modules/__pycache__) | node_modules regular files | Symlinks | Verdict |
|---|---|---|---|---|---|
| `pr-tenant-router` | 17M | 0 | 0 (63 entries, all npm `.bin/` symlinks) | 63, all npm `.bin` | Hollow scaffold — safe to delete, zero loss |
| `gro-4823-claim-guard` | 17M | 0 | 0 (same npm `.bin` pattern) | npm `.bin` | Hollow scaffold — safe to delete, zero loss |
| `g2g6-landing` | 4K | 0 | n/a | 0 | Empty directory |
| `deployed-verify` | 12K | 0 | n/a | 1 **dangling** (`scripts → hd-platform-staging/scripts`) + empty `__pycache__` | Dangling symlink + pycache |

Nothing unique to lose; ~34M reclaimable. Both 17M dirs were project skeletons
(`api/`, `src/`, `scripts/`, `docs/` — all 0-byte) plus a `node_modules` whose only
"files" were `.bin/` symlinks; the 17M was npm metadata/empty dirs, not content.

## Audit recipe (reusable)

1. `du -sb` per top-level entry (true bytes; `du -sh` display inflates empty trees).
2. `find <dir> -type f -not -path '*/node_modules/*' -not -path '*/__pycache__/*'`
   → the real content. **This is the only number that answers "what do we lose".**
3. `find <dir> -type f -path '*/node_modules/*' | wc -l` → package residue; 0 means the
   "size" was scaffolding noise.
4. `find <dir> -type l` + `readlink` on each; `test -e <link>` → dangling check
   (a dangling symlink proves the target checkout moved — the dir is stale).
5. Only if step 2 returns files: sample-read them before classifying.

## Lessons

- Size-based reporting ("17M — keep?") is the wrong answer for scaffolds. The
  deletion-safety question is "are there regular files outside generated caches?",
  not "how big is it?".
- `find | wc -l` counts must be machine-verified per the handoff/count discipline:
  a `du -sh`-derived number is a claim, a `find -type f | wc -l` is a fact.
- This is the /tmp twin of the janitor's core rule: encode "safe to remove" as a
  mechanical check, never an inference from appearance (size, age, name).
