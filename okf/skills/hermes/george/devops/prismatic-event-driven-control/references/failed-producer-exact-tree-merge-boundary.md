# Failed producer recovery to exact-tree merge boundary

Use when an admitted cap-1 producer terminates or overclaims `PASS`, but leaves useful source diffs that may still be salvageable.

## Durable lesson

Do not convert a failed/killed producer into producer success. Preserve the producer failure as a separate fact, then recover only by creating a normal immutable candidate with clean tree, exact-head review, canonical proof, clean-room installed proof, and merge-tree verification.

## Checklist

1. Record the failed producer boundary first:
   - `PRODUCER_COMPLETED=false`
   - exit signal/status
   - any `cancel_requested`/deadline/runtime flags
   - `PRODUCER_RESULT_OVERCLAIMED=true` when result text says `PASS` without a committed exact candidate.
2. Remove undeclared marker files or unrelated residue only after proving they are outside the task contract.
3. Scope repairs to the declared/authorized path set, expanding only with explicit authorization when tests must change.
4. Commit the recovered candidate before independent review. Bind every review to commit and tree.
5. If review finds blockers, repair and recommit; prior reviews are stale for acceptance.
6. Run the canonical suite under an uncontaminated verifier environment; unset misleading inherited `VIRTUAL_ENV`/`PYTHONPATH` when they redirect package installs/imports.
7. Add clean-room installed-wheel proof from an empty CWD when runtime/import/resource behavior matters.
8. Before merge, prove:
   - live PR head equals reviewed candidate;
   - merge commit contains the candidate as ancestor;
   - merge tree equals reviewed candidate tree.
9. After merge, update durable handoff/report artifacts, then run one final ad-hoc verifier that reads those final artifacts and proves deployment remains held.

## Runtime inventory hardening pattern

For event-consumer/service migration work, do not accept a broad string match like “consumer appears in ExecStart.” Instead:

- validate public inventory shape and dependency declarations fail closed;
- keep private launcher/config paths out of public source;
- parse actual `ExecStart` argv, including systemd structured forms;
- accept only the canonical module/command and known value-bearing flags;
- reject substring spoofing, wrong types, nonexistent declared runtime paths, and source-path mismatches.

## Reporting boundary

A clean merge is not deployment. Report:

```text
MERGED=true
DEPLOYED=false
NEXT_AUTHORIZATION_POINT=explicit immutable deployment decision
NOT_CLAIMING=deployment, service restart/unmask/enable, production event proof, Linear write, cap increase
```

## CI exception boundary

Hosted CI failures that execute zero steps are provider/infrastructure signal, not product proof. They may be excepted only when exact-head canonical, clean-room, security, and independent review evidence are complete and recorded. Do not treat hosted CI as acceptance authority.
