from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def run_cli(command: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO / "src")
    return subprocess.run(
        [sys.executable, "-m", "reporting_pipeline.cli", command],
        cwd=REPO,
        env=env,
        capture_output=True,
        text=True,
        timeout=15,
    )


def test_smoke_cli_from_repo_root() -> None:
    result = run_cli("smoke")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip()


def test_reverse_cli_from_repo_root() -> None:
    result = run_cli("reverse-test")
    assert result.returncode == 0, result.stdout + result.stderr
    assert '"status": "PASS"' in result.stdout
