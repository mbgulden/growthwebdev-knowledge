# Ned checkpoint branches and lane-guarded pushes — 2026-07

When Ned checkpoints mixed HDE/Prismatic staging work before public traffic, the local commit may include valuable docs plus scripts. The remote lane guard can reject pushes containing docs/content paths outside Ned's write lane even if the checkpoint branch name is valid.

## Safe pattern

1. Commit locally on a `ned/` branch only after:
   - swarm locks,
   - staged diff review,
   - staged secret scan,
   - real verification.
2. Push only the `ned/` branch, never protected branches.
3. If lane guard rejects non-Ned paths:
   - do not force,
   - do not drop docs silently,
   - create a local `git bundle` for the checkpoint commit,
   - report blocked paths and bundle path,
   - route docs/content files to the owning lane/orchestrator or split into lane-compliant commits.

## Why

A checkpoint is preservation, not ownership override. Lane guard rejection means the work needs routing, not deletion.
