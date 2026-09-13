# Stale-ticket live closeout (Phase 0.5 catches a ticket that's already done)

Session-derived pattern (2026-09-13, Fred cron golden-thread run, GRO-4909 AOT
governance watchdog). Use when a Linear ticket you select as the "next action"
shows an open state (In Progress / Todo) but the underlying work appears already
landed — the ticket outlived the merge.

## Trigger

You pick a ticket as the Golden Thread's next action, but Phase 0.5 live-verify
shows the fix is already on `origin/main`, live production already serves the
correct state, and any watchdog/guard already PASSES. The ticket is in a stale
open state (its `updatedAt` predates the merge). **This is a closeout, not a
build.** Do NOT create a new Linear tree or re-implement — Phase 0.5 exists
precisely to stop "ship already-shipped."

## Verify the ticket is actually done (read-only, before any mutation)

- **Fix commit on the production branch:** `git fetch origin` then
  `git merge-base --is-ancestor <fix-sha> origin/main` (exit 0 = yes).
- **Production branch file state:** `git show origin/main:<path>` to confirm the
  relevant config/content actually changed on main (not just on a branch).
- **Live production URL:** `curl -s -o /dev/null -w "%{http_code}" <prod-url>`
  plus `curl -s <prod-url> | grep -oE '<expected-marker>'` to confirm the marker
  the ticket cares about is served live.
- **Watchdog/guard (if the ticket is a guard failure):** run the actual guard
  (e.g. `python3 scripts/prismatic_web_governance.py --config
  .prismatic-web-governance.json`). Exit 0 = pass. Read the report to confirm the
  specific check named in the ticket now passes; distinguish the ticket's check
  from unrelated pre-existing WARNs (leave those to their lane owner).

## Close out with evidence (this user judges Done by evidence, not by code landing)

1. **Post an evidence comment on the Linear ticket** with the full verification
   packet (commit SHA on main, live-URL status + marker, guard run + exit code,
   note that the ticket's `updatedAt` predates the merge so the state was stale).
2. **Move the ticket to Done** via `issueUpdate` — `id` is a **top-level arg**
   (not inside `input`), `stateId` (UUID) inside `input`. Read the Done UUID from
   `workflowStates(filter: { team: { id: { eq: "<teamId>" } } })` (omit `first` —
   it's not on this filter type).
3. **Read back** the ticket's `state { name type }` to confirm `completed`, and
   confirm it no longer appears in the team's non-completed set (0 matches).

## Do NOT do

- Don't re-run the watchdog / re-curl production as if the guard "might have
  regressed" — it was just verified live this run. Only re-check if a human
  reports a regression or the next AOT cron flags the same check FAIL.
- Don't touch unrelated pre-existing guard WARNs (e.g. a stale content PR, old
  audit branches) — those belong to their lane owner (Kai here), not the agent
  closing this ticket.
- Don't treat the closeout as "the ticket is done so I'll skip Linear" — reconcile
  the ticket state itself, that's the whole point.

## Linear GraphQL gotchas hit building this (see
`agy-gt-linear-auth-routing-and-secret-hygiene-2026-07-18.md` +
`linear-state-id-graphql-2026-07-26.md` for the auth/stateId context)

- `orderBy: priority` is **not** a valid `PaginationOrderBy` enum — drop it; sort
  client-side.
- `IssueFilter.identifier` **does not exist** — filter by `team` + (optionally
  `state.type.neq: "completed"`), then match the identifier client-side.
- `issueUpdate(id: "<uuid>", input: { stateId: "<uuid>" })` — `id` is top-level;
  putting `id` inside `input` returns a 400 validation error.
- `workflowStates` filter does **not** accept `first`.
- Multi-line GraphQL query strings passed via a bash heredoc/`-d` trip a
  "Bad control character in string literal" JSON error — write the query to a
  file and use `curl --data @file.json`, or build the payload in Python
  (`urllib`/`json.dumps`).
