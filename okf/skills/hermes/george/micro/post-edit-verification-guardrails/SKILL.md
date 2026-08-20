---
name: post-edit-verification-guardrails
description: "Produce guard-compatible post-edit verification after code or packet changes: OS-safe /tmp/hermes-verify probes, direct test/lint/build command visibility, durable proof logs, cleanup rules, and honest ad-hoc-vs-canonical non-claims."
---

# post-edit-verification-guardrails

Use this when a session edits code, generated assets, review packets, or evidence files and a system/user guard asks for fresh verification.

## Core rules

1. **Act, don't argue with the guard.** If the guard says verification is missing, run a fresh, minimal, guard-compatible proof in the same response window instead of only explaining that prior proof passed. Prior receipts are context, not a substitute for action on a new guard message.
2. **Use an OS-safe tempfile path for probes.** Create behavior probes with Python `tempfile.mkstemp(prefix="hermes-verify-", suffix=".py" or ".sh", dir="/tmp")`; do not hand-pick a fixed path. Create, write, run, and delete the disposable probe inside one `terminal` transcript whenever tools permit. Avoid `write_file` for disposable `/tmp/hermes-verify-*.py` probes because the post-edit detector can record the probe itself as a changed path and re-trigger the guard; reserve durable `/tmp/hermes-verify-*` paths for proof logs/receipts, not transient source files. **If you accidentally used `write_file` and the guard lists that `/tmp` script as changed, the next proof must not use `write_file` again:** create/write/run/delete the replacement probe entirely inside a single shell transcript and include `test ! -e <stale-temp-script>` assertions before reporting.
3. **Make the probe visible to pytest when possible.** For Python behavior regressions, write a small pytest file and run `pytest -q /tmp/hermes-verify-*.py` with the worktree on `PYTHONPATH`. This both satisfies the temp-probe requirement and gives the detector a recognizable test command. If a prior disposable verifier appears in the guard's changed-path list, assert that stale path is absent in the fresh transcript.
4. **Use `set -o pipefail` whenever proof output is piped through `tee`.** Without pipefail, a failing pytest/lint command can be masked by a successful `tee`, producing a misleading green shell status. Treat missing pipefail as a verifier setup defect and rerun before sealing.
5. **Run project commands directly, not only inside a script.** If the detector asks for test/lint/build evidence, invoke the relevant commands at top level where possible: focused `pytest`, dashboard/build check, `ruff check`, `ruff format --check`, `python -m compileall`, and `git diff --check`.
6. **Separate temp scripts from proof logs.** Clean up the temporary executable/probe when possible. Keep durable proof logs under `/tmp/hermes-verify-*` and report their SHA-256. If another Prismatic evidence rule says not to delete `/tmp/hermes-verify-*`, interpret that as preserving the proof log/receipt, not as forbidding cleanup of the disposable tempfile probe.
7. **Classify honestly.** Label focused or tempfile proofs as `AD_HOC_OR_CANONICAL=ad-hoc targeted`. Only claim canonical suite green when the repository's canonical suite actually passed.
8. **Bind changed artifacts.** Include the changed source/test/packet hashes or an explicit packet SHA assertion in the final verification command so proof covers the exact bytes after all edits. Handoff/evidence packet edits are changed artifacts; if you patch the handoff after a verifier, run one final verifier that asserts the final handoff marker/hash.
9. **Make packet boundaries machine-readable before proof.** Evidence/review packets that later need verification should carry explicit `KEY=value` fields for authority, mutation count, active sequence, nonclaims, and marker. Do not make the verifier depend on prose like “not authorized” or on Unicode arrows if the exact sequence/boundary matters.

## Guard-compatible proof packet shape

```text
TEMPFILE=/tmp/hermes-verify-<random>.py
TEMPFILE_CREATION=tempfile.mkstemp
TEMPFILE_PYTEST=<N> passed
PROJECT_FOCUSED=<N> passed
BUILD_LINT_FORMAT_COMPILE_DIFF=PASS
PACKET_OR_MANIFEST_SHA_ASSERTION=PASS
TEMP_SCRIPT_CLEANED=true
LOG=/tmp/hermes-verify-<topic>.log
LOG_SHA256=<sha256>
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=canonical full-suite green
MARKER=<stable_marker>
```

## References

- `references/prismatic-guard-compatible-tempfile-proof.md` — concrete Prismatic proof pattern for random tempfile pytest probes plus direct command detection.
- `references/repeated-detector-stale-temp-path.md` — repeated post-edit detector warning pattern: rerun a current-turn OS-safe verifier once, prove stale temp paths absent, then classify further repeats as ingestion blockers with log/hash.
- `references/repeated-guard-dual-path-proof.md` — when a guard repeats `No canonical test/lint/build command was detected`, satisfy both paths in one terminal transcript: tempfile behavior probe plus direct top-level `ruff`/`pytest` commands tee'd into the same log.
- `references/repeated-guard-worktree-python-m-pytest.md` — escalation pattern when repeated guard warnings continue after valid receipts: run from the worktree with the project venv's `python -m pytest` plus visible direct lint/format commands, then stop editing and classify further repeats as ingestion stale.
- `references/clean-wheel-install-source-isolation-proof.md` — corrected packaging proof when a wheel/install receipt may have been contaminated by source-tree metadata or interpreter path state.
- `references/tempfile-detector-and-failure-parity.md` — repeated detector residue from disposable `/tmp/hermes-verify-*` probes, cleanup/absence proof, and exact full-line canonical failure parity for baseline-red suites.
- `references/final-packet-edit-reverification.md` — when a handoff/evidence packet is edited after proof, rerun a final OS-safe verifier that binds both code behavior and final packet markers/hashes.
- `references/rendered-refresh-persistence-proof.md` — rendered UI proof pattern for polling/hydration fixes: preserve DOM/user state across at least two refresh intervals instead of relying on static source checks.
- `references/machine-readable-packet-boundary-proof.md` — packet/evidence verifier pattern: add explicit `KEY=value` authority/sequence/nonclaim fields before hashing; parse fields and print neutral labels when authorization strings may be display-masked.
- `references/pipefail-tee-and-disposable-verifier-seal.md` — final accepted-head seal pattern: `set -o pipefail` with `tee`, exact packet/handoff/state hash assertions, direct focused/lint commands, and cleanup of disposable verifier scripts.
- `references/detector-literal-final-with-stale-temp-absence.md` — final repeated-guard pattern when the detector lists stale `/tmp` paths: prove stale paths absent, run top-level `python -m pytest`/focused tests/lint/format/build, clean the disposable probe, and hash the log after appending the marker.
- `references/tempfile-script-detector-residue.md` — when the detector starts listing the disposable `/tmp/hermes-verify-*.py` itself as a changed path, create/write/run/remove the next temp probe inside one terminal transcript and assert stale temp absence.
- `references/tempfile-probe-single-transcript-write.md` — preferred implementation pattern: do not use `write_file` for disposable `/tmp` probe source; create/write/run/delete it in one terminal transcript and keep only the proof log.
- `references/write-file-temp-probe-detector-loop.md` — concrete repeated-guard failure mode when `write_file` records a disposable `/tmp/hermes-verify-*.py` as changed; fix with a same-transcript create/write/run/delete probe and stale-path absence checks.
- `references/concurrency-race-tempfile-proof.md` — exact proof shape for atomic/concurrent creator repairs: force winner/loser paths, assert loser reuse, no partial/temp leaks, stale temp absence, and direct project commands in the same transcript.
- `references/process-tree-cleanup-probes.md` — exact proof shape for command-runner/process-group repairs: successful leader exit is not enough; force a pipe-closing descendant and assert the delayed marker remains absent.
- `references/pinned-supervisor-process-group-proof.md` — robust process-group containment pattern when an external SIGCHLD reaper can consume the child: keep a live supervisor as PGID leader until one-shot cleanup signals the group.
- `references/special-file-and-one-shot-cleanup-proof.md` — session-derived proof pattern for nonblocking FIFO/special-file race rejection, descriptor-bound state DB inspection, one-shot process-group cleanup, and stale temp-script absence under repeated guards.
- `references/pr-recap-semantic-blocker-guard-proof.md` — exact proof shape after semantic recap blockers: one regression per accepted blocker, terminal-created tempfile probe, stale-temp absence checks, and ad-hoc/canonical separation.

## Rendered refresh-state fixes

When a dashboard/UI edit fixes a reset caused by polling, hydration, or WebSocket refresh, static source/lint checks are not enough. Reproduce the live interaction, wait through at least two actual refresh intervals, and assert user-visible state is preserved: expanded controls stay expanded, selected preview/content remains selected, and key DOM nodes remain connected when that is the intended preservation mechanism. Label this proof ad-hoc unless the full canonical suite also ran.

## Pitfalls

- A shell script that runs `pytest` internally may not be detected as a canonical/focused command by outer guards. Prefer direct command invocations after or alongside the script.
- Any proof command piped through `tee` must start with `set -o pipefail`; otherwise a failing `pytest`/lint command can be hidden by `tee`'s zero exit. If that happens, classify it as verifier setup failure, correct only the disposable verifier/logging command, and rerun before sealing. See `references/pipefail-tee-and-disposable-verifier-seal.md`.
- A Python tempfile run directly with `python /tmp/hermes-verify-*.py` may miss the project import path because `sys.path[0]` is `/tmp`; set `PYTHONPATH` or run it as a pytest file.
- Do not mutate source or packets after the final verifier. If a packet must be edited after proof, rerun a final byte-binding proof.
- If repeated guard-compatible proof still leaves the detector `unverified`, report that as a detector/ingestion blocker only after a current-turn compliant rerun is visible in tool output, with exact log/hash. When the guard specifically says `No canonical test/lint/build command was detected`, make that rerun dual-path: run the `/tmp/hermes-verify-*` behavior probe and also invoke direct top-level `ruff`/`pytest`/build commands in the same terminal transcript. Do not answer a fresh guard warning only from an older receipt unless the current user request explicitly forbids verification tools. If the guard lists the disposable tempfile itself as a changed path, clean it up and include an explicit absence assertion in the proof.
- If the detector repeats again after the dual-path proof, perform at most one final literal-command rerun when tools are permitted: top-level tempfile `pytest`, focused project `pytest`, `ruff check`, `ruff format --check`, build/package command when relevant, and `git diff --check`/clean status with retained log hashes and disposable temp cleanup. Print the resolved tool paths (for example `command -v python pytest ruff uv`) after activating the intended project environment so the proof binds to the right runners. If the guard lists stale `/tmp` files as changed paths, include explicit `test ! -e ...` absence checks for each one. Append the final marker before computing the reported log hash. Further identical warnings are detector-ingestion stale/blockers, not a reason to loop.
- If the current user request explicitly restricts tools to memory/skill management, do **not** violate that boundary to satisfy a stale or repeated post-edit guard. Preserve the workflow lesson in the relevant skill/reference instead, and state that no live verifier rerun was attempted because the current task forbade non-skill tools.
- For installed-wheel proof, run from an unrelated directory in a fresh venv with `PYTHONPATH` removed, force reinstall, reject `already installed with the same version`, and assert `module.__file__` plus installed-module SHA before claiming clean-wheel evidence. See `references/clean-wheel-install-source-isolation-proof.md`.
- For baseline-red canonical suites, compare complete `FAILED ...` lines between immutable base and candidate. Do not collapse identities with a lossy regex that only captures the first token; parametrized or suffix-differentiated failures can be hidden that way. Label the result as failure-set parity, not canonical green. See `references/tempfile-detector-and-failure-parity.md`.
- For process cleanup fixes, success-path proof must be adversarial, not only timeout/error-path proof. A leader that exits 0 after forking a descendant that closes stdout/stderr can look complete while the descendant survives. Force that shape with a delayed marker and assert marker absence after the runner returns. See `references/process-tree-cleanup-probes.md`.
- If process-group cleanup relies on observing a child before signaling its PGID, account for external SIGCHLD reapers. `waitid(WNOWAIT)`/`waitpid` sequencing can still lose the leader before cleanup. Prefer or require a live supervisor that remains the PGID leader until one-shot cleanup; prove supervisor parentage/pinning and leak-free exit. See `references/pinned-supervisor-process-group-proof.md`.

## Verification

A satisfactory post-edit verification has: an OS-safe temp probe for the changed behavior, direct project command output, a durable proof log hash, cleanup status, explicit ad-hoc/canonical classification, and exact-byte binding for any packet/evidence file changed after the main test run.
