# Bootstrap-safe repair admission envelopes

Use this reference when a blocked exact-head candidate has a reviewed same-worktree repair task and the next step is a separate one-shot admission envelope/launcher.

## Why this matters

A launcher can verify frozen input hashes but still be unsafe if it imports or executes deployed task-admission modules before checking the hashes. If any frozen deployed input drifts and contains import-time behavior, the launcher must abort before that code can run.

## Required launcher ordering

1. Define only constants and a self-contained hash/mode/type verifier at top level.
2. Freeze every file that can affect admission semantics, including dynamically loaded schema files as well as deployed Python modules, private source config, production policy, and control authorization.
3. For each frozen input, bind **path + SHA256 + exact mode + regular-file/no-symlink type**. Hash-only gates are incomplete when deployed/runtime trust assumes owner-only private controls or read-only deployed release files.
4. Call `verify_frozen_inputs()` before any `sys.path` mutation, dynamic import, deployed-module import, config load, credential open, policy/control write, socket health call, POST, or consumer invocation.
5. Call `verify_frozen_inputs()` again as the first executable line in the public `run()` path and at every authority transition: after disposable validation, at the live execute gate, and immediately before opening controls.
6. In adversarial proof, drift each frozen input independently, including at least one import-time-marker drift in a deployed module, all exact-mode drifts, and dynamically loaded schema byte drift. Prove the launcher exits on mismatch before marker execution or authority opening.
7. Run copied-launcher adversarial tests from an owner-only secure root (`0700`), not a world-writable wrapper ancestry such as plain `/tmp`, when the launcher deliberately rejects unsafe path ancestry. Treat an ancestry rejection as harness setup, then rerun the full proof from the secure root.
8. Remove any reviewer/proof-created launcher bytecode artifacts (`__pycache__`, `.pyc`) and verify none remain before freezing the envelope.

## Repair-event identity boundaries

For a repair of an already-admitted task:

- use a new internal event/task identity when the deployed gateway needs a fresh idempotency namespace;
- bind the real Linear issue separately;
- prove the original event count remains exactly unchanged;
- prove repair admission/outbox/claims/lifecycle rows, writer lease, selectable outbox, and active slots are zero before and after preflight;
- explicitly state `ORIGINAL_EVENT_REPLAY=false` and `EVENT_POST_AUTHORIZED=false` in the envelope.

## Disposable policy proof boundary

If production policy was restored after the original event and no longer allowlists the repair worktree, a disposable owner-only policy can prove parser/schema/Git/task-hash compatibility only. It does not authorize live admission. Bind before/after production policy hashes and keep the live repair event count zero.

## Envelope review gate

A clean repair task review permits envelope preparation, not execution. Freeze the envelope and launcher as separate exact artifacts, then dispatch:

1. full package review: envelope, task copies, deployed-schema binding, blocked checkpoint, zero state, authorization separation, nonclaims;
2. focused launcher review: bootstrap ordering, all frozen input hashes/modes/types including dynamically loaded schemas, one token/POST/consumer path, no original replay, runtime/socket identity, cap-1, restoration, cleanup.

Even after both return CLEAN/PASS, request explicit human authorization for exactly one repair event and one ordinary consumer invocation. General continuation language is not enough.

## Proof packet fields

```text
TASK_ID=<internal repair event id>
LINEAR_ISSUE=<real issue id>
BASE_COMMIT=<blocked candidate commit>
BASE_TREE=<blocked candidate tree>
TASK_SHA256=<reviewed repair task hash>
TASK_REVIEW=<delegation>:CLEAN/PASS
FROZEN_INPUT_COUNT=<count including dynamic schema + deployed modules + private/policy/control files>
FROZEN_INPUTS=<path,sha256,mode,regular,no-symlink for each input>
SCHEMA_SHA256=<dynamically loaded task-admission schema hash>
LAUNCHER_SHA256=<sha256>
PREFLIGHT_RESULT=PASS_PREFLIGHT_ZERO_MUTATION
PROOF_SCOPE=bootstrap gate;schema/hash/mode/type gates;one-shot path;redirect rejection;task/base binding;repair zero state;original event count one;preflight restoration;secure-root drift proof
ORIGINAL_EVENT_COUNT=1
ORIGINAL_EVENT_REPLAY=false
REPAIR_EVENT_COUNT=0
EVENT_POST_AUTHORIZED=false
NOT_CLAIMING=envelope acceptance,event authorization,repair launch,repair correctness,candidate acceptance,canonical suite,PR,merge,deployment,Linear mutation
```
