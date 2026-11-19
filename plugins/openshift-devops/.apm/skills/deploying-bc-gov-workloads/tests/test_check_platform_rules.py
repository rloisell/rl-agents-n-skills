"""Unit and CLI tests for scripts/check_platform_rules.py."""

import subprocess
import sys
from pathlib import Path

import pytest

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from check_platform_rules import (  # noqa: E402
    check_yaml_stream,
    min_cron_interval_minutes,
)

SCRIPT_PY = SKILL_ROOT / "scripts" / "check_platform_rules.py"


@pytest.mark.parametrize(
    ("schedule", "expected"),
    [
        ("* * * * *", 1.0),
        ("*/2 * * * *", 2.0),
        ("*/5 * * * *", 5.0),
        ("*/15 * * * *", 15.0),
        ("0 * * * *", 60.0),
        ("0 2 * * *", 1440.0),
        ("@hourly", 60.0),
        ("@every 3m", 3.0),
        ("@every 1h", 60.0),
    ],
)
def test_min_cron_interval_minutes(schedule: str, expected: float) -> None:
    assert min_cron_interval_minutes(schedule) == expected


def test_cronjob_fast_schedule_without_pvc_fails() -> None:
    manifest = """
apiVersion: batch/v1
kind: CronJob
metadata:
  name: fast-job
spec:
  schedule: "*/2 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: Never
          containers:
            - name: worker
              image: busybox:1.36
"""
    violations = check_yaml_stream(manifest)
    assert [v.rule for v in violations] == ["no-fast-cronjob"]


def test_cronjob_5m_without_pvc_passes() -> None:
    manifest = """
apiVersion: batch/v1
kind: CronJob
metadata:
  name: ok-job
spec:
  schedule: "*/5 * * * *"
  timeZone: America/Vancouver
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: Never
          containers:
            - name: worker
              image: busybox:1.36
"""
    assert check_yaml_stream(manifest) == []


def test_cronjob_under_1h_with_pvc_fails() -> None:
    manifest = """
apiVersion: batch/v1
kind: CronJob
metadata:
  name: pvc-job
spec:
  schedule: "*/30 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: Never
          volumes:
            - name: data
              persistentVolumeClaim:
                claimName: my-pvc
          containers:
            - name: worker
              image: busybox:1.36
"""
    violations = check_yaml_stream(manifest)
    assert [v.rule for v in violations] == ["no-fast-cronjob"]


def test_cronjob_hourly_with_pvc_passes() -> None:
    manifest = """
apiVersion: batch/v1
kind: CronJob
metadata:
  name: pvc-hourly
spec:
  schedule: "0 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: Never
          volumes:
            - name: data
              persistentVolumeClaim:
                claimName: my-pvc
          containers:
            - name: worker
              image: busybox:1.36
"""
    assert check_yaml_stream(manifest) == []


def test_cronjob_cron_tz_fails() -> None:
    manifest = """
apiVersion: batch/v1
kind: CronJob
metadata:
  name: tz-job
spec:
  schedule: "CRON_TZ=America/Vancouver 0 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: Never
          containers:
            - name: worker
              image: busybox:1.36
"""
    violations = check_yaml_stream(manifest)
    assert [v.rule for v in violations] == ["no-unsupported-timezone"]


def test_pdb_rules() -> None:
    bad_pdb = """
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: app-pdb
spec:
  maxUnavailable: 0
  selector:
    matchLabels:
      app: web
"""
    rules = {v.rule for v in check_yaml_stream(bad_pdb)}
    assert rules == {"pdb-zero-max-unavailable", "pdb-unhealthy-eviction-policy"}

    good_pdb = """
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: app-pdb
spec:
  minAvailable: 1
  unhealthyPodEvictionPolicy: AlwaysAllow
  selector:
    matchLabels:
      app: web
"""
    assert check_yaml_stream(good_pdb) == []


def test_termination_grace_period_over_600_fails() -> None:
    bad_deploy = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: slow-shutdown
spec:
  template:
    spec:
      terminationGracePeriodSeconds: 900
      containers:
        - name: app
          image: nginx:1.25
"""
    violations = check_yaml_stream(bad_deploy)
    assert [v.rule for v in violations] == ["termination-grace-period-too-high"]


def test_cli_exit_codes(tmp_path: Path) -> None:
    good = tmp_path / "good.yaml"
    good.write_text("apiVersion: v1\nkind: ConfigMap\nmetadata:\n  name: ok\n", encoding="utf-8")
    res_ok = subprocess.run(
        [sys.executable, str(SCRIPT_PY), "--rendered-file", str(good)],
        capture_output=True,
        text=True,
    )
    assert res_ok.returncode == 0

    bad = tmp_path / "bad.yaml"
    bad.write_text(
        "apiVersion: policy/v1\nkind: PodDisruptionBudget\nmetadata:\n  name: bad\nspec:\n  maxUnavailable: 0\n",
        encoding="utf-8",
    )
    res_fail = subprocess.run(
        [sys.executable, str(SCRIPT_PY), str(bad)],
        capture_output=True,
        text=True,
    )
    assert res_fail.returncode == 1
    assert "pdb-zero-max-unavailable" in res_fail.stdout
