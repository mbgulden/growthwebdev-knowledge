# Wheel resource inspection after a verifier assertion failure (2026-07-25)

## Trigger

A post-edit closeout verifier reaches source/readback/behavior checks, compile, lint, focused tests, and build, then fails in a wheel-inspection assertion because the verifier guessed the packaged resource path rather than reading the actual wheel member list.

## Durable pattern

1. Classify the first failure narrowly as **verifier assertion/setup failure** until the wheel contents prove otherwise. Do not call it a product failure or hide it.
2. Inspect the built wheel member names directly with `zipfile.ZipFile(...).namelist()` and filter for the relevant feature/resource namespace.
3. Correct the verifier to assert the actual packaged path and the intended resource count/content. Do not weaken the assertion to “some files exist.”
4. Rerun the full closeout sequence, not only the wheel-inspection line, so the final receipt has one coherent passing log.
5. Preserve both logs if useful:
   - failed verifier log: proves where the harness assumption broke;
   - corrected verifier log: proves the final artifact/readback/behavior/build state.

## Example wheel inspection snippet

```bash
python3 -m build --wheel --outdir "$TMP/dist" >"$LOG" 2>&1
WHEEL=$(find "$TMP/dist" -maxdepth 1 -name '*.whl' -print -quit)
python3 - <<'PY' "$WHEEL"
import sys, zipfile
z = zipfile.ZipFile(sys.argv[1])
print("\n".join(n for n in z.namelist() if "agy" in n.lower() or "antigravity" in n.lower()))
PY
```

Then assert the exact namespace and count, for example:

```python
resources = [
    n for n in z.namelist()
    if "prismatic/resources/antigravity/workspace/agents/" in n and not n.endswith("/")
]
assert len(resources) == 10, resources
assert "prismatic/agy_customizations.py" in z.namelist()
```

## Reporting boundary

Report the corrected rerun as `AD_HOC_OR_CANONICAL=ad-hoc targeted closeout` unless the full project-defined canonical suite also ran in that same proof. Include `NOT_CLAIMING` for independent review, hosted CI, merge, and deployment when those remain pending.
