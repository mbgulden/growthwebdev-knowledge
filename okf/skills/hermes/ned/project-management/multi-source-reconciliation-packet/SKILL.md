---
name: multi-source-reconciliation-packet
description: Use when a project has accumulated dirty checkouts, local-only branches, open PRs, and Linear issues that contradict each other and a non-destructive inventory is required before any further change. Produces a classified snapshot packet and a parent Linear tracking issue. Trigger on >50 dirty entries, >5 local-only branches, >5 open PRs in a cluster, or any "parent Done while children incomplete" signal.
---

# Multi-Source Reconciliation Packet

## When to use

A project is in a state where **four sources of truth disagree**:

1. Canonical Git checkout: tracked modifications and untracked files.
2. Local-only branches: commits not on `origin/*`.
3. Open GitHub PRs: work that may or may not map to a Linear issue.
4. Linear issues: parent/child state vs. reality.

Use this skill when any of the following is true:

- `git status --short` shows > 50 dirty entries.
- `git branch -r --contains <local-branch>` returns empty for > 5 branches (local-only work).
- A Linear search on the project shows > 5 open PRs in `https://api.github.com/repos/{owner}/{repo}/pulls?state=open`.
- A parent epic is marked `Done` while required children remain `Todo`/`Backlog`.
- Michael (or another owner) says "where are we at" without a clear answer.

Do not use for one-issue refresh, single-PR cleanup, or routine finalization. Those belong to `linear-epic-evidence-reconciliation`.

## Required output

A non-destructive packet containing:

1. **Path-by-path classification** of every dirty entry, into one of six dispositions:
   - `promote-pending` (real work to merge)
   - `superseded` (captured elsewhere)
   - `runtime-only` (cache, pyc, dist backups; ignore rules)
   - `sensitive-review` (`.env`, `.runtime/`, `production*.db`, `cloudflared*token`)
   - `archive` (move to archive folder)
   - `unclassified` (needs owner decision)
2. **Local-only branch catalogue** with ahead/behind vs `origin/main` and `origin/deploy-fresh`, and `git branch -r --contains` to determine `on_origin`.
3. **Open-PR disposition table** — every PR linked to its Linear ID via regex on the PR title, mapped to one of: merge, close, sequence, hold.
4. **Linear reconciliation** — state vs reality discrepancies for the project's issues.
5. **Sign-off checklist** — four explicit decisions Michael must make before any production change.
6. **Production-readiness gate** — a single checklist the agent and owner both check off before merging anything.

## Workflow

1. **Inventory repositories** under `/home/ubuntu/work` using a Python tree walk that excludes `node_modules`, `.venv`, `__pycache__`, `dist`, `build`. For each `.git` directory, fetch:
   - `git remote -v`
   - `git branch --show-current`
   - `git log -1 --format='%h %ci %s'`
   - `git status --short --branch`
   - `git worktree list --porcelain` (text, NOT JSON — see Pitfalls).

2. **Capture raw snapshots** to `/tmp/<project>_dirty.json`, `<project>_branches.json`, `<project>_prs.json`, `<project>_linear.json`. These are runtime-only, ephemeral, and may be deleted.

3. **Classify paths** with a deterministic Python script using regex heuristics:
   - Sensitive: `(database\.db|production.*db|\.env$|\.env\.|cloudflared.*token|secret|password|token\.json|api[_-]?key|service[_-]?account)`
   - Archive: `(dist\.backup|backup-?\d|\.tar|\.tgz|cleanup[_-]archive)`
   - Runtime: `(reminders?\.json|cron_state|\.pyc$|__pycache__)`
   - Content (Kai lane): `(landing|bodygraph|terms|privacy|sitemap|robots|legacy)` matching HTML.
   - Source (Ned lane): everything else authored (.py, .mjs, .json, .yaml, .service, .timer, .md under operations/).

4. **Generate the Markdown packet** into `<canonical-repo>/docs/operations/_reconciliation/<project>-reconciliation-packet-YYYY-MM-DD.md` plus a `*-dirty-snapshot-YYYY-MM-DD.json` companion. **Keep both untracked** by writing into a fresh subdirectory and not adding them to the index.

5. **Open the parent Linear issue**:
   - Title: `[<TAG>-RECONCILE] Non-destructive reconciliation packet before any production change`
   - Project: the project's core project (e.g., `HD Engine Core` for HDE)
   - State: `Todo`
   - Labels: `agent:<lane>`, `epic`, `requires:human-approval`, `dispatch:ready`
   - Description: link to packet doc and snapshot; enumerate children; restate the production-readiness gate.
   - Comment: post a structured summary with disposition totals and the four sign-off items.

6. **Wait for sign-off.** No further production changes until Michael approves.

## Linear API specifics

- `commentCreate` requires `input: CommentCreateInput!`, NOT direct `issueId` + `body` args:
  ```graphql
  mutation($input: CommentCreateInput!) {
    commentCreate(input: $input) { success }
  }
  ```
  with `input = {issueId: "GRO-XXXX", body: "..."}`.
- `issueUpdate` similarly uses `input: IssueUpdateInput!`.
- `workflowStates` is global (no team filter required); pick the one matching `{name: "Todo", type: "unstarted"}`.
- `issueLabels(filter:{name:{eq:$name}})` returns one node per exact match.

## Pitfalls

- **Do not `json.loads()` `git worktree list --porcelain` output.** It is plain text, not JSON. Parse 3-line blocks (see `linear-epic-evidence-reconciliation` for the loop pattern).
- **Do not commit the packet.** The packet documents the dirty state; committing it pollutes the dirty state. Write it into a fresh untracked subdirectory.
- **Do not mass-clean before sign-off.** Cleanup that loses ownership context is unrecoverable. Even runtime-only paths should be classified first.
- **Do not skip the sign-off checklist.** Even if "everything looks obvious," the four decisions (sensitive-artifact plan, branch-ownership, parent-reopen policy, PR-closure authority) need Michael's explicit go-ahead because they cross into irreversible territory.
- **Do not auto-close PRs without owner direction.** Even clearly-superseded PRs may carry local-only commits not visible from a remote view; close only after sign-off.
- **Do not write the packet into a directory already under dispute.** If `docs/operations/` itself has open merge conflicts or a draft commit, use a fresh path like `_reconciliation/` to keep the packet self-contained.
- **Owner override on the decision item:** if Michael says "pull it into your lane and figure it out" (or equivalent), the one remaining decision item also becomes in-scope. The override pattern is stat-only inspection (`os.listdir` + `os.lstat`) without `cat`/`open`/`read`, so the file's contents are never observed. The empty-file canonical SHA-256 (`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`) is a sentinel for "the file was truly zero bytes." If the file is genuinely empty (size 0, mtime set, no associated metadata), record SHA + path + mtime + inode, save the record outside the tracked tree, and either delete or move per the override. Update both the full packet and the Telegram-safe summary to mark "RESOLVED" and include the receipt path. See `references/2026-07-stat-only-sensitive-file-resolution.md`.
- **Archive moves need a SHA-256 manifest + byte-count cross-check**, not just `mv` + `rm`. A move without a manifest is silent about partial copies and lost files. Write the manifest (per-file SHA-256 + declared total bytes) BEFORE the move, then after the move re-walk the destination and confirm declared totals match on-disk totals byte-for-byte (allow at most 1% drift for filesystem metadata, 1024 bytes whichever is greater). See `references/2026-07-archive-move-sha256-manifest.md`.
- **Verifier Markdown-link substring mismatch:** when a packet or PR-batch comment contains a Markdown table row like `| [19](https://github.com/...) | ... |`, the substring to assert against is `[19](https://github.com/...)`, NOT `| [19](url)`. The leading pipe `|` belongs to the table separator, not to the link. Strip it from your marker, or better, just match `[N](url)` as a plain substring anywhere in the body — it survives table reformatting and column re-alignment. The same rule applies when verifying a comment that lists `| # | Base | Head | Linear |` table rows: assert on the link target, not the column delimiter.
- **Public GitHub REST read for PR verification when `gh` auth is missing:** when Ned's environment has no GitHub CLI auth but the reconciliation needs to enumerate or confirm PR state, use `urllib.request` directly:
    ```python
    import urllib.request, json
    url = "https://api.github.com/repos/<owner>/<repo>/pulls?state=open&per_page=100"
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "Ned-Verify",  # GitHub rejects requests without a UA
    })
    prs = json.loads(urllib.request.urlopen(req, timeout=30).read())
    ```
    This pattern is stdlib-only, works inside `execute_code` and `terminal`, and does not require `gh` auth for public read. Pair with a hash-set assertion: `open_nums = {p["number"] for p in prs}; assert all(n in open_nums for n in candidates)`. Use it whenever a reconciliation verifier needs live PR state but the agent does not have GitHub auth in the active profile.
- **When writing a `/tmp/hermes-verify-*` artifact verifier via shell heredoc**, three patterns bite repeatedly. First, credential-regex strings like `mysql://[^@\s]+@` can be mangled by the shell; use string concatenation or skip redundant patterns (postgres + redis usually suffice). Second, the marker strings the verifier checks against MUST be the exact substrings emitted in the document being verified — table rows look like `| 2a |` not `Item 2a`. Before writing the verifier, grep the actual artefact for the substring you intend to assert on; if the format drifted in a recent patch, update the verifier to match the artefact, not the agent's memory of what it wrote. Third, when the verifier must pick one comment out of an issue's history, do not match by substring like `'PR-batch close' in body` because earlier comments may mention the phrase in passing. Match by exact body prefix: `(c['body'] or '').startswith('PR-batch close:')`.

## Verification

After generation, verify:

- Canonical checkout `git status --short` increases by exactly 2 (the new packet.md and snapshot.json, both untracked).
- The Linear issue exists in the correct project, in `Todo`, with the four labels, and has the post comment.
- The packet file contains the four sign-off items and the production-readiness gate as explicit checklists.
- The disposition totals in the packet match the totals in `/tmp/<project>_dirty_classified.json` byte-for-byte.

## Related skills

- `linear-epic-evidence-reconciliation` — the per-parent variant. Load this one first if the question is "should I close this parent epic?" Load `multi-source-reconciliation-packet` instead when the question is "where is this project overall?"
- `ned-lane-discipline-check` — if a path turns out to be lane-blocked (Ned attempting to edit Fred's files, etc.), that skill documents the safe-push guard pattern.
- `worktree-hygiene-and-cleanup-safety` — for the post-sign-off cleanup phase, after the packet is dispositioned.
- `response-contract-and-result-reporting` — for the final report shape back to Michael.

## Support files

- `references/2026-07-hde-reconciliation-packet-example.md` — concrete HDE packet from 2026-07-27 with all 127 dirty entries, 21 local-only branches, 28 open PRs, and 51 Linear issues mapped.
- `references/2026-07-linear-api-gotchas-reconciliation.md` — Linear `commentCreate` / `issueUpdate` / `issueCreate` mutation shape gotchas hit while creating the parent issue and posting the structured comment.
- `references/2026-07-collapse-sign-off-items.md` — pattern for replacing a 4-item checklist with one owner decision plus three pre-resolved rows backed by live evidence. Used to keep the HDE packet self-driving without bypassing Michael's authority.
- `references/2026-07-stat-only-sensitive-file-resolution.md` — what to do when Michael says "pull it into your lane and figure it out": stat-only inspection (`os.listdir` + `os.lstat`) without peeking at file contents, the empty-file SHA-256 sentinel, the deletion/move/quarantine receipt pattern, and how to update the full packet + Telegram summary to mark RESOLVED.
- `references/2026-07-archive-move-sha256-manifest.md` — pattern for moving `archive` or `runtime-only` directories out of a tracked repo: write a SHA-256 manifest (per-file) BEFORE the move, use `os.rename` (atomic) for the move itself, then re-walk the destination and confirm declared byte totals match on-disk totals byte-for-byte. Companion pattern to the stat-only sensitive-file resolution.
- `references/2026-07-linear-comment-and-github-pr-verifier.md` — Linear `comments(last: N)` depth pitfall, `commentUpdate` requiring both `id` and `input`, exact body-prefix filtering across comment history, and the stdlib-only `urllib.request` public GitHub REST read pattern for PR state verification when `gh` auth is missing.
- `github-pr-backlog-hygiene/references/2026-07-hde-analytics-extraction-no-gh-token.md` — companion recipe for the "no GH_TOKEN, branch ready on disk" boundary: anonymous `.patch` retrieval, the `git apply --3way` silent-no-op trap, and the "branch ready, push requires human token" Linear-comment contract. Use this when a reconciliation decides that a fresh scope-clean extraction branch is the right move but the agent has no push authority.