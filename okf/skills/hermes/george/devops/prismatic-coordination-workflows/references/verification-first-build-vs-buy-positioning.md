# Verification-first build-vs-buy and competitive-positioning pattern

Use when Michael asks whether Prismatic is taking the best route, whether a prebuilt platform should replace it, or what makes it worth using beside other agent tools.

## Product-boundary decision

The durable strategic split is:

- **Integrate/buy producers and commodity infrastructure:** coding agents, IDEs, task trackers, PR/CI, agent runtimes, telemetry backends, identity, signing, and—after evidence—a durable workflow substrate.
- **Build/defend Prismatic's trust layer:** exact-artifact claim/evidence contracts, independent verification, stale-evidence invalidation, typed cross-artifact completion, task-manager-neutral promotion state, truthful source/freshness UI, and local/private retained provenance.

Recommended category:

> Verification and promotion control plane for agent work.

Recommended positioning:

> Bring any agent. Keep every artifact. Promote only what you can prove.

If the use case is only issue-to-PR coding, GitHub Agent HQ/Copilot cloud agent plus Claude/Codex or another mature coding-agent service is likely the better primary product. Prismatic remains justified only when independent evidence/promotion, provider neutrality, local ownership, or non-code artifacts matter.

## Competitive review rules

1. Treat vendor pages as vendor capability claims, not independently proven behavior.
2. Use `NOT-OBSERVED` for an undocumented feature; never infer that it is absent.
3. Compare by layers:
   - producer/coding agents;
   - multi-agent command centers;
   - durable workflow runtimes;
   - observability/evaluation;
   - policy/identity;
   - provenance/signing standards;
   - enterprise business-agent platforms.
4. GitHub Agent HQ is the closest threat to a code-only Prismatic command center: multi-agent mission control, third-party agents, review, controls, metrics, GitHub Mobile/VS Code, and GitHub-native issue-to-PR flow make generic orchestration/dashboard features table stakes.
5. Dashboard, multi-agent dispatch, MCP, approvals, task graphs, code review, pause/resume, plugins, and mobile alerts are supporting features, not a moat.
6. Self-build is an internal proof workload, not a strong external product category.

## Standards-first adoption map

- SLSA/in-toto for portable provenance and supply-chain step semantics.
- Sigstore/Cosign for signed attestations.
- OpenTelemetry GenAI conventions for traces/metrics.
- OPA/Cedar-class engines before hardcoded policy becomes a platform.
- OIDC/OAuth/RBAC for hosted/multi-user identity.
- MCP/A2A as untrusted interoperability inputs behind Prismatic identity, policy, and evidence gates.
- Temporal comparison spike before continuing to expand custom retries/cursors/recovery beyond supervised cap 1; do not rewrite without equivalent failure-injection evidence.

## Research OKF structure

A useful build-vs-buy OKF should include:

1. executive verdict and narrowed product definition;
2. exact-current-main local proof plus maturity/non-claims;
3. competitor matrix by layer;
4. current vs planned differentiators, each ranked as moat/supporting/table-stakes/distraction;
5. build/buy/integrate matrix;
6. clean-room credibility objective before new features;
7. exact-evidence objective;
8. producer-neutral adapter objective;
9. cross-artifact proof objective;
10. standards/adoption objective;
11. truthful operator UX objective;
12. external design-partner validation and kill criteria.

## Current-main credibility check

Before strategic optimism, run the documented clean-clone/public smoke on exact current main. A stale smoke or route/plugin identity mismatch is strategic evidence: Prismatic must prevent the same contract drift it claims to govern. Keep focused core tests and public/clean-room smoke as separate proof classes.

## Verification

Bind the research document to:

- exact `origin/main` SHA;
- focused local test log and digest;
- public smoke log and digest (pass or fail);
- source URL reachability report;
- structural marker/OKF-table checks;
- explicit `VENDOR-DOC`, `STANDARD`, `RESEARCH`, `LOCAL-PROOF`, `INTERNAL-PLAN`, and `NOT-OBSERVED` claim classes.

Use a `/tmp/hermes-verify-*` script, save the compact proof log, delete the temporary verifier, and label the result `AD_HOC_OR_CANONICAL=ad-hoc focused` unless a canonical suite actually ran.
