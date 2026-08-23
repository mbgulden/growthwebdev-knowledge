---
name: dev-troubleshooting-patterns
description: Common development and troubleshooting patterns for local environment, Python, and Git.
category: devops
---

# Development & Troubleshooting Patterns

This skill captures common patterns and pitfalls encountered during development, focusing on local environment setup, Python, and Git.

## General Debugging

### Patch Tool Precision
When using the `patch` tool, the `old_string` parameter requires an **exact, multi-line match**, including all whitespace and indentation. Partial or fuzzy matches often fail. If a targeted region is hard to anchor, consider using `execute_code` to read, modify, and rewrite the entire file (being mindful of character limits for `read_file`).

### Python Module Path (`__file__`)
When obtaining the current module's file path from within that module, use Python's built-in `__file__` variable directly. Avoid attempting to import and reference `module.submodule.__file__` from within `submodule.py`, as this can lead to circular import issues or `NameError` (e.g., `prismatic.journal.__file__` inside `prismatic/journal.py` is incorrect; `__file__` is correct).

### Installing Local or Git-based Python Dependencies
If `pip install <package_name>` fails because the package is not found (e.g., `swarmlock`), it likely means the package is a local or Git-based dependency. To install such packages:
1.  **Locate the `pyproject.toml`**: Examine the `pyproject.toml` file of the project that requires the dependency. Look under `[project.optional-dependencies]` or `[project.dependencies]` for lines specifying a Git URL (e.g., `package @ git+https://github.com/user/repo.git@main`).
2.  **Install using the Git URL**: Use `pip install` with the exact Git URL and branch/tag:
    ```bash
    pip install 'package_name @ git+https://github.com/user/repo.git@main'
    ```
    Ensure you are installing into the correct Python environment (e.g., a `pipx` venv: `/home/ubuntu/.local/share/pipx/venvs/hermes-agent/bin/python -m pip install ...`).
