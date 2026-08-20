# `finalize_task.sh` argument-validation pitfall

**Captured:** 2026-06-29 ~20:46Z (Pass-16 on the GRO-484..502 recurring-misroute batch).
**Status:** Validated. Permanent guardrail for any Ned pass that is about to call `finalize_task.sh`.

---

## TL;DR

`~/.hermes/profiles/ned/scripts/finalize_task.sh` accepts ANY positional args without validation. There is no `--help` mode, no placeholder-string check, no Linear-ID pattern check, and no refuse-to-run-on-empty-args gate. If you invoke it without thinking, it WILL:

1. Commit whatever is in the working tree (auto-staging anything untracked), under a `[ned] <issue>: finalize (auto-commit on budget exhaustion)` commit message. The script's auto-commit-on-budget-exhaustion path is on by default.
2. Release the hardcoded locks `tests`, `prismatic`, `scripts`, `.github/workflows` from `swarm_locks.json` — regardless of which issue you actually intended to finalize.
3. Attempt a Linear API state-transition + comment-post with the bogus issue ID. The API rejects it (`WARN: could not resolve Linear UUID for <bogus-value>`), but only AFTER steps 1 and 2 have already mutated real state.

Result: a clearly-bogus commit at the top of `git log`, four unrelated locks released, and a working tree that's no longer in the state you expected.

---

## The failure mode (Pass-16 evidence)

I opened this pass by running `bash ~/.hermes/profiles/ned/scripts/finalize_task.sh --help` to discover the script's CLI. The script has no help mode, so the args resolved as:

- `$1` (issue): `--help`
- `$2` (branch, default): `ned/GRO-PLACEHOLDER`
- `$3` (agent, default): `ned`

Result: a real commit `2885d4a3` was created on the working branch — `[ned] --help: finalize (auto-commit on budget exhaustion)` — auto-staging and committing `okf/operations/2026-06-30-overnight-factory-diagnosis.md` (a sibling-agent file that was untracked in the working tree; the commit-gate auto-staged it because it was in the working tree and the gate doesn't distinguish sibling-owned untracked files). Four locks were also released (the script's hardcoded paths). The Linear API call then failed with `WARN: could not resolve Linear UUID for --help` — but by then the commit and unlocks had already happened.

The branch's git log now has a clearly-bogus commit at the top, which a future reconstructor will have to recognize and reconcile.

---

## Pre-call guard checklist (do this BEFORE invoking the script)

1. **Never invoke `finalize_task.sh` "to see what it does."** It does not have a `--help` / `-h` / `--dry-run-only` mode. Reading the script with `read_file` or `cat` is the safe way to discover its CLI. If you want a dry-run, pass `--dry-run` as the 4th positional arg (the script DOES support that, but only as the 4th arg, after issue / branch / agent — pass them all explicitly).

2. **Always pre-stage your issue ID, branch, and agent as explicit values before calling.** Reject any of: `--help`, `-h`, `?`, empty string, `GRO-PLACEHOLDER`, `XXX`, `TODO`, or any string that doesn't match `^GRO-[0-9]+$` (uppercase GRO prefix + digits only). If you can't fill in a real value, you don't have enough information to call the script — go back to Step 4 (read the task).

3. **Pre-check `git status` before AND after the call.** If a bogus commit lands (like pass-16's `2885d4a3`), `git reset --hard HEAD~1` to undo it BEFORE doing anything else. Do NOT amend / rebase / push; just reset. Then write a follow-up audit-doc note that explains the rollback so the git log stays self-documenting.

4. **Recognize the bogus-commit signature in `git log`:** commit message starts with `[ned]` (lowercase `n` — the script uses lowercase, the human/manual passes use `[Ned]` capital N), contains `finalize (auto-commit on budget exhaustion)`, or has an obviously-non-issue subject like `--help` / `-h` / a flag string. These are signature-fingerprints of an accidental finalize call. Reset and audit-doc.

5. **The script's auto-commit-on-budget-exhaustion path is double-edged.** It exists so a Ned pass that runs out of tool budget can still commit work-in-progress safely. But it also means ANY call to the script, valid or not, will commit whatever is in the working tree. Treat the call as load-bearing: check `git status` first, verify the staged files are yours, then call.

---

## Suggested hardening (not yet implemented — note for a future infra pass)

A future pass could add argument validation to the top of `finalize_task.sh`:

```bash
ISSUE="${1:-}"
BRANCH="${2:-}"
AGENT="${3:-ned}"

if [[ -z "$ISSUE" || "$ISSUE" =~ ^- || "$ISSUE" == "GRO-PLACEHOLDER" || ! "$ISSUE" =~ ^GRO-[0-9]+$ ]]; then
  echo "[finalize] FATAL: issue ID '$ISSUE' is invalid. Expected UPPERCASE GRO-NNNN. Run 'read_file ~/.hermes/profiles/ned/scripts/finalize_task.sh' to discover the CLI." >&2
  exit 64  # EX_USAGE
fi
```

That single guard would have prevented Pass-16's bogus commit entirely. Filed as a follow-up under the `ned_finalize_script_hardening` topic; not Ned's call to land (requires Michael's greenlight on the script edit, since it changes shared infra behavior).

---

## Related references

- `references/okf-prepush-hook-silent-block-detection-and-lane-governance-gap.md` — r133 Symptom-3 protocol (sibling-owned untracked files)
- `references/recurring-batch-suppress-pitfalls.md` — sustained-SUPPRESS pass pitfalls
- `SKILL.md` Pass-16 SILENT-pass update — full narrative + checklist context