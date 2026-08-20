---
name: agy-context-optimization
description: Optimize context window usage, avoid token bloat, prevent the "research-vs-build" trap, and manage prompt timeouts.
version: 1.0.0
---

# AGY Context Optimization & Task Chunking

Prevent AGY token bloat and prompts timeouts by isolating context folders and applying RESEARCH-ONLY constraints.

## Trigger Conditions

Use this skill when processing large codebases, doing research, or when prompts exceed 1200 characters and cause timeouts.

## Numbered Steps with Exact Commands

1. **Create isolated context folder**:
   Do not add the entire workspace root. Instead, copy target files to an isolated directory:
   ```bash
   mkdir -p /tmp/agy-ctx-local
   cp /home/ubuntu/work/project/docs/*.md /tmp/agy-ctx-local/
   ```

2. **Prepend the RESEARCH-ONLY constraint**:
   If the goal is research/analysis, explicitly instruct the model:
   ```
   RESEARCH-ONLY. Do NOT write code. Do NOT create scripts. Do NOT modify any files except the deliverable report(s).
   ```

3. **Launch print run pointing only to context folder**:
   ```bash
   /home/ubuntu/.local/bin/agy --print "RESEARCH-ONLY. Read context from /tmp/agy-ctx-local/ and output analysis to /tmp/report.md"        --dangerously-skip-permissions        --print-timeout 10m        --add-dir /tmp/agy-ctx-local        2>/dev/null
   ```

4. **Verify output deliverable size**:
   ```bash
   ls -la /tmp/report.md
   ```

## Pitfalls

- **Research-vs-Build Trap**: AGY automatically starts building and editing files if given repository access. Use RESEARCH-ONLY and isolate files to `/tmp` to enforce analysis.
- **Large prompt timeout**: Prompts longer than 2200 characters cause long thinking loops and timeouts. Keep prompt instructions short and load files via `--add-dir` or path references instead of pasting file contents.

## Verification Steps

- Check that the repo root is untouched:
  ```bash
  git status
  ```
- Ensure `/tmp/report.md` exists and contains the requested analysis.
