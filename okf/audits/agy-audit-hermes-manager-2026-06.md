---
type: Report
title: AGY Hermes Agent Manager Audit — 2026-06-15
description: AGY audit of the Hermes Agent Manager / Hub, identifying gaps and improvement areas.
resource: /home/ubuntu/work/agentic-swarm-ops/docs/audits/agy-audit-hermes-manager-20260615.md
tags: [report, agy, audit, hermes-manager]
timestamp: 2026-06-19T10:52:02Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/audits/agy-audit-hermes-manager-2026-06.md
last_verified: 2026-06-25
verified_by: kai
status: current
migrated_from: /home/ubuntu/work/agentic-swarm-ops/docs/audits/agy-audit-hermes-manager-20260615.md
---

# Hermes Agent Manager & Swarm Control Surface Audit

### Top Next Action
Integrate the static frontend dashboard mockup ([prismatic-hub-prototype.html](file:///home/ubuntu/work/agentic-swarm-ops/docs/architecture/prismatic-hub-prototype.html)) with the prototype backend server ([server_prototype.py](file:///home/ubuntu/work/agentic-swarm-ops/server_prototype.py)) by creating a lightweight unified web application (using FastAPI or Flask). The frontend should be updated with standard JavaScript to consume live REST endpoints and stream real-time Server-Sent Events (SSE) from the backend, replacing the hardcoded HTML mockups with live data from the active `PtyManager` and `monitor-state.json`.

### Gap Analysis
The project currently faces a critical gap between its high-level vision (an interactive workspace control plane for the swarm) and its fragmented current state:
1. **Lack of Integration**: The frontend exists purely as a static design mockup ([prismatic-hub-prototype.html](file:///home/ubuntu/work/agentic-swarm-ops/docs/architecture/prismatic-hub-prototype.html)) and the backend is a disconnected prototype script ([server_prototype.py](file:///home/ubuntu/work/agentic-swarm-ops/server_prototype.py)). There is no live wiring connecting them.
2. **Missing Workspace Context**: While the design details a Workspace/Session/Run hierarchy, the frontend does not dynamically parse or render the actual YAML-based workspace registries (`hermes-workspaces.yaml`) or live agent state data ([monitor-state.json](file:///home/ubuntu/work/agentic-swarm-ops/monitor-state.json)).
3. **Repository Fragmentation**: The code currently lives nested within the `agentic-swarm-ops` configuration repository rather than in a dedicated project repository, complicating deployment, package versioning, and open-source contribution workflows.
4. **Task/Sprinting Misalignment**: The current active sprint tasks (e.g., GRO-298, GRO-297, GRO-290, GRO-289) focus on capability demonstration and feature building for CYM/SWT, rather than core dashboard infrastructure development.

### Proposed Issues

#### Issue 1: Scaffolding a Dedicated Repository for Prismatic Agent Hub
* **Title**: `PROJ-001`: Extract Prismatic Hub Dashboard & Core Engine into a Dedicated Repository
* **Description**: To support portable, multi-agent deployment and ease versioning, extract the dashboard and core engine code out of the `agentic-swarm-ops` repository. Initialize a new repo `mbgulden/prismatic-hub` with a clean `pyproject.toml` configuration as outlined in the Phase 1 architectural specification.
* **Actionable Steps**:
  1. Initialize the new Git repository.
  2. Scaffolding folders: `prismatic/`, `config/`, `skills/`, and `web/`.
  3. Relocate [pty_manager.py](file:///home/ubuntu/work/agentic-swarm-ops/pty_manager.py) to `prismatic/pty_manager.py` and [prismatic-hub-prototype.html](file:///home/ubuntu/work/agentic-swarm-ops/docs/architecture/prismatic-hub-prototype.html) to `web/index.html`.
  4. Implement basic test pipeline validation.
* **Suggested Agent**: `agent:jules`

#### Issue 2: Build a Unified Backend Server with Live APIs and SSE Streaming
* **Title**: `PROJ-002`: Implement a Unified FastAPI Backend for Live Swarm Telemetry
* **Description**: Create a production-ready FastAPI application to replace the mock [server_prototype.py](file:///home/ubuntu/work/agentic-swarm-ops/server_prototype.py) web server. The server must serve the dashboard UI, interface with the `RunManager` from [pty_manager.py](file:///home/ubuntu/work/agentic-swarm-ops/pty_manager.py), and expose live APIs for agent run execution and system-wide state reporting.
* **Actionable Steps**:
  1. Build endpoints: GET `/api/status` (reads [monitor-state.json](file:///home/ubuntu/work/agentic-swarm-ops/monitor-state.json)), GET `/api/workspaces` (parses `hermes-workspaces.yaml`).
  2. Implement an SSE endpoint `/api/stream` pushing live log chunks appended to the PTY `RingBuffer`.
  3. Serve static files from the frontend assets directory.
* **Suggested Agent**: `agent:hermes`

#### Issue 3: Dynamically Wire the Frontend Mockup to Backend APIs
* **Title**: `PROJ-003`: Wire Prismatic Dashboard UI to Backend REST and SSE Endpoints
* **Description**: Upgrade the vanilla JS/HTML prototype dashboard ([prismatic-hub-prototype.html](file:///home/ubuntu/work/agentic-swarm-ops/docs/architecture/prismatic-hub-prototype.html)) to dynamically fetch state and consume real-time telemetry logs.
* **Actionable Steps**:
  1. Use browser-native `fetch()` on page load to retrieve active workspaces and agent state cards.
  2. Implement an `EventSource` instance listening to `/api/stream` to append incoming run chunks to the Recent Activity panel.
  3. Wire the right drawer component to load session-specific metrics and run telemetry when clicking an agent card.
* **Suggested Agent**: `agent:codex`

#### Issue 4: Implement HALT/PAUSE Safety Controls in the Process Lifecycle
* **Title**: `PROJ-004`: Implement Process Signal Controls (HALT/PAUSE) in PtyManager
* **Description**: Enable dashboard-level process management to halt or pause runaway agent execution. This maps to the safety requirements identified in the visibility porting analysis.
* **Actionable Steps**:
  1. Add `pause()` (using `SIGSTOP`) and `resume()` (using `SIGCONT`) methods to `PtyProcess` in [pty_manager.py](file:///home/ubuntu/work/agentic-swarm-ops/pty_manager.py).
  2. Add `terminate()` (using `SIGKILL`) for immediate hard stops.
  3. Expose POST `/api/runs/{run_id}/pause` and POST `/api/runs/{run_id}/terminate` endpoints.
  4. Connect the frontend "Pause Agent" and "Halt/Close" buttons in the right drawer to these API endpoints.
* **Suggested Agent**: `agent:hermes`
