# Ned HDE lane permission gate pattern

Use this when a preserved Ned checkpoint fails the Prismatic lane guard because HDE operational docs are outside Ned's current lanes.

## Symptom

Remote/pre-push lane guard rejects paths like:

```text
docs/hd-engine/guide-deconditioning-runtime-workflow.md
docs/hde-head-bot-scaling-runbook.md
```

The work may be preserved locally or as a Git bundle, but the remote lane contract blocks it.

## Correct fix

Do **not** tell Ned to bypass with `--no-verify` and do **not** broaden Ned to all `docs/`.

Patch `PRISMATIC_ENGINE.yaml` narrowly:

```yaml
ned:
  lanes:
    owner:
      - scripts/
      - prismatic/
      - plugins/
      - docs/hd-engine/
      - docs/hde-
      - docs/human-design-engine/
```

Also update any agent-facing lane map/reference that still says Ned cannot push docs or should use `--no-verify` for docs. The reference should say HDE operational docs are in Ned's lane; unrelated docs/config/governance should be routed to the owning lane/orchestrator.

## Verification recipe

Create a fresh `/tmp/hermes-verify-*.py` script and print a plain canonical command such as:

```text
CANONICAL_TEST_LINT_BUILD_COMMAND=python3 -m py_compile /home/ubuntu/work/prismatic-engine/scripts/pre-push-hook.py
```

Inside the verifier:

1. Parse `PRISMATIC_ENGINE.yaml`.
2. Import `scripts/pre-push-hook.py` with `importlib.util.spec_from_file_location`.
3. Call `_check_lane_ownership()` for positive examples:

```python
allowed = [
    "docs/hd-engine/guide-deconditioning-runtime-workflow.md",
    "docs/hde-head-bot-scaling-runbook.md",
    "docs/human-design-engine/runtime.md",
    "scripts/hde_runtime_check.py",
    "prismatic/hde_adapter.py",
    "plugins/hde/plugin.json",
]
```

4. Assert `violations == []` and all allowed paths are owned.
5. Call `_check_lane_ownership()` for negative examples:

```python
blocked = [
    "docs/random-prismatic-doc.md",
    "content/hde-marketing.md",
    "assets/hde-diagram.png",
    "research/hde-research.md",
]
```

6. Assert all negative examples remain violations.
7. After merge, read back `origin/deploy-fresh:PRISMATIC_ENGINE.yaml` and repeat the ownership checks so the remote guard contract is proven, not just the local checkout.
8. Clean only the verifier file and label the result as ad hoc targeted verification, not full suite green.

## Pitfalls

- The hook reads the governance YAML, so changing docs alone will not unblock remote pushes.
- Auto-checkpoint commits may split `PRISMATIC_ENGINE.yaml` and reference updates; squash to one clean `[Fred]` commit before PR.
- A stale lane-map reference can keep agents bypassing hooks even after the real YAML is fixed.
- Keep the positive and negative examples in the verifier. A broad `docs/` grant would pass the positive case while violating lane discipline.
