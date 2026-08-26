---
name: ned-lane-discipline-check
description: Ned lane checks; see references/lane-rejection-owner-routing.md and references/2026-07-scoped-ruff-and-pr-template-summary.md.
---

# Ned Lane Discipline Check

See `references/2026-07-scoped-ruff-and-pr-template-summary.md` for the lane-aware PR template, scoped-ruff rule, and the recovery recipe when ruff reformats ~280 unrelated files at once.

## Verify handoff context before acting on it

The "Session handoff" / "Constraints" preamble of a fresh Ned session
sometimes describes a state that does not exist on disk. Common drift:
wrong profile path (`/home/ned/...` vs `/home/ubuntu/.hermes/profiles/ned/...`),
waning symlink targets, a "first slice complete" claim when the
referenced file is missing, or a next-action title that names a real
artifact but a scope the file doesn't cover.

**Always verify before writing code.** Minimum gate:

1. Read the actual `state/current.json` (path is
   `/home/ubuntu/.hermes/profiles/ned/state/current.json`, not the
   `/home/ned/...` variant the preamble may say).
2. Confirm any file the preamble names (`kpi-collections.json`,
   `RENDERER_SPEC.md`, etc.) actually exists at the path it claims.
3. If the file is missing OR the projects/skills referenced are gone,
   **stop and ask** — never invent context for a renderer spec / Linear
   ticket that doesn't exist. Reporting a "blocker: handoff fabricated
   state" is always better than fabricating a plausible-looking spec
   and committing it.

The 2026-07-31 KPI PWP plugin handoff described a "first-slice complete"
state with `kpi-collections.json` and a "second slice spec next" next
action. The actual `current.json` described a Zapier OKF runbook; the
referenced `kpi-collections.json` did not exist in any PWP plugin tree.
A direct read of the real state file + a `find` for the named files
resolved the discrepancy in two tool calls; the alternative was
inventing a renderer for a project that wasn't on the filesystem.

## Finalizer and dependency-gate safety

Before using the task finalizer for a held, dependency-gated, or out-of-lane issue, follow [finalizer dry-run and gated-task safety](references/finalizer-dry-run-and-gated-task-safety.md). In particular, `--dry-run` must be the **first** argument and a blocked child must not be normally finalized into In Review.

## Linear bulk epic/task creation: verify completion, not intent

When asked to create a comprehensive Linear tree from a master plan, treat this as a bulk data mutation job with a verification phase, not a prose/planning task.

Required pattern:

1. Read the source plan and derive an explicit manifest of expected epics, child issues, priorities, labels, parent links, and wait/dispatch policy.
2. Query existing Linear issues first to avoid duplicates.
3. Create epics first, then children with `parentId`.
4. De-duplicate `labelIds` before every `issueCreate`; Linear rejects repeated IDs with `arrayUnique`.
5. Run a final verification query that checks total count, parent count, label coverage, and leaf-issue completeness.

## Ned-as-finalizer guardrails

Linear's "finalize" must not be the first step of a PR-finalization pass. The legit path is:

1. Stop the current branch's work.
2. Move the Linear issue to `In Review` only after the PR is open AND the checks are green.
3. *Then* finalize.

If Michael asks "is this Linear issue ready to be Done?" — cross-check the PR + checks before moving state. A false-free finalization rolls back: Linear state moves to `Done` while the child work is still incomplete, and the seed Linear comment thread becomes a lie.

## Lane-ownership diagnostic

When `scripts/pre-push-hook.py` rejects a push, the error body says which
files are outside Ned's lane:

```
❌ [Prismatic Engine] Lane violation by ned:
   - conftest.py
   - pyproject.toml
   These files are outside ned's lane.
   Owned directories: ['scripts/', 'prismatic/', 'plugins/']
```

The fix is to relocate offenders into one of the owned dirs. The
canonical locations for Prismatic Engine work are:

- `plugins/<plugin>/`                 (new plugin code)
- `plugins/<plugin>/tests/`           (plugin tests)
- `plugins/<plugin>/pytest.ini`       (plugin-local pytest config)
- `plugins/<plugin>/conftest.py`      (plugin-local sys.path bootstrap)
- `prismatic/shipped_plugins/<plugin>/` (symlink→ the canonical plugins/ tree)
- `scripts/`                          (cron + verifier scripts)
- `docs/` should NOT be edited from Ned's branch — other agents own it.

### Handoff packets can cite STALE lane tables — the repo's yaml is authoritative

A handoff doc / Linear ticket / OKF audit can assert lane ownership that no longer
matches the target repo's `PRISMATIC_ENGINE.yaml`. Hit 2026-08-21 (GRO-4831,
prismatic-engine G2+G6 journal bundle): the ticket and Kai's handoff packet both
said "`tests/` is Ned's lane", but the live yaml gave ned only `scripts/`,
`prismatic/`, `plugins/` — `tests/` resolved to fred (`*`), and the pre-push guard
correctly rejected the push. The packet's lane table was simply stale.

Rules:

1. **Before landing anyone's handoff, cross-check the packet's lane claims against
   `PRISMATIC_ENGINE.yaml` IN THE CHECKOUT YOU WILL PUSH FROM** (the guard reads it
   there, not from any canonical copy). `git show HEAD:PRISMATIC_ENGINE.yaml | grep -A5 "ned:"`
   is the 30-second gate. Never trust the doc.
2. **If the acceptance criteria REQUIRE a file outside your lane** (e.g. "PR must
   contain exactly these 3 files" and one is `tests/...`), relocating the file is
   not an option — the deliverable is defined. Do NOT self-expand your lane, and do
   NOT push under another agent's prefix (misattribution, explicitly rejected per the
   2026-08-19 authorization decision). Instead: do the work, verify it (tests + lint),
   commit locally on your own `ned/` branch, then STOP at the guard and present the
   three unblock options to Michael with a recommendation:
   (a) add the dir to ned's owner lanes in the repo yaml (permanent config change —
   the `*`-owner or Michael applies it; recommended when tests co-own with the code
   they test), (b) reassign the landing to the lane-owning agent (e.g. Fred on
   `feature/`), (c) Michael pushes the verified local branch manually. Post the
   blocker + options on the Linear ticket and mark it `In Progress`, not `In Review`.
3. The local commit is safe until pushed — say so explicitly ("commit `X` is safe
   locally, not on origin; nothing is lost") so the human isn't chasing a lost-artifact
   scare.

### Promotion-merge exception: scoped lane extension (needs human permission)

When the task is a **promotion merge** (e.g. merging a staging branch like
`deploy-fresh` into `main`) that legitimately carries files outside Ned's
owned dirs (`functions/`, `reports/`, …), relocating files is wrong — the
merge must land those paths as-is. Pattern (used 2026-08-19 for the HDE prod
deploy promotion, with Michael's explicit permission):

1. **Get explicit permission** — a lane override is a governance change;
   "go ahead" on the deploy is not sufficient by itself. If in doubt, ask
   once and quote the reply in the commit.
2. Edit the repo-local `PRISMATIC_ENGINE.yaml` `agents.ned.lanes.owner` list
   in the **worktree being pushed from** (the pre-push guard reads the
   file from that checkout, not from a canonical copy) and add the needed
   paths.
3. Add a dated comment scoping the extension to the promotion branch, and
   note it is temporary (the 2026-07-17 note in that file says
   revert/narrow before generalizing — honor it).
4. **Commit the yaml change in the same worktree before pushing** — the
   guard re-reads the file at push time, so an uncommitted edit does not
   count.
5. After the promotion PR merges, narrow the lane list back and file a
   pending decision for Michael if the narrowing itself is contested.

See `references/2026-08-prod-deploy-promotion-lane-extension.md` for the
full session record (which files got flagged, the commit, and the follow-ups).

## Two-bug compound failure: pre-push + commit gates

A common additive failure mode is the pre-push hook rejecting the
**commit** (path portability, lane) and the post-commit **PR** check
failing on a pre-existing test (e.g. `test_merge_status.py` tests
broken on `origin/main` because of a missing symbol). Treat them as
separate failure modes:

1. **If the commit gate fails**, scope ruff to owned paths (see
   reference above), replace `pyproject.toml` changes with
   `plugins/<plugin>/pytest.ini`, and `git restore -s origin/main`
   any reformatted-but-not-owned files.
2. **If the CI test matrix fails after merge**, run the canonical
   `pytest -q` against `origin/main` (not the branch) to confirm the
   failure is pre-existing. If so, do not "fix" the new code; annotate
   the PR body with a CI status note + Linear evidence, and post a
   follow-up PR for the actual test regression.

## Companion skill

`finalize-task-script-bug` covers parallel failure modes around the
task finalizer, lane routing, and lock cleanup. Use it when the issue
is gated by another agent or when the finalizer is the next step.
