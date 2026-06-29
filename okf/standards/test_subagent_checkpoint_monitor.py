"""Tests for subagent_checkpoint_monitor.py.

These verify the script that prevents subagent work loss by enforcing
commit cadence. Regression test for Gap 10 subagent losing 50KB when
its 50-tool-call budget hit before committing anything.
"""
from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

SCRIPT = "/home/ubuntu/.hermes/profiles/orchestrator/scripts/subagent_checkpoint_monitor.py"


def _setup_test_repo() -> Path:
    """Create a clean git repo in a temp dir. Returns the path."""
    tmp = Path(tempfile.mkdtemp(prefix="ckpt-test-"))
    subprocess.run(["git", "init", "-q"], cwd=tmp, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test"], cwd=tmp, check=True
    )
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp, check=True)
    (tmp / "README.md").write_text("init")
    subprocess.run(["git", "add", "-A"], cwd=tmp, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "initial"], cwd=tmp, check=True
    )
    return tmp


def _run(repo: Path, *args: str) -> tuple[int, str]:
    """Run the checkpoint monitor. Returns (exit_code, combined_output)."""
    result = subprocess.run(
        ["python3", SCRIPT, "--workspace", str(repo), *args],
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.returncode, result.stdout + result.stderr


def test_clean_worktree_returns_0():
    """Empty dirty files = clean = exit 0."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = _setup_test_repo()
        rc, out = _run(repo, "--max-tool-calls", "50", "--current-tool-call", "1")
    assert rc == 0, f"expected 0, got {rc}: {out}"
    assert "clean worktree" in out
    print("PASS: clean worktree → exit 0")


def test_few_modified_files_no_wip():
    """1 modified file under threshold → dirty but no WIP yet → exit 0."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = _setup_test_repo()
        (repo / "README.md").write_text("modified")
        rc, out = _run(
            repo, "--max-tool-calls", "50",
            "--current-tool-call", "2", "--commit-every", "5",
        )
    assert rc == 0, f"expected 0, got {rc}: {out}"
    assert "no commit needed yet" in out
    print("PASS: under threshold → no WIP → exit 0")


def test_over_file_threshold_triggers_wip():
    """6 modified files >= threshold 5 → WIP commit → exit 0."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = _setup_test_repo()
        for i in range(6):
            (repo / f"file_{i}.txt").write_text(str(i))
        rc, out = _run(
            repo, "--max-tool-calls", "50",
            "--current-tool-call", "3", "--commit-every", "5",
        )
        # Verify WIP commit landed
        log_result = subprocess.run(
            ["git", "log", "--oneline"],
            cwd=repo, capture_output=True, text=True,
        )
    assert rc == 0, f"expected 0, got {rc}: {out}"
    assert "WIP commit created" in out
    assert "[WIP-auto-checkpoint]" in log_result.stdout
    print("PASS: over threshold → WIP commit → exit 0")


def test_high_budget_triggers_wip():
    """Budget at 80% should force WIP even with few files modified."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = _setup_test_repo()
        (repo / "single.txt").write_text("x")
        rc, out = _run(
            repo, "--max-tool-calls", "50",
            "--current-tool-call", "40", "--commit-every", "999",
        )
        log_result = subprocess.run(
            ["git", "log", "--oneline"],
            cwd=repo, capture_output=True, text=True,
        )
    assert rc == 0, f"expected 0, got {rc}: {out}"
    assert "WIP commit created" in out
    assert "budget at 80%" in out
    assert "[WIP-auto-checkpoint]" in log_result.stdout
    print("PASS: budget 80% → force WIP → exit 0")


def test_not_a_git_repo_returns_3():
    """Non-git workspace → exit 3 with error message."""
    with tempfile.TemporaryDirectory() as tmp:
        # No git init — just an empty dir
        rc, out = _run(Path(tmp), "--max-tool-calls", "50", "--current-tool-call", "1")
    assert rc == 3, f"expected 3, got {rc}: {out}"
    assert "not a git repo" in out
    print("PASS: not a git repo → exit 3")


def test_dry_run_does_not_commit():
    """--no-auto-commit should report what would happen but NOT commit."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = _setup_test_repo()
        for i in range(10):
            (repo / f"f_{i}.txt").write_text(str(i))
        # Snapshot commits before
        before = subprocess.run(
            ["git", "log", "--oneline"],
            cwd=repo, capture_output=True, text=True,
        )
        rc, out = _run(
            repo, "--max-tool-calls", "50",
            "--current-tool-call", "1", "--commit-every", "5",
            "--no-auto-commit",
        )
        after = subprocess.run(
            ["git", "log", "--oneline"],
            cwd=repo, capture_output=True, text=True,
        )
    assert rc == 0, f"expected 0, got {rc}: {out}"
    assert "DRY-RUN" in out
    assert "would WIP-commit" in out
    assert before.stdout == after.stdout, "dry-run must NOT create a commit"
    print("PASS: dry-run reports but does not commit")


def test_wip_commit_includes_reason():
    """The WIP commit message should include the trigger reason."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = _setup_test_repo()
        for i in range(7):
            (repo / f"g_{i}.txt").write_text(str(i))
        _run(
            repo, "--max-tool-calls", "50",
            "--current-tool-call", "1", "--commit-every", "5",
        )
        log = subprocess.run(
            ["git", "log", "-1", "--format=%B"],
            cwd=repo, capture_output=True, text=True,
        )
    msg = log.stdout
    assert "[WIP-auto-checkpoint]" in msg
    assert "7 modified files" in msg, f"expected count in message: {msg!r}"
    print("PASS: WIP commit includes reason")
