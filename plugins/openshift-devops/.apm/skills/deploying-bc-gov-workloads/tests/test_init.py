"""Tests for deploying-bc-gov-workloads/scripts/init.py."""
from pathlib import Path
import subprocess
import sys

import yaml

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "init.py"


def run_init(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )


def test_init_creates_expected_files_without_unreplaced_markers(tmp_path: Path) -> None:
    res = run_init("--project", "sample-app", "--registry", "ghcr.io/example-org", cwd=tmp_path)
    assert res.returncode == 0, res.stderr

    expected = [
        ".github/workflows/ci.yml",
        ".github/workflows/cd.yml",
        ".github/CODEOWNERS",
        "gitops/Chart.yaml",
        "gitops/values.yaml",
        "gitops/values-dev.yaml",
        "gitops/values-test.yaml",
        "gitops/values-prod.yaml",
        "Makefile",
        "AGENTS.md",
        ".gitignore",
    ]
    for rel in expected:
        p = tmp_path / rel
        assert p.is_file(), f"Missing {rel}"
        text = p.read_text(encoding="utf-8")
        assert "@@" not in text, f"Unreplaced marker in {rel}"
        assert "{{ project }}" not in text, f"Unreplaced Jinja marker in {rel}"
        if rel.endswith((".yml", ".yaml")):
            yaml.safe_load(text)


def test_init_skip_and_overwrite(tmp_path: Path) -> None:
    target = tmp_path / "Makefile"
    target.write_text("# custom\n", encoding="utf-8")

    res = run_init("--project", "sample-app", "--registry", "ghcr.io/example-org", cwd=tmp_path)
    assert res.returncode == 0
    assert target.read_text(encoding="utf-8") == "# custom\n"

    res2 = run_init("--project", "sample-app", "--registry", "ghcr.io/example-org", "--overwrite", cwd=tmp_path)
    assert res2.returncode == 0
    assert "# custom" not in target.read_text(encoding="utf-8")


def test_init_rejects_invalid_project_name(tmp_path: Path) -> None:
    res = run_init("--project", "Invalid_App", "--registry", "ghcr.io/example-org", cwd=tmp_path)
    assert res.returncode != 0


def test_init_rejects_path_traversal(tmp_path: Path) -> None:
    res = run_init(
        "--project", "sample-app", "--registry", "ghcr.io/example-org", "--target-dir", "..", cwd=tmp_path
    )
    assert res.returncode != 0
