# Runtime services manifest contract pattern

Use after runtime topology inventory shows Prismatic production spans immutable releases, mutable checkouts, profile scripts, or non-git daemons, and before any live repoint/restart is authorized.

## Purpose

Create a source-owned, secret-free desired runtime contract that can be reviewed and tested without touching production. The first manifest slice is not deployment proof; it is a fail-closed contract that makes later convergence/repoint work auditable.

## Bounded producer shape

- Admit one writer at cap 1 from the verified merge/current-main SHA.
- Put the exact task prompt in the agent bus and hash it before dispatch.
- Require producer preflight: task hash, exact base/head, expected branch, clean worktree.
- Limit allowed changed paths to the manifest, validator, focused tests, and operator docs.
- Forbid commits, pushes, PRs, deployment/restart, systemd edits, live env/state reads, Linear mutation, handoff/control-state mutation, and agent dispatch.
- Run any supervisor/asset semantic analysis in a separate read-only lane only; it may classify but not write.

## Manifest invariants

A runtime-services manifest should be deterministic, versioned, and explicit about component ownership. It should cover at least the runtime components discovered in inventory, e.g. gateway, consumer, curator, supervisor, watchdog, webhook drain, and merge daemon.

Required distinctions:

- immutable Engine-owned code/executables via release-path templates under `/home/ubuntu/.prismatic/releases/`;
- release-scoped virtualenv/import path templates where relevant;
- source-owned executable/module path;
- external mutable state paths;
- external environment-file paths by filename/path only, never values;
- owner/project classification and deployment mode;
- separately versioned/excluded components such as `merge-daemon`.

Do not hard-code the current commit into permanent source as the desired future contract unless the slice explicitly creates a generated snapshot. Use templates/placeholders for release identity.

## Fail-closed validator requirements

Use Python standard library only for the validator. Importing it must not parse CLI args, read environment files, touch live services/state, execute subprocesses, or write files.

The validator should reject:

- malformed JSON and wrong top-level/schema version;
- missing/extra/duplicate component IDs;
- unknown per-component fields;
- wrong types, empty strings/lists where invalid;
- executable/import/working-directory/source paths under mutable execution roots: `/home/ubuntu/work/`, `/home/ubuntu/.prismatic/runtime/`, `/home/ubuntu/.hermes/profiles/`;
- inline environment assignments or env files outside the approved env directory;
- state paths inside release/work/runtime/profile trees or with traversal;
- secret/private-key/credential markers in values, without false-positive on safe field names like `environment_files`;
- Engine-owned services not bound to immutable release templates;
- `merge-daemon` falsely declared as Engine-converged.

Prefer structural, field-aware validation over generic recursive string scanning. If helper functions accept Python objects in tests, guard against mapping/string subclasses and custom comparison hooks.

Hook-safety detail: do not normalize untrusted manifest mappings with operations like `set(component)`, key membership checks on subclassed strings, or equality-driven dict lookups until after proving every key is an exact `str` (`type(key) is str`). Extract exact-string keys with identity/type checks first, then compare against constants. A custom `str` subclass can raise from `__eq__` even when the dict visually looks like a normal JSON object in a Python test fixture.

## Test matrix

Cover both the repository manifest and negative mutations using temporary files/objects:

- repo manifest passes;
- exact component set and schema version;
- mutable execution roots rejected for each executable/import/working-directory class;
- mutable state accepted only in explicit state fields;
- malformed JSON, wrong top-level type, missing/extra component, unknown fields, wrong types, empty values;
- inline env value rejected;
- secret marker rejected without rejecting safe field names;
- traversal and forbidden-root state rejected;
- separate-version `merge-daemon` contract;
- module/source consistency: desired entrypoints must map to source-owned artifacts that actually exist, not fictional labels or stale runtime names;
- exact operational component bindings for known components such as consumer, watchdog/profile supervisor, and separately versioned merge-daemon;
- import side-effect trap;
- CLI success and compact deterministic failure;
- mapping/key subclass adversarial cases that prove custom `__eq__`/hook code does not execute.

## Documentation requirements

Docs must say this is a desired source contract, not proof of runtime parity. Explain immutable code vs external mutable state, why dirty runtime/profile assets are preservation/port sources, `merge-daemon` separate ownership, exact-head review expectations, backup/alternate-port/repoint/restart/rollback boundaries, and explicit non-claims.

## Proof packet

```text
STATUS=<PASS|PARTIAL|BLOCKED>
BASE_SHA=<sha>
TASK_SHA256=<sha256>
CHANGED_PATHS=<exact manifest/validator/tests/docs list>
FOCUSED=<result/log>
CANONICAL=<result/log or not run>
LINT=<result/log>
BUILD=<result/log>
LOG_ROOT=<path>
NOT_CLAIMING=deployment,restart,runtime parity,clean-room portability,publishability,cap increase
```
