# 2026-08-04 Ned branch triage — worked example

Companion to `references/2026-07-31-ned-branch-discovery.md`. That reference captured the discovery phase (2,060 refs across 32 repos, 86% closed); this one captures the umbrella-pattern dispatch end-to-end and the investigation methodology that turned the discovery into a per-branch triage.

## Trigger

User asked "What do we do with all the 'Ned' branches and work trees? Make a plan... How do we find out if we even want these Ned branches?"

User asked "I don't need to approve each and every step. Newer stuff takes priority over old stuff unless there is evidence to back up the old. Let's start with linear linkage. Let's go single-threaded and be careful."

User asked "Make a linear task series for Ned to follow so that it's all ready to be worked on and we can start and stop if we need to or if you get interrupted."

The last clause — *start and stop if we need to* — is the explicit trigger for the umbrella + blocking-chain pattern (see `linear-bulk-project-setup`). A plain epic-and-children layout doesn't guarantee resume safety; only a chain with a manifest-as-source-of-truth does.

## What ran

The 9-step plan (1 umbrella + 8 children):

```
GRO-4462  [umbrella]  Triage & merge all Ned branches across 32 repos
GRO-4463  [step 1]    Enumerate ned/* branches + worktrees across 32 repos
GRO-4464  [step 2]    Pull per-branch metadata: Linear linkage, diff size, issue state
GRO-4465  [step 3]    Filter: drop no-linkage + no-work branches
GRO-4466  [step 4]    Sort survivors newest-first, apply promotion rule
GRO-4467  [step 5]    Write final triage manifest with merge order
GRO-4468  [step 6]    Process top branch: rebase, open PR, record URL
GRO-4469  [step 7]    After each merge, re-run breakage check on remaining queue
GRO-4470  [step 8]    Worktree cleanup: remove merged/dropped worktrees, document kept ones
```

7 chain relations (4463 blocks 4464 ... 4469 blocks 4470) + 8 umbrella-blockers (each child blocks 4462) = 15 relations total. See `linear-bulk-project-setup/references/2026-08-ned-branch-triage-linear-setup.md` for the auth gotchas and the mistake-and-fix on `blocks` direction.

## Scope correction (caught on day 1)

The system-reminder handoff at session start said "5 repos". The on-disk `state/current.json` and the live filesystem (`reports/discovery/ned-branches-2026-07-31/` with 2,060 refs across 32 repos) both disagreed — actual scope was **32 repos under `/home/ubuntu/work`**, with the 5-repo prismatic-engine family as a subset. Both the umbrella description and GRO-4463's description were created with "5 repos" before the staleness was detected. Fixed in-flight with one `issueUpdate` rewriting the description + a posted comment. This is the case study behind `linear-bulk-project-setup`'s "scope-correction must propagate to Linear" pitfall.

## Investigation methodology (steps 1+2)

The actual triage ran in two distinct phases:

### Step 1 — Enumerate

A single read-only Python script (`state/triage/enumerate_ned_branches.py`) walked `/home/ubuntu/work` with `os.walk`, found 125 git repos, and emitted one JSON record per `ned/*` ref (2,060 total). For each record it captured: branch name, full ref, source (local/remote), tip SHA, committer date, author, worktree path (if any), and ahead/behind vs `origin/main` (or `main` if origin/main missing).

**Verification:** the 2,060 count exactly matched the prior 2026-07-31 packet's totals (326 active + 1,398 closed-task refs). The 32-repo count matched. Zero discrepancies — the prior packet was accurate.

### Step 2 — Categorize

A two-pass script (`investigate_uncategorized.py` + `investigate_round2.py`) walked each record's category from the prior packet and re-categorized the 336 uncategorized ones:

1. **Branch-name regex**: `GRO-([0-9a-fA-F]{2,})` on the branch name.
2. **Commit-message regex**: `git log -n 30 --format=%H %s <ref>` on every ref whose name didn't match — both local and remote.
3. **Linear API lookup** for any GRO ID not already in the George/deletion caches: `query($teamId: ID!, $number: Float!) { issues(filter: { team: { id: { eq: $teamId } }, number: { eq: $number } }) ... }`. The `number: Float!` type accepts both numeric (2232) and hex (`72BC51` → 7,521,489 as decimal) forms.

Final categorization across all 2,060 refs:

| Category | Count | Resolution source |
|---|---|---|
| `george_active` | 452 | 326 from prior packet + 126 from branch-name/commit-message scan |
| `deletion_candidate` | 1,523 | 1,398 from prior packet + 48 from branch-name/commit-message scan + 77 from "Done - Doc Pending" state via Linear API |
| `review_needed` | 81 | 60 active Linear tasks outside George packet scope + 21 "Done - Doc Pending" not in prior packet |
| `uncategorized_no_linkage` | 4 | No GRO ID found anywhere (hde-staging-price-copy, initial-website) — needs diff inspection in step 3 |

## Bugs caught (and how)

### Bug 1 — Round 1 only scanned commits on local refs

```python
# BUGGY — skip this pattern
if r['source'] == 'local':
    log_text = git_log_text(repo_path, branch, n=30)
    commit_gros = extract_gro_ids(log_text)
```

Result: missed 125 linkages on `origin/ned/X` remote-tracking refs whose local counterpart doesn't exist. Round 2 removed the `source == 'local'` guard and recovered them all. The fix is one line; the cost of not noticing was 125 refs sitting in the "uncategorized" bucket until manual review.

### Bug 2 — Round 1 regex only matched numeric IDs

```python
# BUGGY — drops hex IDs
GRO_PATTERN = re.compile(r"GRO-?\d+", re.IGNORECASE)

# CORRECT — handles both
GRO_PATTERN = re.compile(r"GRO-([0-9a-fA-F]{2,})", re.IGNORECASE)
```

Result: `GRO-72BC51` was matched as `GRO-72` (truncated), the Linear API lookup failed because `72` ≠ `72BC51` (or 7,521,489 as decimal), and the 7 refs across 5 repos pointing at this ID went to the "uncategorized" bucket. The fix matched both forms; the bug was caught because the deletion_manifest was missing the entry and the verification step noticed.

### Bug 3 — Linear API error-handling asymmetry in `execute_code`

`urllib.request.urlopen` raises `urllib.error.HTTPError` on 4xx, but returns a successful response on 200. Mixing the two in the same function call requires either:

```python
# Tuple return — recommended for execute_code sandbox (no requests library)
def gql_raw(query, variables=None):
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())
```

The first attempt did `result = json.loads(r.read())` and crashed with `TypeError: tuple indices must be integers or slices, not str` when HTTPError fired — the wrapped body is a dict, not the original `result` shape. Always return `(status, body)` from GQL helpers and check `status != 200` explicitly.

### Bug 4 — `blocks` direction in Linear GraphQL was inverted on the first attempt

When creating `issueRelationCreate` with `type: "blocks"`, `issueId` is the **blocker** and `relatedIssueId` is the **blocked** — opposite of what the field names suggest. First pass created 15 relations in the inverted direction (4464 was blocking 4463, not vice versa). Detected by querying both endpoints' `relations` and `inverseRelations` fields; fixed by deleting all 15 and recreating with `issueId = later` (the one that must wait) and `relatedIssueId = earlier` (the blocker). Verification recipe: `relations { nodes { type relatedIssue { identifier } } }` on both endpoints must show the same edge label but in opposite directions.

## New active Linear tasks discovered (60, outside George packet scope)

The George packet was scoped to the 5-repo prismatic-engine family. The wider scan of all 32 repos found **60 additional active Linear tasks (118 branches)** in repos the packet didn't cover:

| Repo | New active GRO IDs | Examples |
|---|---|---|
| `hd-platform` | 18 | GRO-3988, 3992, 3995, 3998, 4000, 4003, 4004, 4009, 4010, 4012, 4013 (HDE GREEN campaign) |
| `mbgulden/prismatic-web-publisher` | 5 | GRO-4162, 4170, 4171, 4174, 4176 (PWP Extraction Phase 3-4) |
| `growthwebdev-knowledge` | 4 | GRO-2251, 2278, 2828, 2863 |
| `belief-deprogrammer` | 2 | GRO-501, 562 |
| `beyondsaas-site` | 1 | GRO-539 |
| `prismatic-engine` | 1 | GRO-4208 (`pwp-publish-kpi-tracker`) |
| `prismatic-web-plugin` | 1 | GRO-2191 |
| `agentic-swarm-ops` | 1 | GRO-3542 |
| `active-oahu-tours` | 1 | GRO-2232 (`content-schedule`) |

**Lesson: a scoped inventory is a triage decision, not an inventory decision.** Always run the wide scan first; scope filtering is what step 3 (filter) does. If you only scan the repos named in the prior packet, you miss real work that's actively shipping.

## Edge cases flagged for step 3 (filter)

These need diff inspection or human review to decide keep vs drop:

| Case | Refs | Triage hint |
|---|---|---|
| `GRO-72BC51` (doesn't exist in Linear) | 7 across 5 repos | Strong DROP — branch references a non-existent issue |
| `hde-staging-price-copy-20260718` (no Linear link, dated hotfix) | 2 | REVIEW — check diff to decide |
| `initial-website` (sentinelitad.com, fresh by Fred, 2026-07-28) | 2 | REVIEW — possibly new feature work |
| `Done - Doc Pending` state refs (GRO-545 in 3 repos) | 21 | DROP — effectively closed; documentation phase, not code |

## Verification recipe (steps 1+2 specific)

The end-of-step-2 verification must include these checks:

```bash
# 1. Total record count matches the prior packet
python3 -c "import json; d=json.load(open('state/triage/raw-branches.json')); assert len(d['records']) == 2060, len(d['records'])"

# 2. Sum of categories equals total
python3 -c "
import json
from collections import Counter
d = json.load(open('state/triage/raw-branches.json'))
cats = Counter(r.get('category') for r in d['records'])
assert sum(cats.values()) == 2060, cats
print(dict(cats))
"

# 3. Every george/deletion record is still categorized the same way (no regression)
python3 -c "
import json
raw = json.load(open('state/triage/raw-branches.json'))
george = json.load(open('/home/ubuntu/.hermes/profiles/ned/reports/discovery/ned-branches-2026-07-31/george_merge_packet.json'))
george_keys = {(r['repo'], r['branch']) for r in george['in_review'] + george['in_progress'] + george['todo'] + george['backlog']}
raw_cats = {(r['repo'], r['branch']): r.get('category') for r in raw['records']}
mismatches = [(k, raw_cats[k]) for k in george_keys if raw_cats.get(k) != 'george_active']
assert not mismatches, f'George packet categories regressed: {mismatches[:5]}'
"

# 4. Every review_needed record has a linkage_resolved_via field (proves it went through the API, not just labeled)
python3 -c "
import json
d = json.load(open('state/triage/raw-branches.json'))
needs_review = [r for r in d['records'] if r.get('category') == 'review_needed']
unresolved = [r for r in needs_review if not r.get('linkage_resolved_via')]
assert not unresolved, f'{len(unresolved)} review_needed records lack linkage resolution: {unresolved[:3]}'
"
```

All four checks passed at end of step 2 in the 2026-08-04 session.

## Step 3 outcomes (filter)

Verdict distribution across the **2,263 refs** (note: 203 more than the 2,060 at end of step 2 — see coverage gap below):

| Verdict | Count | Meaning |
|---|---|---|
| `george_active` (MERGE_QUEUE) | 499 | Active Linear task in George packet |
| `review_needed` (active state) | ~58 | Active Linear task not in George packet → MERGE_QUEUE_LOW |
| `review_needed` (Todo/Backlog) | ~25 | Work not started → REVIEW_HUMAN |
| `uncategorized_no_linkage` (ORPHAN_HOTFIX) | 4 | Real diffs but no Linear ticket |
| `deletion_candidate` (DORMANT) | 1,677 | Closed Linear task; do not merge; do not auto-delete |

### Coverage gap caught at step 3 (cross-step scope re-verification)

`prismatic-engine-stable` (203 ned/* refs) was **missed in step 1's scan** — it didn't have any ned/* refs at step-1 time but acquired them before step 3 ran. A re-scan added them; categorization found 43 active + 148 deletion candidates + 12 misc. The point: **a one-shot scan at step 1 is not a sufficient scope guarantee for downstream steps.** At each step boundary, re-verify scope by walking the repo set again and diffing against the prior step's manifest. If the diff is non-empty, classify and merge before proceeding.

```python
# Cross-step coverage check (run before any verdict step)
import os, subprocess
WORK = '/home/ubuntu/work'
found_repos = set()
for d in os.listdir(WORK):
    p = f'{WORK}/{d}'
    if os.path.isdir(p + '/.git'):
        found_repos.add(p)
# Plus nested: research/, mbgulden/, reference-repos/, etc. — use os.walk with depth<=3
# Compare found_repos to raw['absolute_repo_path'] set
uncovered = found_repos - {r['absolute_repo_path'] for r in raw['records']}
if uncovered:
    # Re-scan and merge before proceeding with the verdict
    ...
```

### Verdict rationale resolution

The original plan wording ("drop if all three: no Linear linkage, no unmerged commits, empty/cosmetic diff") conflicted with the practical case where branches link to *closed* Linear tasks. The intent ("drop what's stale") was kept by clarifying the rule charitably: "closed Linear linkage ≡ no linkage for branch-keeps-alive purposes" → 1,677 refs with closed tasks route to DORMANT (not auto-merge, not auto-delete). This interpretation was written into the manifest at `STEP-3-SUMMARY.md` so the rule is reproducible. The user-facing decision: leave DORMANT branches untouched pending a separate deletion-policy approval.

### Edge cases confirmed in step 3

- `GRO-72BC51` doesn't exist in Linear (queried with `number: Float!`, both numeric and hex interpretations). 5 refs across 3 repos; recommend verify-before-drop.
- `GRO-545` is `Done - Doc Pending` (state_type `started`, name prefix `Done`). 8 refs across 3 repos. Round 2's commit-message scan + Linear API confirmed the state; these route to DORMANT, not MERGE_QUEUE.
- The 4 orphan hotfixes (`hde-staging-price-copy-20260718`, `initial-website`) have real diffs (30 files, 926 insertions on the hd-platform one) but no Linear ticket; commit messages say `#NOISSUE`. Flagged as ORPHAN_HOTFIX pending user decision (create retro ticket or drop).

### Linear "blocks" direction gotcha (full transcript)

The first `issueRelationCreate` call used `issueId = later, relatedIssueId = earlier, type = "blocks"`, intending "earlier blocks later". But GraphQL semantics are: with `type: "blocks"`, **`issueId` is the blocker and `relatedIssueId` is the blocked-by** — opposite of what the field names suggest. Verification recipe: query both endpoints' `relations` and `inverseRelations` fields; the same edge label must appear in opposite directions on each side.

First-attempt relation creation produced this wrong-direction graph:
- GRO-4463 `relations`: blocks GRO-4464, GRO-4462 → looks correct on this side
- GRO-4464 `blocked-by` (inverseRelations): GRO-4463 → confirms the wrong direction (4463 was *waiting* for 4464 to finish, not vice versa)

Fix: delete all 15 wrong-direction relations, recreate with `issueId = later, relatedIssueId = earlier` to get the correct semantics. Verified by re-querying and confirming each earlier-child blocks the next later-child and each child blocks the umbrella.

## Total cost so far

- 2 read-only Python scripts (enumerate + investigate, both idempotent)
- 1 Linear task create (umbrella) + 8 children + 15 relations
- 1 Linear update + 1 comment per child (state transitions + summary)
- 9 Linear API calls for state verification
- ~30 Linear API calls for GRO ID lookups during step 2
- Total: ~70 API calls, ~5 minutes elapsed across 2 substantive turns