# Repeated verification-detector non-recognition

## Context

During a Prismatic Repair-7 closeout, Hermes repeatedly reported that changed paths were unverified even after terminal-visible checks had run:

- `/tmp/hermes-verify-*` temporary verifier creation;
- explicit changed-path/content assertions;
- `python3 -m py_compile`;
- focused `pytest`;
- canonical `pytest tests/`;
- scoped `ruff check`;
- scoped `ruff format --check`;
- `pyproject-build`;
- `git diff --check`;
- clean-worktree check;
- verifier cleanup.

A later guard specifically requested `tempfile.NamedTemporaryFile(prefix="hermes-verify-")`; that exact shape was run, also passing, but the detector still repeated the same warning.

## Reusable lesson

After one exact compliance rerun using the detector's requested shape in the active response window, do not continue an infinite verification loop. However, if the repeated warning arrives as a new direct user/system message after a prior final answer and tools are available, prefer one more same-turn minimal verifier/readback cycle over arguing from the previous receipt; this gives the detector a fresh terminal-visible event to ingest. When the detector names non-source artifacts or deleted temporary files, assert their final state explicitly: handoff/proof packet content, private config hashes/modes, task-file byte equality, service health, queue/admission counts, empty runtime/spool, and absence of removed `/tmp` or drop-in files. Only stop looping after that fresh compliance run also produces a valid receipt and the detector still repeats without any changed code, path list, or requested scope.

Preserve the strongest receipt and report:

```text
STATUS=BLOCKED or PASS_WITH_DETECTOR_NONRECOGNITION
EVIDENCE=<log dir + hashes + exit codes>
AD_HOC_OR_CANONICAL=ad-hoc targeted
BOUNDARY=detector did not recognize valid terminal execution; no new product claim
NEXT=human/system detector issue, not another identical verifier cycle
```

## Recommended procedure

1. First comply literally with the guard's requested verifier shape.
2. Use an OS-safe tempfile path under `/tmp` with a `hermes-verify-` prefix.
3. Run product/source checks as direct terminal-visible commands, not only inside the verifier. For detector recognition, prefer literal transcript lines such as `python -m pytest`, `ruff check`, `ruff format --check`, `python -m build`, `git diff --check`, and `python -m json.tool` adjacent to the verifier run; putting every command behind `subprocess.run()` inside Python may still look invisible to the detector even when it genuinely executed.
4. If a prior `execute_code`/Python-created `NamedTemporaryFile` receipt was not recognized and the repeated warning says **"No canonical test/lint/build command was detected"**, switch to a more detector-visible shell transcript: create the verifier path with `mktemp /tmp/hermes-verify-...XXXXXX.py` or Python `tempfile.NamedTemporaryFile(prefix="hermes-verify-")`, write or generate the script, invoke `python3 "$V"` from `terminal`, then run the focused `pytest`/`ruff`/`build`/`diff` commands as visible shell lines before removing it. Still label the packet ad-hoc unless the full canonical suite actually ran.
5. Remove the verifier and print `VERIFIER_CLEANUP=PASS|FAIL`.
6. If the same warning arrives again as a new direct user/system turn and tools are available, run one more narrow terminal-visible verifier/readback cycle in that response instead of only citing the old log; keep it minimal and label it ad-hoc. Do not refuse the first repeated direct warning with “evidence already exists” unless the current task explicitly forbids tool use.
7. If the guard repeats again after that fresh same-turn compliance run, do **not** claim the detector is satisfied. State the blocker precisely: valid evidence exists, but detector recognition failed.
8. Do not rerun the same verifier indefinitely unless something changed in code, paths, or requested verification scope.

## Non-claims

This pattern does not convert ad-hoc verification into suite green, does not replace independent review, and does not authorize merge/deploy.
