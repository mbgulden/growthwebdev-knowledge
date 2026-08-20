---
name: agy-codebase-inspection
description: Perform rapid searches and analysis of codebase layout, symbol tracing, and index mapping.
version: 1.0.0
---

# AGY Codebase Inspection

Inspect files, search for strings and code patterns, locate definitions, and map project directories.

## Trigger Conditions

Use this skill when arriving in a new workspace or debugging an issue where the file structure is unknown.

## Numbered Steps with Exact Commands

1. **Map the project directories**:
   List top level structure up to depth 3:
   ```bash
   find . -maxdepth 3 -not -path '*/.*' -not -path '*/node_modules*'
   ```

2. **Search for exact keywords using ripgrep**:
   Search case-insensitively for a function name:
   ```bash
   rg -i "def handle_oauth" --glob "*.py"
   ```

3. **Locate imports and definitions**:
   Find where the routing system is referenced:
   ```bash
   rg -n "import prismatic"
   ```

4. **Read specific file sections**:
   Verify code contents:
   ```bash
   head -n 50 ./prismatic/dispatcher.py
   ```

## Pitfalls

- **Ripgrep lockups on large binary folders**: Ensure node_modules, build directories, and dotfiles are skipped.
- **Synology NAS Deadlock**: Avoid letting search tools (like `find`) traverse Mount paths like `/home/ubuntu/mounts/synology-*`.

## Verification Steps

- Ensure target search runs quickly and returns actual file references.
  ```bash
  rg --version
  ```
