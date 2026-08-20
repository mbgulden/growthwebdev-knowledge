# Finalizer dry-run and gated-task safety

## Trigger

Use this when a Ned task is held behind an unmet dependency, lane guard, or ordered rollout gate and you need to inspect finalization behavior without changing Git, locks, or Linear.

## Safe dry-run invocation

`finalize_task.sh` accepts `--dry-run` **only as its first argument**:

```bash
bash ~/.hermes/profiles/ned/scripts/finalize_task.sh --dry-run GRO-XXXX ned/GRO-XXXX ned
```

Do not append `--dry-run` after the issue/branch/agent arguments. The parser treats only `$1` as the flag; a trailing flag can leave `dry_run=false` and perform the normal commit/unlock/Linear-transition/comment path.

Before proceeding, confirm the output includes `dry_run=true` and only `[dry-run] would:` actions. If it does not, stop and treat the command as mutating.

## Gated-task rule

A dependency gate is not a completed task. If the prerequisite is unmerged or not independently accepted:

1. Do not run normal finalization: it promotes the child to In Review and posts completion evidence even when no implementation occurred.
2. Keep the child in Todo and report the exact prerequisite, PR/ancestry evidence, and human decision needed.
3. Release only locks acquired for the aborted investigation, using the actual lock owner/path.
4. If an accidental finalization occurs, immediately verify Linear state and comments, restore the appropriate state (normally Todo), and post a concise correction that explicitly lists non-claims (no build, artifact, deploy, or code change). Verify the correction comment and clean branch before reporting.

## Why it matters

The finalizer is deliberately broad: in addition to Git, it can unlock shared lanes and mutate Linear. A clean working tree is not sufficient protection against an erroneous finalization.
