# PWP independent repository sequencing and evidence-only repair pattern

Use this reference when George coordinates an independent Prismatic-adjacent repository whose implementation owner is another agent, especially Ned owning `mbgulden/prismatic-web-publisher`. Ned's exact Telegram mention for PWP coordination is `@Nedbotnedbot_bot`; use that mention when dispatching/directing Ned and do not substitute Fred/Kai identities.

## Trigger

- Michael states that Ned is working the independent PWP repository or following assigned linear tasks.
- George has a local candidate/review artifact in the PWP repo, but Ned remains implementation owner.
- An independent exact-head review returns `REPAIR` for stale evidence bindings rather than source/package/CI behavior.
- A `RESULT.md`, PR body, handoff, or control-state correction changes the candidate commit after a prior review.

## Ownership boundary

George may repair review/evidence artifacts needed to keep the coordination plane truthful, but must not silently become a competing PWP producer.

Required boundary language:

```text
IMPLEMENTATION_OWNER=Ned
GEORGE_ROLE=coordination_review_and_sequence_guard
NO_SECOND_WRITER=true
GENERIC_DISPATCH=PAUSED
```

Ned may continue non-overlapping assigned linear tasks. If work overlaps the active candidate, require an exact report before proceeding:

```text
TASK=<task id>
HEAD=<commit>
TREE=<tree>
BASE=<base commit>
CHANGED_PATHS=<paths>
RESULT_PACKET=<path/hash>
OVERLAP_WITH_ACTIVE_CANDIDATE=<yes/no + paths>
```

## Chat/directive delivery proof

If George tries to direct Ned through Telegram or a scheduler bridge, do not claim delivery from generated output alone.

Use the exact mention:

```text
NED_MENTION=@Nedbotnedbot_bot
```

Verify all three when possible:

1. correct target chat/group title or lane;
2. exact bot/member identity or @-mention route, using `@Nedbotnedbot_bot` for Ned;
3. gateway/scheduler delivery result, not just cron stdout.

If Telegram returns `Chat not found`, record `DELIVERED=false` and rely on durable handoff/control-state until a verified route exists. If Michael corrects an agent identity mid-session, update both durable memory and this class reference before future dispatches.

## Evidence-only repair workflow

When independent review returns `REPAIR` because `RESULT.md`/handoff/PR body contains stale bindings while code/package behavior passes:

1. Classify as **evidence repair**, not implementation expansion.
2. Patch only the stale evidence fields: task contract hash, base SHA/tree, proof-log paths/digests, non-claims, or self-reference-safe placeholders.
3. Avoid impossible self-reference loops. A committed `RESULT.md` cannot embed its own final commit SHA/hash unless a separate external artifact binds it. Use explicit placeholders such as:

```text
CANDIDATE_HEAD_SHA=BOUND_BY_EXTERNAL_REVIEW_ARTIFACT
CANDIDATE_TREE_SHA=BOUND_BY_EXTERNAL_REVIEW_ARTIFACT
EXACT_PROOF_LOG=BOUND_BY_EXTERNAL_REVIEW_ARTIFACT
EXACT_PROOF_LOG_SHA256=BOUND_BY_EXTERNAL_REVIEW_ARTIFACT
```

Then label older logs clearly:

```text
PRE_EVIDENCE_REPAIR_BEHAVIOR_LOG=<path>
PRE_EVIDENCE_REPAIR_BEHAVIOR_LOG_SHA256=<sha256>
```

4. Commit the evidence-only repair. This creates a new head/tree.
5. Rerun visible focused verification on the new exact head, at minimum:

```text
pytest
ruff check
ruff format --check
git diff --check
package/clean-room proof when the candidate touches packaging or CI
```

6. Invalidate the prior review for promotion even if it said the source behavior passed. Dispatch a fresh read-only exact-head review bound to the new head/tree/base.
7. Update durable control state and compact handoff with:

```text
ACTIVE_CANDIDATE=<new head>
ACTIVE_TREE=<new tree>
REPAIR_REVIEW=<old review id + reason>
INDEPENDENT_REVIEW=<new review id PENDING>
PUSHED=false
PR_CREATED=false
MERGED=false
DEPLOYED=false
```

## Fresh-clone / interpreter-isolation proof repair

When a PWP task documents fresh-clone, source-isolation, or clean-room import proof, do not accept `env -u PYTHONPATH python3` as deterministic isolation by itself. On a Hermes host, `python3` may resolve to an active pipx/venv interpreter that already has `prismatic` installed, so the probe can be contaminated even with `PYTHONPATH` removed.

Use a deterministic isolated interpreter probe for “source checkout is not being imported” claims:

```bash
cd /tmp
env -i HOME="$HOME" PATH=/usr/bin:/bin /usr/bin/python3 -I - <<'PY'
import importlib.util, sys
for name in ("prismatic", "prismatic_web_publisher"):
    spec = importlib.util.find_spec(name)
    print(name, spec)
    assert spec is None
print("EXECUTABLE", sys.executable)
print("ISOLATED", sys.flags.isolated)
PY
```

Required evidence fields:

```text
AMBIENT_INTERPRETER=<sys.executable for rejected/old command, if relevant>
ISOLATED_EXECUTABLE=/usr/bin/python3
ISOLATED_FLAG=1
IMPORT_SPECS_BEFORE_INSTALL=prismatic None; prismatic_web_publisher None
NON_CLAIM=not installed-wheel behavior unless install/import proof also ran
```

If Ned's PR or docs use the ambient-interpreter pattern, post a same-branch repair request rather than merging: record the contamination boundary, replace the command/output, preserve non-claims, then require fresh exact-head CI and independent review after the repaired head appears. Do not launch the next PWP slice while the proof-repair PR is open.

## Promotion gate

Do not push/open PR/merge from the repaired head until the fresh exact-head review returns `CLEAN`. Local green proof plus an old review is not enough after any new commit.

After `CLEAN`:

1. Re-read local head/tree/base, worktree cleanliness, remote branch absence or exact parity, and current `origin/main` before pushing.
2. Push only the reviewed branch/head; do not delete branches unless explicitly authorized.
3. Open one focused PR with exact `HEAD`, `TREE`, `BASE_TREE`, review id, CI expectations, marker, and non-claims.
4. Read back PR state, head ref/OID, body markers, mergeability, and check rollup. Treat `UNSTABLE`/pending checks as a hold, not a failure or pass.
5. Watch PR-head hosted CI to real conclusions. Require all required matrix/package jobs green on the reviewed head before merging.
6. Before merge, perform a final exact readback: PR state open/non-draft, `mergeStateStatus=CLEAN`, remote branch head equals reviewed head, worktree clean, and all checks success.
7. Squash-merge only under the standing reviewed-source merge policy. Retain the branch unless Michael authorizes deletion.
8. Fetch/read back remote `main`, verify merge commit and tree parity with the reviewed candidate tree, then watch post-merge `main` CI to success before closing the source slice.
9. Update durable handoff/control state with `PR`, `MERGE_SHA`, `MERGE_TREE`, PR CI run, main CI run, `branch_deleted=false`, owner boundary, and explicit non-claims.
10. Sequence Ned's next already-assigned linear task from the merge SHA; George must not start a competing producer lane.

Closeout proof fields:

```text
PR=<url/number>
REVIEWED_HEAD=<sha>
REVIEWED_TREE=<tree>
INDEPENDENT_REVIEW=<delegation id CLEAN>
PR_CI_RUN=<id PASS>
MERGE_SHA=<sha>
MERGE_TREE=<tree>
MAIN_CI_RUN=<id PASS>
IMPLEMENTATION_OWNER=Ned
NED_MENTION=@Nedbotnedbot_bot
BRANCH_DELETED=false
NOT_CLAIMING=deploy, PE cutover, service restart, runtime/cursor mutation, replay, Linear write, generic-dispatch resume, cap increase
```

## Proof packet shape

```text
TASK=PWP-LINEAR-STACK-FOUNDATION-1
STATUS=PARTIAL|PASS
OWNER=Ned
GEORGE_SCOPE=coordination/evidence repair only
HEAD=<exact head>
TREE=<exact tree>
BASE=<exact base>
RESULT=<PASS|REPAIR|PENDING>
LOG=<path>
LOG_SHA256=<sha256>
AD_HOC_OR_CANONICAL=<ad-hoc targeted|GitHub CI|canonical suite>
NOT_CLAIMING=push, PR, merge, deploy, cap increase, generic dispatch resume, Ned delivery unless verified
```
