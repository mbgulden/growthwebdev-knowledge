# Ned cron finalize path + clean branch recovery

## Trigger

Use this when a Ned cron/autonomous task is ready for `finalize_task.sh`, or when a task branch was polluted by an auto-checkpoint/WIP commit that does not satisfy the `[Ned] ... (#ISSUE)` convention.

## Durable lessons

### Use the absolute finalize script path in Ned cron shells

In Ned profile cron shells, `$HOME` may be `/home/ubuntu/.hermes/profiles/ned/home`. Running:

```bash
bash ~/.hermes/profiles/ned/scripts/finalize_task.sh GRO-XXXX ned/GRO-XXXX ned
```

can expand to a bogus nested path like:

```text
/home/ubuntu/.hermes/profiles/ned/home/.hermes/profiles/ned/scripts/finalize_task.sh
```

Use the absolute path instead:

```bash
FINALIZE_LOCK_FILES='plugins/pwp tests docs scripts' \
  /home/ubuntu/.hermes/profiles/ned/scripts/finalize_task.sh GRO-XXXX ned/GRO-XXXX ned
```

This is not a general claim that `~` is broken; it is a Ned cron/profile-shell pitfall.

### Recover cleanly from auto-checkpoint/WIP branch pollution

If an auto-checkpoint/WIP commit lands on the task branch with a nonstandard message, do not force-push or rewrite shared/protected history. Create a clean final branch from the target base, apply the net diff, and recommit once with the required Ned prefix.

Example pattern:

```bash
git checkout -b ned/GRO-XXXX-final origin/deploy-fresh
git diff origin/deploy-fresh..ned/GRO-XXXX | git apply --index
git commit -m '[Ned] <task summary> (#GRO-XXXX)'
python3 -m pytest <focused tests> -q
git push -u origin HEAD
FINALIZE_LOCK_FILES='plugins/pwp tests docs scripts' \
  /home/ubuntu/.hermes/profiles/ned/scripts/finalize_task.sh GRO-XXXX ned/GRO-XXXX-final ned
```

Keep the original branch for forensic fallback. The clean branch should be the one used for PR/finalize evidence.

## Verification nudge follow-up

If the system later says no canonical verification was detected, obey the nudge narrowly: create a `/tmp/hermes-verify-*` script, exercise the changed behavior directly, remove the verifier, and report it explicitly as ad-hoc verification rather than suite green.
