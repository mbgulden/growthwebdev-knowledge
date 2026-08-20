---
name: cross-repo-branch-linear-reconciliation
description: >-
  Use when you have many local-or-remote agent-name-prefixed branches across
  many git repos and need to figure out which ones are stale leftovers from
  already-closed Linear tasks, which are live work, and which are duplicates.
  Pattern: scan repos for refs by name prefix; batch tip-dedup to detect close
  duplicates; sample Linear task-state lookup for matched GRO-XXXX identifiers;
  and produce a per-repo classification report. Trigger when a single profile has
  more than 100 agent-prefix branches across more than 10 repos, or when the user
  asks 'did this work land somewhere', 'are these branches stale', or 'reconcile
  the X branches'.
---

# Cross-Repo Branch vs. Linear Reconciliation

## When to use

A single agent profile (ned, fred, kai, george, etc.) has accumulated many `agent:*` branches across many git repos. The user wants to know:

- Which branches are stale leftovers from already-closed Linear tasks?
- Which branches are live work (the matching Linear task is open)?
- Which branches are close duplicates of each other (same tip SHA)?
- Which repos have so many dead refs they should be archived?

The 2026-07-31 case study: 2,060 `ned/*` refs across 32 repos under `/home/ubuntu/work`. 0 tip-dedup groups. 86% of sampled GRO-XXXX identifiers mapped to closed Linear tasks (69/80 = Done, 3/80 = Canceled). The remaining 11% were live work (In Progress / In Review).

## When NOT to use

- Single repo, manageable branch count (under 50). Just look at `git branch --merged main` and `git branch --no-merged main`.
- The user wants to delete branches. Capture the manifest first per `branch-deletion-approval`; this skill is for the inventory phase.
- The user wants to triage stacked PRs. That's `github-pr-backlog-hygiene` or `prismatic-pr-batch-cleanup`. This skill is for branches without a corresponding PR (typical of agent-local branches that never opened a PR or whose PR was already merged).

## Required output

A non-destructive inventory containing:

1. **Per-repo branch count by status** (merged-into-main / unmerged / active). Use **strict-ancestor** semantics: `git merge-base --is-ancestor <ref> <main>` returns true iff the branch tip is reachable from main. Do not conflate "branch is merged" with "branch is in the merged-set list" — a remote-tracking branch whose corresponding local branch was merged is NOT itself merged.
2. **Tip-dedup groups** — branches sharing the same tip SHA. If two `agent:*` branches have the same tip, they are dupes; one can be deleted. Tip-dedup detects "same work on N branches" which is the easiest cleanup.
3. **Linear task-state correlation** — for branches whose name contains a `GRO-XXXX` (or `gro-XXXX`), look up the task state in Linear. Branches mapping to `Done`/`Canceled` are stale; branches mapping to `In Progress`/`In Review` are live; branches mapping to `Backlog` are likely stale too (the work hasn't even started). **Bulk-fetch all closed tasks in one paginated `issues(filter: { state: { name: { in: ["Done", "Canceled"] } } })` pull** rather than per-ID — the 2026-07-31 case study pulled 3,138 closed tasks in 31 GraphQL pages (one Linear API call per page, NOT 3,138 calls). Use this to build a local closed-ID cache, then look up against it.
4. **Per-repo classification** based on the above: how much of each repo's branch volume is mergeable, how much is archive-tier, how much is live.
5. **Suggested bounded moves** — A/B/C-style cleanup proposals, with risk estimates. **Do not execute deletion.** The `branch-deletion-approval` rule requires an explicit Michael sign-off plus a manifest before any deletion.

### 5b. CHOOSE THE RIGHT `main` PER REPO

Forks and clones frequently have a **stale local `main`** that does not match `origin/main`. The prismatic-engine repo at `/home/ubuntu/work/prismatic-engine` had local `main` at 7 commits while `origin/main` was at 87 commits — every `ahead/behind` was computed against a stale target until the catch. The 2026-07-31 failure mode: a branch "7 commits ahead of main, 250 behind" was actually a much healthier branch than the report's "ahead of main" implied, because main itself was 80 commits behind reality.

**Before computing ahead/behind or diff stats, sanity-check the target ref:**

```python
# Is local main stale relative to origin/main?
rc, out, _ = git(["rev-list", "--count", "main..origin/main"], cwd=repo)
if rc == 0:
    local_main_behind = int(out.strip() or 0)
    target = "origin/main" if local_main_behind > 50 else "main"
```

Report the chosen target per repo in the packet so the consumer (George, another agent) knows what they're diffing against. If local main is unreachable, fall back to `main` (only if it exists) and flag the repo as "main unknown — cross-check required".

### 5c. HAND-OFF PACKET FOR ANOTHER AGENT (the George-pattern)

After the inventory, if the user wants another agent (e.g. George) to execute the merge or cleanup work, **build a hand-off packet** rather than just dumping the report. The packet is a separately consumable shape distinct from the inventory:

- **Dedup by Linear ID.** Multiple branches under different repos can map to the same GRO-XXXX. Pick a canonical primary branch (preference: `prismatic-engine` if present, else the local branch, else the first remote-tracking ref) and list the others as "also in: `repo:branch`" rows.
- **Sort by Linear state, then priority, then last-commit date.** State order: In Review → In Progress → Todo → Backlog. Within a state, URG/HIGH first, then oldest commit first (oldest work most likely to be abandoned).
- **One table per state**, with columns: priority, Linear ID, title, repo, branch, last commit, behind, diff stat.
- **A short markdown README** at the top of the packet that lists every file, the TL;DR, and the suggested next steps for the recipient. The 2026-07-31 packet's `GEORGE_README.md` was 3.7 KB and listed `GEORGE_PACKET.md`, `george_merge_packet.json`, `george_worktrees.sh`, and the deletion manifest as "do not uncomment without approval" — that file alone dropped George's onboarding time from ~30 min to ~5 min.
- **A worktree-prep script** (see `worktree-hygiene-and-cleanup-safety` for cleanup-side guidance). The hand-off packet should ship a script that creates the worktrees the recipient will need, not just a list of branches. The 2026-07-31 `george_worktrees.sh` created 10 worktrees (`/tmp/george-merge-<GRO-XXXX>`) on `origin/main` based on the priority-sorted list, with the remaining branches listed for manual creation. The script is read-only by default (no destructive commands); the recipient runs it.
- **Do NOT execute the worktrees yourself.** Production worktree creation is on the recipient's side per `outbound-action-gate`. Build the script, document the script, hand it off.

## Workflow

### 1. Discover repos

```python
import os
for dirpath, dirnames, filenames in os.walk(root):
    depth = dirpath[len(root):].count(os.sep)
    if depth > max_depth:
        dirnames[:] = []
        continue
    if ".git" in dirnames:
        repos.append(dirpath)
        # IMPORTANT: check for .git BEFORE filtering .git out of dirnames
        dirnames[:] = [d for d in dirnames if d != ".git"]
    dirnames[:] = [d for d in dirnames if d not in {".venv", "node_modules", ...}]
```

**Pitfall**: the order matters. If you filter `.git` out of `dirnames` BEFORE checking `if ".git" in dirnames`, the check always fails and you find 0 repos. This was a real bug in the 2026-07-31 first cut.

### 2. Find `agent:*` branches (local + remote)

```python
# Local: refs/heads/<agent-prefix>/
# Remote: refs/remotes/*/<agent-prefix>/
branches = []
for ref_type in ("refs/heads/", "refs/remotes/"):
    rc, out, _ = git(["for-each-ref", "--format=%(refname)", ref_type], cwd=repo)
    if rc == 0:
        for line in out.strip().split("\n"):
            display = line.replace(ref_type, "")
            if display.startswith(f"{agent_prefix}/") or f"/{agent_prefix}/" in display:
                branches.append((display, line))
```

For each branch, batch-collect the tip SHA via `git rev-parse --verify <refs...>`. Do not run `git rev-parse` per branch — for 2,000 branches that's 4,000 subprocess invocations.

### 3. Compute merged-into-main (strict-ancestor)

**Local branches**: `git branch --merged <main> --format=%(refname:short)` returns a single list. Intersect with your local branch set.

**Remote branches**: `git branch` does not show remote refs. Use `git merge-base --is-ancestor <remote_ref> <main>` per branch, or batch with `git for-each-ref --format='%(refname) %(objectname)' refs/remotes/` followed by `git merge-base --is-ancestor <ref> <main>` in a loop.

**Pitfall**: do not conflate "this local branch was merged" with "this remote-tracking branch's tip is reachable from main." A remote-tracking branch's tip is the SHA of the remote's tip, not the local branch's tip. If the local branch was fast-forwarded into main but the remote was not updated, the remote-tracking branch points to a now-historical SHA.

This is the bug that hit the 2026-07-31 first cut: it reported 394 "merged" branches when the strict-ancestor count was 115. The first count was thinking "merged-by-name" and the second was "merged-by-SHA".

### 4. Tip-dedup

Group branches by tip SHA. If any group has more than 1 branch, the duplicates are easy cleanup candidates:

```python
from collections import defaultdict
tips = defaultdict(list)
for display, ref in branches:
    sha = sha_map.get(ref)
    if sha:
        tips[sha].append(display)
dup_groups = {sha: names for sha, names in tips.items() if len(names) > 1}
```

**Caveat**: tip-dedup only catches exact duplicates. Branches that were rebased or have one extra commit on top will have different tips. The 2026-07-31 case showed 0 tip-dedup groups across 2,060 refs — every branch had a unique tip. The dedup was real but at the *commit-level-containment* level, not the tip level. Doing commit-level containment is O(n squared) and was deferred to a later pass.

### 5. Linear task-state correlation

For each branch whose name contains a `GRO-XXXX` (or `gro-XXXX`), look up the Linear task state. Use the `linear-api-operations` skill's `title: { contains: ... }` filter pattern, or per-ID `issue(id: "<GRO-XXXX>")` for a known set.

**GRO-XXXX identifiers are EITHER numeric (`GRO-2232`) OR hex (`GRO-72BC51`).** Linear allocates IDs from a numeric sequence, but the API also exposes short hex identifiers for some legacy/snapshot issues. The 2026-08-04 triage found `GRO-72BC51` referenced by 7 branches across 5 repos — the standard `\d+` regex silently dropped it, and Linear API said the ID "doesn't exist" when queried as numeric. It did exist, as a hex ID. **Always use a regex that accepts both forms:**

```python
import re
# Matches GRO-2232 (numeric) and GRO-72BC51 (hex), case-insensitive, normalizes to upper.
GRO_PATTERN = re.compile(r"GRO-([0-9a-fA-F]{2,})", re.IGNORECASE)
def extract_linear_ids(text):
    """Find all GRO-XXXX-style IDs (numeric or hex) anywhere in text."""
    return {f"GRO-{m.group(1).upper()}" for m in GRO_PATTERN.finditer(text)}
```

The older regex `\b([Gg][Rr][Oo])-?(\d+)` silently dropped hex IDs — branches like `ned/GRO-72bc51` would be misclassified as "no Linear link" and routed to the drop queue. That's a real failure mode caught only at the verification step in the 2026-08-04 case study.

For the Linear API lookup itself, accept either numeric or hex as the `number` argument:

```python
suffix = linear_id.replace("GRO-", "")
try:
    n = int(suffix)            # numeric: GRO-2232 → 2232
except ValueError:
    n = int(suffix, 16)        # hex: GRO-72BC51 → 7,521,489 (interpreted as decimal)

# GraphQL filter shape (variable types matter):
# query($teamId: ID!, $number: Float!) {
#   issues(filter: { team: { id: { eq: $teamId } }, number: { eq: $number } }) { nodes { ... } }
# }
# `teamId` MUST be `ID!`, `number` MUST be `Float!` — see linear-api-operations pitfall.
```

**If your branch-name scan only catches the IDs that match the standard `GRO-\d+` shape, you'll systematically mis-bucket all hex IDs as "unlinked" and they will sit in the noise queue.** Always include the hex form in your regex from the start.

**5a. Two-pass linkage: branch name THEN commit messages.** A branch whose name has no `GRO-XXXX` may still have one in its commit messages. The 2026-08-04 triage first pass did branch-name only and left 190 of 336 uncategorized refs unresolved. Running `git log -n 30 --format=%H %s <ref>` and scanning the output with the same regex recovered linkages on **125 of those 190** — including all the duplicate-ref cases like `origin/ned/GRO-72bc51` where the branch name had no GRO but the commits did. Don't stop at branch names.

**5b. Remote refs MUST be commit-scanned too — local-only scanning misses them.** This is the single most common first-pass bug. If your loop guards the commit-message scan with `if r['source'] == 'local':`, you'll skip every `origin/ned/X` remote-tracking ref, even though `git log <remote_ref>` works fine and returns the same commit history. The 2026-08-04 round 1 had exactly this bug and missed 125 linkages on the first pass. Round 2 removed the `source == 'local'` guard and the recovered count jumped from 146 to 269.

**5c. "Done - Doc Pending" and similar soft-closed states count as closed for triage.** Linear's workflow may include states like `Done - Doc Pending` (state_type `started`, state.name "Done - Doc Pending") that are effectively closed for code-triage purposes — the work landed; only the docs are pending. The original deletion-manifest filter (`state: { name: { in: ["Done", "Canceled"] } }`) misses these. The 2026-08-04 triage found 21 refs across 3 repos in this state (all GRO-545 — Social Proof / Testimonials), which the George packet treated as "active" because the Linear API didn't return them as Done. Treat any state whose name starts with `Done` (or whose description mentions "doc pending", "ready for review", or similar finalization language) as effectively closed. Verify by reading the state's `description` field; don't just match on `name`.

**5d. Bulk-fetch all closed tasks in one paginated pull, not per-ID queries.** The 2026-07-31 first pass did 80 individual `issue(id: "...")` queries and ran out of rate budget; the bulk-fetch pulled 3,138 closed tasks in 31 GraphQL pages (one network round-trip per page). Use the local cache for classification; reserve per-ID queries for the "active or unknown" set — and even there, batch them with `number: { in: [...] }` rather than `issue(id:)` in a loop.

```python
# Cap sample to avoid blowing API rate limits
sample_ids = sorted(all_linear_ids)[:LINEAR_SAMPLE]
for lid in sample_ids:
    r = linear_query('{ issue(id: "%s") { identifier state { name } } }' % lid)
    # bucket by state.name
```

In the 2026-07-31 sample of 80 unmerged branch IDs: 69 Done, 7 In Progress, 1 In Review, 3 Canceled. **86% of the work landed on another branch.** This is the answer to "did this work land somewhere?".

### 6. Report

Markdown write-up with:

- Headline numbers (total, repo count, merged count, tip-dedup count, sample size, correlation table).
- Per-repo breakdown table (top 10 to 15 by branch count).
- Linear state-bucket table with examples.
- Three or more **bounded moves** (lowest-risk highest-volume first).
- A process-change recommendation (e.g. prune `agent:*` branches on Linear task closure).

Do not write the report into the repo's `docs/` unless the user confirms; use `~/.hermes/profiles/<profile>/reports/discovery/<topic>-<date>/` to keep it self-contained and untracked.

## From inventory to action (the umbrella-pattern dispatch)

The inventory this skill produces is non-destructive by design. When the user wants to **act** on the inventory — open PRs, merge branches, clean up worktrees — the action phase gets its own Linear workstream, not ad-hoc commits. The canonical shape is:

1. **Inventory first** (this skill) — produces a per-repo classification report.
2. **Linear workstream second** — `linear-bulk-project-setup`'s blocking-chain + umbrella pattern: 1 umbrella issue + N children in execution order, with all children blocking the umbrella. The manifest from this skill's report feeds the children; the umbrella represents "the action phase is closed."
3. **Source of truth during action** — a repo-local manifest at `state/triage/<topic>.md`, NOT Linear. Linear holds dispatch state; the manifest holds work state. On resume, the manifest is read first; Linear is reconciled to match.

The 2026-08-04 Ned branch triage workstream was the first end-to-end use of this combined pattern. See `linear-bulk-project-setup/references/2026-08-ned-branch-triage-linear-setup.md` for the full transcript (auth gotchas, the `blocks` direction mistake, the verification recipe).

## Pitfalls

- **Do not conflate "branch is merged" with "tip is reachable from main"** — these are different. The 2026-07-31 first cut overstated merged count by 3x because of this.
- **Do not filter `.git` out of `dirnames` before checking.** Check first, then filter. Every Python `os.walk` needs this order to find `.git` directories.
- **Do not execute deletions.** The `branch-deletion-approval` skill requires Michael's explicit sign-off plus a manifest. This skill is for the inventory phase only.
- **Do not O(n squared) the containment check.** `git branch --contains <sha>` per branch is O(n squared) when run per-branch. For 2,000 branches that's hours. Use tip-dedup (cheap) plus Linear correlation (bounded) instead. Commit-level containment is a separate pass.
- **Do not use mental estimates for counts in the report.** If the report says "394 merged", the reader trusts it. Run the verification command and quote the result; the 2026-07-31 session showed how a miscount (from one flawed interpretation) can flow into a Linear comment, an OKF doc, and a state file before anyone re-counts. See `references/2026-07-31-ned-branch-discovery.md` for the full case study.
- **Do not open the inventory as a Linear task before the user asks.** The user might want to skim the report first and decide the scope. Wait for "file this as a task" before opening anything.
- **Do not use bearer tokens or Linear API keys in the verifier file body.** The discovery script runs in `/tmp/` and stays around. Use env vars (`os.environ["LINEAR_API_KEY"]`).
- **Do not assume local `main` is the merge target.** Forks and stale clones can have local `main` 80+ commits behind `origin/main`. Compute `git rev-list --count main..origin/main` first; pick the more recent target. Report the chosen target per repo in the packet. The 2026-07-31 prismatic-engine `ahead=7, behind=104` looked like a tiny branch ahead of a nearly-current main, but main was 80 commits behind origin/main so the actual story was different.
- **Do not per-ID-query Linear for closure status** — bulk-fetch all Done/Canceled tasks in one paginated `issues(filter: { state: { name: { in: ["Done", "Canceled"] } } })` pull. The 2026-07-31 first pass did 80 individual `issue(id: "...")` queries and ran out of rate budget; the bulk-fetch pulled 3,138 closed tasks in 31 GraphQL pages (one network round-trip per page). Use the local cache for classification; reserve per-ID queries for the "active or unknown" set.
- **Do not estimate what `merge-tree` will tell you on a fork.** On fork repos (prismatic-engine family, hd-platform, etc.), `git merge-tree main <branch>` fails with "refusing to merge unrelated histories" because the branch and main have unrelated commit graphs. Conflict checking must happen in a worktree against `origin/main` after a fresh fetch, not via merge-tree. The hand-off packet must include this caveat for the recipient.
- **Do not use a numeric-only GRO-XXXX regex.** Linear IDs can be numeric (`GRO-2232`) or hex (`GRO-72BC51`). A `\d+` regex silently drops hex IDs and routes them to the drop queue. Use `[0-9a-fA-F]{2,}` and accept both forms from the start. Verified via live API 2026-08-04 — 7 refs across 5 repos were mis-bucketed in the first pass because the regex missed the hex form.
- **Do not stop at branch-name GRO-ID extraction.** A branch named `ned/fix-pr203-conflict` (no GRO-ID) can have a commit message `[Ned] GRO-1620: ship-time plugin load verification gate (#GRO-1620)` that resolves the linkage. Two-pass scanning (branch name → commit messages) recovered 125 of 190 unresolved refs in the 2026-08-04 case study. Skip the commit-message pass and you'll mark real work as droppable.
- **Do not gate the commit-message scan on `source == 'local'`.** Remote-tracking refs (`origin/ned/X`) also have commit history accessible via `git log <ref>`, and they're the most common form for refs created on a different machine and never checked out locally. The 2026-08-04 round 1 had exactly this bug and missed 125 linkages on the first pass. Drop the source filter; `git log` handles both local and remote refs transparently.
- **Do not treat "Done - Doc Pending" as active.** Custom Linear workflow states whose name starts with `Done` (e.g., `Done - Doc Pending`, `Done - Awaiting Review`) are state_type `started` but effectively closed for code triage. The original `state.name in [Done, Canceled]` filter misses these. Treat any state whose name starts with `Done` as closed; verify via the state's `description` field if uncertain. The 2026-08-04 triage found 21 refs in this state (all GRO-545 — Social Proof / Testimonials).
- **Do not scope a triage pass so tightly that you miss out-of-scope-but-active work.** The 2026-08-04 George packet was scoped to the 5-repo prismatic-engine family and found 326 active branches across 82 Linear tasks. A wider scan of all 32 repos found **60 additional active Linear tasks** (118 branches) in repos the packet didn't cover — hd-platform (HDE GREEN campaign), mbgulden/prismatic-web-publisher (PWP Extraction Phase 3-4), growthwebdev-knowledge, belief-deprogrammer, beyondsaas-site, prismatic-engine, prismatic-web-plugin, agentic-swarm-ops, active-oahu-tours. If you only scan the repos named in the prior packet, you miss this. Always run the wide scan first; scope filtering is a triage decision, not an inventory decision.

## Support files

- `references/2026-07-31-ned-branch-discovery.md` — the worked example that motivated this skill: 2,060 ned/* refs across 32 repos, 86% of sampled GRO-XXXX identifiers mapping to closed Linear tasks, the verification iteration loop that corrected the off-by-one repo count and the tip-vs-merge confusion.
- `references/2026-08-04-ned-branch-triage.md` — the umbrella-pattern dispatch end-to-end: 9-issue Linear chain (1 umbrella + 8 children) with `state/triage/` as the manifest source-of-truth. Documents the two-pass investigation (branch-name + commit-message scan), the bug that local-only commit scanning misses remote refs, the hex-ID (`GRO-72BC51`) regex fix, the "Done - Doc Pending" soft-closed-state classification, and 60 newly-discovered active Linear tasks found outside the George packet's 5-repo scope.
- `scripts/sweep.py` — re-runnable inventory script. Copy to `/tmp/`, set `AGENT_PREFIX=ned`, `REPO_ROOTS=/home/ubuntu/work`, `LINEAR_SAMPLE=80`, and run. Produces a structured JSON to `/tmp/cross_repo_branch_inventory.json`. Does NOT delete branches.

## Related skills

- `multi-source-reconciliation-packet` — the broader class-level skill that handles "four sources of truth disagree". Use this when the disagreement extends beyond branches (PRs, Linear, dirty checkouts).
- `branch-deletion-approval` — required for the action phase after this skill produces the inventory.
- `worktree-hygiene-and-cleanup-safety` — for the worktree cleanup phase after the branch cleanup.
- `linear-api-operations` — for the Linear task-state lookup pattern.
- `ad-hoc-verification-contracts` — for the verification script that proves the report numbers match the live data.
- `session-state-handoff` — for the cold-start state file that should mention this report exists.
