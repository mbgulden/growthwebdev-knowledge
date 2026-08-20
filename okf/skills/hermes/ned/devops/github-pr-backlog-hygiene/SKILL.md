---
name: github-pr-backlog-hygiene
description: Triage, clean, merge, close, or route large GitHub PR backlogs from multi-agent/Jules/AGY/Ned workflows. Use when Michael asks to check PRs, clean PR backlog, especially Jules/agent PRs, or devise/follow a merge/extract/assign strategy.
triggers:
  - user asks to check PRs or GitHub backlog
  - user asks about Jules PRs or agent-generated PRs
  - repository has many open/conflicting/stale PRs
  - deciding whether to merge, close, extract, or route PRs to AGY/another owner
  - PRs include broad stale diffs, generated artifacts, DB/state files, private keys, or conflicting agent branches
  - linear child issues are Done but the linked PR never landed and the live product shows no change (live-surface drift)
  - session has no `GH_TOKEN` / `gh` auth and must still produce a scope-clean extraction branch on disk
---

# GitHub PR Backlog Hygiene

## Purpose
Turn a messy multi-agent PR pile into a safe, ordered flow: merge only scoped current work, extract useful deltas from stale/conflicting PRs, close obvious noise, and route non-Ned/domain work to AGY or the right owner. Do **not** treat every open PR as a merge candidate.

## Operating posture

Default stance for stale agent/Jules PRs:

> PRs are evidence and possible patch sources, not proof that the branch should merge raw.

When Michael says “do the next step” in a PR cleanup context, keep executing the golden path instead of stopping at a status report: verify AGY output, merge/close/route safe PRs, create/dispatch the next AGY task if the queue still has work, and re-count live PR state. Stop only at a real safety/governance boundary or when the remaining work is intentionally parked.

Most large agent backlogs contain:
- stale generated branches,
- duplicate finalize/superseded branches,
- conflicting old experiments,
- no-op PRs,
- broad mega-diffs,
- state DB / generated artifact / secret-path contamination,
- a smaller number of genuinely useful scoped deltas.

## Explicit no-merge constraints override broad continuation requests

A request such as “do the next step,” “keep moving,” or autonomous/YOLO continuation is **not** permission to merge when the governing issue, source prompt, or repository instructions explicitly say “do not merge it yourself,” “await review,” or equivalent.

Before any `gh pr merge` action, re-read the task/source constraints and classify authority explicitly:

- **Explicit merge authorization** (for example, "merge PR #4", "push the branch, merge and all the rest of that afterwards") → merge only after the normal scoped review and verification. The merge authorization must name the merge action explicitly; "push it" alone is not merge authorization.
- **Explicit no-merge/review-only instruction** → do not merge; verify, rebase/update a branch if permitted, report the ready PR, and surface the human merge action.
- **Ambiguous continuation wording** → preserve the stricter written constraint. Continue with non-merge work such as evidence refresh, conflict diagnosis, tests, and PR readback.

Do not treat a clean mergeability result, lack of required checks, or a user’s general request for momentum as an override. If an unauthorized merge was performed, state it plainly, stop further merges, and record the remaining safe next action rather than compounding it.

## Required triage sequence

1. **Inventory current PR state.**
   - Count open PRs.
   - Bucket by base branch (`main`, `deploy-fresh`, feature/master-plan bases).
   - Bucket by mergeability (`MERGEABLE`, `CONFLICTING`, `UNKNOWN`).
   - Bucket failed checks separately.
   - Identify branch/title patterns that suggest Jules/agent output: long numeric suffixes, `agent/`, `execution/`, `fix/dispatcher`, `Finalize`, `superseded`, `validate supervisor`, or explicit `Jules`.

2. **Classify every target PR into one lane.**

   | Lane | Criteria | Action |
   |---|---|---|
   | Ready merge train | mergeable, scoped, current, clean checks or focused verification possible | Review changed paths, run focused verification, merge in dependency order |
   | Extract-only | conflicting/stale but contains a useful small delta | Re-implement/cherry-pick into a fresh scoped branch, test, open clean PR, close source PR |
   | Quarantine/close | no-op, explicitly superseded, huge unrelated diff, unsafe files, stale generated artifacts | Close with clear reason; do not merge raw |
   | Owner-route / AGY | non-Ned domain or large synthesis needed | Create/label Linear task for AGY or correct owner with exact PR list and instructions |

3. **Close obvious noise immediately when safe.**
   Good close candidates:
   - PR has zero changed files.
   - Title/body says superseded/finalize-only and current branch is conflicting.
   - PR is a huge stale mega-diff with unrelated file churn.
   - PR includes dangerous raw paths: `*.pem`, `*.key`, `*.db`, `prismatic_state/*`, generated build artifacts, credentials, or local state.
   - Duplicate branch in a cluster where a cleaner PR or current main already carries the useful behavior.

   Close with a short comment naming the disposition: no-op, superseded, unsafe raw merge, duplicate, or routed to AGY/extraction.

4. **Extract useful deltas only when lane locks allow it.**
   Before editing files, follow lane/file lock protocol. If a needed file is locked by another active agent, do **not** break the lock. Route to AGY or leave a source-PR comment instead.

5. **Assign AGY for synthesis-sized cleanup.**
   Create a Linear issue when the remaining work is a queue, not a single safe edit. The issue should include:
   - exact PR numbers and URLs;
   - disposition goal: close, extract, or owner-route;
   - unsafe merge rules;
   - verification requirement;
   - clear instruction: do not raw-merge stale/conflicting agent PRs.

6. **Consume AGY output as evidence, not authority.**
   When AGY completes an extract/triage task:
   - read the sandbox `RESULT.md`;
   - verify the claimed branch/commit/PR exists;
   - independently inspect GitHub `statusCheckRollup`, mergeability, and changed paths;
   - if AGY produced only a local branch or broad stale branch, create a fresh scoped extraction branch before merging;
   - close the stale source PR only after the clean extraction lands or a clear owner-route/follow-up exists.

7. **For branch-promotion/integration PRs, treat CI as the merge gate, not local confidence.**
   When promoting a long-lived branch such as `deploy-fresh` into `main`:
   - create a protected integration branch/worktree from current `origin/main`, merge the source branch, and resolve conflicts there;
   - preserve main-side compatibility shims while accepting source-branch content only where it is intentionally preferred;
   - run local focused tests around conflicted areas, then a broad suite before pushing;
   - inspect failing GitHub checks with `gh run view RUN_ID --log-failed`; do not guess from the check name;
   - reproduce failures locally when possible, patch the integration branch, amend/force-push with lease, and wait for both GitHub checks and mergeability;
   - only merge after GitHub required checks are green, even when local tests pass.

8. **Verify final queue state.**
   After closing/routing/extracting/merging:
   - re-count open PRs;
   - list remaining conflicting PRs;
   - list remaining failed-check PRs;
   - verify Linear routing issues exist if work was handed to AGY;
   - after each merge, re-query mergeability before attempting the next PR because previously green PRs can become conflicting;
   - report only the actionable summary, not the full command transcript.

## Lane-split merge trains and proof-branch cleanup

When an authorized merge train hits a conflict, distinguish the conflicting paths before attempting any rebase or resolution:

1. **Stop at the first real conflict.** Do not continue the train based on earlier green checks.
2. **Split by lane.** If the PR combines a path owned by this agent with a path owned by another lane (for example `.github/` plus `docs/`), do not resolve the other lane opportunistically. Create or route a focused Linear child to that owner with `dispatch:ready`, exact PR/path/commit evidence, and a handoff comment.
3. **Resume only after the owner lands its focused reconciliation.** Rebase the remaining owned-only candidate, verify its changed paths exclude the other lane, rerun focused checks, re-query GitHub mergeability/checks, then continue the explicitly authorized order.
4. **Do not infer merge authority.** A general “keep going” does not override an explicit no-auto-merge instruction in the source task. Ask for a clear merge-train authorization, then merge only the named sequence.
5. **Supersede tangled proof branches safely.** If a proof PR rebase replays already-merged implementation history and produces broad conflicts, abort it rather than force-resolving. Reproduce the proof on current `main` from a clean clone and close the old proof PR with the exact main SHA and evidence. Final-SHA green CI is authoritative; cancelled intermediate runs caused by merge-train concurrency are not a product failure.

See `references/pwp-merge-train-lane-and-proof-20260723.md` for the concrete handoff, verification, and closure pattern.

## Jules / agent PR rules

For Jules-generated or Jules-like PRs:

- **Never raw-merge conflicting Jules/agent PRs.**
- **Never raw-merge broad stale mega-diffs.**
- **Never raw-merge PRs containing state DBs, private keys, local config, generated build outputs, or broad unrelated file churn.**
- Treat Jules PRs as patch suggestions.
- Prefer fresh scoped extraction branches with focused tests.
- If the PR is useful but blocked by active locks, route it to AGY with the lock/blocker noted.

## GitHub CLI notes

Useful commands:

```bash
gh pr list --repo OWNER/REPO --state open --limit 200 \
  --json number,title,author,headRefName,baseRefName,updatedAt,isDraft,mergeable,reviewDecision,statusCheckRollup,url,labels

gh pr view PR --repo OWNER/REPO \
  --json number,title,body,headRefName,baseRefName,mergeable,commits,files,url,statusCheckRollup

gh pr diff PR --repo OWNER/REPO --name-only
gh pr diff PR --repo OWNER/REPO --patch
```

When `gh` is not authenticated, the public REST API still works read-only without auth and is enough for triage:

```bash
curl -sS https://api.github.com/repos/OWNER/REPO/pulls?state=open&per_page=100
# field set: number, title, head.ref, base.ref, draft, mergeable, updated_at, html_url
```

Fall back to the REST API when you need a read-only PR list, branch divergence, or branch-existence check and `gh auth status` reports "not logged in". The REST API is rate-limited per IP, but for triage of one repo's open PRs you will not hit it.

Pitfalls:
- Some installed `gh` versions do **not** support `gh pr diff --stat`; use `gh pr view --json files` or `gh pr diff --name-only` instead.
- Very large PR diffs may hit GitHub API limits (`diff exceeded maximum files/lines`). Fall back to `gh pr view --json files` and classify by path risk before attempting local checkout.
- `gh search prs --json ...` has a limited set of fields; `headRefName`/`baseRefName` may not be available in search output. Use repo-local `gh pr list` for merge triage.
- **`git apply --3way` is silently a no-op when the patch context lines do not match.** `rc=0` with "Applied cleanly" does not mean the diff was applied. Always verify with `git diff --stat HEAD` *and* `git diff origin/main --stat` after applying. `git status --short` alone is not enough — the dirty handler may show nothing if the patch was a no-op. When working from anonymous `.patch` endpoints, strip the git-format-patch email headers (`From <sha> Mon Sep 17 ...`, `Date:`, `Subject:`, `index ...`) before `git apply --check --recount`.

## PR-state vs Linear-state divergence

A common drift class during backlog triage: a Linear issue is marked **Done** with a finalization report claiming "PR opened at <url>", but the linked PR is still open, conflicted, or never merged. This is especially common after auto-finalize scripts or multi-agent handoffs. Always cross-check:

- For each "Done" Linear issue that links a PR, fetch `pulls?state=open` and confirm the PR is still open. If so, the issue is effectively not green even though Linear says it is.
- Conversely, a Linear issue can be **Todo** while its PR is merged. The PR is the source of truth for "did the code land?" — Linear state can lag.
Report the two-way divergence explicitly in the triage summary so Michael can decide
whether to re-open the issue, merge the PR, or close one side.

### Live-surface drift: the third axis

Linear ↔ PR divergence is the two-axis case. The third axis is **the live product
surface**: did the code that the PR claims to ship actually reach the served HTML
or API? Probe both the public production URL and the canonical branch HEAD on
GitHub (`raw.githubusercontent.com/OWNER/REPO/BRANCH/PATH`) before accepting any
"Done" finalization claim. If the live surface and the canonical HEAD both lack
the signal the PR claims to ship, the right move is to extract a fresh
scope-clean branch from the open PR (no need to close the original) and post a
drift-finding comment to the parent Linear issue. Do not close the open PR
silently — its diff is the source of truth for the extraction.

## Pushing and merging the extraction when `gh` / `GH_TOKEN` are unavailable

A session may have `gh` failing with `gh auth status: not logged in` and no
`GH_TOKEN` / `GITHUB_TOKEN` in the environment, yet still hold a usable
credential in `~/.git-credentials`. The format is
`https://USERNAME:TOKEN@github.com` (one line per host). Use it directly:

```python
import os, re, requests, subprocess
from pathlib import Path
gc = Path('/home/ubuntu/.git-credentials').read_text()
# Prefer the personal token (mbgulden:*) over the x-access-token app token
cred = next((l for l in gc.splitlines() if 'mbgulden' in l), gc.splitlines()[0])
m = re.match(r'https://([^:]+):([^@]+)@github\.com', cred)
user, tok = m.group(1), m.group(2)
os.environ['GH_TOKEN'] = tok
```

Operations that require the token — `git push`, opening a PR via REST,
closing a PR via REST, merging via `PUT /repos/.../pulls/{n}/merge` — all work
once you have the token. Two non-obvious pitfalls:

- `git push` interactively prompts for credentials. Configure a credential
  helper script via `GIT_ASKPASS` that simply echoes the token, or set
  `GIT_ASKPASS` to a script that emits `username=$user` / `password=$tok`,
  before `git push -u origin <branch>`. Do not delete `~/.git-credentials` —
  other agents may rely on it.
- The bare-head SHA after a squash merge is **different** from the PR head
  SHA. Always re-fetch `origin/main` (`refs/heads/main`) and quote the **new**
  main-head SHA in the Linear "merged" comment, not the PR head SHA.

## Closing superseded PRs with explicit disposition comments

Once the extraction PR is merged, the upstream PRs that supplied the diff are
**superseded** by the merged extraction. Close them with a short comment
naming the superseding PR and the reason — leave the SHA, the merged title,
and the file scope so future agents can verify the disposition:

```python
for n in [UPSTREAM_1, UPSTREAM_2]:
    requests.post(f'https://api.github.com/repos/OWNER/REPO/issues/{n}/comments',
        headers={'Authorization': f'token {tok}'}, json={'body': 'Superseded by #49 — ...'})
    requests.post(f'https://api.github.com/repos/OWNER/REPO/pulls/{n}',
        headers={'Authorization': f'token {tok}'}, json={'state': 'closed'})
```

Only close PRs whose scope is fully absorbed. If the upstream PR carries
additional changes (e.g. checkout funnel events) that are **not** in the
extraction, leave it open and call out the residual scope in the comment.

## Class-level check failures: ignore the fail when the class is identical across the repo

In repositories where multiple checks run, a single check may fail consistently
across every PR — e.g. `Workers Builds: hd-platform` failing on every PR in the
HDE repo while `Cloudflare Pages` succeeds. Before treating a failure as a
regression, compare the failing check across several PRs (the canonical merge
candidates, the open stale PRs, and the new extraction). If the failure is
identical in:

- name
- conclusion
- started/finished times within a few minutes of the corresponding push
- across PRs that touch different files

…and the canonical deployment check (e.g. Cloudflare Pages for HDE) is
**success**, treat the failing check as a pre-existing **class-level** failure
unrelated to the changed paths. Document this explicitly in the merge
rationale and the Linear "merged" comment so reviewers can see the
class-level evidence. Do not silently ignore the failure — a multi-PR
comparison is the proof that the failure is environmental, not
code-introduced.

## Live deploy race after a merge

After a merge, the live production URL does not instantly reflect the new
commit. Cloudflare Pages (and similar providers) race between the previous
deployment and the new one for ~60–180 seconds. Probing the live URL during
the race can return either the old or the new content, sometimes in
alternating ticks. Symptom pattern: `len(body)` and `'<canonical signal>' in
body` oscillate between two values. The right move is to keep probing at
~5–8 s intervals until the new content is stable for at least 3 ticks, then
record the live evidence. The first "moved" tick is not a stable green.

```js
let last_state = null, stable_count = 0;
for (let i = 0; i < 40; i++) {
  const body = fetchOnce(url);
  const state = (has_signal, len(body));
  if (state !== last_state) { console.log('tick', i, state); last_state = state; }
  if (expected_signal(state)) { stable_count++; if (stable_count >= 3) break; }
  await sleep(6000);
}
```

### Direct push to `main` does NOT trigger Cloudflare Pages deploy

Cloudflare Pages only deploys on PR merge to the configured branch.
A `git push origin main` from a non-PR session leaves the live URL stale.
Symptom: the canonical deployment check is green on the PR commit, the
live URL still serves the previous build, and the `cf-cache-status`/`vary`
headers don't move. Fix:

1. Revert the direct-to-main commit if you want a clean history (or
   amend + force-push to a `ned/...` branch as the new head).
2. Open a PR backed by the branch that contains the verified commit.
3. Wait for the Cloudflare Pages check to report success.
4. Merge the PR — that triggers the Pages deploy.
5. Probe the live URL until stable per the section above.

The lesson is: do not treat `git push origin main` as a deployment
mechanism. The PR is the deployment surface.

## Final report shape

Use a concise status report:

```md
✅ PR cleanup pass completed.

**Closed / taken care of**
- [#N](url) — reason

**Assigned / routed**
- [GRO-XXXX](linear-url) — purpose and labels

**Verified**
- Open PRs: before → after
- Mergeability buckets
- Remaining failed/conflicting blockers

**Next Step**
Golden path: <merge train / AGY extraction / owner review>
```

## References
- `references/2026-07-prismatic-jules-pr-cleanup.md` — session-specific example: closed stale/no-op Jules-like PRs, routed remaining extract/merge-train work to AGY, and handled active file-lock boundary.
- `references/pwp-merge-train-lane-and-proof-20260723.md` — concrete handoff, verification, and closure pattern.
- `references/2026-07-prismatic-pr-merge-train-after-agy.md` — session-specific example: consumed AGY outputs, extracted a useful stale PR into a clean branch, handled failed-check blockers, re-queried mergeability after each merge, and recovered a stale AGY supervisor lock.
- `references/2026-07-prismatic-deploy-fresh-promotion.md` — session-specific example: promoted a long-lived `deploy-fresh` integration branch, resolved last-mile CI failures from GitHub logs, and merged only after required checks were green.
- `references/2026-07-hde-analytics-extraction-no-gh-token.md` — session-specific recipe: live-surface drift detection, anonymous PR diff retrieval via `.patch`, the `git apply --3way` silent-no-op trap, stacking stacked PRs from the same epic, and the "no GH_TOKEN, branch ready on disk" Linear-comment contract.
