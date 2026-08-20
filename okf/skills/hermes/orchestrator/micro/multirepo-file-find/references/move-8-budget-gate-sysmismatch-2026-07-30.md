# Move 8 — the inverse: file exists, but the import path is wrong

Companion to the main worked example. The example above covers "the file
is not in the working tree, but the user's claim is true." This is the
mirror case: "the file IS in the working tree, but the import is broken
because the consumer's `sys.path` points to the wrong location."

## The scenario

Planning message claimed: "rebuild `prismatic.linear.budget` (only .pyc
orphan on disk)."

What the obvious check returned:

```bash
$ find /home/ubuntu/.prismatic -name "budget.py" -path "*/linear/*"
/home/ubuntu/.prismatic/published/work/prismatic-engine/prismatic/linear/budget.py   # 6427 bytes
/home/ubuntu/.prismatic/published/prismatic-engine/prismatic/linear/budget.py       # 6427 bytes
```

The module exists. Twice. The "missing module" claim was wrong.

## What actually broke

The consumers don't import the module by its real path. They `sys.path.insert`
to a fixed location and then `from prismatic.linear.budget import ...`:

```python
# linear_helpers.py
sys.path.insert(0, "/home/ubuntu/work/prismatic-engine")
from prismatic.linear.budget import LinearBudget
```

`/home/ubuntu/work/prismatic-engine` does not exist on this machine. The
real location is `/home/ubuntu/.prismatic/published/work/prismatic-engine/`.

Result: every script that called `linear_helpers._linear_budget_check`
raised `ModuleNotFoundError` and the gate was silently bypassed.

## The diagnostic recipe

Before recreating a "missing" module, run the three-step investigation:

1. **Locate the module for real.** `find /home/ubuntu -name "X.py" -path "*/Y/*"`.
   If the file exists somewhere, the planning message is wrong about it being missing.

2. **Find every consumer.** `grep -rln "from <module> import" /home/ubuntu` to
   enumerate sites that would break. Read the ones that don't match the
   obvious path.

3. **Inspect every consumer's `sys.path` setup.** The `sys.path.insert(...)`
   lines tell you where the consumer thinks the module lives. If those paths
   don't exist on the host, the bug is the path, not the module.

```bash
# Step 2: find consumers
grep -rln "from prismatic.linear.budget" /home/ubuntu/.hermes/profiles/orchestrator/scripts

# Step 3: read the import line in each consumer
grep -B1 "from prismatic.linear.budget" /home/ubuntu/.hermes/profiles/orchestrator/scripts/linear_helpers.py
# Output:
#     sys.path.insert(0, "/home/ubuntu/work/prismatic-engine")
#     from prismatic.linear.budget import LinearBudget
```

The `sys.path.insert` line is the smoking gun. The path doesn't exist.

## The fix shape

Two options, in order of preference:

1. **Self-contained shim** (Move 8 chose this): write a new module that
   doesn't depend on the broken path. Lives at
   `scripts/prismatic_linear_budget_compat.py`. All consumers import
   from the shim. Decouples the gate from the broken mount.

2. **Path correction**: redirect the consumer's `sys.path.insert` to the
   real location. Smaller change, but couples the orchestrator to a
   specific mount path that may itself be wrong on the next host.

The shim is preferred when the consumer's logic is small enough to live
on its own (the LinearBudget class is ~150 lines). The path correction
is preferred when the consumer is tightly coupled to PR feature surface
that you can't reasonably duplicate.

## Verification recipe (for the shim case)

The shim must be tested end-to-end against the actual consumer:

```python
# e2e: ensure the consumer's gate now WORKS (not silently bypassed)
import os
os.environ["LINEAR_BUDGET_DB"] = tiny_db  # small budget
import importlib
importlib.reload(sys.modules["linear_helpers"])
try:
    linear_helpers._linear_budget_check("test")
    # PASS: gate ran clean
except linear_helpers.LinearBudgetBlocked as e:
    # PASS: gate ran and denied (proves the gate is LIVE)
    assert "exhausted" in str(e).lower()
```

The "gate ran and denied" outcome is the strong signal. Pre-fix, the
gate would have raised `ModuleNotFoundError` and been silently bypassed.
Post-fix, the gate actively rejects — proving the code path is now
executed.

## When NOT to use this recipe

- The module genuinely is missing (no `.py` and no `.pyc` matching the
  expected name anywhere on disk). Then rebuild from git history or
  scrap the import.
- The consumer's `sys.path` is correct and the module is at the path
  it claims. The bug is elsewhere.
- The module has a `py.typed` marker or a wheels distribution that
  should be installed via pip rather than via `sys.path` manipulation.
  Then fix the install, not the path.

## See also

- Main worked example: `multirepo-file-find-technique.md` — the "file
  not in working tree" case.
- `prismatic-evidence-handling` — the `__file__`-relative path recipe
  for verifiers that touch the same broken path reality.
- `plan-reconciliation-after-peer-review` — the "don't fabricate
  work" pitfall. The Move 8 case is the inverse: the planning message
  *itself* was the fabrication, and the agent's job was to surface
  the truth.
