# Provider-neutral verification program pattern

Use when hosted CI becomes unavailable, non-authoritative, or too provider-specific for Prismatic merge policy. The durable lesson is not “ignore CI”; it is to move merge authority into an exact-artifact clean-room receipt model where provider status is an optional projection, not the semantic source of truth.

## Policy shape

A Prismatic merge candidate may be eligible only when at least one approved independent verifier backend emits a validated, exact-head, clean-room verification receipt. GitHub Actions can be an approved hosted verifier backend, but GitHub status alone must not define the verification semantics.

Provider-neutral core owns:

- verification-policy schema/version;
- verification-receipt schema/version;
- repository/source identity;
- exact base/head/tree/path binding;
- clean-room source acquisition;
- command policy and execution result;
- environment/toolchain digest;
- log and artifact hashes;
- verifier/backend identity;
- freshness, expiry, supersession, and revocation;
- producer/verifier separation;
- merge-judge input and fail-closed validation.

Keep source acquisition and verifier execution as separate axes:

- **Source adapters/acquisition forms** own trigger, source identity, refs, retrieval handoff, and optional status projection: GitHub, Bitbucket, GitLab, Forgejo/Gitea, local bare repositories, and offline Git bundles.
- **Approved verifier backends** execute policy in a clean room and may emit receipts: hosted provider runners, self-hosted clean-room workers, and explicitly supervised emergency clean-room verifiers.

A local repository or bundle is not a verifier backend merely because it supplies source bytes. Schema contracts must bind both `source_kind`/provider identity and `backend_class`/backend identity; neither axis may substitute for the other.

## Sequencing pattern

1. **Do not use docs as a bypass.** Policy docs can establish the direction, but existing held PRs remain held until the runner/validator/trust/conformance gates exist and a fresh validated receipt binds their exact head.
2. **Create a Linear epic plus ordered children.** Use a parent issue for the program and child tasks for: docs/ADR, schemas, clean-room acquisition, runner, validator/merge gate, signing/trust, hosted verifier backend, source/provider adapters, self-hosted verifier backend, conformance/migration.
3. **Keep task-manager-neutral queue truth.** Mirror the epic and active child into the durable queue/control/handoff so Prismatic can continue if Linear is stale/unavailable.
4. **Use cap 1 for implementation.** After the architecture PR, admit only the first implementation child as sole writer. Keep downstream children `dispatch:paused` until predecessor review/closeout.
5. **Treat architecture PR as source-of-truth candidate, not implementation.** PR body and handoff must explicitly say runner, validator, signing, adapters, and migration receipt do not yet exist.
6. **Hash-bind task contracts and hierarchy receipts.** Include Linear hierarchy JSON, active task contract SHA, exact branch/base/worktree, watcher job, and non-claims in the handoff.
7. **Install a change-only watcher per active producer.** Verify unchanged-baseline silence before scheduling and record watcher id in queue/control/handoff.
8. **Close with a focused temp verifier.** After editing docs, queue, handoff, control JSON, watcher scripts, or PR bodies, run a `/tmp/hermes-verify-*` script plus literal visible focused commands (`pytest`, `ruff check`, `ruff format --check`, `python -m build`) and label it `AD_HOC_OR_CANONICAL=ad-hoc targeted` unless the full canonical suite actually ran.

## Proof packet fields

```text
POLICY=<one approved independent exact-head clean-room receipt; provider status optional projection; source adapters distinct from verifier backends>
LINEAR_EPIC=<issue id>
LINEAR_CHILDREN=<range/list>
DOCS_PR=<url>
DOCS_HEAD=<sha>
DOCS_TREE=<tree>
DOCS_REVIEW=<delegation/result state>
ACTIVE_CHILD=<issue id>
ACTIVE_EXECUTION=<bus/task id>
ACTIVE_TASK_SHA256=<sha256>
ACTIVE_WATCHER=<cron/job id>
DOWNSTREAM_CHILDREN=<dispatch:paused list>
PR_MIGRATION_RECEIPT_EXISTS=false
MERGE_POLICY_SWITCHED_IN_PRODUCTION=false
ACTIVE_PRODUCERS=1
ACTIVE_AGY_PRODUCERS=0
NOT_CLAIMING=<implementation complete, merge, deploy, migration receipt>
```

## Detector-visible verification reminder

If Hermes reports edited paths as unverified after a successful closeout, rerun verification with literal command names visible in the terminal transcript rather than only through shell variables. Include:

```bash
python3 -m py_compile /path/to/watcher.py /tmp/hermes-verify-*.py
python3 -m json.tool /path/to/queue.json
python3 -m json.tool /path/to/control-state.json
PYTHONPATH=/path/to/worktree /path/to/python scripts/validate_okf_docs.py
PYTHONPATH=/path/to/worktree /path/to/python -m pytest -q tests/test_okf_docs.py
/path/to/ruff check scripts/validate_okf_docs.py tests/test_okf_docs.py
/path/to/ruff format --check scripts/validate_okf_docs.py tests/test_okf_docs.py
git diff --check
PYTHONPATH=/path/to/worktree /path/to/python -m build --outdir /tmp/<dist>
python3 /tmp/hermes-verify-*.py
rm -f /tmp/hermes-verify-*.py
```

Report this as ad-hoc targeted verification. Do not call it canonical full-suite green.
