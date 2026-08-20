# Bootstrap-before-import hash gate pattern

Session signal: GRO-4275 admission launcher V1/V2 reviews found that a launcher can have correct frozen-input hashes but still be unsafe if the verification occurs after adding deployed code to `sys.path`, importing deployed modules, or reading deployed configuration. Drifted import-time code could execute before rejection.

Reusable rule:

1. Preserve blocked launcher/envelope bytes before modifying them.
2. Put a self-contained verifier near the top of the launcher that uses only stdlib and literal path/hash/mode bindings.
3. Invoke the verifier before:
   - `sys.path` changes;
   - any `from prismatic...` or other deployed-code import;
   - config/policy/control reads;
   - report/temp directory creation;
   - DB reads or subprocess/wrapper construction.
4. Re-invoke the verifier at the first line of the main `run()`/entry function.
5. Re-invoke again after disposable validation, at the execute live gate, and immediately before opening credentials/control or posting the event.
6. Add an adversarial proof: copy the release to a disposable location, inject import-time marker code into a bound module while changing its hash, run the launcher/preflight, and prove rejection happens and the marker file/log is absent.
7. Count the verifier call sites and verify their ordering line-by-line, not just by grepping for function names.

Proof packet fields to capture:

```text
BLOCKED_PRIOR_SHA256=<preserved launcher/envelope>
LAUNCHER_SHA256=<corrected launcher>
HASH_GATE_ORDER=bootstrap_before_sys_path_and_deployed_imports;run_entry;post_validation;execute_live_gate;immediately_pre_control
ADVERSARIAL_IMPORT_PROOF=marker_absent_on_source_hash_drift
PREFLIGHT_REPORT=<path>
PREFLIGHT_REPORT_SHA256=<sha>
ZERO_LIVE_STATE=PASS
EXECUTION_COMMAND_RUN=false
```

Pitfall: A verifier that runs after imported deployed code is not an execution-time integrity gate; it is only a post-import drift detector. Reviewers should block it even when preflight is zero-mutation.