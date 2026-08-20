---
name: agy-linear-task-execution-loop
description: Pull, process, execute, and bookend tasks from the Linear backlog autonomously.
version: 1.0.0
---

# AGY Linear Task Execution Loop

Follow a structured lifecycle to request, execute, and verify Linear board tasks autonomously.

## Trigger Conditions

Use this skill when running in autonomous worker mode to clear tickets from the developer backlog.

## Numbered Steps with Exact Commands

1. **Check backlog for assigned tickets**:
   Run GraphQL query to fetch the top ticket assigned to `agent:antigravity-cli` (primary label ID: `2fdf7706-b9ed-4d6e-87a5-04ffe882a0b4`).

2. **Submit Implementation Plan**:
   Post a comment detailing the steps and files to be touched. Move ticket status to "In Progress".

3. **Execute the work**:
   Complete the code edits, audits, or visual designs.

4. **Verify correctness**:
   Run unit tests and UI screenshots.

5. **Post Walkthrough (Book End)**:
   Submit a comment with absolute file links to all deliverables:
   ```
   ### Completion Summary
   - Refactored user router: [router.js](file:///home/ubuntu/work/project/router.js)
   - Verified tests pass.
   ```

6. **Relabel issue**:
   Change assignment label to `agent:fred` to return control to the orchestrator.

## Pitfalls

- **Skipping plans**: Jumping straight to building without posting a plan violates swarm discipline. Always post the plan comment first.
- **Stale ticket states**: Ensure state transitions (Todo -> In Progress -> Done) are executed.

## Verification Steps

- Verify ticket state is updated on the board and labels are swapped.
