---
type: Reference
title: "Agy Instance Scheduler Design"
description: "Mirrored from Google Drive on 2026-06-25. Source: Drive file 1ccEFMfC6yiaFmnDcskzsSm9WnPgg2ebyki5xT63CPdg (modified 2026-06-08). Originally part of the Prismatic source plugin plans and AGY architecture reports."
resource: https://docs.google.com/document/d/1ccEFMfC6yiaFmnDcskzsSm9WnPgg2ebyki5xT63CPdg/edit?usp=drivesdk
tags: [drive-mirror, prismatic, gemini-evaluation, agy-report, source-plugin-plans]
timestamp: 2026-06-25T04:04:36.827Z
git_repo: mbgulden/growthwebdev-knowledge
linear_issue: TBD
last_verified: 2026-06-25
verified_by: fred
status: current
drive_file_id: "1ccEFMfC6yiaFmnDcskzsSm9WnPgg2ebyki5xT63CPdg"
drive_modified: "2026-06-08T10:10:38.781Z"
---

\# Prismatic Engine Spec — Parallel Instance Scheduler Design  
\*\*Linear Issue:\*\* \[GRO-820\](https://linear.app/growthwebdev/issue/GRO-820)    
\*\*Author:\*\* AGY (Antigravity Senior Systems Architect)    
\*\*Date:\*\* June 8, 2026    
\*\*Status:\*\* Complete — Ready for Review

\---

\#\# 1\. Executive Summary

When multiple Prismatic Engine loops (instances) run concurrently on the same git repository, they compete for a finite pool of agents (\`fred\`, \`kai\`, \`agy\`). Without an orchestrating scheduler, conflicts arise: agents are double-booked, tasks wait indefinitely, and circular dependency deadlocks occur. 

This document designs the \*\*Prismatic Instance Scheduler\*\*, a core component that coordinates parallel execution loops, manages agent allocation state, detects deadlocks, and enforces priority-based scheduling.

\---

\#\# 2\. Scheduling State & Instance Identity

\#\#\# 2.1 Instance Identity  
Each Prismatic Engine execution loop is initialized with a unique identifier (\`instance\_id\`), typically defined as an environment variable (\`PRISMATIC\_INSTANCE\_ID\`) or passed via the CLI (e.g. \`--instance-id pe-content-1\`).  
\* \*\*Linear Linking:\*\* Every Linear issue processed by an instance is labeled with \`instance::\<instance\_id\>\`. This allows the instance to track its own tasks.

\#\#\# 2.2 Central Status Registry (\`agent\_status.json\`)  
To track agent availability across separate processes, the scheduler uses a centralized status file located in the locks directory: \`/home/ubuntu/.antigravity/agent\_status.json\`.

\`\`\`json  
{  
  "agents": {  
    "agy": {  
      "status": "busy",  
      "spawnable": true,  
      "limit": "hardware",  
      "active\_runs": \[  
        {  
          "task\_id": "GRO-901",  
          "instance\_id": "pe-content-1",  
          "capability": "designer",  
          "pid": 45102,  
          "started\_at": "2026-06-08T07:50:00Z"  
        }  
      \]  
    },  
    "kai": {  
      "status": "idle",  
      "max\_concurrent": 1,  
      "active\_runs": \[\]  
    }  
  }  
}  
\`\`\`

\---

\#\# 3\. Preemption & Priority Queuing

Tasks are scheduled based on pipeline and issue priority (1 \= Highest/Critical, 4 \= Lowest/Backlog). When resources are constrained, the scheduler applies the following priority rules:

\#\#\# 3.1 Preemption Strategies  
1\. \*\*Cooperative Suspend (Default):\*\* The scheduler sends a pause signal (\`SIGUSR1\` or writes a \`.pause\` signal file) to the running agent process.  
   \* The agent serializes its in-memory task state to \`state\_checkpoint.json\`.  
   \* The agent commits its current file modifications to a temporary Git branch (\`suspend/\<task\_id\>\`).  
   \* The agent releases all locks in \`swarm\_locks.json\` and updates its status in \`agent\_status.json\` to \`PAUSED\`.  
   \* When resumed, the agent checks out the temporary branch, loads the checkpoint, and continues.  
2\. \*\*Let it Finish (Non-preemptive):\*\* For minor priority differences, the scheduler allows the active step to complete, but blocks the agent from starting the next pipeline step.  
3\. \*\*Hard Cancel & Rollback:\*\* Used only for critical priority 1 emergencies. The scheduler terminates the agent process (\`SIGKILL\`), rolls back the Git worktree, releases locks, and places the task back in the queue.

\---

\#\# 4\. Deadlock Detection & Resolution

A deadlock occurs when instances enter circular wait states. For example:  
\* \*\*Instance 1\*\* holds Agent \`agy\` and waits for Agent \`fred\`.  
\* \*\*Instance 2\*\* holds Agent \`fred\` and waits for Agent \`agy\`.

\`\`\`mermaid  
graph TD  
    I1\["Instance 1"\] \--\>|Holds| A\["Agent agy"\]  
    I1 \--\>|Waits for| F\["Agent fred"\]  
    I2\["Instance 2"\] \--\>|Holds| F  
    I2 \--\>|Waits for| A  
\`\`\`

\#\#\# 4.1 Deadlock Detection Algorithm  
The scheduler constructs a \*\*Wait-For Graph (WFG)\*\* by querying \`agent\_status.json\` and \`run\_records.db\`. It runs a cycle-detection check (Tarjan's or depth-first search) every 30 seconds.

\#\#\# 4.2 Resolution Strategy  
Once a cycle is detected:  
1\. \*\*Priority Check:\*\* Identify the task in the cycle with the lowest priority.  
2\. \*\*Preempt Lower Priority:\*\* Suspend or cancel the lowest-priority task to release its agent allocation.  
3\. \*\*Age-based Tie Breaker:\*\* If priorities are equal, preempt the youngest task (the one that started last).

\---

\#\# 5\. Sequence Diagram: 3 Instances Competing for 2 Agents

This diagram shows three instances (\`pe-1\`, \`pe-2\`, \`pe-3\`) competing for agents \`agy\` and \`fred\`.

\`\`\`mermaid  
sequenceDiagram  
    autonumber  
    participant PE1 as Instance 1 (Priority 2\)  
    participant PE2 as Instance 2 (Priority 3\)  
    participant PE3 as Instance 3 (Priority 1\)  
    participant Sched as Instance Scheduler  
    participant Reg as Central Status Registry  
      
    Note over PE1,PE2: Initial State: agy and fred are idle  
      
    PE1-\>\>Sched: Request agent 'agy' (Task A)  
    Sched-\>\>Reg: Read availability  
    Reg--\>\>Sched: agy is idle  
    Sched-\>\>Reg: Claim agy (Instance pe-1, Task A)  
    Sched--\>\>PE1: ✅ Agent allocated  
      
    PE2-\>\>Sched: Request agent 'fred' (Task B)  
    Sched-\>\>Reg: Read availability  
    Reg--\>\>Sched: fred is idle  
    Sched-\>\>Reg: Claim fred (Instance pe-2, Task B)  
    Sched--\>\>PE2: ✅ Agent allocated  
      
    Note over PE3: Urgent Priority 1 Task C Arrives  
    PE3-\>\>Sched: Request agent 'agy' (Task C, Priority 1\)  
    Sched-\>\>Reg: Read availability  
    Reg--\>\>Sched: agy is busy (pe-1, Task A, Priority 2\)  
      
    Note over Sched: Preemption Triggered: Priority 1 \> Priority 2  
    Sched-\>\>PE1: Send PAUSE signal to Task A  
    activate PE1  
    PE1-\>\>PE1: Commit to suspend/task-a & release locks  
    PE1--\>\>Sched: Acknowledged Pause  
    deactivate PE1  
      
    Sched-\>\>Reg: Release agy from Task A, allocate to Task C  
    Sched--\>\>PE3: ✅ Agent allocated  
      
    Note over PE3,PE2: Task C completes. agy becomes idle  
    PE3-\>\>Sched: Release agent 'agy'  
    Sched-\>\>Reg: Mark agy idle  
      
    Note over Sched: Resume Task A  
    Sched-\>\>Reg: Allocate agy to Task A  
    Sched-\>\>PE1: Send RESUME signal to Task A  
    activate PE1  
    PE1-\>\>PE1: Restore from suspend/task-a  
    deactivate PE1  
\`\`\`

\---

\#\# 6\. Proposed Dispatch Algorithm (Pseudocode)

\`\`\`python  
def schedule\_loop(self):  
    while True:  
        \# 1\. Update active task heartbeats and prune stale allocations  
        self.prune\_stale\_allocations()  
          
        \# 2\. Run cycle-detection on Wait-For Graph  
        cycles \= self.detect\_deadlocks()  
        if cycles:  
            self.resolve\_deadlock(cycles\[0\])  
              
        \# 3\. Retrieve all pending tasks ordered by priority, then creation time  
        pending\_tasks \= self.db.query("SELECT \* FROM tasks WHERE status \= 'QUEUED' ORDER BY priority ASC, created\_at ASC")  
          
        for task in pending\_tasks:  
            required\_role \= task.role  
            agent \= self.resolve\_agent\_for\_task(required\_role)  
              
            if agent:  
                \# If agent is idle, allocate immediately  
                self.allocate\_agent(agent, task)  
            else:  
                \# If agent is busy, check if we can preempt  
                current\_allocations \= self.get\_active\_allocations(required\_role)  
                lowest\_priority\_alloc \= min(current\_allocations, key=lambda x: x.priority)  
                  
                if task.priority \< lowest\_priority\_alloc.priority: \# 1 is higher priority than 3  
                    self.preempt\_task(lowest\_priority\_alloc.task\_id)  
                    self.allocate\_agent(lowest\_priority\_alloc.agent\_id, task)  
                      
        time.sleep(POLL\_INTERVAL)  
\`\`\`

\---

\#\# 7\. Integration Points with \`dispatcher.py\`

To integrate the Instance Scheduler into Fred's \`dispatcher.py\`, the following modifications must be made:

1\. \*\*State Store Centralization:\*\* Modify \`DEFAULT\_DB\_PATH\` to resolve to the central \`/home/ubuntu/.antigravity/\` workspace instead of \`./prismatic\_state\`. This ensures all instances share the same database file (\`event\_router.db\`), giving the scheduler a unified view of all pipelines.  
2\. \*\*Scheduler Thread Initialization:\*\* In \`dispatcher.py\`'s startup sequence, spin up a background thread that executes the \`schedule\_loop\` algorithm.  
3\. \*\*Process Signaling Implementation:\*\* Add process control methods to the dispatcher:  
   \`\`\`python  
   def pause\_task(self, task\_id: str):  
       """Sends a pause signal to the active agent process."""  
       run\_record \= self.db.get\_run\_record(task\_id)  
       if run\_record and run\_record.pid:  
           os.kill(run\_record.pid, signal.SIGUSR1) \# SIGUSR1 triggers suspend checkpoint  
           self.db.update\_status(task\_id, "PAUSED")  
             
   def resume\_task(self, task\_id: str):  
       """Sends a resume signal to the paused agent process."""  
       run\_record \= self.db.get\_run\_record(task\_id)  
       if run\_record and run\_record.pid:  
           os.kill(run\_record.pid, signal.SIGCONT)  
           self.db.update\_status(task\_id, "RUNNING")  
   \`\`\`  
4\. \*\*Git Hook Workspace Synchronization:\*\* Introduce workspace isolation in \`prismatic/workspace.py\` using git worktrees. When an instance starts, instead of executing inside the main clone folder, it executes:  
   \`\`\`bash  
   git worktree add ../instances/{task\_id} {branch\_name}  
   \`\`\`  
   This ensures that concurrent writes do not interfere with each other on the local disk.  
