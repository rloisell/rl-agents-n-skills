#!/usr/bin/env python3
"""
BC Gov OpenShift manifest validator - v2.0.0

Runs the full 4-tool policy pipeline against rendered Helm manifests:
  1. helm template  - renders the Helm chart to raw YAML
  2. datree         - checks org label/schema rules
  3. polaris        - checks security and reliability best practices
  4. kube-linter    - checks Kubernetes lint rules
  5. conftest/OPA   - hard-deny Rego rules (NetworkPolicy, Route, AVI)
  6. platform-rules - BC Gov Kyverno CronJob, PDB, and drain grace period rules

Usage:
    python validate.py --chart-dir gitops/ [--values gitops/values.yaml --values gitops/values-dev.yaml] [--policy-dir <path>]
    python validate.py --rendered-file rendered.yaml  # skip helm render, use existing file
    python validate.py --chart-dir gitops/ --tool datree  # run only one tool

Exit codes:
    0  all tools passed
    1  one or more tools failed
    2  prerequisite tool not found
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

PLUGIN_VERSION = "2.0.0"

POLICY_TOOLS = ["datree", "polaris", "kube-linter", "conftest", "platform-rules"]


def find_policy_dir(explicit: str) -> str:
    """Find policy files — try explicit path, then common install locations."""
    if explicit and os.path.isdir(explicit):
        return os.path.abspath(explicit)

    candidates = [
        # Skill-bundled policies: scripts/ is sibling of assets/policies/
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "assets", "policies"),
        # Local repo fallback
        os.path.join(os.getcwd(), "policies"),
    ]
    for c in candidates:
        if os.path.isdir(c):
            return os.path.abspath(c)

    return ""


def run(cmd: list, label: str, fail_on_error: bool = True) -> int:
    """Run a command and return its exit code."""
    print(f"\n{'-' * 60}")
    print(f"  [{label}]  {' '.join(cmd)}")
    print(f"{'-' * 60}")
    result = subprocess.run(cmd, capture_output=False, text=True)
    return result.returncode


def check_tool(name: str) -> bool:
    found = shutil.which(name) is not None
    if not found:
        print(f"  WARN: {name} not found in PATH -- skipping this check")
    return found


def main() -> None:
    parser = argparse.ArgumentParser(
        description=f"BC Gov OpenShift manifest validator v{PLUGIN_VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--chart-dir", default="gitops",
                        help="Helm chart directory to render (default: gitops)")
    parser.add_argument("--values", action="append", default=[],
                        help="Values file(s) for helm template; repeat for multiple overlays (default: <chart-dir>/values.yaml)")
    parser.add_argument("--rendered-file", default="",
                        help="Use an already-rendered YAML file instead of running helm template")
    parser.add_argument("--policy-dir", default="",
                        help="Directory containing policy files (auto-detected if omitted)")
    parser.add_argument("--tool", default="", choices=POLICY_TOOLS + [""],
                        help="Run only this tool (default: run all)")
    parser.add_argument("--release-name", default="test-release",
                        help="Helm release name for rendering (default: test-release)")
    args = parser.parse_args()

    policy_dir = find_policy_dir(args.policy_dir)
    if not policy_dir:
        print("ERROR: Cannot find policy directory. Specify --policy-dir explicitly.")
        sys.exit(1)

    print(f"\n=== BC Gov OpenShift Manifest Validator v{PLUGIN_VERSION} ===")
    print(f"Policy directory: {policy_dir}")

    failures = []
    with tempfile.TemporaryDirectory() as tmpdir:
        # Step 1: Render or use provided file
        if args.rendered_file:
            rendered = os.path.abspath(args.rendered_file)
            if not os.path.isfile(rendered):
                sys.exit(f"ERROR: --rendered-file '{rendered}' does not exist")
            print(f"\n  Using pre-rendered file: {rendered}")
        else:
            rendered = os.path.join(tmpdir, "rendered.yaml")
            chart_dir = os.path.abspath(args.chart_dir)
            values_files = args.values if args.values else [os.path.join(chart_dir, "values.yaml")]

            if not check_tool("helm"):
                print("ERROR: helm is required. Install from https://helm.sh/docs/intro/install/")
                sys.exit(2)

            helm_cmd = ["helm", "template", args.release_name, chart_dir]
            for vf in values_files:
                helm_cmd += ["--values", vf]
            helm_cmd += ["--output-dir", tmpdir]
            rc = run(helm_cmd, "helm template")
            if rc != 0:
                print("\nFAIL: helm template failed -- fix chart errors before running policy tools")
                sys.exit(1)

            # Collect all rendered YAML into one file
            import glob as _glob
            rendered_files = _glob.glob(os.path.join(tmpdir, "**", "*.yaml"), recursive=True)
            with open(rendered, "w") as out:
                for rf in rendered_files:
                    with open(rf) as inp:
                        out.write(inp.read())
                        out.write("\n---\n")
            print(f"\n  Rendered to: {rendered} ({len(rendered_files)} files)")

        # Step 2: datree
        if (not args.tool or args.tool == "datree") and check_tool("datree"):
            datree_policy = os.path.join(policy_dir, "datree-policies.yaml")
            cmd = ["datree", "test", rendered]
            if os.path.isfile(datree_policy):
                cmd += ["--policy-config", datree_policy]
            rc = run(cmd, "datree")
            if rc != 0:
                failures.append("datree")
                if args.tool:
                    sys.exit(rc)

        # Step 3: polaris
        if (not args.tool or args.tool == "polaris") and check_tool("polaris"):
            polaris_cfg = os.path.join(policy_dir, "polaris.yaml")
            cmd = ["polaris", "audit", "--format", "pretty", "--audit-path", rendered]
            if os.path.isfile(polaris_cfg):
                cmd += ["--config", polaris_cfg]
            rc = run(cmd, "polaris")
            if rc != 0:
                failures.append("polaris")
                if args.tool:
                    sys.exit(rc)

        # Step 4: kube-linter
        if (not args.tool or args.tool == "kube-linter") and check_tool("kube-linter"):
            kl_cfg = os.path.join(policy_dir, "kube-linter.yaml")
            cmd = ["kube-linter", "lint", rendered]
            if os.path.isfile(kl_cfg):
                cmd += ["--config", kl_cfg]
            rc = run(cmd, "kube-linter")
            if rc != 0:
                failures.append("kube-linter")
                if args.tool:
                    sys.exit(rc)

        # Step 5: conftest/OPA
        if (not args.tool or args.tool == "conftest") and check_tool("conftest"):
            cmd = ["conftest", "test", rendered,
                   "--policy", policy_dir, "--all-namespaces", "--fail-on-warn"]
            rc = run(cmd, "conftest/OPA")
            if rc != 0:
                failures.append("conftest")
                if args.tool:
                    sys.exit(rc)

        # Step 6: BC Gov platform rules (Kyverno CronJob, PDB, drain grace period)
        if not args.tool or args.tool == "platform-rules":
            platform_rules_script = os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "check_platform_rules.py"
            )
            if os.path.isfile(platform_rules_script):
                cmd = [sys.executable, platform_rules_script, "--rendered-file", rendered]
                rc = run(cmd, "platform-rules")
                if rc != 0:
                    failures.append("platform-rules")
                    if args.tool:
                        sys.exit(rc)

    print(f"\n{'=' * 60}")
    if failures:
        print(f"  FAIL: {', '.join(failures)}")
        print(f"  Fix the issues above and re-run: python ./scripts/validate.py --chart-dir gitops/")
        sys.exit(1)
    else:
        print("  PASS: All policy checks passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
