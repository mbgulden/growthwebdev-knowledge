# Multi-repo + Working-Tree File Find — Worked Example

The agent knows a file *should* exist (per a handoff, a counter record, or a
planning message) but the obvious search paths come up empty. The file is not
on the working tree of the current working directory. The session is starting
to feel like a hallucination — but the file genuinely exists somewhere.

This is the worked example from 2026-07-30, when a handoff claiming
`agy_post_publish_review.py` was patched returned empty for `ls` and for
`search_files` in `/home/ubuntu/work`. The file lived in a sibling repo at
`~/.hermes/profiles/orchestrator/scripts/` — a path the user had to help
the agent find by saying "search branches and worktrees and all over."

## Step 1 — what the obvious search returned

```bash
$ pwd
/home/ubuntu

$ ls -la
# 70+ directories; nothing obviously called handoff/profile/scripts

$ search_files pattern="agy_post_publish_review" target="files"
# (timeout / empty)

$ find /home/ubuntu/work -name "agy_post_publish_review.py"
# empty — the file is not in /home/ubuntu/work
```

Conclusion: **the file is not in the working tree, but the user's
real-world claim ("Move 5 already wired this script") is true.** The next
move is to find the file, not to fabricate it.

## Step 2 — enumerate git repos

```bash
$ find /home/ubuntu -maxdepth 5 -type d -name .git 2>/dev/null
```

This returns ~200 paths. The relevant ones for the AGY scripts were:

```text
/home/ubuntu/.prismatic/published/work/prismatic-engine/.git
/home/ubuntu/.hermes/profiles/orchestrator/scripts/.git
/home/ubuntu/.prismatic/published/agentic-swarm-ops/.git
/home/ubuntu/.hermes/profiles/fred/skills/.git
```

The orchestrator scripts repo is the surprising one — it's not in `/home/ubuntu/work`,
it's in `~/.hermes/profiles/orchestrator/scripts/`. The repo has its own
`.git` and is the source of truth for the scripts used by the orchestrator
profile.

## Step 3 — search for the file by name across all branches

```bash
$ git -C /home/ubuntu/.hermes/profiles/orchestrator/scripts log \
    --all --pretty=format: --name-only --diff-filter=A \
    -- agy_post_publish_review.py
```

**HIT:** commit `d7a577a [Fred] Add post-publish review chain + scheduled
repo-wide audit`. The file lives at `agy_post_publish_review.py` in this repo
and is on the working tree.

The same pattern works for `registry_writer.py`, `registry_reconciler.py`,
and `cron/jobs.json` — but `cron/jobs.json` lives in `~/.hermes/profiles/orchestrator/cron/`,
not in the scripts repo. Many orchestration files are split across multiple
repos per profile.

## Step 4 — confirm the file is on the working tree, not just in history

```bash
$ ls -la /home/ubuntu/.hermes/profiles/orchestrator/scripts/agy_post_publish_review.py
-rw-r--r-- 1 ubuntu ubuntu 11897 Jun 23 17:52 agy_post_publish_review.py
```

The file is on disk at the named path. (Bonus: the mtime is 5 weeks old,
which is itself a signal that the handoff's "patch verified" claim was wrong
— the file was last touched 2026-06-23, before the claimed work. The
handoff-claim-verification-recipe captures this.)

## Recap: the full Python pattern

```python
import subprocess
candidates = [
    "/home/ubuntu/.prismatic/published/work/prismatic-engine",
    "/home/ubuntu/.hermes/profiles/orchestrator/scripts",
    "/home/ubuntu/.prismatic/published/agentic-swarm-ops",
    # ... add more as needed
]
for fn in ["agy_post_publish_review.py", "registry_writer.py", "jobs.json"]:
    for r in candidates:
        if not os.path.isdir(r):
            continue
        res = subprocess.run(
            ["git", "-C", r, "log", "--all", "--pretty=format:",
             "--name-only", "--diff-filter=A", "--", fn],
            capture_output=True, text=True, timeout=15
        )
        if res.stdout.strip():
            print(f"HIT: {r} :: {fn}")
            # also show the working-tree path
            wp = os.path.join(r, fn)
            if os.path.exists(wp):
                print(f"  WORKING: {wp} size={os.path.getsize(wp)}")
```

This is the recipe that broke the 2026-07-30 dead-end. Without it, the agent
would have either fabricated the script or refused to proceed.

## See also

- `../session-state-handoff/references/handoff-claim-verification-recipe.md`
  — once you've found the file, verify the handoff's claim about it.
- `../proactive-execution-discipline/SKILL.md` — the "verify before acting"
  gate that should have been triggered before the handoff was honored.
