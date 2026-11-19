"""Standalone test suite for scripts/validate.py."""

import subprocess
import sys
from pathlib import Path

import pytest

SKILL_ROOT = Path(__file__).resolve().parent.parent
VALIDATE_PY = SKILL_ROOT / "scripts" / "validate.py"
POLICY_DIR = SKILL_ROOT / "assets" / "policies"


def run_validate(*args, expect_fail=False):
    """Run validate.py with given args; return (stdout, stderr, returncode)."""
    cmd = [sys.executable, str(VALIDATE_PY), *args]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(SKILL_ROOT))
    if not expect_fail and result.returncode not in (0, 2):
        pytest.fail(
            f"validate.py failed unexpectedly (rc={result.returncode}):\n"
            f"{result.stdout}\n{result.stderr}"
        )
    return result.stdout, result.stderr, result.returncode


def test_validate_help_exits_zero():
    stdout, _, rc = run_validate("--help")
    assert rc == 0
    assert "chart" in stdout.lower()


def test_validate_missing_rendered_file_fails():
    _, _, rc = run_validate(
        "--rendered-file", "nonexistent-file-99999.yaml",
        expect_fail=True,
    )
    assert rc == 1


def test_validate_invalid_policy_dir_falls_back_or_fails():
    # find_policy_dir falls back to assets/policies when explicit path does not exist,
    # then fails on missing chart/helm or passes if tools missing.
    _, stderr, rc = run_validate(
        "--chart-dir", "nonexistent-chart",
        "--policy-dir", "/nonexistent/policy/dir/99999",
        expect_fail=True,
    )
    assert rc in (1, 2)
    assert "Traceback" not in stderr


def test_validate_uses_shutil_which():
    source = VALIDATE_PY.read_text(encoding="utf-8")
    assert "shutil.which" in source


def test_validate_multiple_values_flags_accepted():
    _, stderr, _ = run_validate(
        "--values", "a.yaml",
        "--values", "b.yaml",
        "--rendered-file", "nonexistent.yaml",
        expect_fail=True,
    )
    assert "unrecognized arguments" not in stderr.lower()


def test_validate_tool_filter_accepts_valid_choice():
    _, stderr, _ = run_validate(
        "--tool", "datree",
        "--rendered-file", "nonexistent.yaml",
        expect_fail=True,
    )
    assert "invalid choice" not in stderr.lower()


def test_validate_tool_filter_rejects_invalid_choice():
    _, stderr, rc = run_validate(
        "--tool", "not-a-real-tool",
        expect_fail=True,
    )
    assert rc != 0
    assert "invalid choice" in stderr.lower() or "error" in stderr.lower()


def test_validate_tools_skipped_when_missing(tmp_path):
    """When policy tools are absent, validate.py warns and skips without crashing."""
    rendered = tmp_path / "rendered.yaml"
    rendered.write_text(
        "apiVersion: v1\nkind: ConfigMap\nmetadata:\n  name: test\n",
        encoding="utf-8",
    )
    assert POLICY_DIR.is_dir(), f"Missing bundled policy dir: {POLICY_DIR}"

    _, stderr, rc = run_validate(
        "--rendered-file", str(rendered),
        "--policy-dir", str(POLICY_DIR),
        expect_fail=True,
    )
    assert rc in (0, 1, 2)
    assert "Traceback" not in stderr


def test_validate_platform_rules_passes(tmp_path):
    """validate.py --tool platform-rules passes on compliant manifests."""
    rendered = tmp_path / "rendered.yaml"
    rendered.write_text(
        "apiVersion: v1\nkind: ConfigMap\nmetadata:\n  name: test\n",
        encoding="utf-8",
    )
    stdout, _, rc = run_validate(
        "--tool", "platform-rules",
        "--rendered-file", str(rendered),
    )
    assert rc == 0
    assert "PASS" in stdout


def test_validate_platform_rules_fails_on_violation(tmp_path):
    """validate.py --tool platform-rules fails on Kyverno/PDB/grace violations."""
    rendered = tmp_path / "rendered.yaml"
    rendered.write_text(
        "apiVersion: policy/v1\n"
        "kind: PodDisruptionBudget\n"
        "metadata:\n"
        "  name: bad-pdb\n"
        "spec:\n"
        "  maxUnavailable: 0\n",
        encoding="utf-8",
    )
    stdout, _, rc = run_validate(
        "--tool", "platform-rules",
        "--rendered-file", str(rendered),
        expect_fail=True,
    )
    assert rc == 1
    assert "pdb-zero-max-unavailable" in stdout
