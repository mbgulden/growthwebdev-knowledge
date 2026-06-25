---
type: Reference
title: "Agy Alchemy Mode Design"
description: "Mirrored from Google Drive on 2026-06-25. Source: Drive file 1HAEDUltWbt-eFs-PaGZIajX3iQNgbJtU5tmO9cCNMa0 (modified 2026-06-08). Originally part of the Prismatic source plugin plans and AGY architecture reports."
resource: https://docs.google.com/document/d/1HAEDUltWbt-eFs-PaGZIajX3iQNgbJtU5tmO9cCNMa0/edit?usp=drivesdk
tags: [drive-mirror, prismatic, gemini-evaluation, agy-report, source-plugin-plans]
timestamp: 2026-06-25T04:04:30.570Z
git_repo: mbgulden/growthwebdev-knowledge
linear_issue: TBD
last_verified: 2026-06-25
verified_by: fred
status: current
drive_file_id: "1HAEDUltWbt-eFs-PaGZIajX3iQNgbJtU5tmO9cCNMa0"
drive_modified: "2026-06-08T10:10:12.992Z"
---

\# Prismatic Engine Spec — Alchemy Mode Design  
\*\*Linear Issue:\*\* \[GRO-820\](https://linear.app/growthwebdev/issue/GRO-820)    
\*\*Author:\*\* AGY (Antigravity Senior Systems Architect)    
\*\*Date:\*\* June 8, 2026    
\*\*Status:\*\* Complete — Ready for Review

\---

\#\# 1\. Executive Summary

In standard agent execution loops, raw user prompts are fed directly to LLMs, producing unpredictable results ("Mystery Gift Out"). \*\*Alchemy Mode\*\* is an opinionated quality-assurance layer that wraps the core Prismatic Engine. It enforces structured intake, recipe-based agent chains, strict quality gates, and provenance logging to deliver gold-standard repeatable outputs ("Lead In $\\rightarrow$ Gold Out").

\---

\#\# 2\. Research Foundations

To design an industrial-grade quality layer for AI agents, we borrow principles from three fields:

\#\#\# 2.1 Creative Agency Briefing Formats  
In advertising and content production, human teams never write copy based on a raw sentence. They use a \*\*Creative Brief\*\*. A brief contains:  
\* \*\*Objectives & Key Messages:\*\* What must the audience understand?  
\* \*\*Target Audience:\*\* Demographic, interests, intent.  
\* \*\*Tone of Voice:\*\* Explicit boundaries (e.g., "Informative but conversational, never corporate").  
\* \*\*Mandatories & Brand Constraints:\*\* Inviolable rules (e.g., specific trademark references, legal disclaimers).

\#\#\# 2.2 CI/CD Quality Gates  
In software engineering, code is not deployed based on developer confidence. It passes through \*\*Build Gates\*\*:  
\* \*\*Static Analysis:\*\* Linting and syntactic correctness.  
\* \*\*Dynamic Analysis:\*\* Unit and integration test suites.  
\* \*\*Semantic Gates:\*\* Blocking merges if test coverage drops or if deprecations are introduced.

\#\#\# 2.3 Constitutional AI (Anthropic)  
Constitutional AI aligns model outputs by having a critic model evaluate drafts against a set of written principles (a "constitution") and iterate on the draft. In Alchemy Mode, quality gates translate this constitution into structured YAML check lists that a reviewer agent applies to verify compliance.

\---

\#\# 3\. Alchemy Mode vs. Standard Mode Comparison

| Dimension | Standard Mode | Alchemy Mode |  
|---|---|---|  
| \*\*Intake Process\*\* | Raw user prompt fed directly to agent. | Raw input converted to structured brief by briefing agent. |  
| \*\*Workflow Routing\*\* | Ad-hoc single agent or basic linear transitions. | Predefined, multi-stage recipes mapping roles and gates. |  
| \*\*Validation\*\* | Basic lint/test validation (if defined). | Multi-stage Quality Gates with explicit YAML checklists. |  
| \*\*Self-Healing\*\* | Limited to basic compiler loop retries. | Structured feedback loop returning failing items to creator. |  
| \*\*Decisions logged\*\* | Git commit message only. | Full provenance JSON tracking edits, rationales, and critiques. |  
| \*\*Outcomes\*\* | High variance, style drift, minor details missed. | Consistent style, compliance with constraints, verifiable quality. |

\---

\#\# 4\. Structured Intake Brief Schema

Before any recipe starts, a \*\*Briefing Agent\*\* parses the user's raw input into a structured brief. This brief is saved as a JSON/YAML file in the worktree (\`brief.json\`):

\`\`\`json  
{  
  "core\_ask": "Create a high-converting tour page for Mokulua Islands Kayak Tour",  
  "audience": "Adventurous tourists, families with teenagers, couples looking for scenic views",  
  "brand\_voice": "Adventurous, local, environmentally conscious, authentic Hawaiian respect",  
  "success\_criteria": \[  
    "Primary H1 contains the keyword 'Mokulua Islands Kayak Tour'",  
    "Booking links use shortname 'oahukayak'",  
    "Includes difficulty level (Strenuous)",  
    "Correctly uses Hawaiian diacritical marks (e.g., Mōkulua, Oʻahu)"  
  \],  
  "constraints": {  
    "word\_count": "600-800 words",  
    "forbidden\_phrases": \["hidden gem", "must-see", "world-class", "corporate-speak"\],  
    "required\_sections": \["Overview", "What's Included", "What to Bring", "FAQ"\]  
  },  
  "preserved\_heart": "The sense of raw, untouched natural beauty and the thrill of kayaking in open ocean swells."  
}  
\`\`\`

\---

\#\# 5\. Recipe System Schema (\`recipe.yaml\`)

Recipes define the agent execution pipeline, specifying roles, inputs, outputs, and quality gates.

\`\`\`yaml  
id: "tour-page-recipe"  
name: "Repeatable Tour Page Production"  
version: 1

pipeline:  
  \- step: 1  
    name: "competitor-research"  
    role: "researcher"  
    description: "Scan competitor pricing and local rules for Mōkulua kayaking"  
    outputs: \["research/competitor\_notes.md"\]

  \- step: 2  
    name: "content-drafting"  
    role: "writer"  
    inputs: \["research/competitor\_notes.md", "brief.json"\]  
    outputs: \["content/tours/mokulua.md"\]  
    quality\_gates: \["draft-gate"\]

  \- step: 3  
    name: "seo-brand-review"  
    role: "reviewer"  
    inputs: \["content/tours/mokulua.md", "brief.json"\]  
    quality\_gates: \["publishing-gate"\]  
    next: "integrate"  
\`\`\`

\---

\#\# 6\. Quality Gate Schema (\`quality\_gates.yaml\`)

Quality gates evaluate output files against structured assertions. Assertions can be verified by code scripts (regex, compiler) or LLM critic reviews.

\`\`\`yaml  
gates:  
  draft-gate:  
    description: "Basic structure and syntax checks"  
    criteria:  
      \- check: "File exists and is not empty"  
        type: "script"  
        run: "test \-s content/tours/mokulua.md"  
        severity: "blocker"  
      \- check: "No corporate placeholder text"  
        type: "regex"  
        pattern: "\\\\\[insert here\\\\\]|TODO|placeholder"  
        severity: "blocker"

  publishing-gate:  
    description: "SEO, Brand Voice, and Accuracy checks"  
    criteria:  
      \- check: "Primary H1 contains 'Mokulua Islands Kayak Tour'"  
        type: "regex"  
        pattern: "^\# .\*Mokulua Islands Kayak Tour.\*"  
        severity: "blocker"  
      \- check: "Correct usage of Hawaiian diacritical marks (Mōkulua, Oʻahu, Kāneʻohe)"  
        type: "agent\_review"  
        rubric: "Ensure correct kahakō (macrons) and ʻokina (glottal stops) are used. Flag 'Mokulua' without macron or 'Oahu' without okina."  
        severity: "blocker"  
      \- check: "No forbidden phrases (e.g., 'hidden gem', 'must-see')"  
        type: "regex"  
        pattern: "(?i)hidden gem|must-see|world-class"  
        severity: "warning"  
      \- check: "Booking links point to shortname 'oahukayak'"  
        type: "regex"  
        pattern: "https://fareharbor\\\\.com/embeds/book/oahukayak/"  
        severity: "blocker"  
\`\`\`

\---

\#\# 7\. Provenance & Decision Tracking

To ensure accountability, every file modification made under Alchemy Mode must log its rationale. The agent writes a JSON entry to \`provenance.json\` in the worktree:

\`\`\`json  
{  
  "task\_id": "GRO-904",  
  "step": 2,  
  "agent\_id": "kai",  
  "timestamp": "2026-06-08T07:55:00Z",  
  "modified\_files": \["content/tours/mokulua.md"\],  
  "rationale": {  
    "h1\_structure": "I formatted the title as '\# Mokulua Islands Kayak Tour' to satisfy the primary keyword and H1 constraint in the brief.",  
    "diacritical\_marks": "I used 'Mōkulua' and 'Oʻahu' to comply with the brand voice guidelines. I noticed competitor pages frequently misspell these and flagged it in notes.",  
    "link\_format": "Embedded the booking link: https://fareharbor.com/embeds/book/oahukayak/book/ to ensure shortname accuracy."  
  }  
}  
\`\`\`

\---

\#\# 8\. Failure Modes & Self-Healing Loop

If any blocker constraint in a Quality Gate fails:  
1\. \*\*Report Generation:\*\* The verifier (either a script or a reviewer agent) generates a structured failure report (\`gate\_feedback.json\`):  
   \`\`\`json  
   {  
     "gate": "publishing-gate",  
     "status": "failed",  
     "failures": \[  
       {  
         "check": "Correct usage of Hawaiian diacritical marks",  
         "severity": "blocker",  
         "feedback": "Line 24: Used 'Mokulua' instead of 'Mōkulua'."  
       }  
     \]  
   }  
   \`\`\`  
2\. \*\*Re-routing:\*\* The dispatcher intercepts the transition, rolls back the Git workspace to the pre-push state, and re-routes the task back to the previous agent (\`writer\`), injecting \`gate\_feedback.json\` into its context.  
3\. \*\*Retry Quota:\*\* The agent is allowed up to 3 self-healing attempts. If it fails on the 3rd attempt, the dispatcher halts execution, locks the workspace, and escalates to the Staging Governor (Fred) or flags the Linear issue with \`state::stalled\`.

\---

\#\# 9\. Full Worked Example: Mokulua Tour Page

\#\#\# Step 1: Intake Briefing  
The user submits: \*"Write a tour page for our Mokulua Kayaking Tour. It's a tough paddle, so people need to be in shape. Book links should go to our FareHarbor page oahukayak."\*  
The Briefing Agent converts this into \`brief.json\` (as shown in Section 4).

\#\#\# Step 2: Drafting  
Agent \`kai\` (in writer capability) receives \`brief.json\`. It drafts \`content/tours/mokulua.md\`.  
\`\`\`markdown  
\# Mokulua Islands Kayak Tour

Join us for a strenuous kayak adventure to the beautiful twin islands of Mōkulua, off the coast of Oʻahu. 

Difficulty: Strenuous.  
\[Book Now\](https://fareharbor.com/embeds/book/oahukayak/book/)  
\`\`\`  
\`kai\` logs the changes in \`provenance.json\` (as shown in Section 7).

\#\#\# Step 3: Quality Gate Evaluation  
The dispatcher executes \`publishing-gate\` on \`content/tours/mokulua.md\`:  
\* Check 1 (H1 keyword): \*\*PASS\*\* (\`\# Mokulua Islands Kayak Tour\` matches)  
\* Check 2 (Diacritical marks): \*\*PASS\*\* (\`Mōkulua\`, \`Oʻahu\` match)  
\* Check 3 (Forbidden phrases): \*\*PASS\*\* (no "hidden gem" or "must-see" present)  
\* Check 4 (Booking links): \*\*PASS\*\* (\`oahukayak\` embedded link matches)

\#\#\# Step 4: Integration  
All checks pass. The dispatcher transitions the branch to \`ready-for-merge\`. The Staging Governor (\`fred\`) reviews the logs, verifies compile hooks, and merges to \`deploy-fresh\`.

\---

\#\# 10\. Alchemy Pipeline Concurrency & Agent Constraints

When orchestrating multi-stage recipes (e.g., intake briefing \-\> research \-\> drafting \-\> quality gates \-\> integration), the Dispatcher and Scheduler enforce the revised agent constraint model to prevent lock contention and resource starvation:

1\. \*\*Orchestration & Integration (Fred):\*\* A single-instance agent (\`max\_instances: 1\`). Fred coordinates the execution of the recipe dispatcher, manages gate transitions, and performs the final merge to \`deploy-fresh\`. One orchestration pipeline runs at a time.  
2\. \*\*Drafting (Kai):\*\* A single-instance agent (\`max\_instances: 1\`). When multiple recipes are in the drafting step concurrently, the scheduler queues them in a FIFO queue. Only one writer session executes at any given time.  
3\. \*\*Research & Design (AGY):\*\* A multi-instance spawnable platform. AGY instances are spawned dynamically for research and design steps. Because AGY is spawnable, the scheduler allocates a new process instance for each parallel recipe, bounded only by bare-metal host capacity (RAM/CPU).  
4\. \*\*Code & Content Review (Jules):\*\* A multi-session agent supporting up to 50 concurrent sessions. Parallel review steps are executed concurrently using independent Jules sessions, ensuring that the verification of quality gates never bottlenecks the pipeline.  
5\. \*\*Autobot Tasks:\*\* A single-instance agent (\`max\_instances: 1\`) reserved for automated cleanup/infrastructure tasks.

