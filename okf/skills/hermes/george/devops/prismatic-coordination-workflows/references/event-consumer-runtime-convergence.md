# Event-driven consumer runtime convergence lessons

Use this reference when coordinating or reviewing Prismatic slices that replace a legacy polling consumer with a one-shot/event-driven consumer, especially when doctor/runtime inventory is part of the acceptance gate.

## Durable workflow lessons

- **Stop/disable is not containment when another unit owns activation.** If a disabled legacy service keeps returning, inspect timers/services and dependency edges such as `BindsTo=` before admitting new work. Durable containment may require masking the activating unit as well as the legacy service, with rollback paths preserved.
- **Admission and launch are different gates.** A persisted task-admission event can be valid while the launcher still fails because its private exact-task registry/config environment is absent. Do not repost the event blindly; inspect event/claim state and repair launcher binding, then invoke the existing event at most once under the authorized contract.
- **A producer `PASS` after signal/cancel is not acceptance.** If the producer exits via `SIGTERM`/cancel/timeout and reports success, treat it as an exception until `HEAD`, tree, path scope, clean status, and local proof bind the candidate.
- **Doctor/runtime checks must parse authoritative service state, not substrings.** Use strict `systemctl show` properties (`LoadState`, `ActiveState`, `UnitFileState`, `ExecStart`/command identity as needed). Fail closed on missing output, unknown states, malformed rows, duplicate candidates, or command mismatch. For `ExecStart`, parse actual argv including systemd structured `{ ... argv[]=... ; ... }` forms; do not accept label substrings, module prefixes/suffixes, shell echo, duplicate/missing value flags, or unknown flags as proof of the canonical consumer.
- **Runtime inventory must be schema-like, not truthy.** Validate exact field types, complete required dependency names, exact source-path bindings, and exact canonical service identity. Reject malformed arrays/objects/strings even if truthy. Include adversarial tests for booleans where ints/strings are expected, integer stand-ins for booleans, counterfeit `/tmp/...task_admission_policy...` lookalikes, arbitrary source prefixes, missing/extra fields, and duplicate consumer declarations.
- **Installed-wheel runtime inventory needs an explicit external config path.** Source-tree relative inventory may pass in editable/dev mode but fail in wheel installs. Installed runtimes should support and test an absolute `PRISMATIC_RUNTIME_SERVICES_CONFIG` override; absence should fail closed with a clear reason.
- **Legacy command mocks can hide strict parser regressions.** When tightening doctor behavior, update old CLI tests that globally mock `subprocess.run` to return realistic safe `systemctl show` key/value output rather than generic strings.

## Verification pattern

1. Prove exact candidate identity and path containment before review:

```text
HEAD=<sha>
TREE=<tree>
STATUS=clean
CHANGED_FROM_BASE=<only authorized paths>
```

2. Run focused behavior gates for doctor/runtime convergence:

```bash
PYTHONPATH=. python3 -m pytest -q \
  tests/test_runtime_services.py \
  tests/test_doctor_module.py \
  tests/test_task_admission_consumer.py \
  tests/test_task_admission.py \
  tests/test_task_admission_api.py \
  tests/test_doctor_command.py
ruff check prismatic/doctor.py tests/test_doctor_module.py tests/test_runtime_services.py tests/test_doctor_command.py
ruff format --check prismatic/doctor.py tests/test_doctor_module.py tests/test_runtime_services.py tests/test_doctor_command.py
python3 scripts/validate_runtime_services.py config/runtime-services.json
```

3. For clean-room proof, unset inherited verifier contamination and prove both sides:

```bash
env -u VIRTUAL_ENV -u PYTHONPATH <pytest-capable-python> -m build --wheel --outdir "$DIST"
env -u VIRTUAL_ENV -u PYTHONPATH <pytest-capable-python> -m venv --system-site-packages "$ROOT/venv"
env -u VIRTUAL_ENV -u PYTHONPATH "$ROOT/venv/bin/python" -m pip install --no-deps "$WHEEL"
# From an empty CWD: assert no override fails closed; absolute PRISMATIC_RUNTIME_SERVICES_CONFIG succeeds.
```

4. Commission fresh exact-head rereview after any semantic repair. Prior exact-head review is invalidated by a new commit, even when all findings were repaired.

## Report boundary

Keep reports explicit:

```text
AD_HOC_OR_CANONICAL=<focused|canonical suite|clean-room installed-wheel>
NOT_CLAIMING=<fresh review/PR/merge/deploy if not done>
```
