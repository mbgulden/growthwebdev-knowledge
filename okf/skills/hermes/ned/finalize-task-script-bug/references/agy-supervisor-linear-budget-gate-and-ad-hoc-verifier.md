# AGY supervisor Linear budget gate + repeated ad-hoc verifier pattern

## When this applies

Use this when AGY appears idle even though Linear has `agent:agy` + `dispatch:ready` work, or when a post-edit verifier prompt says there is no fresh canonical test/lint/build evidence for a touched code path.

## Durable lesson

A long-running AGY supervisor can be process-alive but operationally stale. Do not stop at `ps` or `systemctl active`.

Check all three:

1. Process health: supervisor process exists and is not zombie/stale.
2. Log freshness: `/tmp/longrun-watchdog.log` mtime and recent lines show current polling/launch activity.
3. Work evidence: Linear issues receive `Started:` comments and logs show `picked up`, `launching AGY`, `STARTED.md`, `RESULT.md`, and ideally `DONE`.

## Linear budget preflight failure mode

Observed AGY restart blocker:

```text
LinearBudget unavailable: ModuleNotFoundError: No module named 'prismatic.linear.budget'
startup gates failed; aborting before worker spawn
```

Fix class: restore/importable `prismatic.linear.budget.LinearBudget` in the active engine checkout and avoid optional early-startup imports that may not exist in the supervisor context. The budget module should be importable with only stdlib + repository path and should honor `PRISMATIC_STATE_DIR` for `linear_budget.db`.

Minimum behavior contract:

- `from prismatic.linear.budget import LinearBudget, linear_budget` succeeds.
- Import does not require optional settings glue such as `prismatic.core.settings`.
- `LinearBudget(db_path=...)` creates `budget_state` and `budget_logs` tables.
- `check_and_consume()` logs both consume and reject events.

## Repeated detector prompt pattern

If the system repeats:

```text
Verification status: unverified
No canonical test/lint/build command was detected.
Create a focused temporary verification script under /tmp using a hermes-verify- prefix...
```

run a fresh verifier every time; do not cite a previous run. The detector keys on fresh evidence.

Required shape:

1. Create the verifier with Python `tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp")` or equivalent OS-safe API.
2. Print the verifier path, changed path, and that this is ad-hoc focused verification, not suite green.
3. Assert the changed behavior directly, not just import success.
4. Print assertion summary and `verification_exit=0` on success.
5. Delete the temporary verifier in `finally` and print cleanup status.

Example assertions for `prismatic/linear/budget.py`:

- module imports and exposes `LinearBudget` + `linear_budget`;
- optional settings module is not imported;
- `PRISMATIC_STATE_DIR` override is honored;
- DB file and expected schema are created;
- consume/reject behavior matches a small bucket;
- `budget_logs` records consume/reject actions.

## Reporting language

Say explicitly: **ad-hoc focused verification, not full suite-green**.

Do not claim the entire repo is verified unless a canonical suite/build actually ran and passed.