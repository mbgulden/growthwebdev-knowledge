# HDE state-of-things audit — 2026-07-27

Use this reference when Michael asks a broad "where are we at for X?" question that turns out to require triangulating **multiple repos + Linear parents + open PRs + live services + ops docs** rather than executing one feature.

## Trigger

Michael asked: "Please focus on Human Design Engine. Where are we at for that? Check out all the repos, linear tasks and documentation and make sure we know where we are at and where we are going."

This was a reconnaissance request, not an execution request. The right response was a state-of-things report; jumping into cleanup or shipping would have skipped the actual question.

## What "where are we at" actually requires

The user's question hides four sub-questions, each answered by a different system:

| Sub-question | Source |
|---|---|
| Is the engine actually running? | systemd + listening sockets + prod/staging URL probes |
| What is the canonical source? | Git repos + worktrees + branches + remotes |
| What is the engineering plan? | Linear issues + parent/child state + comments |
| What is deployed? | GitHub PRs + Cloudflare Pages + Pages/Workers checks |

Each sub-question has its own ground truth and its own drift. The job is to surface the drifts, not to claim any one source is authoritative.

## Pattern that worked in this session

1. **Inventory HDE-relevant Git repos in parallel** with a Python walk over `/home/ubuntu/work`, filtered by name/remote containing `hd-platform`, `human-design`, `humandesign`, `HDE`. For each repo collect:
   - `git branch --show-current`
   - `git log -1 --format='%h %ci %s'`
   - `git remote -v`
   - `git status --short --branch`
   - `git worktree list --porcelain`
   The worktree list is essential — `/tmp/hd-platform-*` and `hd-platform-GRO-####` worktrees carry branches the canonical checkout has forgotten.

2. **Probe services with `systemctl show` + `ss -ltnp`** for each `hde-*` service. `ExecStart` says what *should* be running; `ss -ltnp` says what *is*. In this session every `hde-*` unit was `active running` and the listening ports matched the unit files, so services were healthy — that fact alone reframes the report from "engine is broken" to "engine is healthy, planning is broken."

3. **Probe live URLs** in one parallel curl batch:
   - production canonical
   - staging canonical
   - key business route (e.g. `/free-human-design-reading-generator/`)
   - one synthetic health route (e.g. `/health`) — record 404s honestly; do not assume silence equals success.

4. **Linear inventory**: GraphQL `issues(first:100, orderBy:updatedAt)` paginated 25× = 2500 issues scanned, then classified by project + labels + title regex for HDE/bodygraph/Sanctuary. ~47 matches in this session. Bucket by state with `Counter`.

5. **Drill into suspect parents**: for any parent marked Done, fetch children + last 3 comments. In this session, `GRO-4004`, `GRO-4010`, `GRO-3992` were Done but had Todo/Backlog children — this is the **parent-Done-children-incomplete** drift class and must be called out, not papered over.

6. **GitHub public API** for open PRs (works without `gh auth`):
   ```
   GET https://api.github.com/repos/mbgulden/hd-platform/pulls?state=open&per_page=100
   ```
   In this session: 29 open PRs. Bucket by base.ref to see how many are on `main` vs `deploy-fresh`. Note any PR stacked on another feature branch instead of the intended release base.

7. **Quantify bloat**: `du -sh` vs `git count-objects -vH`. In this session `hd-platform` was 1.1 GB total but only ~66 MB in git objects — most size was working/generated material. That tells you the repo is dirty in working files, not in history.

## Output shape that landed well

The final report used four sections plus a drift table:

1. **What is working now** — green checks with concrete URLs/PIDs/HTTP codes
2. **The intended direction** — North Star quote + golden-path diagram, drawn from existing repo docs
3. **Repository reality** — repo-by-repo state including worktree count, dirty files, divergence from base, size breakdown
4. **GitHub state** — PR count, bucket by base/mergeability, examples with URLs
5. **Linear state** — bucketed counts + drift table (Done parent + Todo children)
6. **Documentation state** — strategic docs vs operational/status docs
7. **Priority plan** — P0/P1/P2/P3 with concrete next actions
8. **Bottom line** — three 🟢/🟡/🔴 lines stating where the engine, product, and delivery system actually stand

## Why this matters

Multi-agent workflows drift in characteristic ways:

- Linear Done state gets out of sync with children, PRs, and deployed reality.
- Local checkouts grow dirty; worktrees accumulate; one canonical branch stops being canonical.
- Launch/audit docs go stale relative to the work that followed.
- Services stay up while planning breaks.

The "where are we at" question is a request to **report the drift**, not to fix it. If the answer is "engine is up but planning is fragmented," the Next Step is "reconcile PRs and Linear before shipping features," not "merge the next branch."

## Pitfalls

- Do not start cleanup or shipping during the reconnaissance. The question is about state.
- Do not trust a parent epic's state alone. Always fetch children.
- Do not trust "open PR" without checking whether its branch still exists locally.
- Do not trust a launch audit doc without re-reading it against current Linear and PR state.
- Do not claim "everything is healthy" from one source. Health in services does not imply health in planning.
- Do not skip the bloat check. A 1.1 GB checkout with 66 MB of git objects is a working-tree problem, not a history problem.
- Do not use closed-form prompts that imply a single answer. The "where are we at" question needs the four-way drift table to be useful.