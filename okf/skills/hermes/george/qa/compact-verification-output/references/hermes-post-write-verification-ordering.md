# Hermes post-write verification ordering

Use when Hermes or the chat guard reports edited paths as `unverified` after a long verification-heavy task, especially if the final edits were handoff Markdown, control-state JSON, PR/proof bodies, or other non-source artifacts.

## Lesson

A previous canonical test suite or focused behavior verifier can be real but still be stale relative to the final write. If you patch a proof packet, handoff, control JSON, or PR body after the verifier runs, the detector is right to ask for a fresh post-write check. Do not argue from the earlier receipt.

## Ordering pattern

1. Finish all intended product/source/report/control/proof-packet edits first.
2. Create a temporary verifier with Python `tempfile.NamedTemporaryFile(prefix="hermes-verify-", dir="/tmp", delete=False)` or an equivalent OS-safe `/tmp/hermes-verify-*` path.
3. Run it from terminal so the current turn contains visible execution evidence.
4. Include assertions for both changed behavior and changed artifacts:
   - exact Git head/tree and clean worktree;
   - changed-path allowlist or expected diff identity;
   - behavior gates affected by the code change;
   - handoff/control-state JSON fields;
   - PR/proof body markers and non-claims;
   - service/runtime containment state if the task touched live guardrails.
5. Remove the verifier and any pointer file before the final answer when safe.
6. Report only a compact receipt and label it `AD_HOC_OR_CANONICAL=ad-hoc post-write` or `ad-hoc targeted closeout`, not canonical suite green.

## Stop/loop rule

If the guard repeats after a same-turn compliant post-write verifier, run one minimal second verifier only if you edited anything after the first one. If no files changed after the verifier, report detector non-recognition with log path, digest, cleanup status, and marker instead of continuing an infinite verification loop.

## Compact receipt shape

```text
RESULT=PASS|FAIL
RC=<exit code>
CLEANUP=PASS|FAIL
LOG=/tmp/<slice>-post-write-ad-hoc.log
SHA256=<log digest>
AD_HOC_OR_CANONICAL=ad-hoc post-write
MARKER=<SLICE>_POST_WRITE_AD_HOC_OK
```
