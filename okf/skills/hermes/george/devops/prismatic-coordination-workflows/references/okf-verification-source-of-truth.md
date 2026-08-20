# OKF verification source-of-truth pattern

Session-derived from the Prismatic merge-factory + Tariq Shaukat verification research work. Use when Michael asks for OKF/source-of-truth docs, verifier architecture, or systemic verification.

## Core framing

Prismatic's durable framing is:

```text
Objective -> Key Result -> Function -> Evidence
```

For verification architecture, this must expand beyond code tests into a typed claim/evidence system. Producer output, self-review, screenshots, manifests, and `DONE` markers are claims, not proof. Proof is bound to an exact artifact/revision, reproduced independently, and scoped by explicit non-claims.

## Shaukat/verifiers research takeaways to preserve

Source: Tariq Shaukat, "In the Land of AI Agents, the Verifiers Are King".

Reusable philosophy:

1. Plausible output is not correctness; better models can produce more convincing failures.
2. Generation is not the only bottleneck; verification, review capacity, maintainability, and trust become bottlenecks.
3. Use a loop: guide -> generate -> verify -> solve/remediate -> feed back into the next loop.
4. Embed verification in the software lifecycle; do not treat it as a final spot-check.
5. Watch for cognitive surrender: high-volume plausible agent output makes reviewers more likely to accept without independent proof.
6. Low-complexity, maintainable code improves agent usefulness; technical debt compounds under automation.

Claim classification rule:

- Vendor statistics and customer case studies stay labeled as vendor/case-study claims until independently corroborated.
- Survey statistics can be cited as survey evidence, not universal causal facts.
- External benchmark/task-horizon claims are directional context, not permission for unattended production automation.
- Prismatic should prefer local measured metrics for defect escape, repair loops, merge outcomes, rollback readiness, evidence retention, and provenance accuracy.

## Canonical source-of-truth document requirements

A proper Prismatic OKF/verification source of truth should include:

1. Architecture map: agent-level verification and system-level verification.
2. Ownership map: producer, independent verifier, merge judge, release/deploy authority, production owner, docs owner.
3. Claim taxonomy: producer claim, independent review, deterministic test, canonical suite, CI, installed-artifact proof, browser/media proof, production proof, security proof, rollback proof.
4. Evidence schema: task id, producer id, verifier id, exact commit/artifact digest, source lineage, command, environment, log path, log digest, proof class, scope, non-claims, expiry/invalidation conditions, decision.
5. Supersession rules: any revision change, path-port, dependency/env change, service restart, or evidence mutation invalidates the previous approval unless explicitly reverified.
6. Drift gates: link OKF rows to real files/routes/tests/scripts/owners and fail closed when docs cite missing paths or stale markers.
7. Runbooks: exact steps for producer review, repair, PR creation, merge, post-merge proof, rollback, and production proof.
8. Glossary and ADR index so future operators know which document supersedes older Fred/Kai/AGY loop language.

## Agent-level verification model

```text
Guide
  -> Produce
  -> Self-check (untrusted)
  -> Independent verifier
  -> Deterministic checks
  -> Exact-artifact attestation
  -> CI/canonical suite
  -> Merge judge
  -> Post-merge verification
  -> Production/delivery proof only when authorized
```

Never allow producer self-check to skip independent verification. Never count a producer-completed Linear state as merge-complete.

## System-level verification model

Verify the orchestrator itself, not only individual output:

- queue atomicity and duplicate dispatch prevention;
- lease ownership, stale-worker fencing, and same-principal renewal/acquire edge cases;
- concurrency caps and promotion gates;
- source/worktree isolation and clean current-main path-porting;
- PR head equals reviewed head;
- CI/check enforcement and branch-policy gaps;
- artifact provenance, evidence immutability, and secret-safe logging;
- installed-package behavior outside mutable source checkouts;
- production/runtime checkout durability;
- dashboard/API truthfulness and mock/sample labeling;
- rollback and stale-worker recovery drills;
- defect escape and repair-loop metrics.

## Hermes verification-guard pattern

If a turn edits files but Hermes reports no fresh canonical/lint/build command was detected, do not just restate older proof. Add a small ad-hoc verifier that exercises the changed behavior and the exact artifact identities involved:

1. Create the verifier with Python `tempfile` under `/tmp` and a `hermes-verify-` filename prefix.
2. Keep it focused: changed docs/validators/tests, expected markers, exact Git SHAs, clean worktree state, post-merge readback, local handoff/review assertions, or other direct behavior touched in the turn.
3. Run it from the relevant workdir and fail closed with assertions.
4. Remove the temporary file when possible.
5. Report the result as `AD_HOC_OR_CANONICAL=ad-hoc focused`; explicitly say it is not full canonical-suite green unless a real canonical suite was also run.

Minimal reusable sketch:

```python
import os, tempfile
from hermes_tools import write_file, terminal, shell_quote

fd, path = tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp")
os.close(fd)
try:
    write_file(path, """\
# assertions and focused commands here
print('RESULT=PASS')
print('AD_HOC_OR_CANONICAL=ad-hoc focused')
""")
    result = terminal("python3 " + shell_quote(path), timeout=180, workdir="/path/to/repo")
finally:
    try:
        os.unlink(path)
    except FileNotFoundError:
        pass
```

## Review pitfalls

- Do not mix broad source-of-truth docs into an unrelated code repair PR.
- Do not let a documentation branch rewrite older useful architecture docs blindly; add canonical supersession links and preserve useful details.
- Do not quote presentation/vendor numbers as Prismatic-proven facts.
- Do not claim dashboard/source-of-truth completion without link/schema/drift validation and exact-SHA review.
- If docs still describe an older Fred-only loop while George is the active merge judge, flag the drift and either reconcile or explicitly scope the document historically.
- If Hermes asks for a temporary verification script after edits, the proof class is ad-hoc focused by default; do not let the existence of an earlier full-suite log turn that temporary script into a new canonical-suite claim.
