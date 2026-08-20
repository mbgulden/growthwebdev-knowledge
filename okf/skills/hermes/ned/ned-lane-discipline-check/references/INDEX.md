# Ned Lane Discipline Check — References Index

* **Created:** 2026-07-01
* **Last updated:** 2026-07-01
* **Owner:** agent:ned

This index catalogs the 28 reference documents supporting the `ned-lane-discipline-check` skill.

---

## Reference Directory Inventory

| File | Status | Summary / Action |
| :--- | :--- | :--- |
| **[anchor-existence-validation-by-body-content.md](anchor-existence-validation-by-body-content.md)** | `active` | Refinement for validating anchor comment existence by checking the comment body content instead of the user ID (since all sub-agents authenticate under Michael Gulden's API key). |
| **[anchor-threshold-crossing-transition.md](anchor-threshold-crossing-transition.md)** | `active` | Outlines the 3-step transition protocol to run when the active anchor comment is older than 6 hours. |
| **[bash-heredoc-backtick-pitfall.md](bash-heredoc-backtick-pitfall.md)** | `active` | Details pitfalls of shell-escaping backticks and parentheses in inline GraphQL queries using bash heredocs. |
| **[batch-b-phase1-activeoahu-detector.md](batch-b-phase1-activeoahu-detector.md)** | `active` | Specific detector signature, correct-lane mapping, and standing-cure text for Batch B (Phase 1 Active Oahu storefront hardware + Human Design curriculum). |
| **[bulk-verify-graphql-recipe.md](_archive/bulk-verify-graphql-recipe.md)** | `superseded` | Recipe for verifying a batch of Linear issues via GraphQL in one shot. Superseded by `linear-dequeue-graphql-recipe.md`. Moved to `_archive/`. |
| **[curator-flag-stale-backlog-misroute-fingerprint.md](curator-flag-stale-backlog-misroute-fingerprint.md)** | `active` | Codification of the curator flag stale-backlog auto-routing trap, where backlog issues are misrouted to Ned. |
| **[finalize-task-sh-argument-validation-pitfall.md](finalize-task-sh-argument-validation-pitfall.md)** | `active` | Details argument-validation pitfall when calling `finalize_task.sh` with out-of-lane issues. |
| **[finalize-task-sh-three-failure-modes-and-rollback.md](finalize-task-sh-three-failure-modes-and-rollback.md)** | `active` | Documents the three main failure modes of `finalize_task.sh` and their rollback procedures. |
| **[fresh-misroute-batch-detector-gap.md](fresh-misroute-batch-detector-gap.md)** | `active` | Canonical disposal playbook when a misroute batch does not match any registered signature in `suppress_class_detect.py`. |
| **[in-lane-subsumed-by-prior-investigation.md](in-lane-subsumed-by-prior-investigation.md)** | `active` | Playbook refinement for cases where rotated-in issues are in-lane but subsumed by a prior root-cause investigation. |
| **[interview-content-fabrication-trap.md](interview-content-fabrication-trap.md)** | `active` | Refinement for content-interview issues where the description requires recording audio/video (which Ned cannot do without fabricating voices). |
| **[linear-dequeue-graphql-recipe.md](../../../../../work/okf/operations/linear-dequeue-graphql-recipe.md)** | `promote-to-okf` | General recipes for posting comments and reversing state promotions via Linear GraphQL. Promoted to OKF Operations. |
| **[linear-label-change-quirks.md](linear-label-change-quirks.md)** | `active` | Explores quirks of Linear API `IssueUpdate` calls, such as auto-transitioning status on label changes. |
| **[linear-lane-filter-query.md](linear-lane-filter-query.md)** | `active` | Canonical Linear GraphQL query shapes and filters for Ned's pickup checks. |
| **[mixed-batch-triage-recipe.md](mixed-batch-triage-recipe.md)** | `active` | Playbook for triaging a batch that contains a mix of in-lane and misrouted issues. |
| **[ned-r153-batch-anchor-shift-detection.md](ned-r153-batch-anchor-shift-detection.md)** | `active` | Anchor detection logic for cron pickups to find the correct recurrence-detection anchor. |
| **[ned-r154-batch-b-sustained-suppress-manual-curl-20260629.md](ned-r154-batch-b-sustained-suppress-manual-curl-20260629.md)** | `active` | Manual curl procedures used when the scorer script was inaccessible. |
| **[pass-log-2026-06.md](_archive/pass-log-2026-06.md)** | `archive` | Log of cron triage passes from late June 2026. Superseded by `recurring-batch-suppress-2026-06-29.md`. Moved to `_archive/`. |
| **[pass-n25-sustained-byte-identical-feed-ratchet.md](pass-n25-sustained-byte-identical-feed-ratchet.md)** | `active` | Lightweight 3-step ratchet playbook for byte-identical scanner feeds. |
| **[per-issue-branch-vs-ratchet-subsumption-asymmetry.md](per-issue-branch-vs-ratchet-subsumption-asymmetry.md)** | `active` | Differentiates how subsumption is handled during scanner-rotation-disposal versus per-issue-branch pickup. |
| **[phase1-activeoahu-hardware-batch-playbook.md](phase1-activeoahu-hardware-batch-playbook.md)** | `active` | Standing playbooks and cures for Phase 1 storefront hardware batch issues. |
| **[recurring-batch-suppress-2026-06-29.md](recurring-batch-suppress-2026-06-29.md)** | `active` | Quick reference for the recurring-batch SUPPRESS pattern and the 5a.5 silent-protocol gate. |
| **[recurring-batch-suppress-pitfalls.md](recurring-batch-suppress-pitfalls.md)** | `active` | Lessons learned and pitfalls observed during recurring-batch suppression runs. |
| **[recurring-misroute-batch-playbook.md](recurring-misroute-batch-playbook.md)** | `active` | Playbook for recurring-misroute batches that Michael has dequeued multiple times. |
| **[suppress-detector-cli-drift.md](suppress-detector-cli-drift.md)** | `active` | Documents CLI drift in `suppress_class_detect.py` where option flags became misaligned. |
| **[sustained-silent-cron-subset-cadence-irregularity.md](sustained-silent-cron-subset-cadence-irregularity.md)** | `active` | Playbook refinements for handling cadence irregularities and subset changes on silent cron jobs. |
| **[telemetry-silence-investigation-recipe.md](telemetry-silence-investigation-recipe.md)** | `active` | Step-by-step recipe for investigating missing table writes in the event router telemetry. |
| **[telemetry-wiring-subtask-misroute-pattern.md](telemetry-wiring-subtask-misroute-pattern.md)** | `active` | Diagnostics and signatures for telemetry-wiring sub-tasks that get auto-routed to Ned. |
