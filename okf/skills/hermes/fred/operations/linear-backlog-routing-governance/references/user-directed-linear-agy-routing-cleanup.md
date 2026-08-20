# User-Directed Linear Cleanup and AGY Routing

Use this reference when Michael reviews an AGY/open-task audit and gives direct disposition calls such as “cancel this,” “already done,” “make this an OKF doc,” or “move the rest to AGY.”

## Durable lesson

Michael’s direct queue-disposition calls are authoritative. Do not re-litigate stale/done decisions unless the requested mutation is destructive outside Linear or conflicts with a safety rule.

## Workflow

1. **Live preflight**
   - Query all named issues in one Linear GraphQL read using team key + numeric issue numbers.
   - Fetch workflow states, labels, and assignees in the same pass.
   - Normalize the `linear_api_compat.linear_call()` response shape: it may return the GraphQL `data` object directly.

2. **Cancel stale/done/duplicative issues**
   - Move user-identified stale/done issues to `Canceled`.
   - Remove all operational `agent:*` and `dispatch:*` labels so canceled issues cannot re-enter queues.
   - Leave non-operational taxonomy labels such as `engine_consumable` if already present.
   - Post a short comment with Michael’s disposition and the cleanup date.

3. **Convert doc-only work to OKF**
   - If Michael says “make this into an OKF doc,” update the Linear title/description to an OKF documentation/standardization task.
   - Remove `agent:agy` and `dispatch:ready`; route to `agent:fred` unless another OKF owner is explicitly named.
   - Create the OKF artifact in a clean worktree from `origin/main`, not a dirty feature branch.
   - Add/update the relevant OKF index.
   - Verify frontmatter, required sections, local links, index link, and token/secret smoke with `/tmp/hermes-verify-*`.
   - Merge the OKF PR and post the PR/path evidence back to Linear.

4. **Route remaining executable items to AGY**
   - Add `agent:agy` + `dispatch:ready`.
   - Remove stale competing `agent:*` labels unless intentionally preserving a non-operational taxonomy label.
   - Always remove stale `agent:needs-human-review`, `agent:peer-review`, and `dispatch:paused` unless Michael explicitly says the item still needs human review.
   - If AGY/dispatcher immediately moves issues to In Progress and stale NHR labels remain or reappear, run a second cleanup pass.

5. **Verification**
   - Run a final live Linear readback over every touched issue.
   - Assert canceled issues have `state.type == canceled` and no `agent:*`/`dispatch:*` labels.
   - Assert OKF-converted issue is not AGY-routed, has the OKF evidence comment, and the OKF doc exists on `origin/main`.
   - Assert AGY-routed issues have `agent:agy + dispatch:ready` and lack stale human-review/peer-review/paused labels.
   - Report this as ad-hoc targeted verification, not full Linear/OKF suite green.

## Pitfalls

- Do not classify all `agent:needs-human-review` labels as “Michael needed.” They are often stale sludge.
- Do not leave `dispatch:ready` on canceled or completed issues.
- Do not trust a dirty OKF worktree for documentation landing; use a clean worktree and small PR.
- Do not treat a failed mutation schema as partial success. Verify before continuing; Linear `issueUpdate` requires the issue id as a separate argument in this environment.
