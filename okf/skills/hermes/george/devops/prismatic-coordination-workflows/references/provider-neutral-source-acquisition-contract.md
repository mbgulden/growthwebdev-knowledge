# Provider-neutral source acquisition contract

Use this reference when admitting or correcting Prismatic provider-neutral source acquisition slices.

## Class-level lesson

Provider-neutral source acquisition is its own verification-foundation layer: it obtains immutable Git objects and proves exact source identity in a disposable checkout. It is not a verifier backend and it is not a merge decision.

Place source-acquisition code under `prismatic.verification`, not under a generic `prismatic.provider_neutral` package and not inside the type-specific `prismatic.verifiers` registry unless current architecture explicitly changes.

## Correct boundary

Source acquisition may:

- fetch or import a source from provider remote, local bare repository, or offline Git bundle;
- prove the exact ref object, peeled candidate commit, candidate tree, object format, object completeness, tree safety, detached checkout state, and deterministic source-acquisition digest;
- return an immutable checkout plus metadata for the later verifier-execution slice.

Source acquisition must not:

- execute product verification commands;
- inspect hosted-provider checks/statuses as authority;
- create a full verification receipt or pass/fail merge judgment;
- authorize merge, deploy, Linear writes, downstream launches, or cap increases;
- depend on mutable source checkout state, object alternates, partial clones, or retained remote credentials.

## Contract shape to preserve

For the first source-acquisition slice, prefer a very small path scope, for example:

```text
prismatic/verification/__init__.py
prismatic/verification/source_acquisition.py
tests/test_source_acquisition.py
```

Public API should be stable, explicit, and small:

- marker constant such as `SOURCE_ACQUISITION_V1_OK`;
- frozen `SourceAcquisitionPolicy`;
- frozen `SourceAcquisitionRequest`;
- frozen `AcquiredSource`;
- stable `SourceAcquisitionError(code=...)`;
- `acquire_source(...)`;
- `validate_acquired_source(...)`.

## Required invariants

- Allow source kinds as source forms, not execution backends: `provider_remote`, `local_bare_repository`, `offline_git_bundle`.
- Require coherent kind/provider combinations. Provider remote needs a real provider; local/bundle forms use provider `none`.
- Require full lowercase 40-hex SHA-1 commit and tree IDs; reject prefixes, symbolic refs, option-like values, uppercase, `HEAD`, branches, and tags in SHA fields.
- Require `source_ref` to be a full `refs/heads/...` or `refs/tags/...` ref. Annotated tags may peel to candidate commit, but record the unpeeled ref-object SHA.
- Fetch the exact full ref into a private ref; the fetched private ref, not stale `ls-remote`, is authoritative.
- Use an existing absolute non-symlink workspace root; create a random mode-0700 child; initialize with empty template.
- Scrub Git environment: no `GIT_DIR`, worktree/index/object/config overrides, arbitrary credentials, or inherited HOME; set `GIT_CONFIG_NOSYSTEM=1`, `GIT_TERMINAL_PROMPT=0`, and private temp HOME.
- Never use `shell=True`; enforce per-command and total deadlines; kill process groups on timeout; bound output size and sanitize errors.
- Reject unsafe transports: `ext::`, shell-style transports, queries/fragments, URL passwords/tokens, HTTPS userinfo. SSH may contain username but no password.
- For local/bundle sources, use absolute no-follow paths, reject symlink components, require bare repo or valid self-contained bundle as appropriate, and prove no network dependency.
- Prove full object integrity: object format `sha1`, candidate type commit, candidate tree exact, not shallow/promisor/partial/alternate-backed, bounded `git fsck --full --strict`, bounded complete tree inspection.
- Reject tree symlinks, gitlinks, unsafe paths, platform-escaping paths, case-folded `.git` components, controls, backslashes, absolute paths, `.` and `..` components.
- Checkout detached exact candidate with HFS/NTFS protections and recursive submodules disabled; verify exact HEAD/tree, clean status including untracked, no alternates, no symlinks/submodules.
- Compute a deterministic digest over canonical JSON and a fixed domain separator; exclude timestamps, temp paths, environment values, checkout UUIDs, and hosted status.
- `validate_acquired_source()` must fail closed if HEAD/tree/digest/cleanliness/symlink state changes before later verifier execution.

## Mandatory proof classes

Success probes:

- local bare branch acquisition;
- self-contained offline bundle;
- provider remote through local test fixture, e.g. `file://` only when explicitly allowed for tests;
- annotated tag peel retaining unpeeled object;
- deterministic digest across different checkout paths;
- detached clean checkout with no alternates;
- fresh wheel imports package/API from empty CWD with no source `PYTHONPATH`.

Fail-closed probes:

- incoherent/disallowed kind-provider;
- non-bare local source;
- malformed/short/symbolic/option-like SHAs and refs;
- missing exact ref, ref/candidate mismatch, non-commit candidate, tree mismatch;
- shallow/promisor/alternate-backed/corrupt/missing objects;
- malformed/truncated/wrong-ref/prerequisite bundle;
- symlink source/bundle/root/parent;
- tree symlink/gitlink/unsafe path/workspace escape;
- dirty tracked/untracked checkout;
- changed HEAD/tree/digest after acquisition;
- timeouts, output overflow, secret-bearing URL, secret canary leakage;
- failure cleanup leaves no partial destination;
- local/bundle paths succeed with network unavailable.

## Async review arrives after dispatch

If a read-only architecture review returns after a producer has already started and materially corrects the contract:

1. Stop the active worker and its timer before letting it produce a commit.
2. Snapshot exact untracked attempt paths for forensics with hash.
3. Remove only those exact untracked attempt paths and prove the worktree is back to exact clean base.
4. Mark the claimed task `CANCELLED_CONTRACT_SUPERSEDED`, not product failure, and move/archive it out of the active claimed lane.
5. Freeze a corrected task packet with explicit prior-attempt warning and corrected package/path boundary.
6. Redispatch one corrected producer at cap 1, read back task hash/context, verify claimed task ID from worker status/cmdline, and rebind watcher/control/handoff to the corrected task.
7. Keep successors paused and do not reuse old review/proof evidence.

## Candidate review gate after producer output

When the corrected producer produces a source-acquisition candidate, do not accept or reject from the producer packet alone:

1. Preserve the exact candidate head/tree/parent, changed-path allowlist, and bundle/ref identity before review.
2. If producer tests fail under an incomplete or borrowed interpreter, classify that as **verifier-environment failure** until reproduced under the configured review environment. The durable lesson is to rerun exact-head proof with the environment that has the canonical test/build dependencies, not to weaken the suite or dismiss the candidate.
3. Keep style/static tooling pinned separately when needed; using a full-dependency interpreter for pytest/build and a separate known-good Ruff binary is acceptable if both are recorded explicitly.
4. Launch only read-only independent exact-head reviews while the candidate is preserved. If an ordered controller and a manual continuation both launch reviewers, reconcile state as **dual read-only review pending** rather than hiding one. This is not a cap violation when both are no-side-effect reviewers.
5. Make the gate fail closed: any `REPAIR` verdict stops the line and reopens the same task; only unanimous `CLEAN` permits PR/promotion preparation.
6. Do not admit successors while reviews are pending, even if local canonical proof is green.
7. Recompute and reconcile artifact digests after controllers recreate bundles or refs. Trust `sha256sum` plus `git -C <worktree> bundle verify <bundle>` over stale queue/handoff values, then update queue/control/handoff together.

## Stop-the-line repair after a valid `REPAIR` review

When any valid exact-head reviewer reports `REPAIR`, stop the line even if local focused/canonical suites are green and even if another read-only review is still pending.

1. Classify provider refusals separately as `NO_VERDICT`; they neither satisfy nor fail the product gate.
2. Independently reproduce at least one reported bypass on the exact candidate head when feasible, using a temporary fixture that does not modify the candidate worktree.
3. Inspect the actual implementation enough to confirm every reported contract gap before dispatching repair; do not reduce the repair to the single reproduced bypass if the review identified multiple material gaps.
4. Freeze a same-task repair packet on top of the rejected candidate head, not current `main` and not a successor issue, with the same path allowlist unless the repair explicitly requires a reviewed scope change.
5. Start exactly one producer at cap 1, read back the filesystem-bus task hash/context/status, and rebind watcher/queue/control/handoff to the repair task. Keep all successors paused.
6. In durable state, preserve: rejected candidate head/tree/bundle, valid review id/verdict, reproduction log path/digest, repair task id/hash/base, watcher id, queue digest, and non-claims.

## Source-acquisition repair invariant checklist

A source-acquisition implementation can pass broad tests while still missing authority-critical invariants. During review or repair, directly probe these areas:

1. **Detached HEAD is an invariant, not just commit equality.** Acquisition must return a detached checkout, and `validate_acquired_source()` must reject an attached branch at the same commit/tree. A useful regression acquires a valid checkout, runs `git switch -c attached-same-commit`, and proves validation fails closed.
2. **Authentication handles must be validated and scrubbed, not ignored.** If the public API accepts `askpass_helper` or `ssh_auth_socket`, it must either implement the frozen contract or reject those API parameters from the schema itself. Helpers/sockets need absolute no-symlink paths, correct file type, executable/socket checks, provider-remote-only use, scrubbed `GIT_ASKPASS`/`SSH_ASKPASS`/`SSH_AUTH_SOCK`, no raw token/password API values, and secret-canary non-leak tests.
3. **Output limits must be streaming hard limits.** A post-`communicate()` byte count is not a bound. Commands must drain/terminate process groups deterministically on overflow, keep retained output bounded for text and binary commands, apply the tighter tree-listing limit when relevant, preserve total/per-command deadlines, and return stable overflow errors without raw output.
4. **Full-object proof must include partial/promisor/reachability rejection.** In addition to strict `fsck`, reject shallow state, alternates, `extensions.partialClone`, `remote.*.promisor`, partial-clone filters, `.promisor` markers, and missing reachable objects. Use bounded plumbing such as `rev-list --objects --missing=print <candidate>` with `GIT_NO_LAZY_FETCH=1`, and fail closed on any missing marker.
5. **Offline bundles need exact-ref and change fencing.** Verify no-follow regular bundle identity, enumerate bundle heads and require exactly one exact requested ref, reject prerequisite-dependent or wrong/ambiguous refs, and revalidate identity/content immediately before and after fetch so replacement races clean up and fail closed.

## Compact proof packet

```text
COMMAND=<contain superseded task, preserve exact candidate, reproduce bypass, dispatch same-task repair, rebind watcher/state, or rerun exact-head review>
RESULT=PASS|FAIL|BLOCKED
LOG=<path>
SCOPE=provider-neutral source acquisition admission/correction/review/repair gate
AD_HOC_OR_CANONICAL=ad-hoc operational state proof, targeted proof, or canonical suite as actually run
NOT_CLAIMING=repair complete; review CLEAN; PR opened; merged; downstream admitted; cap increased
MARKER=SOURCE_ACQUISITION_V1_OK|SOURCE_ACQUISITION_V1_REPAIR_OK
```
