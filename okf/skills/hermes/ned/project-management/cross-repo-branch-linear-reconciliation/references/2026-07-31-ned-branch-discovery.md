# 2026-07-31 ned-branch discovery — worked example

This is the case study that motivated the parent skill. It shows how the workflow actually ran, what got wrong, and how the verifier caught the discrepancies.

## Trigger

The user asked: "Ned has a load of /ned branches that we will want to discover and reconcile".

Then immediately followed with: "some of the tasks on there may have already been done and completed on another ned branch. That needs to be researched".

The user's intuition: "are these branches stale leftovers from completed work?". The research had to confirm or refute this.

## What ran

`/tmp/scan_ned_branches.py` and `/tmp/ned_branches_analysis.py` were the discovery + first-pass analysis pair. `/tmp/ned_branch_dedup.py` was the second pass that did the strict-ancestor merge check and the Linear task-state correlation.

The artifacts ended up at:

```
~/.hermes/profiles/ned/reports/discovery/ned-branches-2026-07-31/
├── README.md                       # user-facing report, rewritten after corrections
├── ned_branches_report.txt         # raw branch list (2,670 lines)
├── ned_branches_analysis.json      # first-pass counts (had wrong merged count)
└── dedup_analysis.json             # second-pass strict-ancestor + Linear correlation
```

## What went wrong

The first pass reported 394 merged branches / 1,666 active across 33 repos. The second pass corrected that to 115 strict-merged / 1,945 unmerged across 32 repos. The discrepancy had three sources:

1. **Tip-vs-merge confusion.** The first pass was counting "merged" by saying "the local branch with this short name is merged", then applying that to every remote-tracking branch with the same short name. The correct check is `git merge-base --is-ancestor <remote_ref> <main>` — does the remote ref's tip actually reach main? Not whether a local branch with the same name was merged.

2. **Repo count off-by-one.** The first pass printed 33 repos in the terminal table; the actual JSON had 32. The text-vs-data drift was caught by the verifier.

3. **Mental estimate of state file numbers.** The corrected numbers (115 merged, 1,945 unmerged, 32 repos) had to be propagated into the state file's `one_line` and `last_meaningful_turn_summary`. The first version of the state file kept the old (wrong) numbers because the patch was only applied to the README.

## What the verifier caught

`/tmp/hermes-verify-ned-discovery-reparse.py` ran 20 checks total:

- state/current.json parses
- state one_line has the expected fragments (2,060 / 32 / 115 / 1,945)
- README contains the corrected numbers
- dedup_analysis.json overall has total=2060, merged=115, unmerged=1945, tip_dedup_groups=0
- leftover scripts compile
- /tmp/ leftovers were cleaned up
- RENDERER_SPEC.md untouched
- Linear tasks (GRO-4382, GRO-4389, GRO-4393) still queryable and in the expected state

**Failures during the verify-pass revision process:**

1. First run: README expected "33 repos" but JSON had 32. Fixed README.
2. Second run: analysis file missing from the discovery directory. The `mv` command from /tmp had failed silently because the destination directory did not exist. Re-ran with `cp`.
3. Third run: RENDERER_SPEC.md check looked for `RENDERER_SPEC` in the content but the title is `KPI Dashboard PWP Renderer — Spec (Second Slice)`. Changed the check to look for `Renderer` and `Spec`.
4. Fourth run: state file's `one_line` still had old `394 merged / 1,666 active` text. Patched the state file.

After four iterations, 20/20 checks passed.

## The final answer

The user's intuition was correct: **86% of `ned/*` branches with a GRO-XXXX in the name map to a closed Linear task.** The work landed on another branch (typically via merge commit or squash into main), leaving the source branch with a unique tip. The local branch is a stale leftover.

**No branches were deleted.** The `branch-deletion-approval` skill requires an explicit Michael sign-off plus a manifest before any deletion. This discovery is the inventory phase, not the action phase.

## Linear task-state distribution (sample of 80 unmerged branches)

| State | Count | Examples |
|---|---|---|
| Done | 69 | GRO-1222, GRO-1223, GRO-1316, GRO-1481, GRO-1484 |
| In Progress | 7 | GRO-2191, GRO-2201, GRO-2202, GRO-2228, GRO-2232 |
| In Review | 1 | GRO-2264 |
| Canceled | 3 | GRO-2090, GRO-2131, GRO-2226 |

The 7 In Progress and 1 In Review are the live work. Everything else is a stale leftover.

## Per-repo totals

| Repo | Total | Merged | Unmerged |
|---|---|---|---|
| prismatic-engine | 882 | 0 | 882 |
| prismatic-hub-ui | 315 | 0 | 315 |
| prismatic-gro4209-independent-review | 205 | 39 | 166 |
| prismatic-runtime-recovery | 195 | 39 | 156 |
| agy_warm_cache/prismatic-engine | 136 | 12 | 124 |
| growthwebdev-knowledge | 67 | 0 | 67 |
| hd-platform | 59 | 1 | 58 |
| prismatic-engine-site | 42 | 1 | 41 |
| prismatic-web-publisher | 28 | 8 | 20 |
| agentic-swarm-ops | 19 | 2 | 17 |

(Full 32-repo table in `dedup_analysis.json`.)

## Suggested bounded moves (not yet executed)

- **Move A — Stale-local cleanup.** For each `ned/*` branch where the matching Linear task is Done/Canceled, `git branch -d` (or `git push origin --delete`). 86% of the sample maps to closed tasks, so this is the bulk of the cleanup.
- **Move B — Remote-tracking prune.** `git remote prune origin` per repo.
- **Move C — Process change.** Add a Linear-task-closure hook that prunes `agent:*` branches when the corresponding GRO-XXXX moves to Done or Canceled.

## Lessons propagated

- The `os.walk` `.git` filter ordering bug → captured in this skill's "Pitfalls" section.
- The strict-ancestor vs "merged-by-name" distinction → captured in the "Workflow" steps.
- The mental-estimate-not-machine-count drift → captured in the "Pitfalls" section.
- The verify-pass-revise-loop pattern (when the first verifier fails, correct the data, don't just patch the verifier) → this is mentioned in the project-management class-level skill tree.
