# Read-only Prismatic Engine adapter proof

Use this only after the standalone PWP repository has an explicit optional PE adapter. It is a compatibility check, not standalone acceptance or a cutover.

## Reproducible shape

1. Clone the candidate PWP branch into a disposable directory and make an immutable detached PE worktree at the approved freeze SHA.
2. Create a venv outside both checkouts; install PWP non-editably with only its dev dependencies.
3. Run adapter-focused tests from outside the PWP repository with `PYTHONPATH=<immutable-pe-worktree>`. This permits the adapter to resolve only PE's published/current interface and capability-router modules while ensuring `prismatic_web_publisher` resolves from `site-packages`.
4. Run a direct import/subclass probe for the adapter and PE plugin base class. Print both module paths.
5. Assert `git -C <immutable-pe-worktree> status --porcelain` is empty after the test.
6. Record candidate and PE commit/tree IDs, exact test result, module paths, read-only status, and explicit non-claims in the task RESULT/evidence document.

## Boundary wording

A PASS means: the optional adapter was compatible with the specified immutable PE checkout. It does **not** mean the PWP standalone wheel/resources/fresh-clone gates passed, PE Core changed, a monorepo copy can be removed, or any deployment/cutover is approved.

## Finalization ordering

Commit the evidence document before the test. After the test, update it with actual IDs/results and commit again. Derive the final PWP commit/tree *after* the evidence commit rather than carrying forward a pre-evidence tree ID. Use the normal finalizer, then independently read back Linear state/comment and unlock the exact acquired lock path with the same owner argument shape if needed.
