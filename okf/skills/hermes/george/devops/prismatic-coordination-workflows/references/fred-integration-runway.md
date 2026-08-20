# Fred integration runway — current-main porting pattern

Use this reference when George needs to turn many Fred-built branches/PRs into a safe Prismatic integration sequence.

## Trigger

Michael asks for Fred to integrate everything they have been building, continue Prismatic completion, or convert agent work into actually working repo/runtime changes.

## Pattern

1. **Finish and review the active slice first**
   - Check the bus task state, artifact/outbox, branch/worktree, PR, and marker.
   - Do not accept Fred's packet at face value. Run George probes against the changed behavior.
   - If blockers exist, issue a narrow repair task rather than broad rework.

2. **Convert accepted work into one focused PR**
   - Push only the verified branch/diff.
   - Open/read back the PR.
   - Verify state, draft flag, mergeability, head SHA, file list, body markers, and GitHub checks.
   - Report pending/failing CI honestly; do not call CI green until GitHub reports green.

3. **Inventory Fred's backlog before launching the next slice**
   Suggested classifications:
   - `OPEN_PR_CURRENT_MAIN_PORT` — old PR has useful assets but needs current-main port.
   - `FOCUSED_ORPHAN_ASSET_REVIEW` — branch is not an open PR but may contain a small reusable asset.
   - `SUPERSEDED_OR_ALREADY_IN_MAIN` — no integration needed except possible closure recommendation.
   - `QUARANTINE_DIVERGED_NO_BLIND_MERGE` — old/highly divergent branch; asset-mine only.
   - `QUARANTINE_SECRET_PATH_REVIEW` — branch diff references secret/private-key paths; avoid reading/pasting contents and never blind-merge.

4. **Sequence bounded filesystem-bus tasks**
   - Start from merged `main` in a clean isolated worktree.
   - Give Fred a marker-specific branch and explicit result contract.
   - Preserve side-effect boundaries (`merge=false`, `deploy=false`, `github_pr_create=false`, etc.) unless Michael authorized otherwise.
   - Keep one next integration slice active once the prior slice has a focused PR.

5. **Use read-only parallel PR subreviews for triage**
   - Safe for overlap/path/dependency analysis.
   - Not sufficient for success claims, pushes, PR edits, merges, or deploys.
   - George must verify outputs before acting on them.

6. **Keep durable operator state updated**
   - Update `PRISMATIC_CURRENT_HANDOFF.md` with accepted PR URL/SHA/CI state, active bus task id, inventory counts, and non-claims.
   - Maintain a short-interval change-only watcher that stays silent on unchanged state.

## Proof block shape

```text
COMMAND=<inventory + focused PR + active next task verification>
RESULT=<PASS|PARTIAL|BLOCKED>
LOG=<review/inventory/watch log path>
SCOPE=<Fred integration runway, not full Prismatic completion>
AD_HOC_OR_CANONICAL=<ad-hoc targeted|GitHub CI|canonical suite>
NOT_CLAIMING=<merge, deploy, production proof, canonical suite, old PR closure>
MARKER=<integration runway marker>
```

## Pitfalls

- Do not let a first green focused PR become a stopping point when Michael asked for continued completion; queue or start the next bounded slice if authorized.
- Do not wholesale merge old Fred branches just because they are Fred-owned; current-main path-level porting is safer.
- Do not expose secret material while classifying sensitive branches. Path presence is enough to quarantine.
- Do not equate local targeted probes with canonical suite green or production proof.
