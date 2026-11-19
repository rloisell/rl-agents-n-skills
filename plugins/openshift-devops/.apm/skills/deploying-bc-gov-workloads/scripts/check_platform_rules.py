#!/usr/bin/env python3
"""Deterministic BC Gov OpenShift platform rules checker for rendered YAML.

Checks rendered Kubernetes/OpenShift manifests for platform admission and
resiliency rules not covered by standard upstream linters:
  1. Kyverno CronJob rules:
     - no-unsupported-timezone: CRON_TZ= / TZ= in spec.schedule (use spec.timeZone)
     - no-fast-cronjob: schedule faster than every 5m, or faster than every 1h with a PVC
  2. PodDisruptionBudget (PDB) rules:
     - pdb-zero-max-unavailable: spec.maxUnavailable == 0 (or "0%")
     - pdb-unhealthy-eviction-policy: missing unhealthyPodEvictionPolicy: AlwaysAllow
  3. Node drain grace period:
     - termination-grace-period-too-high: terminationGracePeriodSeconds > 600
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

MAX_TERMINATION_GRACE_SECONDS = 600
MIN_CRON_INTERVAL_MINUTES = 5
MIN_CRON_PVC_INTERVAL_MINUTES = 60

CRON_MACROS_MINUTES: dict[str, int] = {
    "@yearly": 525600,
    "@annually": 525600,
    "@monthly": 43200,
    "@weekly": 10080,
    "@daily": 1440,
    "@midnight": 1440,
    "@hourly": 60,
}

_EVERY_DURATION_RE = re.compile(r"(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?$", re.IGNORECASE)
_CRON_TZ_PREFIX_RE = re.compile(r"^\s*(?:CRON_TZ|TZ)\s*=\s*\S+\s*")


@dataclass(frozen=True)
class Violation:
    """Single platform rule violation."""

    rule: str
    resource: str
    message: str


def _expand_cron_field(field: str, min_val: int, max_val: int) -> list[int] | None:
    """Expand a single 5-field cron part into sorted integer values."""
    values: set[int] = set()
    for part in field.split(","):
        part = part.strip()
        if not part:
            return None
        step = 1
        if "/" in part:
            base, step_str = part.split("/", 1)
            if not step_str.isdigit() or int(step_str) <= 0:
                return None
            step = int(step_str)
        else:
            base = part

        if base == "*":
            start, end = min_val, max_val
        elif "-" in base:
            lo_str, hi_str = base.split("-", 1)
            if not (lo_str.isdigit() and hi_str.isdigit()):
                return None
            start, end = int(lo_str), int(hi_str)
        elif base.isdigit():
            val = int(base)
            if not (min_val <= val <= max_val):
                return None
            if "/" in part:
                start, end = val, max_val
            else:
                values.add(val)
                continue
        else:
            return None

        if start < min_val or end > max_val or start > end:
            return None
        values.update(range(start, end + 1, step))

    return sorted(values) if values else None


def min_cron_interval_minutes(schedule: str) -> float | None:
    """Return the minimum interval in minutes between consecutive CronJob runs, or None if unparseable."""
    cleaned = _CRON_TZ_PREFIX_RE.sub("", schedule).strip()
    lower = cleaned.lower()

    if lower in CRON_MACROS_MINUTES:
        return float(CRON_MACROS_MINUTES[lower])

    if lower.startswith("@every "):
        dur_str = lower[len("@every "):].strip()
        match = _EVERY_DURATION_RE.match(dur_str)
        if not match or not any(match.groups()):
            return None
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        return hours * 60 + minutes + seconds / 60.0

    parts = cleaned.split()
    if len(parts) != 5:
        return None

    minutes = _expand_cron_field(parts[0], 0, 59)
    hours = _expand_cron_field(parts[1], 0, 23)
    if not minutes or not hours:
        return None

    times = [h * 60 + m for h in hours for m in minutes]
    if len(times) == 1:
        return 1440.0

    gaps = [times[i + 1] - times[i] for i in range(len(times) - 1)]
    gaps.append((1440 - times[-1]) + times[0])
    return float(min(gaps))


def _resource_label(doc: dict[str, Any]) -> str:
    kind = str(doc.get("kind", "Unknown"))
    meta = doc.get("metadata") or {}
    name = str(meta.get("name", "<unnamed>"))
    ns = meta.get("namespace")
    return f"{kind}/{ns}/{name}" if ns else f"{kind}/{name}"


def _extract_pod_spec(doc: dict[str, Any]) -> dict[str, Any] | None:
    kind = doc.get("kind")
    spec = doc.get("spec")
    if not isinstance(spec, dict):
        return None

    if kind == "Pod":
        return spec
    if kind in {"Deployment", "StatefulSet", "DaemonSet", "ReplicaSet", "Job", "ReplicationController"}:
        tpl = spec.get("template")
        if isinstance(tpl, dict) and isinstance(tpl.get("spec"), dict):
            return tpl["spec"]
    if kind == "CronJob":
        job_tpl = spec.get("jobTemplate")
        if isinstance(job_tpl, dict):
            job_spec = job_tpl.get("spec")
            if isinstance(job_spec, dict):
                tpl = job_spec.get("template")
                if isinstance(tpl, dict) and isinstance(tpl.get("spec"), dict):
                    return tpl["spec"]
    return None


def _has_pvc(pod_spec: dict[str, Any] | None) -> bool:
    if not pod_spec:
        return False
    volumes = pod_spec.get("volumes")
    if not isinstance(volumes, list):
        return False
    return any(isinstance(v, dict) and "persistentVolumeClaim" in v for v in volumes)


def check_document(doc: dict[str, Any]) -> list[Violation]:
    """Check a single parsed Kubernetes/OpenShift YAML document for platform rule violations."""
    if not isinstance(doc, dict) or "kind" not in doc:
        return []

    violations: list[Violation] = []
    kind = doc.get("kind")
    res = _resource_label(doc)
    spec = doc.get("spec") if isinstance(doc.get("spec"), dict) else {}

    if kind == "CronJob":
        schedule = spec.get("schedule")
        if isinstance(schedule, str):
            if "CRON_TZ=" in schedule or re.match(r"^\s*TZ=", schedule):
                violations.append(
                    Violation(
                        rule="no-unsupported-timezone",
                        resource=res,
                        message="CronJob spec.schedule must not contain CRON_TZ=/TZ=; use spec.timeZone instead.",
                    )
                )

            interval = min_cron_interval_minutes(schedule)
            pod_spec = _extract_pod_spec(doc)
            has_pvc = _has_pvc(pod_spec)
            if interval is not None:
                if has_pvc and interval < MIN_CRON_PVC_INTERVAL_MINUTES:
                    violations.append(
                        Violation(
                            rule="no-fast-cronjob",
                            resource=res,
                            message=(
                                f"CronJob with a mounted PVC runs every {interval:g}m (< 60m). "
                                "Widen schedule to >=1h or replace with a go-crond Deployment."
                            ),
                        )
                    )
                elif interval < MIN_CRON_INTERVAL_MINUTES:
                    violations.append(
                        Violation(
                            rule="no-fast-cronjob",
                            resource=res,
                            message=(
                                f"CronJob runs every {interval:g}m (< 5m). "
                                "Widen schedule to >=5m or replace with a go-crond Deployment."
                            ),
                        )
                    )

    if kind == "PodDisruptionBudget":
        max_unavail = spec.get("maxUnavailable")
        if max_unavail == 0 or max_unavail == "0%":
            violations.append(
                Violation(
                    rule="pdb-zero-max-unavailable",
                    resource=res,
                    message="PodDisruptionBudget maxUnavailable=0 blocks cluster node drains.",
                )
            )
        eviction_policy = spec.get("unhealthyPodEvictionPolicy")
        if eviction_policy != "AlwaysAllow":
            violations.append(
                Violation(
                    rule="pdb-unhealthy-eviction-policy",
                    resource=res,
                    message="PodDisruptionBudget should set spec.unhealthyPodEvictionPolicy: AlwaysAllow.",
                )
            )

    pod_spec = _extract_pod_spec(doc)
    if pod_spec is not None:
        grace = pod_spec.get("terminationGracePeriodSeconds")
        if isinstance(grace, (int, float)) and not isinstance(grace, bool) and grace > MAX_TERMINATION_GRACE_SECONDS:
            violations.append(
                Violation(
                    rule="termination-grace-period-too-high",
                    resource=res,
                    message=(
                        f"terminationGracePeriodSeconds={grace} exceeds Platform Ops node-drain cap "
                        f"of {MAX_TERMINATION_GRACE_SECONDS}s."
                    ),
                )
            )

    return violations


def check_yaml_stream(content: str) -> list[Violation]:
    """Parse a multi-document YAML string and return all platform rule violations."""
    violations: list[Violation] = []
    for doc in yaml.safe_load_all(content):
        if isinstance(doc, dict):
            violations.extend(check_document(doc))
    return violations


def check_files(paths: list[Path]) -> list[Violation]:
    """Check one or more YAML files and return all violations."""
    violations: list[Violation] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        violations.extend(check_yaml_stream(text))
    return violations


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Check rendered Kubernetes/OpenShift YAML for BC Gov platform rules."
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Rendered YAML file(s) to check.",
    )
    parser.add_argument(
        "--rendered-file",
        dest="rendered_file",
        default="",
        help="Rendered YAML file path (alternative to positional argument).",
    )
    args = parser.parse_args(argv)

    raw_paths = list(args.files)
    if args.rendered_file:
        raw_paths.append(args.rendered_file)

    if not raw_paths:
        parser.error("Provide at least one YAML file or --rendered-file.")

    paths = [Path(p) for p in raw_paths]
    for p in paths:
        if not p.is_file():
            print(f"ERROR: File not found: {p}", file=sys.stderr)
            return 1

    try:
        violations = check_files(paths)
    except yaml.YAMLError as exc:
        print(f"ERROR: Failed to parse YAML: {exc}", file=sys.stderr)
        return 1

    if violations:
        for v in violations:
            print(f"FAIL [{v.rule}] {v.resource}: {v.message}")
        return 1

    print("PASS: All BC Gov platform rules passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
