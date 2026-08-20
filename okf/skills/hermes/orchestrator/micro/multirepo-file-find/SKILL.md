---
name: multirepo-file-find
description: Recipes for finding a file across many git repos, worktrees, and release snapshots when the obvious path is wrong. Use when a handoff, counter record, or planning message names a file that doesn't exist at the obvious location; the file probably lives in a sibling repo, on a different branch, or in a recovered release directory. Companion to handoff-claim-verification-recipe. Load when the file the agent needs is not in the current working tree.
category: micro
triggers:
  - handoff names a file that doesn't exist at the claimed path
  - agent needs to find a script shared across multiple sub-projects
  - search_files / find / grep returns empty for what should be a common file
  - user says "search branches, worktrees, and all over"
  - the obvious path is wrong and the agent is tempted to fabricate the file
---

# Multi-repo + Working-Tree File Find

## Core principle

When the obvious path is wrong, the file is not fake — the path is wrong. The
right move is a controlled sweep across the actual versioned trees, not
fabricating the file from the description.

The inverse case applies too: **when the file already exists but the import
fails**, the path is wrong — not the file. Before recreating a "missing"
module, locate the consumer's import path and verify it's pointing at the
real location. (Worked example: 2026-07-30 Move 8, where the planning
message said "prismatic.linear.budget module is missing (.pyc orphan)" but
the module existed at `/home/ubuntu/.prismatic/published/work/prismatic-engine/`;
the actual bug was `linear_helpers.py` doing
`sys.path.insert(0, "/home/ubuntu/work/prismatic-engine")` — a path that
didn't exist on this machine. The fix was a self-contained shim, not a
module rebuild.)

## The three-step recipe

### Step 1: enumerate git repos

```bash
find /home/ubuntu -maxdepth 5 -type d -name .git 2>/dev/null
```

Narrows the search class from "every Python file" to "every versioned tree."
A second filter narrows further:

```bash
find /home/ubuntu -maxdepth 5 -type d -name .git 2>/dev/null \
  | grep -vE "agy_sandboxes|GRO-[0-9]"
```

Excludes the many `~/.prismatic/releases/...` and `recovery/agy-*/agy_sandboxes/GRO-*/`
artifacts that share `.git` but are not the canonical source.

### Step 2: search by name (fast) and by content (slow)

```bash
# By name — fast, finds tracked files
git -C <repo> ls-files --others --cached --exclude-standard -z -- <name>

# By content (regex) — finds the file across all branches' history
git -C <repo> log --all --pretty=format: --name-only --diff-filter=A -- <path>
```

The `git log --all --diff-filter=A` recipe is the canonical answer for "was a
file with this name ever added to this repo, and on which branch?" Covers
files that were renamed or deleted.

### Step 3: search across all repos for the symbolic pattern

```python
import subprocess
for repo in candidate_repos:
    res = subprocess.run(
        ["git", "-C", repo, "log", "--all", "--pretty=format:",
         "--name-only", "--diff-filter=A", "--", filename],
        capture_output=True, text=True, timeout=15
    )
    if res.stdout.strip():
        # found it
        ...
```

Combined with the `find` from Step 1, this is the recipe that broke the
2026-07-30 dead-end.

## When NOT to use this

- The file is in the current working directory and `ls` would show it.
- The repo is a known canonical location and the user named it.
- The CLI tool (rg, fd) is already installed and configured for one tree.

## Anti-patterns

- **Don't conclude "the file doesn't exist" after one `os.walk` that times out.**
  Naive walks hit the 5-minute cap. Use `find` with a depth limit, then `git`
  per repo.
- **Don't trust the handoff's claimed path.** The handoff may have been
  written by a session with a different working directory, mount, or
  container snapshot. The file is real; the path may not be.
- **Don't skip the `git log --all` step.** A file committed on a feature branch
  but not on main is invisible to `git ls-files` and non-recursive searches.

## Pitfall

- **`os.walk` on `/home/ubuntu` may take 5+ minutes.** Time-bounded `find`
  with a depth cap is the right primary tool. If `find` times out, narrow
  the path further by filtering on directory name before recursing.

## Pitfall: `find` returning 0 results due to `Permission denied` (added 2026-08-04)

`find` does NOT print permission errors by default — it silently skips
directories it cannot read and returns **only the matches it did find**. If
a single restricted subtree in the search root contains all the matches
you expected, the command returns 0 results with no indication that the
search was effectively aborted.

Observed 2026-08-04 on hermes-webtop: `find /home/ubuntu/work/prismatic-engine-stable -name "test_agy_*.py"` returned 0 results. The tests **existed** at `tests/test_agy_task_auto_inject.py` and `tests/test_agy_pending_hold.py`. But a permission-denied subtree earlier in the walk (a sibling release dir owned by root) caused `find` to abort the recursion silently before reaching `tests/`.

**Recipe for safe multi-tree find:**

1. **Probe for permission-denied subtrees first.** `find /home/ubuntu -type d ! -readable 2>/dev/null` lists dirs that will silently break recursion. Use the list to construct explicit `-path` exclusions:
   ```bash
   find /home/ubuntu -type d ! -readable 2>/dev/null | head -20
   ```
2. **Run `find` with explicit `-not -path` exclusions** for each unreadable subtree:
   ```bash
   find /home/ubuntu/work \
     -not -path "*/deployments/gro4318-*" \
     -not -path "*/.git/*" \
     -name "test_agy_*.py"
   ```
3. **Verify the search actually completed** by checking the exit code. `find` exits non-zero if it hit any error including `Permission denied`:
   ```bash
   find /path -name foo.py; echo "find exit=$?"
   ```
   Exit 0 = clean. Exit 1 = some entries were skipped (often permissions). Trust the 0-result answer only when exit=0.
4. **As a fallback, use `os.walk` with explicit `PermissionError` handling.** This is slower but cannot silently abort:
   ```python
   import os
   from pathlib import Path
   hits = []
   for root, dirs, files in os.walk(start):
       if 'deployments/gro4318' in root: continue  # known-bad subtree
       for f in files:
           if f.startswith('test_agy_') and f.endswith('.py'):
               hits.append(Path(root) / f)
   ```
   The `if 'deployments/gro4318' in root: continue` line is the manual equivalent of `-not -path "*/deployments/gro4318-*"`. Keep an exclusion list in your verifier script.
5. **In a verifier script, ALWAYS prefer `os.walk` over `subprocess.run(["find", ...])`.** `find` gives no indication of incomplete search; `os.walk` with explicit exception handling does. Even when `find` is the right tool for the user, your verifier should not silently fail on permission errors.

**Anti-pattern:** interpreting `find` returning 0 results as "file does not exist" without checking exit code. The file might be there; the search might have aborted 4 levels up.

## Reference

- `references/multirepo-file-find-technique.md` — worked example from
  2026-07-30, with the full Python pattern.
- `references/move-8-budget-gate-sysmismatch-2026-07-30.md` — companion
  case: the file exists, but the consumer's `sys.path` is wrong. The
  Move 8 budget-gate restoration. Use when the import fails but the
  module is present on disk.
- `references/handoff-claim-verification-recipe.md` (in session-state-handoff)
  — companion discipline for once you've found the file, verify the
  handoff's claim about it.

## Related

- `prismatic-evidence-handling` — CWD-independent `__file__`-relative paths in
  verifier scripts. Same session-surface root cause: the sandbox fs resolver
  desyncs after repeated absolute-path opens in a single Python process. When
  you find the file and write a verifier for it, also use that skill's path
  recipe so the verifier doesn't trip on the same quirk.

## Inverse case: file exists at the right path but git doesn't track it (2026-07-31)

The file-present cases (wrong path → wrong consumer import path, file not in
expected repo at all) are both "find the file" problems. The third case is
"the file is here, the consumer is correct, but it's never been `git add`-ed".
Observed in Move 14 (2026-07-31):

- `~/.hermes/profiles/orchestrator/scripts/registry_writer.py` (5.7 KB)
  was imported from `agy_post_publish_review.py`, `agy_peer_review.py`,
  and `agent_backlog_surgeon.py`, all tracked.
- `registry_writer.py` itself showed up as `??` in `git status --short`.
- Net effect: the consumers (tracked) would not reproduce in a fresh
  `git clone` of the repo, because their dependency was an artifact
  only present in this working tree.

Recipe for finding untracked-but-referenced files:

```bash
# 1. List untracked files
git status --short | grep -E '^\?\?' | sed 's/^?? //'

# 2. For each, ask git grep if any tracked file mentions it
for f in $(git status --short | grep -E '^\?\?' | sed 's/^?? //'); do
    base=$(basename "$f")
    git grep -l -F "$base"
done
```

Intersection of "untracked" and "referenced from tracked" is the audit gap.
Triage the intersection: commit the foundational ones (registry writer,
gate helpers, anything imported from multiple places); ignore the
experimental scratch scripts with no callers.

The class of bug is "code looks fine in this session but won't reproduce in
another" — same root cause family as the import-path case, just deferred
to `git clone` time instead of `import` time.

## Live-dashboard file-serving architecture (2026-07-31)

When Michael asks for a clickable link to a markdown file in the live
Prismatic dashboard (`https://prismatic.growthwebdev.com`), the file
discovery has its own surface that this skill now covers explicitly:

1. **Probe the live API first.** Before claiming "I cannot fabricate a
   URL," hit `https://prismatic.growthwebdev.com/api/workspaces` and
   `https://prismatic.growthwebdev.com/api/workspace-tree/node?...` to
   confirm the file tree browser is live and what its `workspace_id` is.

2. **Three distinct roots, only one of them serves.** The workspace-tree
   plugin auto-discovers workspaces from `/home/ubuntu/work/` but the live
   George gateway (running since 2026-07-29) is pinned to a specific
   release dir that the API actually serves from. The served path can be
   identified by file-size fingerprinting: pick a known file the API
   returns, then `stat -c '%s'` each candidate root until you find the
   exact byte match.

3. **The canonical served paths for `Prismatic Engine` workspace:**
   - **Live API serves from:** `/home/ubuntu/.prismatic/releases/<release-sha>/docs/`
     (e.g. `b5f474e6` for the pre-PR-382 deployment). These dirs are
     read-only (`dr-xr-xr-x` perms, owned by root). Modifying the file
     here is necessary but **not sufficient** — the George gateway must
     be restarted for the new file to appear in `/api/workspace-tree/node`.
   - **Auto-discover scans:** `/home/ubuntu/.prismatic/repos/prismatic-engine-control/docs/`
     (the control repo, 81 docs). This is what you'd intuitively expect to
     serve from, but doesn't.
   - **Local dev checkout:** `/home/ubuntu/work/prismatic-engine/docs/`
     (9 docs). Not served by the live API even though the plugin walks
     `/home/ubuntu/work/`.
   - **Active version symlink:** `/home/ubuntu/.prismatic/active` →
     `/home/ubuntu/.prismatic/versions/v0.1.0-ac48b21/docs/` (26 docs).
     Not served by the live API.

4. **To drop a new doc into the live dashboard:**
   - `sudo cp <file> /home/ubuntu/.prismatic/releases/<release-sha>/docs/`
   - `sudo chown ubuntu:ubuntu <dst>` (gateway runs as ubuntu; root:root
     may trigger an ownership check that excludes the file from listing)
   - `sudo chmod 644 <dst>` (the release dir is `555`; new files default
     to umask that may make them unreadable to the gateway)
   - `sudo systemctl restart hermes-gateway-george.service` to clear
     the gateway's in-process tree cache.
   - **Do not restart the gateway without explicit Michael authorization.**
     Restarting `hermes-gateway-george` interrupts George's active agent
     session. The dashboard-readiness-vs-agent-disruption tradeoff is a
     real cost — surface it, don't silently pay it.

5. **Verify by:** `curl -s "https://prismatic.growthwebdev.com/api/workspace-tree/preview?workspace_id=<id>&path=docs/<file>.md"`
   should return `{"ok":true,...}` with the file content. If it returns
   `{"detail":"workspace object unavailable"}`, the cache hasn't cleared
   or the file ownership is wrong.

**This is not the canonical dashboard's intended workflow.** Real
deployment should commit the file to `prismatic-engine-control` and roll
forward through a normal deploy cycle. The `sudo + restart` path is a
break-glass repair, not the steady-state answer.

See `references/live-dashboard-file-serving-architecture-2026-07-31.md`
for the full worked session including the size-fingerprinting recipe.
