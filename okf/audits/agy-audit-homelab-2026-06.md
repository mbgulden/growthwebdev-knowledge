---
type: Report
title: AGY Homelab Repo Audit — 2026-06-15
description: AGY gap analysis of the homelab repository with prioritized next actions.
resource: /home/ubuntu/work/agentic-swarm-ops/docs/audits/agy-audit-homelab-20260615.md
tags: [report, agy, audit, homelab]
timestamp: 2026-06-19T10:52:02Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/audits/agy-audit-homelab-2026-06.md
last_verified: 2026-06-19
verified_by: kai
status: current
migrated_from: /home/ubuntu/work/agentic-swarm-ops/docs/audits/agy-audit-homelab-20260615.md
---

### Top Next Action
The highest-impact next step to advance toward the vision is to **clone the `mbgulden/SovereignSentinel` GitHub repository onto the disk and merge the existing local `homelab` files into it**. 

Specifically:
1. Clone `mbgulden/SovereignSentinel` (utilizing the default branch `master`) to `~/work/SovereignSentinel`.
2. Move the local monitoring tools from `~/work/homelab/ops/` ([node_scanner.py](file:///home/ubuntu/work/homelab/ops/node_scanner.py) and [proxmox_connector.py](file:///home/ubuntu/work/homelab/ops/proxmox_connector.py)) into the cloned repository.
3. Set up the local scripts to write their inventory JSON outputs directly into the version-controlled workspace.
4. Create an initial commit with the current hardware and VM/LXC snapshots to establish a baseline.

This establishes the repository as the single version-controlled source of truth, enabling agents to commit and track updates (resolving `GRO-1597`).

---

### Gap Analysis
The biggest gaps between the current state and the project vision are:
1. **No Version-Controlled Workspace:** While the project vision is to have a committed and tracked source of truth, the `SovereignSentinel` repository is not cloned on disk. The existing scanning scripts are run in an untracked local folder (`~/work/homelab`), and their JSON outputs are completely un-versioned, preventing historical tracking or change analysis.
2. **Issue Stagnation due to Missing Agent Labels:** All 39 issues are stalled in the Backlog with zero agent labels. Because the Hermes orchestrator uses labels (such as `agent:antigravity-cli` or `agent:codex`) to route issues to autonomous agents, the entire backlog is currently invisible to the swarm and is receiving no active attention.
3. **No Automated or Scheduled Scanning:** The collection scripts must be triggered manually. There is no active systemd daemon (such as requested in `GRO-1628`) or cron job automating the scans to detect hardware drift or node failures (requested in `GRO-1599`).

---

### Proposed Issues
1. **Title:** `Clone SovereignSentinel repository and migrate local homelab scripts`
   - **Description:** Clone the remote `mbgulden/SovereignSentinel` repository (branch `master`) to `~/work/SovereignSentinel` and migrate the local node scanner and Proxmox connector scripts into its folder structure.
2. **Title:** `Triage and label the 39 unassigned Homelab Inventory Backlog issues`
   - **Description:** Review the 39 backlog issues and apply appropriate routing labels (e.g. `agent:codex`, `agent:antigravity-cli`, and `requires:human-approval`) to enable autonomous swarm execution.
3. **Title:** `Daemonize Proxmox connector and node scanner via systemd or cron`
   - **Description:** Implement a systemd service or a local cron job to execute the node scanner and Proxmox connector scripts on a regular schedule (e.g., weekly) and log status.
4. **Title:** `Implement git-based hardware drift detection and alerting`
   - **Description:** Create a script to compare newly scanned hardware inventory snapshots against version-controlled baselines, flagging changes or offline nodes.
5. **Title:** `Consolidate scanner outputs into a single unified inventory.json`
   - **Description:** Update both collector scripts to merge their respective VM, container, and physical host details into a unified `inventory.json` schema.
