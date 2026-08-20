---
name: python-development-environment-setup
category: devops
description: Best practices for setting up and managing Python development environments, especially in systems with PEP 668 enabled or when dealing with `ModuleNotFoundError` during testing.
---

## Overview

This skill outlines the recommended workflow for configuring Python development environments to avoid common pitfalls like `externally-managed-environment` errors (PEP 668) and `ModuleNotFoundError` when running tests or scripts.

## Core Principles

1.  **Always use Virtual Environments:** For any project with Python dependencies, create and activate a virtual environment. This isolates project dependencies from the system Python installation and prevents conflicts.
2.  **Install in Editable Mode for Local Development:** When working on a Python package locally, install it in editable mode (`pip install -e .`) within its virtual environment. This ensures that changes to the source code are immediately reflected without needing reinstallation.

## Workflow

### 1. Create a Virtual Environment

Navigate to your project's root directory and create a virtual environment (e.g., named `.venv`):

```bash
python3 -m venv .venv
```

### 2. Activate the Virtual Environment

Activate the virtual environment. The command depends on your shell:

```bash
# For Bash/Zsh
source .venv/bin/activate

# For Fish shell
source .venv/bin/activate.fish

# For PowerShell
.venv\\Scripts\\Activate.ps1
```

### 3. Install Project in Editable Mode

Once activated, install your project (and its dependencies) in editable mode:

```bash
pip install -e .
```

This addresses `externally-managed-environment` errors and ensures that `ModuleNotFoundError` for your project's packages is resolved within the development environment.

## Pitfalls

### PEP 668: Externally Managed Environment

If you encounter `error: externally-managed-environment` when trying to `pip install` directly, it means your Python installation is managed by the operating system, and direct `pip` installs are blocked to prevent system breakage. The solution is always to use a virtual environment as described above.

### `OSError: [Errno 8] Exec format error` when running shell scripts from Python

When executing shell scripts (e.g., for ad-hoc verification) from Python using `subprocess.run`, and you encounter `OSError: [Errno 8] Exec format error`, it usually means the script is not being interpreted correctly. Instead of running the script directly (e.g., `subprocess.run([script_path])`), explicitly invoke the shell interpreter:

```python
import subprocess
import os

script_path = "/path/to/your/script.sh"
os.chmod(script_path, 0o755) # Ensure executable
subprocess.run(["bash", script_path], capture_output=True, text=True, check=False)
```

This ensures that `bash` (or `sh`) is used to execute the script, resolving potential interpretation issues.

### `ModuleNotFoundError` during testing

If tests fail with `ModuleNotFoundError` for your project's modules, even after installing in editable mode, double-check that:

*   The virtual environment is activated.
*   The `pytest` command (or your test runner) is executed from within the virtual environment (e.g., `.venv/bin/pytest`).
*   Your `pyproject.toml` or `setup.py` correctly defines your package for editable installation.

## Ad-hoc Verification Pattern

When the system requests ad-hoc verification after code changes, and a canonical test/lint/build command isn't readily available or fails in the sandbox environment, directly invoking the test runner from the activated virtual environment via the `terminal` tool is a reliable approach:

```bash
cd /path/to/your/project && source .venv/bin/activate && .venv/bin/pytest path/to/specific/test_file.py -v --tb=short
```

This pattern ensures the test runs in the correct environment and provides clear output.
