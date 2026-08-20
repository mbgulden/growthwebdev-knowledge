---
name: agy-systematic-debugging
description: Systematic reproduction, isolation, patch application, and verification of software defects.
version: 1.0.0
---

# AGY Systematic Debugging

Analyze errors methodically, locate failure points, design minimal repros, patch code, and verify.

## Trigger Conditions

Use this skill when code is throwing errors, crashing, or producing unexpected behavior.

## Numbered Steps with Exact Commands

1. **Isolate and capture stack trace**:
   Check logs or execute command with stderr redirected:
   ```bash
   python3 ./src/main.py 2> /tmp/error.log
   cat /tmp/error.log
   ```

2. **Create minimal reproduction script**:
   Write a standalone python script in the scratch directory:
   ```python
   # /home/ubuntu/.gemini/antigravity-cli/scratch/repro.py
   # imports and minimal calls triggering the bug
   ```

3. **Apply target logging (Print debugging)**:
   Add detailed trace statements before the failing line to print object states and types.

4. **Code Patching**:
   Perform precise contiguous replacement of the buggy section using edit tools.

5. **Validate recovery**:
   Run the reproduction script and confirm the error no longer occurs.

## Pitfalls

- **Fixing symptoms vs. root causes**: Do not catch exceptions globally without understanding why they happen.
- **Uncommitted edits**: Keep track of what you changed. Use `git diff` to review code modifications before finishing.

## Verification Steps

- Execute reproduction script and ensure zero errors:
  ```bash
  python3 /home/ubuntu/.gemini/antigravity-cli/scratch/repro.py
  ```
