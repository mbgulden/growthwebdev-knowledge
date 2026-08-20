---
name: agy-subagent-communication
description: Define, invoke, and communicate with specialized subagents asynchronously to parallelize tasks.
version: 1.0.0
---

# AGY Subagent Communication

Spawn and manage subagents to scale operations and divide research/build tasks.

## Trigger Conditions

Use when a task is large enough to be split into parallel subtasks (e.g., auditing multiple directories or testing different features).

## Numbered Steps with Exact Commands

1. **Define a specialized subagent**:
   Create a subagent definition:
   ```json
   {
     "name": "css_validator",
     "description": "Validates CSS styles against the design system",
     "system_prompt": "You are a CSS validator. Look at file contents and highlight violations.",
     "toolSummary": "Define CSS validator subagent",
     "toolAction": "Defining subagent"
   }
   ```

2. **Invoke the subagent**:
   Launch the subagent in background:
   ```json
   {
     "Subagents": [
       {
         "TypeName": "css_validator",
         "Role": "Style Auditor",
         "Prompt": "Read /tmp/styles.css and list all non-standard colors."
       }
     ],
     "toolSummary": "Invoke CSS style validator",
     "toolAction": "Invoking subagent"
   }
   ```

3. **Communicate with subagent**:
   Send additional directions:
   ```json
   {
     "Recipient": "subagent_conversation_id_example",
     "Message": "Include checks for border-radius values too.",
     "toolSummary": "Send border check prompt",
     "toolAction": "Sending message"
   }
   ```

4. **Poll or Wait for notifications**:
   Wait for completion notifications containing the final subagent output.

## Pitfalls

- **Redundant Invocation Loops**: Spawning new subagents for minor task changes wastes resources. Reuse active subagents by sending messages instead.
- **Workspace Conflicts**: Parallel subagents writing to the same directory will overwrite each other. Use `branch` or `share` mode to isolate files.

## Verification Steps

- List active subagents and verify status:
  ```json
  {
    "Action": "list",
    "toolSummary": "List subagents",
    "toolAction": "Listing subagents"
  }
  ```
