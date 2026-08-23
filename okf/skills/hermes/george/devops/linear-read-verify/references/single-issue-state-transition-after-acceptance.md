# Single-issue Linear state transition after exact-head acceptance

Use this reference only when all of the following are true:

- Michael has explicitly authorized the specific Linear write, or standing authorization in the active Prismatic lane covers `mark <issue> Done after exact-head CLEAN/PASS`.
- The implementation candidate has an independently accepted exact head (`CLEAN/PASS`) and the issue transition is the final bookkeeping action for that accepted slice.
- The intended mutation is exactly one issue state field, e.g. `Todo` -> canonical `Done`.
- No labels, descriptions, assignees, relations, parent/child topology, comments, projects, or other issues need mutation.

If any condition is false, fall back to the normal fail-closed Linear writer packet workflow.

## Safe bounded pattern

1. **Bind source and authorization**
   - Record the accepted commit/tree and independent review handle.
   - Confirm the worktree exact head matches the accepted head and tracked status is clean.
   - State the mutation scope in one sentence: `one issue stateId only; no topology/prose/labels/comments`.

2. **Live baseline read**
   - Query only the target issue by identifier.
   - Capture: issue id, identifier, `updatedAt`, `completedAt`, current state id/name/type, team id/key, and available completed states.
   - Select the canonical completed state by exact id/name/type (`Done`, `completed`) rather than guessing from display order.

3. **Guard before write**
   - Fail closed if the issue id, identifier, prior state, prior `updatedAt`, or prior `completedAt` differs from the live baseline.
   - Fail closed if the canonical target state is missing or ambiguous.
   - Fail closed if the local candidate head/tree no longer matches the independently reviewed exact head.

4. **Durable intent before mutation**
   - Append a JSONL receipt line before the mutation with: timestamp, target issue id/identifier, expected-before state/timestamp, intended target state, candidate commit/tree, and non-claims.
   - Use a restricted temp or profile-local path; never include credentials.

5. **One mutation**
   - Execute a single `issueUpdate(id, input:{stateId:<Done>})`.
   - Do not retry by reposting the mutation if the transport result is ambiguous. Reconcile by readback first.

6. **Immediate reconciliation**
   - Read the same issue back through the read-only broker when possible.
   - Accept only if state id/name/type match the canonical completed state and `completedAt` is non-null.
   - Append a result receipt line with status, after-state, updatedAt, completedAt, and any redacted mutation error class.
   - Hash the receipt and report compactly.

## Reporting packet

```text
RESULT=<PASS|BLOCKED>
ISSUE=<TEAM-N>
MUTATION_SCOPE=stateId-only
BEFORE=<state name/id updatedAt completedAt>
AFTER=<state name/id updatedAt completedAt>
CANDIDATE_HEAD=<sha>
REVIEW=<handle:CLEAN/PASS>
RECEIPT=<path>
RECEIPT_SHA256=<sha256>
NOT_CLAIMING=push,PR,merge,deployment,cron/timer mutation,production DB mutation,or downstream issue start
```

## Post-mutation drift forensics (hit live 2026-08-21, GRO-4821)

Within ~10 minutes of a successful `Done` mutation, a re-run of the same writer can fail its `updatedAt` drift guard, or a later readback can show a different `completedAt`/`updatedAt` than the receipt. **Do not assume a fault and do not re-mutate.** The issue may have been legitimately toggled by a human (Linear attributes API calls to the account owner, so the history trail shows your mutation AND Michael's manual toggles under the same actor name).

1. **Query the issue history trail — it is the authoritative audit record:**
   ```graphql
   query C($id: String!) {
     issue(id: $id) {
       identifier
       history(first: 20) {
         nodes {
           createdAt
           autoClosed
           fromState { id name }
           toState { id name }
           actor { name }
         }
       }
     }
   }
   ```
   Reconstruct the full sequence (e.g. `Todo→Done` (mutation) → `Done→In Progress` (manual) → `In Progress→Done` (manual)). If the final `toState` is the canonical completed state, the target holds — the later entries are human-driven, not agent action.
2. **Schema notes (verified live 2026-08-21):** `issue.history` exists (type `IssueHistoryConnection`, nodes carry `fromState`/`toState`/`actor`/`autoClosed`/`changes`/label deltas). `Comment` has **no `author` field** — use `user { name }`. `issue.pullRequests` does not exist (no PR-link field on `Issue` in this workspace).
3. **`completedAt` resets on re-entry.** Every re-entry into a completed state sets a new `completedAt`; the receipt records the mutation's own readback, which may differ from the live value — that is expected, not drift corruption. Never "recover" a receipt because live timestamps moved.
4. **Record the full trail in the handoff state file** (e.g. a `blocker.note` line: timestamps + transitions + actor attribution) so a future agent doesn't misread the toggles as an agent regression.
5. **A drift-guard BLOCKED on re-run is the guard working.** Report it as PASS-with-explanation (guard fired, zero writes), then cite the history trail for the source of the drift.

## Pitfalls

- Do not create a fresh precontract, blocker document, or broad writer review merely to move one already-accepted issue to `Done` when the scope is exactly one state field and authorization is already present.
- Do not use session history as current Linear proof; always take a live baseline and a readback.
- Do not mutate `Done - Doc Pending` unless the active request specifically asks for that state; bind the exact canonical target.
- Do not start the next Linear issue in the same mutation/report unless Michael explicitly asked for it. Advance the pointer only.
