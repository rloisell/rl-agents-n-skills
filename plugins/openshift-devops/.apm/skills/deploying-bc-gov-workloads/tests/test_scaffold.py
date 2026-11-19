"""Standalone test suite for scripts/scaffold.py."""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

SKILL_ROOT = Path(__file__).resolve().parent.parent
SCAFFOLD = SKILL_ROOT / "scripts" / "scaffold.py"


@pytest.fixture(autouse=True)
def in_skill_root():
    """Ensure CWD is SKILL_ROOT so relative output dirs satisfy path traversal guard."""
    old = os.getcwd()
    os.chdir(SKILL_ROOT)
    yield
    os.chdir(old)


@pytest.fixture
def scaffold_out_dir(request):
    """Create a unique relative output dir inside SKILL_ROOT/tests/.tmp_out."""
    test_name = re.sub(r"[^a-zA-Z0-9_-]", "_", request.node.name)[:50]
    rel = Path("tests") / ".tmp_out" / test_name
    abs_d = SKILL_ROOT / rel
    abs_d.mkdir(parents=True, exist_ok=True)
    yield rel
    shutil.rmtree(abs_d, ignore_errors=True)
    tmp_base = SKILL_ROOT / "tests" / ".tmp_out"
    if tmp_base.exists() and not any(tmp_base.iterdir()):
        tmp_base.rmdir()


def run_scaffold(*extra_args, expect_fail=False, output_dir=None):
    """Run scaffold.py with given args; return (stdout, stderr, returncode)."""
    cmd = [sys.executable, str(SCAFFOLD)]
    if output_dir:
        cmd += ["--output-dir", str(output_dir)]
    cmd += list(extra_args)
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(SKILL_ROOT))
    if not expect_fail and result.returncode != 0:
        pytest.fail(
            f"scaffold.py failed (rc={result.returncode}):\n{result.stdout}\n{result.stderr}"
        )
    return result.stdout, result.stderr, result.returncode


def read_output(output_dir: Path, filename: str) -> str:
    path = SKILL_ROOT / output_dir / filename
    assert path.exists(), f"Expected output file not found: {path}"
    return path.read_text(encoding="utf-8")


def assert_no_markers(content: str, filename: str = "") -> None:
    remaining = re.findall(r"@@\w+@@", content)
    assert not remaining, f"Unreplaced markers in {filename}: {remaining}"


def assert_valid_yaml(content: str, filename: str = "") -> None:
    if "{{" in content:
        return
    try:
        list(yaml.safe_load_all(content))
    except yaml.YAMLError as exc:
        pytest.fail(f"Invalid YAML in {filename}:\n{exc}\n\nContent:\n{content}")


HELM_TYPES = [
    ("deployment", "my-api", ["--name", "my-api", "--port", "8080"], "my-api-deployment.yaml"),
    ("service", "my-api", ["--name", "my-api", "--port", "8080"], "my-api-service.yaml"),
    ("route", "my-api", ["--name", "my-api"], "my-api-route.yaml"),
    ("statefulset", "pg", ["--name", "pg", "--port", "5432"], "pg-statefulset.yaml"),
    ("hpa", "my-api", ["--name", "my-api"], "my-api-hpa.yaml"),
    ("pdb", "my-api", ["--name", "my-api"], "my-api-pdb.yaml"),
    ("ingress", "my-api", ["--name", "my-api", "--host", "my-api.example.com"], "my-api-ingress.yaml"),
    ("pvc", "pg-data", ["--name", "pg-data"], "pg-data-pvc.yaml"),
    ("job", "db-migrate", ["--name", "db-migrate"], "db-migrate-job.yaml"),
    ("serviceaccount", "my-api", ["--name", "my-api"], "my-api-serviceaccount.yaml"),
    ("configmap", "my-api", ["--name", "my-api"], "my-api-configmap.yaml"),
    ("cronjob", "my-task", ["--name", "my-task", "--schedule", "0 2 * * *"], "my-task-cronjob.yaml"),
]


@pytest.mark.parametrize("rtype,name,extra_args,expected_file", HELM_TYPES, ids=[t[0] for t in HELM_TYPES])
def test_helm_type_produces_valid_output(rtype, name, extra_args, expected_file, scaffold_out_dir):
    run_scaffold("--type", rtype, *extra_args, output_dir=scaffold_out_dir)
    content = read_output(scaffold_out_dir, expected_file)
    assert_no_markers(content, expected_file)
    assert_valid_yaml(content, expected_file)
    assert f"scaffold.py v" in content
    assert f"--type {rtype}" in content
    assert name in content


CI_TYPES = [
    ("docker-ci", ["--image", "my-app", "--registry", "ghcr.io/my-org"], "my-app-docker.yml"),
    ("sast-ci", ["--project-key", "my-proj", "--sonar-host", "https://sonar.example.com"], "sast.yml"),
]


@pytest.mark.parametrize("rtype,extra_args,expected_file", CI_TYPES, ids=[t[0] for t in CI_TYPES])
def test_ci_type_produces_valid_output(rtype, extra_args, expected_file, scaffold_out_dir):
    run_scaffold("--type", rtype, *extra_args, output_dir=scaffold_out_dir)
    content = read_output(scaffold_out_dir, expected_file)
    assert_no_markers(content, expected_file)
    assert_valid_yaml(content, expected_file)
    assert f"--type {rtype}" in content


def test_ingress_defaults_to_dataclass_medium(scaffold_out_dir):
    run_scaffold(
        "--type", "ingress",
        "--name", "my-api",
        "--host", "my-api.example.com",
        output_dir=scaffold_out_dir,
    )
    content = read_output(scaffold_out_dir, "my-api-ingress.yaml")
    assert "dataclass-medium" in content


def test_networkpolicy_ingress_from_router(scaffold_out_dir):
    run_scaffold(
        "--type", "networkpolicy",
        "--name", "my-api",
        "--port", "8080",
        "--ingress-from-router",
        output_dir=scaffold_out_dir,
    )
    content = read_output(scaffold_out_dir, "my-api-networkpolicy.yaml")
    assert_no_markers(content, "my-api-networkpolicy.yaml")
    assert "AllowIngressFrom" in content
    assert "openshift-ingress" in content
    assert "my-api" in content


def test_networkpolicy_egress_to_apps_and_cidr(scaffold_out_dir):
    run_scaffold(
        "--type", "networkpolicy",
        "--name", "my-api",
        "--port", "8080",
        "--egress-to-apps", "postgresql:5432",
        "--egress-to-cidr", "198.51.100.0/24:443",
        output_dir=scaffold_out_dir,
    )
    content = read_output(scaffold_out_dir, "my-api-networkpolicy.yaml")
    assert_no_markers(content)
    assert "AllowEgressTo" in content
    assert "postgresql" in content
    assert "198.51.100.0/24" in content


def test_networkpolicy_internet_egress_requires_approval(scaffold_out_dir):
    _, _, rc = run_scaffold(
        "--type", "networkpolicy",
        "--name", "my-api",
        "--egress-internet",
        output_dir=scaffold_out_dir,
        expect_fail=True,
    )
    assert rc != 0


def test_networkpolicy_internet_egress_with_approval(scaffold_out_dir):
    run_scaffold(
        "--type", "networkpolicy",
        "--name", "my-api",
        "--port", "443",
        "--egress-internet",
        "--justification", "External OAuth provider",
        "--approved-by", "TICKET-1234",
        output_dir=scaffold_out_dir,
    )
    content = read_output(scaffold_out_dir, "my-api-networkpolicy.yaml")
    assert "justification" in content
    assert "approvedBy" in content


def test_invalid_k8s_name_rejected(scaffold_out_dir):
    _, _, rc = run_scaffold(
        "--type", "deployment",
        "--name", "My-App",
        output_dir=scaffold_out_dir,
        expect_fail=True,
    )
    assert rc != 0


def test_path_traversal_rejected():
    outside = str(SKILL_ROOT.parent)
    _, _, rc = run_scaffold(
        "--type", "service",
        "--name", "my-api",
        "--output-dir", outside,
        expect_fail=True,
    )
    assert rc != 0


def test_dry_run_does_not_write(scaffold_out_dir):
    stdout, _, _ = run_scaffold(
        "--type", "deployment",
        "--name", "my-api",
        "--port", "8080",
        "--dry-run",
        output_dir=scaffold_out_dir,
    )
    assert "[DRY-RUN]" in stdout
    abs_dir = SKILL_ROOT / scaffold_out_dir
    files = list(abs_dir.iterdir()) if abs_dir.exists() else []
    assert len(files) == 0


def test_force_overwrites_existing(scaffold_out_dir):
    args = ["--type", "service", "--name", "my-api", "--port", "8080"]
    run_scaffold(*args, output_dir=scaffold_out_dir)

    stdout, _, _ = run_scaffold(*args, output_dir=scaffold_out_dir)
    assert "SKIPPED" in stdout

    stdout, _, _ = run_scaffold(*args, "--force", output_dir=scaffold_out_dir)
    assert "SKIPPED" not in stdout


def test_missing_required_arg_fails(scaffold_out_dir):
    _, _, rc = run_scaffold(
        "--type", "deployment",
        output_dir=scaffold_out_dir,
        expect_fail=True,
    )
    assert rc != 0


def test_deployment_custom_probe_paths(scaffold_out_dir):
    run_scaffold(
        "--type", "deployment",
        "--name", "my-api",
        "--port", "9090",
        "--probe-live-path", "/actuator/health/liveness",
        "--probe-ready-path", "/actuator/health/readiness",
        output_dir=scaffold_out_dir,
    )
    content = read_output(scaffold_out_dir, "my-api-deployment.yaml")
    assert "/actuator/health/liveness" in content
    assert "/actuator/health/readiness" in content
    assert_no_markers(content)
