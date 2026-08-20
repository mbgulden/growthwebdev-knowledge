# Prompt4 packet-gate PR workflow reference

Session pattern captured from a Prismatic governance repair where Prompt4 was falsely blocked by stale aggregate packet logic and an incomplete terminal-run reconciliation path.

## Durable lessons

### 1. Diagnose the computed gate, not just the symptom

If a dashboard/monitor says a packet is blocked, locate where `BLOCKED_PACKET_PRESENT` or the equivalent field is computed. In this case the useful path was to inspect monitor code, writeback code, and tests until the aggregation rule was visible.

The durable distinction:

- Bad pattern: “any blocked packet marker exists anywhere in Linear comments/logs.”
- Good pattern: “classify the latest valid packet per assigned agent, with terminal-run/writeback reconciliation included.”

### 2. A gate fix may not unlock the next prompt

Even after the monitor reports Prompt4 correctly, keep the boundary explicit. The fix can establish accurate preflight/gate state while still not claiming Prompt5 readiness, production deployment, or canonical full-suite green.

Useful PR/body wording:

> This fixes Prompt4 gate classification/reporting. It does not unlock Prompt5 automatically.

### 3. Branch prefix can be a governance lane, not just a naming convention

A `fix/...` branch may look semantically correct but can map to Jules’ review-only lane in `PRISMATIC_ENGINE.yaml`. For broad orchestrator/governance fixes, check branch prefix ownership first. If the hook rejects the push, rename to the correct lane prefix rather than bypassing the hook.

Observed pattern:

```text
fix/prompt4-latest-packet-gate -> rejected by lane guard
feature/prompt4-latest-packet-gate -> valid orchestrator-owned prefix
```

Verification after rename:

```bash
git push -u origin feature/prompt4-latest-packet-gate
git ls-remote origin refs/heads/feature/prompt4-latest-packet-gate
```

Confirm remote SHA equals local `git rev-parse HEAD`.

### 4. PR readback should verify scope and language

After `gh pr create`, immediately read the PR back and assert the public artifact matches intent:

- open, non-draft;
- correct base/head refs;
- head SHA equals pushed commit;
- file list exactly matches expected focused scope;
- PR body includes markers, test evidence, and non-claims;
- GitHub checks are watched/read until they have real conclusions.

Example final proof shape:

```text
COMMAND=git push feature/<slice>; gh pr create --base main; gh pr checks <n> --watch; final GitHub PR readback
RESULT=PASS
LOG=<verification-log-path>
SCOPE=Push verified governance gate fix and open focused PR
AD_HOC_OR_CANONICAL=GitHub CI
NOT_CLAIMING=PR merged,Prompt5 unlocked,production deployed,auto-merge enabled,canonical full-suite green
MARKER=<SLICE_MARKER>
```

### 5. Keep session records as appendices, not new narrow skills

This pattern belongs under the class-level Prismatic coordination workflow skill. Future similar slices should add concise references here rather than creating one-off skills named for individual PRs, issue numbers, or transient marker strings.
