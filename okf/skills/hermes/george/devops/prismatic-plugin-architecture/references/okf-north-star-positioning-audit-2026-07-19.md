# OKF / North Star positioning audit pattern — 2026-07-19

## Session learning

When Michael asks to turn positioning language into an OKF/North Star audit report, treat it as a **product doctrine alignment audit**, not just copywriting.

The useful framing from this session:

```text
Prismatic is an evidence-first work orchestration layer for AI agents, plugins, and operators.
Prismatic makes AI agent work auditable and safe to integrate.
Prismatic is a task-manager-agnostic control plane that turns agent output into verified work packets, artifacts, and promotion decisions.
```

This aligns with the canonical docs:

- `docs/north-star.md` — install, immediate value, governed capabilities, dashboard operation, safe detach without losing state/artifacts/provenance/audit history.
- `docs/okf-evidence-map.md` — `Objective → Key Result → Function → Evidence` and every workflow visible/auditable/dashboard-operable.
- OKF North Star audit/synthesis docs — original gaps around runs-without-you, governance, work beyond code, and helping others build dreams.

## Reusable audit move

Upgrade the OKF shape from:

```text
Objective → Key Result → Function → Evidence
```

to:

```text
Objective → Key Result → Function → Evidence → Promotion Decision
```

Promotion decision values that fit Prismatic's control-plane thesis:

| Decision | Meaning |
|---|---|
| `promote` | Evidence is sufficient to move work forward. |
| `open_or_update_pr` | Code change is clean enough to create/update a PR. |
| `needs_approval` | Human approval is required before execution/export/publish/deploy. |
| `blocked` | Missing proof, failed checks, policy block, or unsafe state. |
| `superseded` | Output is obsolete because better/newer work exists. |
| `clean_rebuild` | Useful idea exists, but implementation/output is contaminated. |
| `manual_review` | Ambiguous or high-risk; operator must decide. |
| `reject` | Work should not be integrated. |

## Recommended report structure

1. **Status: PASS/PARTIAL/BLOCKED** — state whether the requested positioning aligns with North Star/OKF.
2. **Source alignment matrix** — compare the requested thesis against `north-star.md`, `okf-evidence-map.md`, and current runway handoff.
3. **Product thesis** — primary one-liner, safety one-liner, control-plane one-liner.
4. **OKF upgrade** — explain `Evidence → Promotion Decision` as the missing explicit layer.
5. **North Star woven into OKF maps** — public launch, plugin governance, artifact/provenance, dashboard-primary, media/business plugins.
6. **Immediate next slice** — usually point back to the implementation gate that proves the thesis; as of this session: `AGY_COMPLETED_WORK_INTEGRATION_GATE_OK`.
7. **Boundary/non-claims** — docs/report only unless repo docs were actually patched and verified.
8. **Compact proof packet** — verify the generated Markdown report with a `/tmp/hermes-verify-*` script and report as ad-hoc targeted, not canonical suite green.

## Pitfalls

- Do not frame this as tagline polish only. Michael wants the North Star woven in so Prismatic stays on-track.
- Do not narrow Prismatic to AGY/Linear/dashboard/PR helper. Those are adapters/surfaces; the category is evidence-first AI work orchestration.
- Do not claim implementation or repo-doc updates unless you actually patched and verified the repo.
- Do not omit the next proof slice. Tie positioning back to a concrete gate such as completed-work integration, dashboard evidence board, artifact/provenance, or plugin governance.
