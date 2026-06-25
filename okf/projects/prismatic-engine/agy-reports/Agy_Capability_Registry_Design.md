---
type: Reference
title: "Agy Capability Registry Design"
description: "Mirrored from Google Drive on 2026-06-25. Source: Drive file 1NV6cnlUxyjntAjrngW3h8egWoeFV2xuzbzXqWGdQetA (modified 2026-06-08). Originally part of the Prismatic source plugin plans and AGY architecture reports."
resource: https://docs.google.com/document/d/1NV6cnlUxyjntAjrngW3h8egWoeFV2xuzbzXqWGdQetA/edit?usp=drivesdk
tags: [drive-mirror, prismatic, gemini-evaluation, agy-report, source-plugin-plans]
timestamp: 2026-06-25T04:04:32.858Z
git_repo: mbgulden/growthwebdev-knowledge
linear_issue: TBD
last_verified: 2026-06-25
verified_by: fred
status: current
drive_file_id: "1NV6cnlUxyjntAjrngW3h8egWoeFV2xuzbzXqWGdQetA"
drive_modified: "2026-06-08T10:10:18.519Z"
---

\# Prismatic Engine Spec — Agent Capability Registry Design  
\*\*Linear Issue:\*\* \[GRO-820\](https://linear.app/growthwebdev/issue/GRO-820)    
\*\*Author:\*\* AGY (Antigravity Senior Systems Architect)    
\*\*Date:\*\* June 8, 2026    
\*\*Status:\*\* Complete — Ready for Review

\---

\#\# 1\. Executive Summary

In current iterations of the Prismatic Engine, workspace governance rules (directory lanes, branch prefixes, locks) are bound statically to \*\*agents\*\* (e.g., \`fred\`, \`kai\`, \`agy\`). However, multi-modal agents like \`agy\` can perform multiple roles (e.g., design, research, review, synthesis). Binding static lanes to an agent identity limits their operational scope and creates conflict patterns.

This document designs the \*\*Agent Capability Registry\*\*, which shifts workspace governance from agent-centric static profiles to \*\*per-task role assignments\*\*. 

\---

\#\# 2\. Design Questions & Solutions

\#\#\# 2.1 Configuration Location: \`PRISMATIC\_ENGINE.yaml\` vs. \`capabilities.yaml\`  
\*\*Recommendation:\*\* Unified configuration in \`PRISMATIC\_ENGINE.yaml\`.  
\* \*\*Rationale:\*\* Keeping the capability registry within \`PRISMATIC\_ENGINE.yaml\` prevents configuration drift. Workspace settings, agent binary paths, pipelines, and capabilities all share dependencies (e.g., pipeline steps map to capabilities, which map to lanes and agents). A single file ensures repository state is declaratively tracked in one Git commit.

\#\#\# 2.2 Routing Decision Mechanics  
The dispatcher determines task routing using a two-tiered resolution process:  
1\. \*\*Pipeline Config:\*\* The dispatcher polls Linear for issues. When it detects a pipeline label (e.g., \`pipeline::content-pipeline\`), it loads the pipeline definition. Each step in the pipeline specifies a \*\*capability/role\*\* (e.g., \`role: designer\`), not an agent name.  
2\. \*\*Dynamic Capability Resolution:\*\* The dispatcher queries the capability registry to find which agents are registered for that capability, checks their availability, selects the best agent, and spins up the execution.  
3\. \*\*Linear Direct Label Override:\*\* For ad-hoc issues without a pipeline, a Linear label format such as \`role::researcher\` can be applied. The dispatcher interprets this label to route the issue to an agent registered under that capability.

\#\#\# 2.3 Agent Concurrency: Running Multiple Capabilities Simultaneously  
\*\*Problem:\*\* Can \`agy\` run a \`research\` task and a \`review\` task concurrently?  
\* \*\*Solution:\*\* Yes, by spawning a new AGY instance per capability, isolated via \*\*Git Worktrees\*\*.  
  \- Since AGY is a multi-agent platform, it does not multiplex or switch capabilities within a single process. Instead, the dispatcher spawns a dedicated, independent AGY process instance for each incoming task.  
  \- Concurrency safety is managed at the hardware utilization level rather than a fixed configuration limit, allowing AGY to scale instances dynamically based on bare-metal capacity.  
  \- Jules can scale up to 50 concurrent sessions. Other agents like Fred, Kai, and Autobot remain strictly constrained to single-instance execution (\`max\_concurrent: 1\`).

\#\#\# 2.4 Capability Unavailability & Queueing  
\* \*\*Mechanism:\*\* When a task requires a capability but all registered agents are at their concurrency limits, the task is marked as \`QUEUED\` in the database (\`run\_records.db\` / \`event\_router.db\`).  
\* \*\*Preemption:\*\* If a high-priority task arrives, it can preempt a running task of lower priority by sending a pause signal to the running agent container/process, releasing its locks, and queuing it for resumption later.

\#\#\# 2.5 Interaction with Workspace Governance (Lanes & Locks)  
\* \*\*Dynamic Scoping:\*\* Rather than loading static agent-wide lanes, the dispatcher injects the capability's specific \`lanes\` and \`branch\_prefix\` into the task's execution environment.  
\* \*\*Prompt Injection:\*\* The system prompt (\`SOUL.md\` overlay) is dynamically updated before agent startup to outline the capability's allowed directories.  
\* \*\*Pre-Push Validation:\*\* The git \`pre-push\` hook verifies claims by looking up the specific task ID (\`HERMES\_TASK\_ID\`) to see what capability was assigned, and matches the push changes against that capability's allowed lanes.

\---

\#\# 3\. Proposed YAML Schema (\`PRISMATIC\_ENGINE.yaml\`)

\`\`\`yaml  
version: 2

settings:  
  locks\_dir: "/home/ubuntu/.antigravity"  
  heartbeat\_ttl\_ms: 300000  
  staging\_branch: "deploy-fresh"  
  staging\_governor: "fred"

\# Register agents and their executable environments  
agents:  
  agy:  
    executable: "/home/ubuntu/.local/bin/agy"  
    spawnable: true  
    limit: "hardware"  
    stall\_recovery:  
      max\_cycles: 6  
      escalate\_to: "fred"  
  kai:  
    executable: "/home/ubuntu/.local/bin/kai"  
    max\_concurrent: 1  
  fred:  
    executable: "/home/ubuntu/.local/bin/fred"  
    max\_concurrent: 1  
  autobot:  
    executable: "/home/ubuntu/.local/bin/autobot"  
    max\_concurrent: 1  
  jules:  
    executable: "/home/ubuntu/.local/bin/jules"  
    max\_concurrent: 50

\# Define capabilities mapping roles to agents, lanes, and branch formats  
capabilities:  
  designer:  
    agents:  
      agy:  
        branch\_prefix: "design/"  
        lanes: \["assets/", "designs/"\]  
        write\_allowed: true  
    default\_agent: "agy"

  researcher:  
    agents:  
      agy:  
        branch\_prefix: "research/"  
        lanes: \["research/"\]  
        write\_allowed: true  
      kai:  
        branch\_prefix: "research-content/"  
        lanes: \["research/", "content/"\]  
        write\_allowed: true  
    default\_agent: "agy"

  reviewer:  
    agents:  
      agy:  
        branch\_prefix: "review/"  
        lanes: \["\*"\]  
        write\_allowed: false  \# Read-only across all directories  
      jules:  
        branch\_prefix: "review-code/"  
        lanes: \["\*"\]  
        write\_allowed: false  
    default\_agent: "jules"

\# Define task pipelines  
pipelines:  
  design-flow:  
    steps:  
      \- step: 1  
        role: "designer"  
        next: 2  
      \- step: 2  
        role: "reviewer"  
        next: "integrate"  
\`\`\`

\---

\#\# 4\. Routing Decision Tree Flow Diagram

\`\`\`mermaid  
graph TD  
    A\["Linear Event / Polling Loop"\] \--\> B{"Has pipeline::\* Label?"}  
      
    B \-- Yes \--\> C\["Read Pipeline Config from YAML"\]  
    C \--\> D\["Identify Current Step & Required Role"\]  
      
    B \-- No \--\> E{"Has role::\* Label?"}  
    E \-- Yes \--\> F\["Identify Required Role directly"\]  
    E \-- No \--\> G\["Reject: Unroutable issue"\]  
      
    D \--\> H\["Query Capability Registry for Role"\]  
    F \--\> H  
      
    H \--\> I\["Get Registered Agents for Role"\]  
    I \--\> J{"Is Default Agent available & below max\_concurrent?"}  
      
    J \-- Yes \--\> K\["Assign Task to Default Agent"\]  
    J \-- No \--\> L{"Are there backup agents for this capability?"}  
      
    L \-- Yes \--\> M{"Are any backup agents available?"}  
    M \-- Yes \--\> N\["Assign Task to Backup Agent"\]  
    M \-- No \--\> O\["Queue Task in Database (Status: QUEUED)"\]  
    L \-- No \--\> O  
      
    K \--\> P\["Spin up Workspace (Git Worktree)"\]  
    N \--\> P  
      
    P \--\> Q\["Inject Capability Lanes and Prompt Rules"\]  
    Q \--\> R\["Execute Agent Process"\]  
\`\`\`

\---

\#\# 5\. Worked Example: AGY Receiving Three Tasks

Assume the following tasks are queued:  
1\. \*\*Task 1 (GRO-901):\*\* "Design new logo icon" (Requires \`designer\` capability)  
2\. \*\*Task 2 (GRO-902):\*\* "Review hawaiian diacritical marks in content" (Requires \`reviewer\` capability)  
3\. \*\*Task 3 (GRO-903):\*\* "Research competitor tour pricing" (Requires \`researcher\` capability)

\#\#\# Execution Trace:  
1\. \*\*Dispatcher Scans & Resolves:\*\*  
   \* Task 1 resolves to role \`designer\` $\\rightarrow$ Agent \`agy\` chosen.  
   \* Task 2 resolves to role \`reviewer\` $\\rightarrow$ Agent \`jules\` (default) is busy $\\rightarrow$ falls back to \`agy\`.  
   \* Task 3 resolves to role \`researcher\` $\\rightarrow$ Agent \`agy\` (default) chosen.  
2\. \*\*Worktree Allocation & Lane Injection:\*\*  
   \* \*\*Task 1\*\* runs in worktree \`/home/ubuntu/work/instances/gro-901\`. \`agy\` is injected with system prompts limiting modifications to \`assets/\` and \`designs/\`. Branch created: \`design/gro-901-logo\`.  
   \* \*\*Task 2\*\* runs in worktree \`/home/ubuntu/work/instances/gro-902\`. \`agy\` is injected with read-only rules across \`\*\`. Branch created: \`review/gro-902-marks\`.  
   \* \*\*Task 3\*\* runs in worktree \`/home/ubuntu/work/instances/gro-903\`. \`agy\` is injected with modifications limited to \`research/\`. Branch created: \`research/gro-903-pricing\`.  
3\. \*\*Pre-Push Validation:\*\*  
   \* If \`agy\` tries to write to \`src/main.py\` in Task 1, the pre-push hook checks \`HERMES\_TASK\_ID=gro-901\` and rejects the push because \`src/\` is not in the \`designer\` capability's allowed lanes.

\---

\#\# 6\. Integration Points with Fred's \`dispatcher.py\`

To implement this registry, \`prismatic/dispatcher.py\` must undergo the following modifications:

1\. \*\*Decoupling Executables:\*\* Remove hardcoded constants \`AGY\_PATH\`, \`JULES\_PATH\`, and \`CODEX\_PATH\`. Instead, load them dynamically in the \`Dispatcher\` class constructor from the parsed \`PRISMATIC\_ENGINE.yaml\` configuration.  
2\. \*\*Dynamic Routing Resolution:\*\* Refactor \`get\_next\_agent\` to evaluate role capabilities.  
   \`\`\`python  
   def resolve\_agent\_for\_task(self, role: str) \-\> str | None:  
       """Looks up available agents for a required role/capability."""  
       cap \= self.config.get("capabilities", {}).get(role)  
       if not cap:  
           return None  
         
       \# Check default agent  
       default\_agent \= cap.get("default\_agent")  
       if self.is\_agent\_available(default\_agent):  
           return default\_agent  
             
       \# Fallback to other registered agents  
       for agent in cap.get("agents", {}).keys():  
           if self.is\_agent\_available(agent):  
               return agent  
                 
       return None  
   \`\`\`  
3\. \*\*Generic Agent Execution Wrapper:\*\* Replace \`launch\_agy\` and \`launch\_jules\` with a generic command executor:  
   \`\`\`python  
   def launch\_agent(self, agent\_name: str, task\_id: str, payload: SignalPayload, lanes: list\[str\], read\_only: bool):  
       """Prepares Git worktree, configures system environments, and executes agent."""  
       worktree\_path \= self.setup\_worktree(task\_id)  
       agent\_exe \= self.config\["agents"\]\[agent\_name\]\["executable"\]  
         
       \# Generate dynamic contract profile  
       self.write\_contract\_profile(worktree\_path, lanes, read\_only)  
         
       \# Launch subprocess  
       cmd \= \[agent\_exe, "--workspace", worktree\_path, "--task", payload.task\_description\]  
       subprocess.Popen(cmd, env=dict(os.environ, HERMES\_TASK\_ID=task\_id, HERMES\_CAPABILITY\_LANES=json.dumps(lanes)))  
   \`\`\`  
4\. \*\*Lock Verification Refactor:\*\* Decouple lock authorization. The lock check should query the database for the active capability of the executing agent to authorize writes.  
