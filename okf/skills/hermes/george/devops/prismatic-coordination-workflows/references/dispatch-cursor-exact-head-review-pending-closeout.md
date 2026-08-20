# Dispatch cursor exact-head review-pending closeout

Use this addendum for Prismatic dispatch-cursor/generation repair candidates when an AGY/producer process times out or is SIGTERM'd after leaving edits, and local verification appears green but independent review is still pending.

## Trigger

- Producer exits nonzero/SIGTERM/timeout after edits or a commit.
- Candidate touches only the bounded allowed paths, but no trusted result packet is available.
- George must decide whether to preserve, locally verify, relaunch, or move to independent exact-head review.

## Required sequence

1. **Preserve before judging.** Treat the edits as an untrusted candidate snapshot. Create a reconstructable `git diff --binary` patch, record path hashes/modes, verify patch reconstruction in a scratch worktree, then commit the untouched snapshot if exact reconstruction passes.
2. **Bind exact identity.** Record `HEAD`, `TREE`, clean/dirty state, patch path, patch SHA-256, task SHA-256, base SHA/tree, allowed changed paths, and producer process/session exit class.
3. **Inspect semantics before canonical.** For dispatch cursor/generation work, inspect the actual loop ordering and lock scope: generation binding through claim/Linear/spawn/vacuum, shared cursor lock held through repair source revalidation/backup/final cursor write, SQLite writer exclusion while mutating repair state, deterministic plan recomputation, and no cursor mutation before all backup members are durable.
4. **Run targeted proof and adversarial probes.** In addition to focused tests, run isolated probes for:
   - strict lowercase UUIDv4 and canonical UTC timestamp acceptance/rejection;
   - tampered supplied repair plans rejected before backups/cursor mutation;
   - file and parent-directory fsync failure propagation;
   - no leaked partial backup files and no deletion of pre-existing collisions;
   - WAL/main/cursor coherent backup behavior where WAL mode is present;
   - same-path DB replacement and repair/consumer cursor serialization hazards.
5. **Run canonical/package proof only after semantic probes pass.** Label focused, adversarial, canonical, static, and installed-wheel/build proof separately. A canonical pass alone is not a clean review.
6. **Dispatch fresh independent exact-head review after every new commit.** Any new repair commit invalidates all prior clean/repair review and CI evidence. Give the reviewer exact `HEAD`, `TREE`, changed-path scope, task digest, local proof summary, prior defect list, and strict no-side-effect boundaries.
7. **Update durable state to review-pending, not complete.** Set producer session/PID to `null` when no producer remains active; record the review delegation id and local proof logs/digests. Keep cap 1 occupied by the exact task until review returns `CLEAN` and subsequent promotion gates pass.
8. **Report boundaries explicitly.** Do not claim independent review clean, GitHub CI, PR, merge, release, deploy/restart, live cursor repair, Linear writes, generic dispatch resume, or cap increase from local green evidence.

## Compact proof packet

```text
STATUS=REPAIR_N_EXACT_HEAD_REVIEW_PENDING
HEAD=<candidate sha>
TREE=<candidate tree>
WORKTREE=CLEAN
PATCH=<path>
PATCH_SHA256=<sha256>
FOCUSED=<summary>
ADVERSARIAL=<summary + log + sha256>
CANONICAL=<summary + log + sha256>
STATIC=<compile/ruff/format summary>
PACKAGE=<build/install marker + log + sha256>
REVIEW=<delegation id pending>
CAP=1 occupied
NOT_CLAIMING=independent review clean, CI, PR, merge, release, deploy, live repair, Linear write, generic dispatch resume, cap increase
```

## Pitfalls

- Do not trust process exit class alone. SIGTERM can leave useful edits, a commit, or nothing; inspect the exact worktree before deciding.
- Do not let live bus `max(rowid)` drift invalidate state verifiers if the invariant is unchanged cursor and `cursor > current max(rowid)` while dispatch remains paused.
- Do not edit handoff/control state after proof without a final state consistency update; durable state should reflect `review-pending`, not producer-active or complete.
- Do not conflate structural code inspection with adversarial proof. If a reviewer previously found a semantic defect, reproduce or refute it with an isolated probe against the exact head.
