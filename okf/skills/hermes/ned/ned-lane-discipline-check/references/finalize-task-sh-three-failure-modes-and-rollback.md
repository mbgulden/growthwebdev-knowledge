# `finalize_task.sh` — three failure modes & rollback protocol

**Captured:**
- Mode 1 (bogus-arg): 2026-06-29 ~20:46Z (Pass-16 on GRO-484..502)
- Mode 2 (working-tree isolation): 2026-06-30 ~03:34Z (Pass-N+34)
- Mode 3 (wrong-issue, NEW): 2026-06-30 ~04:34Z (Pass-N+41 on GRO-145..162)

**Status:** All three empirically validated. Use this reference as the canonical
recipe for any future finalize_task.sh incident.

---

## Mode 1 — Bogus-arg failure

`finalize_task.sh` invoked with non-Real-issue args: `--help`, `-h`, `?`, empty,
`GRO-PLACEHOLDER`, `XXX`, `TODO`, or any string that doesn't match `^GRO-[0-9]+$`.

**Side effects:** script auto-commits the working tree (stages everything,
including untracked sibling files) + releases hardcoded locks + Linear API
rejects the bogus ID.

**Recovery:** `git reset --hard HEAD~1`. Linear API never succeeded so no
state revert needed. Audit-doc the rollback.

**Evidence:** commit `2885d4a3 [ned] --help: finalize (auto-commit on budget
exhaustion)` on the shared repo.

**Full reference:** `references/finalize-task-sh-argument-validation-pitfall.md`
(this is the original Pass-16 codification).

---

## Mode 2 — Working-tree isolation failure

`finalize_task.sh` invoked correctly on a real issue, but the working tree
had sibling-owned untracked files (`inventory.json`) and modifications
(`prismatic/gateway/server.py`). Pre-commit hook does NOT distinguish
sibling-owned files; script auto-stages + commits them.

**Side effects:** script auto-commits sibling files under YOUR branch
(`inventory.json` 937 lines + sibling `prismatic/gateway/server.py` 10 lines
were auto-committed in the Pass-N+40→41 boundary event).

**Recovery:** `git reset HEAD <file>` per-file BEFORE the script's auto-commit
fires, then commit only your own files. **Prevention is the key:** verify
`git status --short` and stage by specific path (`git add scripts/ops/...md`),
NEVER `git add .` or `-A`.

**Evidence:** observed in Pass-N+41 working tree at the boundary (`M
prismatic/gateway/server.py` + `?? inventory.json` from sibling-agent
churn). See SKILL.md Pass-N+34 entry for the original codification.

---

## Mode 3 — Wrong-issue finalize (NEW — Pass-N+41)

`finalize_task.sh` invoked correctly on a **real** issue ID that is NOT in
Ned's lane. Script auto-commits the working tree + releases locks + Linear API
**succeeds** because the issue ID is real, state-mutating the wrong-lane
issue (typically Backlog → In Review).

**Side effects:** both (a) git commit on the wrong-issue branch and (b) Linear
state mutation in the wrong lane.

**Evidence:** commit `a2c1e15f [ned] GRO-165: finalize (auto-commit on
budget exhaustion)` on `ned/gro-485-triage-pass-1` + GRO-165 state
transition to "In Review" in Linear (GRO-165 is an active-oahu pre-launch
task → Fred's lane, not Ned's).

### Why Mode 3 is harder to recover from than Modes 1/2

Modes 1 and 2 only require git rollback — Linear never accepted the bogus
or correctly-bounded the impact. Mode 3 mutates **real, visible Linear
state** that Michael sees daily (Backlog scans). If you don't revert Linear
state, the wrong-lane issue is left in "In Review" and a future cron pass
will pick it up as ready for review — which is doubly wrong (wrong lane +
wrong state).

### Rollback protocol (validated — canonical recipe)

**Order matters: Linear FIRST, then git.**

1. **Verify the regression via `git log --oneline -3` AND Linear state query.**
   Bogus-commit signature: lowercase `[ned]` prefix (not `[Ned]` capital),
   contains `finalize (auto-commit on budget exhaustion)`, or has an
   issue-ID subject that's not in Ned's lane. Cross-check Linear state.

2. **Revert the Linear state mutation FIRST.**
   Why first: Linear state is the user-visible regression; Michael scans
   Backlog daily; git is internal. Use `mutation IssueUpdate` with the
   correct `stateId` and `labelIds`.

   ```bash
   # Find Backlog state UUID for your team
   curl -s https://api.linear.app/graphql \
     -H "Authorization: $LINEAR_API_KEY" -H "Content-Type: application/json" \
     -d '{"query":"{ workflowStates(filter: {name: {eq: \"Backlog\"}}) { nodes { id } } }"}'

   # Find the wrong-lane label UUID (e.g. agent:fred)
   curl -s https://api.linear.app/graphql \
     -H "Authorization: $LINEAR_API_KEY" -H "Content-Type: application/json" \
     -d '{"query":"{ issueLabels(filter: {name: {eq: \"agent:fred\"}}) { nodes { id } } }"}'

   # Revert: drop wrong lane, add correct lane, state → Backlog
   write_file /tmp/revert.json with mutation + variables
   curl --data-binary @/tmp/revert.json https://api.linear.app/graphql
   ```

   **Pitfall:** do NOT use `stateId: null` — Linear doesn't accept null for
   stateId in IssueUpdate; you need the actual Backlog state UUID.

3. **Reset the local branch to the prior commit.**
   `git reset --hard <prior-sha>` where `<prior-sha>` is `HEAD~1` if the bad
   commit is the head. Verify with `git status --short` (should be clean).

4. **Verify the remote is clean** via `git ls-remote origin <branch>`.
   - If the bad commit was pushed → you need `git push --force-with-lease`
     to overwrite.
   - If NOT pushed (Pass-N+41 case — remote was at `ebc69803` from Pass-N+24,
     never received `a2c1e15f`) → local reset is sufficient.

5. **Write a follow-up audit doc** explaining the rollback.
   Use `scripts/ops/gro-<low>-<high>-batch-routing-Nth-pass-infra-findings.md`
   naming convention. The git log should be self-documenting — future
   reconstructors need to know WHY the commit immediately before this pass
   was chosen as the rollback target.

6. **Run the current pass's relabel batch as normal.**
   The wrong-issue finalize often leaves sibling issues still misrouted; the
   rollback pass is a natural opportunity to relabel the rest of the feed too.

### Critical pitfall to AVOID in the rollback

- **Do NOT push the rollback before reverting Linear state.** Order: revert
  Linear → reset git → push git. If you push first and then realize Linear
  state is still wrong, you have a public rollback commit without the Linear
  side-revert.
- **Do NOT amend the bad commit.** Use `git reset --hard HEAD~1` and write a
  follow-up commit (the audit doc). Amending erases the evidence of the
  regression; future reconstructors need the bad commit's SHA in `git
  reflog` + the audit doc.
- **Do NOT call `finalize_task.sh` to "clean up" the wrong-issue finalize.**
  That's what caused the regression. Use direct GraphQL mutations.

### Likely root cause (Pass-N+41 case)

The Window-B stripped-prompt variant (`20759afd096b`, "Read the Linear
issue from the script output above. Execute it fully.") likely picked up
GRO-165 from a scanner feed and ran the bare-minimum execution recipe
(which includes `finalize_task.sh GRO-165 ned/GRO-165 ned` as step 7)
without first applying the rotation-equivalence ratchet. GRO-165 was in
Ned's lane by label but NOT by content.

**Window-B tells:**
- lowercase `[ned]` commit prefix (script default), not human/manual
  `[Ned]` capital
- timing within a 15-min Window-B interval boundary
- no skill loader hints in Window-B's prompt

**Recommended fix (priority):** harden Window-B's prompt with an inline
reference to `ned-lane-discipline-check` OR ensure the dispatcher doesn't
auto-apply `agent:ned` to out-of-lane items.

---

## Prevention (preferred over recovery)

For all three modes, **before calling `finalize_task.sh`**:

1. **Confirm the issue is in Ned's lane.** If `agent:ned` is auto-applied
   by the dispatcher on a stale backlog item that's actually content/product,
   the call will produce Mode 3. Apply the rotation-equivalence ratchet
   FIRST (criterion (a)+(b)+(c) check). If SUPPRESS → never call
   `finalize_task.sh`.

2. **Confirm the working tree is clean of sibling content.** `git status
   --short` + verify the staged set is exactly your files. If sibling
   untracked files exist (`??`), use `git reset HEAD <file>` per-file or
   stage by specific path.

3. **Confirm the issue ID matches `^GRO-[0-9]+$`** (uppercase GRO prefix +
   digits only). Reject `--help`, `-h`, `?`, empty string, `GRO-PLACEHOLDER`,
   `XXX`, `TODO`.

4. **Pre-read `finalize_task.sh`** to understand its CLI. Use `read_file`, NOT
   `bash finalize_task.sh --help` (the latter will auto-execute on `--help`
   per Mode 1).