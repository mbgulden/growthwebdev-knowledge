# Digest-binding review: detached helper vs classifier path

Use this when reviewing Prismatic tests that purport to prove digest or authority binding.

## Lesson

A test that validates an isolated helper against arbitrary sample bytes does not prove the production/classifier admissibility path enforces digest binding. Review must trace the admissibility decision itself.

## Review probes

- Locate the function/path that actually classifies or admits a candidate export.
- Confirm that path parses the binding fields, not only that a helper exists.
- Confirm it recomputes SHA-256 from exact canonical bytes supplied to the classifier path.
- Confirm it compares recomputed values to parsed bindings inside the decision path.
- Confirm malformed, uppercase, wrong-length, placeholder, alias/short-SHA, missing-byte, and mismatch cases fail at classifier level.
- Confirm monkeypatching/bypassing any detached digest helper cannot make a mismatched candidate admissible.
- If real production hook/manifest/config bytes are out of scope or absent, require zero admitted production lines and fail closed.

## Blocking finding shape

```text
RESULT=BLOCKED
FINDING=detached helper/shape-only digest proof does not exercise classifier admissibility
CLASSIFIER_DIGEST_BINDING_PRESENT=false
REPAIR_REQUIRED=move recomputation/comparison into classifier-level test interface and add adversarial bypass regression
NOT_CLAIMING=candidate acceptance, PR, merge, deployment, or production hook implementation
```

## Boundary

This is a semantic proof gap, not a style issue. A locally green focused suite can still be blocked when the asserted invariant is tested outside the real decision path.
