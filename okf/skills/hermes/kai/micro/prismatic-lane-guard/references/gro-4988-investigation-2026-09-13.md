# GRO-4988 investigation (2026-09-13) — lane guard blocking `okf/skills/`

Session-specific detail for the first real diagnosis of the Prismatic lane guard.
Kept here as the worked example behind `prismatic-lane-guard`.

## Trigger
User: Fred and kai need access to `okf/skills/`; "this whole lane thing is really not
helping us. I thought we got rid of it." A blocked auto-regen commit (all under
`okf/skills/`) was stuck unpushed in a `/tmp` worktree.

## Verified mechanism (reproduce in any managed repo)
1. Hook is real: `ls .git/hooks/ | grep -v sample` → `pre-push`; `git config
   core.hooksPath` empty.
2. Backing script: `grep -rl PRISMATIC_ENGINE --include=*.py .` →
   `scripts/prismatic-pre-push-hook.py` (~271 lines).
3. Config: `PRISMATIC_ENGINE.yaml` at repo ROOT.
4. `okf/skills/` literal grep → exit 1 (false negative). Parsing the yaml with PyYAML
   and resolving the path through the hook's own functions showed the path was in
   **no** agent's lanes; only Fred + George (owner `*`) passed.
5. Historical corroboration: a prior "auto-regen ... landing blocked by hub lane
   guard" commit and a PR addendum documenting the same block.

## importlib unit-test recipe (the only deterministic BLOCK/ALLOW verdict)
The hook filename is hyphenated, so import it explicitly:

```python
import importlib.util
spec = importlib.util.spec_from_file_location(
    "pph", "/path/to/scripts/prismatic-pre-push-hook.py")
pph = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pph)
# Then call the module's lane-resolution function with the real config for
# each registered agent, asserting BLOCK/ALLOW on the target path.
```

Run this against the REAL config (not a copy) before and after any yaml edit. A lane
fix is not "done" until the target path flips BLOCK → ALLOW for the affected agent.

## Bootstrap self-block (the key structural finding)
`PRISMATIC_ENGINE.yaml` sits at repo root, which is outside every agent's content
lane. Therefore the agent who needs the fix (kai) cannot push the fix — the hook
blocks the very file being edited. Confirmed by resolving `kai → PRISMATIC_ENGINE.yaml
= BLOCK`. This is why the fix must either (a) add a config-file exception to the hook
in the same PR, (b) route through the governance merge path, or (c) be a formal
deprecation decision. Do not claim a lane fix is shippable without resolving this.

## Dual-repo census
- OKF knowledge hub (`growthwebdev-knowledge`): has the guard + the blocked path →
  needs the lane grant.
- AOT mirror (`active-oahu-tours-mirror`): independent yaml + hook, but does NOT
  contain `okf/skills/` and kai already owns `okf/` there → **no change needed**.
Always report which repo needed the change and which did not.

## Governance constraints honored
- Merge authority for `content/` is Fred; merges go through PR, main-block unchanged.
- Commit convention: real Linear issue ref, e.g. `[Kai] ... (#GRO-4988)`.
- Approval structure lives in `okf/decisions/` (commit-authorization decision doc).
- If lanes are to be removed, that is a **formal deprecation decision** (strip the
  lane check, keep main-block + lock checks), not a silent config edit.

## Ordering trap (auto-regen re-land)
The stuck regen branch must be rebased onto main **after** the fixed yaml is merged,
because the regen branch's own push re-validates against the yaml it contains.
Pushing the regen before the yaml lands on main fails again. Sequence:
lane-fix PR → Fred merges to main → rebase + push regen as `content/kai/*`.

## State at session end (what was done vs open)
Done: mechanism verified; GRO-4988 filed (Linear); `content/kai-*` branch cut from
`origin/main`; yaml edited in worktree to add `okf/skills/` to kai's lanes + decision
note; AOT mirror confirmed unchanged.
Open: config-file exception not yet implemented in the hook (so the yaml edit itself
is still BLOCK for kai); unit-test not re-run post-edit; PR not yet pushed; auto-regen
not yet re-landed. Next session must implement the exception, re-run the importlib
test, then push the PR.

## Tooling note (environment quirk, not a durable rule)
During this session terminal/execute_code output repeatedly collapsed to placeholder
lines ("1 lines output"). Workaround that worked: write command output to `/tmp`
files and read them back in slices, or print explicit char-limited slices from
execute_code. If this recurrence stops, drop the workaround.
