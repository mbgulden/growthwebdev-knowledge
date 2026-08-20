# Prismatic Proof Loop Rate-Limit Follow-up — 2026-07-08

## When this applies

Use this reference when a Golden Thread / Linear task-creation run partially creates epics/tasks, then Linear mutations hit the shared tenant quota (`429 RATELIMITED`, 2500 requests/hour).

## Durable workflow lesson

1. **Attempt live Linear once, but do not spin.** If Linear returns `429 RATELIMITED`, stop mutating and switch to offline preservation.
2. **Persist the full desired task tree offline.** Save both JSON and Markdown under a durable output directory. Include known live partial state, desired epics, child tasks, parent-child intent, and exit criteria.
3. **Update the idempotent continuation script.** The retry script should upsert by title, preserve parent-child links, remain silent while still rate-limited, and print a final issue list exactly once on success.
4. **Add root-cause work to the task tree, not just the chat.** If rate limits were unexpected after an event-driven migration, create a task to find the actual request burners and budget bypasses.
5. **Verify the script edit before reporting.** Create a temporary verifier under `/tmp` using `tempfile` with a `hermes-verify-` filename prefix. Keep it offline/non-mutating:
   - `py_compile` the changed script.
   - Parse the script with `ast`.
   - Extract static `epics` data without executing Linear calls.
   - Assert expected epic count, child count, added root-cause task placement, and required exit-criterion phrases.
   - Assert/report `linear_api_calls_made = 0`.
   - Delete the verifier and report cleanup.
6. **Label evidence correctly.** This is **ad hoc targeted verification**, not canonical/full-suite green.

## Rate-limit root-cause task shape

Title:

`[Prismatic] Root-cause Linear API rate-limit exhaustion after event-based migration`

Recommended parent:

`[Epic] Prismatic Proof Loop 4 — Operator Control Plane / Phone-First Factory View`

Exit criterion:

A report names the top Linear request burners, exact scripts/jobs/processes, whether each is event-driven vs polling, and lands either a fix or explicit disable/owner action for every burner above budget.

## Investigation cues from this session

- An event-driven supervisor can still contain fallback Linear polling/fetch paths.
- Direct `urllib` GraphQL calls to `https://api.linear.app/graphql` can bypass the shared `LinearBudget` wrapper.
- A stale or empty `linear_budget.db` while the live API is exhausted means active calls are likely happening outside local budget accounting or in a different state directory.
- Watchdog restart loops can repeatedly trigger startup fetches even if the primary design is event-driven.

These cues are starting hypotheses only; verify from live process list, logs, cron state, and budget DB before claiming root cause.
