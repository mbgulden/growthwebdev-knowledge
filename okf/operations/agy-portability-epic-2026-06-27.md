# Portability & Abstraction Epic: Decoupling Prismatic Engine from VM 800

This document outlines the architectural blueprint, structural guidelines, and ready-to-use task templates for the **Portability & Abstraction Epic**. The objective is to decouple the Prismatic Engine codebase from environment-specific assumptions (such as `/home/ubuntu/` home directories, local network IPs, and Synology NAS paths) so it can be deployed on other servers, cloud providers, or a local developer machine.

---

## 1. Context & Architectural Problem

Recent infrastructure sweeps revealed that VM-specific assumptions have leaked into the core repositories. If a developer attempts to install or run the Prismatic Engine on a new system (e.g., AWS, GCP, or a local macOS/Windows machine), the execution will fail due to hardcoded path defaults.

### Identified Environmental Leakage Points
Our codebase scan located several key areas where local environment defaults are hardcoded:
1.  **Hardcoded `/home/ubuntu` Defaults:**
    *   `prismatic/distributed_watchdog.py:56`: `PRISMATIC_HOME = Path(os.environ.get("PRISMATIC_HOME", "/home/ubuntu"))`
    *   `prismatic/lock.py:54`: `_PRISMATIC_HOME = Path(os.environ.get("PRISMATIC_HOME", "/home/ubuntu"))`
    *   `prismatic/agents/hermes.py:140`: `prismatic_home = os.environ.get("PRISMATIC_HOME", "/home/ubuntu")`
2.  **Hardcoded System Directories:**
    *   `SOUL.md:115`: Hardcoded reference to the swarm lock manager at `/home/ubuntu/.antigravity/swarm_locks.json`.
3.  **Local Networking & Mount Assumptions:**
    *   Various scripts reference the specific network path `/home/ubuntu/mounts/synology-agentic-context/` instead of resolving it dynamically via a configured workspace root.

---

## 2. Portability Principles

To ensure future contributions remain environment-agnostic, the following rules are added to the [SKILL.md](file:///C:/Users/Michael%20Gulden/Github/Hermes/scratch/SKILL.md) and engine guidelines:

1.  **Resolve User Home Dynamically:** 
    *   *Incorrect:* `Path("/home/ubuntu/.config")`
    *   *Correct:* `Path.home() / ".config"` (resolves correctly to `/home/ubuntu`, `/home/ec2-user`, `/Users/username`, or `C:\Users\username`).
2.  **Environment Variable Overrides:** 
    *   Always use a fallback-to-portable default structure:
        ```python
        # Standard cross-platform resolution
        DEFAULT_WORK_DIR = Path.home() / "work"
        WORK_DIR = Path(os.environ.get("PRISMATIC_WORK_DIR", DEFAULT_WORK_DIR))
        ```
3.  **Configuration Isolation:**
    *   All secrets, API tokens, Tailscale IPs, and remote host names must live in a `.env` template file, never hardcoded in the codebase.

---

## 3. Epic Task Templates

The following templates are ready to be copied directly into Linear to create the Epic issues.

```carousel
### Task 1: Abstract User Home and Base Directories
<!-- slide -->
### Task 2: Decouple Swarm Lock Manager Path
<!-- slide -->
### Task 3: Extract Local IP and Port Bindings
<!-- slide -->
### Task 4: Package Engine via Docker Compose
<!-- slide -->
### Task 5: Execute Portability Verification Wave
```

---

### [Task 1] Abstract User Home and Base Directories

*   **Title:** `[PORTABILITY-1] Refactor hardcoded /home/ubuntu paths in Prismatic Engine core`
*   **Description:**
    ```markdown
    The core Prismatic Engine code has hardcoded defaults pointing to `/home/ubuntu` in several locations. This prevents the engine from running on systems with different usernames or operating systems.
    
    Refactor the following files to use dynamic user-home path resolution via `pathlib.Path.home()` or the current working directory:
    
    1.  [prismatic/distributed_watchdog.py](file:///home/ubuntu/work/prismatic-engine/prismatic/distributed_watchdog.py#L56)
        - Change `PRISMATIC_HOME = Path(os.environ.get("PRISMATIC_HOME", "/home/ubuntu"))`
        - To: `PRISMATIC_HOME = Path(os.environ.get("PRISMATIC_HOME", Path.home()))`
        
    2.  [prismatic/lock.py](file:///home/ubuntu/work/prismatic-engine/prismatic/lock.py#L54)
        - Change `_PRISMATIC_HOME = Path(os.environ.get("PRISMATIC_HOME", "/home/ubuntu"))`
        - To: `_PRISMATIC_HOME = Path(os.environ.get("PRISMATIC_HOME", Path.home()))`
        
    3.  [prismatic/agents/hermes.py](file:///home/ubuntu/work/prismatic-engine/prismatic/agents/hermes.py#L140)
        - Change `prismatic_home = os.environ.get("PRISMATIC_HOME", "/home/ubuntu")`
        - To: `prismatic_home = os.environ.get("PRISMATIC_HOME", str(Path.home()))`
        
    **Verification Criteria:**
    - Run the unit tests locally on a different path to ensure `/home/ubuntu` is no longer required.
    - Confirm `pytest` passes with no import errors on `Path.home()`.
    ```

---

### [Task 2] Decouple Swarm Lock Manager Path

*   **Title:** `[PORTABILITY-2] Decouple swarm lock file path from home directory`
*   **Description:**
    ```markdown
    The Swarm Lock Manager path is currently hardcoded in documentation and scripts to `/home/ubuntu/.antigravity/swarm_locks.json`.
    
    Refactor the lock manager to:
    1. Resolve the default location relative to `Path.home() / ".antigravity/swarm_locks.json"`.
    2. Allow overriding the lock file path via the environment variable `ANTIGRAVITY_LOCK_FILE`.
    3. Update the lock protocol instructions in [SOUL.md](file:///home/ubuntu/work/prismatic-engine/SOUL.md#L115) to explain the portable configuration options.
    
    **Verification Criteria:**
    - Export `ANTIGRAVITY_LOCK_FILE=/tmp/custom_locks.json` and verify the lock manager writes to this path.
    - Verify that the default fallback resolves correctly under a non-standard user profile.
    ```

---

### [Task 3] Extract Local IP and Port Bindings

*   **Title:** `[PORTABILITY-3] Extract local hostnames, IPs, and port bindings to environment configuration`
*   **Description:**
    ```markdown
    The Prismatic Web Plugin (PWP) and core service scripts reference specific local IP addresses (like `192.168.1.59`) and hypervisor coordinates (like `100.90.63.4`).
    
    1. Audit the `prismatic-engine` and `prismatic-web-plugin` repos for hardcoded IP strings (`192.168.*` or `100.90.*`).
    2. Extract these network configurations into a `.env.template` file at the repository root.
    3. Use `python-dotenv` or environment fallback logic to load coordinates (e.g., `PRISMATIC_IDE_IP`, `PRISMATIC_DASHBOARD_PORT`) at runtime.
    4. Provide fallback defaults of `localhost` or `127.0.0.1` so the system runs locally out-of-the-box.
    
    **Verification Criteria:**
    - Running the engine without a `.env` file should fall back to `localhost` and run successfully.
    - Adding a local `.env` file should successfully override default ports and hostnames.
    ```

---

### [Task 4] Package Engine via Docker Compose

*   **Title:** `[PORTABILITY-4] Containerize Prismatic Engine core and dashboards with Docker Compose`
*   **Description:**
    ```markdown
    To make deployment simple on other servers (AWS, GCP, or local machines), we need a portable, containerized environment.
    
    1. Create a `Dockerfile` at the root of the `prismatic-engine` repository.
    2. Base it on a stable Python image (e.g. `python:3.11-slim`).
    3. Expose the dashboard server ports dynamically.
    4. Create a `docker-compose.yml` that:
       - Spins up the Prismatic Engine core container.
       - Binds a local workspace directory (simulating the sandboxes).
       - Mounts credentials via environment variables or volume mounts.
    
    **Verification Criteria:**
    - Run `docker compose build` and `docker compose up -d`.
    - Verify the core services start up cleanly inside the container without depending on any host-level paths.
    ```

---

### [Task 5] Execute Portability Verification Wave

*   **Title:** `[PORTABILITY-5] Execute validation wave on non-standard directory path`
*   **Description:**
    ```markdown
    Perform an end-to-end validation test of the portability refactoring.
    
    1. Create a temporary user profile (or simulate one in the sandbox) with a home directory that is NOT `/home/ubuntu`.
    2. Clone the `prismatic-engine` repo into a non-standard local path (e.g., `/tmp/portability-test-sandbox/`).
    3. Run the full test suite (`pytest`) in this environment.
    4. Verify that no file creates directories or files outside `/tmp/portability-test-sandbox/` or the temporary home directory.
    
    **Verification Criteria:**
    - Complete run with 100% test coverage passing.
    - Confirm no files were written to `/home/ubuntu/` or `/archive/` during execution.
    ```
