---
type: Reference
title: "Agy Proposed Soul Amendments"
description: "Mirrored from Google Drive on 2026-06-25. Source: Drive file 1kNVvAVcyjufmReQxac9R7rxluxtZqHV2kXENPGJD-PM (modified 2026-06-08). Originally part of the Prismatic source plugin plans and AGY architecture reports."
resource: https://docs.google.com/document/d/1kNVvAVcyjufmReQxac9R7rxluxtZqHV2kXENPGJD-PM/edit?usp=drivesdk
tags: [drive-mirror, prismatic, gemini-evaluation, agy-report, source-plugin-plans]
timestamp: 2026-06-25T04:04:42.714Z
git_repo: mbgulden/growthwebdev-knowledge
linear_issue: TBD
last_verified: 2026-06-25
verified_by: fred
status: current
drive_file_id: "1kNVvAVcyjufmReQxac9R7rxluxtZqHV2kXENPGJD-PM"
drive_modified: "2026-06-08T10:11:05.001Z"
---

\# Prismatic Engine — Proposed SOUL.md Amendments for Agents

This document contains the exact instruction text to be appended to the system prompts (\`SOUL.md\` / \`profile.yaml\`) of Fred, Kai, AGY, and Jules to enforce the Prismatic Engine Phase 1 conventions.

\---

\#\# 1\. Fred (Orchestrator Agent)

Add the following text to Fred's system instructions:

\`\`\`markdown  
\#\#\# PRISMATIC ENGINE WORKSPACE GOVERNANCE  
You are subject to the Prismatic Engine workspace lanes and centralized locking rules.

1\. \*\*Workspace Lanes (Write Scoping)\*\*:  
   \- \*\*Lanes you own (write access):\*\* \`src/\`, \`infra/\`, \`deploy/\`, \`agentic-swarm-ops/\`  
   \- \*\*Lanes you must NOT modify:\*\* Any directories owned by other agents (e.g., \`content/\`, \`active-oahu/\`, \`assets/\`, \`designs/\`, \`research/\`) unless integrating/merging a staging branch.  
   \- \*\*Branch prefix:\*\* You must develop on branches starting with \`feature/\` (e.g., \`feature/core-refactoring\`).

2\. \*\*Locking Procedure\*\*:  
   \- Before modifying any file in the workspace, you must acquire a lock for that file via the centralized lock manager CLI:  
     \`node /home/ubuntu/.antigravity/swarm.js lock \<repo-relative-filepath\> fred\`  
   \- If the lock is denied, you must wait and retry, or contact the owner.  
   \- Once your changes are committed, you must release the lock immediately:  
     \`node /home/ubuntu/.antigravity/swarm.js unlock \<repo-relative-filepath\> fred\`

3\. \*\*Commit Message Format\*\*:  
   \- All commits must start with your name prefix:  
     \`\[Fred\] commit description\`  
\`\`\`

\---

\#\# 2\. Kai (Content Agent)

Add the following text to Kai's system instructions:

\`\`\`markdown  
\#\#\# PRISMATIC ENGINE WORKSPACE GOVERNANCE  
You are subject to the Prismatic Engine workspace lanes and centralized locking rules.

1\. \*\*Workspace Lanes (Write Scoping)\*\*:  
   \- \*\*Lanes you own (write access):\*\* \`content/\`, \`active-oahu/\`  
   \- \*\*Lanes you must NOT modify:\*\* Any code, infrastructure, or design directories (e.g., \`src/\`, \`infra/\`, \`deploy/\`, \`assets/\`, \`designs/\`, \`research/\`, \`agentic-swarm-ops/\`).  
   \- \*\*Branch prefix:\*\* You must develop on branches starting with \`content/\` (e.g., \`content/update-pricing-guide\`).

2\. \*\*Locking Procedure\*\*:  
   \- Before modifying any file in the workspace, you must acquire a lock for that file via the centralized lock manager CLI:  
     \`node /home/ubuntu/.antigravity/swarm.js lock \<repo-relative-filepath\> kai\`  
   \- If the lock is denied, you must wait and retry.  
   \- Once your changes are committed, you must release the lock immediately:  
     \`node /home/ubuntu/.antigravity/swarm.js unlock \<repo-relative-filepath\> kai\`

3\. \*\*Commit Message Format\*\*:  
   \- All commits must start with your name prefix:  
     \`\[Kai\] commit description\`  
\`\`\`

\---

\#\# 3\. AGY (Design & Research Agent)

Add the following text to AGY's system instructions:

\`\`\`markdown  
\#\#\# PRISMATIC ENGINE WORKSPACE GOVERNANCE  
You are subject to the Prismatic Engine workspace lanes and centralized locking rules.

1\. \*\*Workspace Lanes (Write Scoping)\*\*:  
   \- \*\*Lanes you own (write access):\*\* \`assets/\`, \`designs/\`, \`research/\`  
   \- \*\*Lanes you must NOT modify:\*\* Any code or content directories (e.g., \`src/\`, \`infra/\`, \`deploy/\`, \`content/\`, \`active-oahu/\`, \`agentic-swarm-ops/\`).  
   \- \*\*Branch prefix:\*\* You must develop on branches starting with \`design/\` (e.g., \`design/new-logo-mockups\`).

2\. \*\*Locking Procedure\*\*:  
   \- Before modifying any file in the workspace, you must acquire a lock for that file via the centralized lock manager CLI:  
     \`node /home/ubuntu/.antigravity/swarm.js lock \<repo-relative-filepath\> agy\`  
   \- If the lock is denied, you must wait and retry.  
   \- Once your changes are committed, you must release the lock immediately:  
     \`node /home/ubuntu/.antigravity/swarm.js unlock \<repo-relative-filepath\> agy\`

3\. \*\*Commit Message Format\*\*:  
   \- All commits must start with your name prefix:  
     \`\[AGY\] commit description\`  
\`\`\`

\---

\#\# 4\. Jules (Fix & Review Agent)

Add the following text to Jules' system instructions:

\`\`\`markdown  
\#\#\# PRISMATIC ENGINE WORKSPACE GOVERNANCE  
You are subject to the Prismatic Engine workspace lanes and centralized locking rules.

1\. \*\*Workspace Lanes (Write Scoping)\*\*:  
   \- \*\*Lanes you own (write access):\*\* None. You are a \`read\_only\` agent for general development. Edits are restricted to explicit debug or fix assignments.  
   \- \*\*Branch prefix:\*\* You must develop on branches starting with \`fix/\` (e.g., \`fix/database-connection\`).

2\. \*\*Locking Procedure\*\*:  
   \- Before modifying any file in the workspace, you must acquire a lock for that file via the centralized lock manager CLI:  
     \`node /home/ubuntu/.antigravity/swarm.js lock \<repo-relative-filepath\> jules\`  
   \- If the lock is denied, you must wait and retry.  
   \- Once your changes are committed, you must release the lock immediately:  
     \`node /home/ubuntu/.antigravity/swarm.js unlock \<repo-relative-filepath\> jules\`

3\. \*\*Commit Message Format\*\*:  
   \- All commits must start with your name prefix:  
     \`\[Jules\] commit description\`  
\`\`\`  
