# Distributed-Execution Header (field 8)

When 2+ agents may pick up tasks from the same Linear epic tree — which is the default for any non-trivial epic — every task description must include a **Distributed-Execution Header** as its eighth field. Without it, parallel/sequential pickup is silent: agents don't know which siblings to ship together, which files need a swarm lock first, or which pytest line proves the slice.

This file is the canonical spec. Refer to it from any build-out that includes field 8.

## When to use field 8

Use it whenever:

- The epic has 3+ tasks (any non-trivial epic).
- 2+ agents might pick up tasks from the same epic tree.
- Cross-task coordination matters (shared files, shared cron schedule, shared schema).
- The user asks "could 3-5 agents do this in parallel/sequence?" — answer with field 8, not prose.

Default: use it. The cost is ~10 lines of structured description per task; the benefit is coordination that does not require re-reading the whole epic.

## The header (verbatim shape)

Append this to every child task description, after the seven fields, with a blank line before `DISTRIBUTED EXECUTION HEADER`:

```markdown
DISTRIBUTED EXECUTION HEADER
- depends_on_siblings: [GRO-NNNN, GRO-NNNN] | none (first task in epic)
- blocks: [GRO-NNNN] | none (last task in epic)
- branch_slug: <agent-prefix>/<short-slug>
- swarm_locks: [<repo-relative-path>, ...]
- pytest_command: pytest <repo-relative/test-path>::<test-id>
- evidence_comment_template: |
  /tmp/hermes-verify-<unique>.py created with tempfile and cleaned in finally.
  Scope: ad hoc targeted verification, not suite green.
  Branch: <branch_slug>
  Acceptance tests passed: <test-id-1>, <test-id-2>.
  Captured at <UTC ISO timestamp>.
- pickup_signal: agent:in-progress NOT present on this issue
- review_signal: agent:peer-review-blocked required before Done
- coordination: see <okf-reference-doc>
```

## Field-by-field spec

### `depends_on_siblings`

The list of tasks in the **same epic** that must land together as one PR (sequential ordering). Use the empty-list form when the task is first in its epic.

Examples:
- `[GRO-4222, GRO-4223]` — pick up only after both have merged.
- `none (first task in epic)` — pick up freely.

### `blocks`

The list of tasks in the same epic that wait for this one to land before they can start (sequential ordering). Use the empty-list form when the task is last in its epic.

Examples:
- `[GRO-4224, GRO-4225]` — these tasks block until you ship.
- `none (last task in epic)` — no downstream within this epic.

### `branch_slug`

Exact branch name to open. Per `prismatic-engine/PRISMATIC_ENGINE.yaml`:

- fred → `feature/<slug>`
- ned → `ned/<slug>`
- kai → `content/<slug>`
- agy → `design/<slug>`
- jules → `fix/<slug>`

`<slug>` is the task's short slug, derived from the task title (lowercase, hyphen-separated, ≤40 chars). All agents picking up sibling tasks in the same epic should use the SAME branch slug, so a single PR collects the full epic.

### `swarm_locks`

The list of repo-relative file paths to lock via `node $PRISMATIC_HOME/.antigravity/swarm.js lock <path> <agent>` before editing. Release after commit. Heartbeat every 60s while editing. Stale TTL: 5 minutes. If the swarm lock tool is unavailable, **stop and ask fred** — do not edit the file without a lock.

Examples:
- `['prismatic-engine/prismatic/lane_contracts.py']` — single-file edit.
- `['prismatic-engine/pe/api/routers/crons.py', 'prismatic-engine/pe/api/tests/test_crons_router.py']` — multi-file edit.

### `pytest_command`

The exact `pytest <path>::<test_id>` line that proves the slice. Pick a real test ID from the suite — not a placeholder. If the task does not warrant a unit test (e.g., documentation-only task), use `echo '<rationale>'` instead.

Examples:
- `pytest prismatic-engine/prismatic/tests/test_lane_contracts.py::test_agy`
- `pytest prismatic-engine/pe/api/tests/test_crons_router.py::test_neg_404_400_401`
- `echo 'documentation only; sign-off recorded in OKF'`

### `evidence_comment_template`

What to post as a Linear comment when moving to `In Review`. The minimum content is path to the `/tmp/hermes-verify-*.py` script (or note that no script was needed), exit code, acceptance test IDs passed, UTC ISO timestamp.

### `pickup_signal`

Always: `agent:in-progress NOT present on this issue`. Tells the agent to run `gh issue view GRO-XXXX --json labels` first and confirm the label is absent before claiming.

### `review_signal`

Always: `agent:peer-review-blocked required before Done`. Tells the agent that even after their tests pass, they cannot move to `Done` without explicit peer approval.

### `coordination`

Link to the OKF doc that explains the multi-agent pattern at the workspace level. For this build-out, the canonical reference is `okf/standards/references/distributed-execution-multi-agent-task-pickup.md`.

## Lifecycle (recommended)

```
Todo  --(agent picks up + sets agent:in-progress)-->  In Progress
In Progress  --(evidence posted)-->  In Review  (label: agent:peer-review-blocked stays)
In Review  --(peer approves)-->  Done
In Review  --(peer rejects)-->  In Progress  (label: agent:peer-review-blocked stays)
In Progress  --(blocked)-->  Todo  (label: dispatch:blocked + agent:needs-human-review)
```

## Claim protocol (every pickup agent must follow)

1. Run `gh issue view GRO-XXXX --json labels` (or GraphQL) to confirm `agent:in-progress` is **not** present.
2. If clear, atomically add `agent:in-progress` via `issueUpdate` **before** reading any source code.
3. If the task is already `agent:in-progress`, post a comment asking for status and move to a different task in the same epic.
4. After pickup: acquire swarm lock for every file in `swarm_locks`, open branch with the slug from `branch_slug`, implement, test, post evidence, request review.
5. Move to `In Review` (do NOT self-approve to `Done`).

## Handoff protocol (when pausing)

1. Post a comment with: current state, what works, what's pending, files touched, branch name.
2. Add `agent:needs-human-review`.
3. Remove `agent:in-progress` (so another agent can pick up).
4. Do **not** delete the feature branch.

## Pitfalls

- Do not skip field 8 for non-trivial epics. The cost of including it is ~10 lines; the cost of skipping is silent collisions.
- Do not put a literal credential prefix (e.g. `ghp_`) inside an OKF artifact even as a "what to watch for" example. Use category wording.
- Do not pick up a task with `agent:in-progress`. Post a comment and find another.
- Do not skip the swarm lock; the lane contract is explicit.
- Do not self-approve to `Done` — even if you wrote all the tests.
- Do not delete a feature branch on handoff; the pickup agent needs it.
- Do not assume `agent:peer-review-blocked` is optional; it is required for tasks touching shared code paths.
- Do not split an epic across multiple PRs unless the tasks are explicitly marked as parallelizable.
- Do not pick up a task whose `depends_on_siblings` includes an unfinished task — coordinate first.