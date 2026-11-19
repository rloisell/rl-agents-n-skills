#!/usr/bin/env python3
"""
Initialize an application repository for OpenShift Emerald deployment.

Generates the full boilerplate scaffolding:
  .github/workflows/ci.yml
  .github/workflows/cd.yml
  .github/CODEOWNERS
  gitops/Chart.yaml
  gitops/values.yaml
  gitops/values-dev.yaml
  gitops/values-test.yaml
  gitops/values-prod.yaml
  Makefile
  AGENTS.md
  .gitignore  (appended)

Safety features:
  - Kubernetes name validation on --project
  - Path traversal guard on --target-dir
  - Post-render validation failing on any unreplaced @@MARKER@@
  - Idempotent skip-if-exists unless --overwrite is set
"""
import argparse
import os
import re
import sys

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "assets", "templates")

ENV_LABELS = {
    "dev": "development",
    "test": "test",
    "prod": "production",
}

ENV_REPLICAS = {
    "dev": "1",
    "test": "1",
    "prod": "2",
}

ENV_ROUTE_ENABLED = {
    "dev": "true",
    "test": "true",
    "prod": "true",
}


def validate_k8s_name(name: str) -> None:
    """Fail fast if project name does not meet Kubernetes naming rules."""
    if not re.match(r"^[a-z][a-z0-9-]{1,62}$", name):
        sys.exit(
            f"ERROR: '{name}' is not a valid Kubernetes name. "
            "Must start with a lowercase letter, contain only [a-z0-9-], and be 2-63 characters."
        )


def guard_target_dir(target_dir: str) -> str:
    """Resolve and validate that target_dir is inside the current working directory."""
    cwd = os.path.realpath(os.getcwd())
    resolved = os.path.realpath(os.path.abspath(target_dir))
    try:
        common = os.path.commonpath([cwd, resolved])
    except ValueError:
        common = ""
    if common != cwd:
        sys.exit(
            f"ERROR: --target-dir '{target_dir}' resolves to '{resolved}' which is outside "
            f"the current working directory '{cwd}'. Refusing to write."
        )
    return resolved


def guard_unreplaced_markers(content: str, filename: str) -> None:
    """Fail if any @@MARKER@@ placeholder remains unreplaced."""
    leftover = re.findall(r"@@[A-Z0-9_]+@@", content)
    if leftover:
        sys.exit(f"ERROR: Unreplaced marker(s) in {filename}: {', '.join(sorted(set(leftover)))}")


def load_template(filename: str) -> str:
    """Load a template file from assets/templates/."""
    path = os.path.join(TEMPLATES_DIR, filename)
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def render(tpl: str, replacements: dict[str, str], filename: str) -> str:
    """Substitute @@MARKER@@ placeholders and verify none remain."""
    for marker, value in replacements.items():
        tpl = tpl.replace(marker, value)
    guard_unreplaced_markers(tpl, filename)
    return tpl


def write_file(path: str, content: str, overwrite: bool) -> None:
    """Write content to path unless it already exists and overwrite is False."""
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    if os.path.exists(path) and not overwrite:
        print(f"  skip (exists): {path}")
        return
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"  [OK] {path}")


def append_gitignore(target_dir: str, additions: str) -> None:
    """Idempotently append Helm ignore rules to .gitignore."""
    gi_path = os.path.join(target_dir, ".gitignore")
    marker = "# Helm"
    if os.path.exists(gi_path):
        with open(gi_path, "r", encoding="utf-8") as fh:
            existing = fh.read()
        if marker in existing:
            print(f"  skip (already has Helm section): {gi_path}")
            return
        with open(gi_path, "a", encoding="utf-8") as fh:
            fh.write("\n" + additions)
        print(f"  [OK] appended Helm entries to {gi_path}")
    else:
        with open(gi_path, "w", encoding="utf-8") as fh:
            fh.write(additions)
        print(f"  [OK] {gi_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Initialize an application repository for OpenShift Emerald deployment"
    )
    parser.add_argument("--project", required=True, help="Short project name, e.g. my-app (Helm release name)")
    parser.add_argument("--registry", required=True, help="Container image registry, e.g. ghcr.io/<org>")
    parser.add_argument("--team", default="<team-name>", help="Team name for the owner label in values.yaml")
    parser.add_argument("--team-handle", default="<team-github-handle>", help="GitHub team handle for CODEOWNERS")
    parser.add_argument("--namespace-dev", default="", help="OpenShift namespace for dev (default: <project>-dev)")
    parser.add_argument("--namespace-test", default="", help="OpenShift namespace for test (default: <project>-test)")
    parser.add_argument("--namespace-prod", default="", help="OpenShift namespace for prod (default: <project>-prod)")
    parser.add_argument("--solution-path", default="./MySolution.sln", help=".NET solution file path")
    parser.add_argument("--test-folders", default="tests/MyApp.Tests", help="Space-separated test project folder(s)")
    parser.add_argument("--main-component", default="web-api", help="Primary workload name for CD rollout verification")
    parser.add_argument("--target-dir", default=".", help="Root directory of the target repository (default: .)")
    parser.add_argument("--policy-ref", default="v2.0.0", help="Pinned policy repo ref for CD pipeline")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files (default: skip existing)")
    args = parser.parse_args()

    validate_k8s_name(args.project)
    td = guard_target_dir(args.target_dir)

    ns_dev = args.namespace_dev or f"{args.project}-dev"
    ns_test = args.namespace_test or f"{args.project}-test"
    ns_prod = args.namespace_prod or f"{args.project}-prod"

    base_replacements = {
        "@@PROJECT@@": args.project,
        "@@REGISTRY@@": args.registry,
        "@@TEAM@@": args.team,
        "@@TEAM_HANDLE@@": args.team_handle,
        "@@NAMESPACE_DEV@@": ns_dev,
        "@@NAMESPACE_TEST@@": ns_test,
        "@@NAMESPACE_PROD@@": ns_prod,
        "@@SOLUTION_PATH@@": args.solution_path,
        "@@TEST_FOLDERS@@": args.test_folders,
        "@@MAIN_COMPONENT@@": args.main_component,
        "@@POLICY_REF@@": args.policy_ref,
    }

    print("\n=== Initializing Emerald repo structure ===\n")

    write_file(
        os.path.join(td, ".github", "workflows", "ci.yml"),
        render(load_template("ci.tpl.yml"), base_replacements, "ci.tpl.yml"),
        args.overwrite,
    )
    write_file(
        os.path.join(td, ".github", "workflows", "cd.yml"),
        render(load_template("cd.tpl.yml"), base_replacements, "cd.tpl.yml"),
        args.overwrite,
    )
    write_file(
        os.path.join(td, ".github", "CODEOWNERS"),
        render(load_template("CODEOWNERS.tpl"), base_replacements, "CODEOWNERS.tpl"),
        args.overwrite,
    )
    write_file(
        os.path.join(td, "gitops", "Chart.yaml"),
        render(load_template("Chart.tpl.yaml"), base_replacements, "Chart.tpl.yaml"),
        args.overwrite,
    )
    write_file(
        os.path.join(td, "gitops", "values.yaml"),
        render(load_template("values.tpl.yaml"), base_replacements, "values.tpl.yaml"),
        args.overwrite,
    )

    for env in ("dev", "test", "prod"):
        env_replacements = {
            **base_replacements,
            "@@ENV@@": env,
            "@@ENV_LABEL@@": ENV_LABELS[env],
            "@@REPLICAS@@": ENV_REPLICAS[env],
            "@@ROUTE_ENABLED@@": ENV_ROUTE_ENABLED[env],
        }
        write_file(
            os.path.join(td, "gitops", f"values-{env}.yaml"),
            render(load_template("values-env.tpl.yaml"), env_replacements, "values-env.tpl.yaml"),
            args.overwrite,
        )

    write_file(
        os.path.join(td, "Makefile"),
        render(load_template("Makefile.tpl"), base_replacements, "Makefile.tpl"),
        args.overwrite,
    )
    append_gitignore(td, load_template("gitignore-additions.tpl"))
    write_file(
        os.path.join(td, "AGENTS.md"),
        render(load_template("AGENTS.md.tpl"), base_replacements, "AGENTS.md.tpl"),
        args.overwrite,
    )

    print("\n=== Done ===\n")
    print("Next steps:")
    print("  1. Run scripts/scaffold.py for each component to populate gitops/templates/")
    print("  2. Fill in component values in gitops/values.yaml and values-{dev,test,prod}.yaml")
    print("  3. Set GitHub environment secrets: OPENSHIFT_SERVER, OPENSHIFT_TOKEN (dev, test, prod)")
    print("  4. Run: helm dependency update ./gitops && python scripts/validate.py --chart-dir ./gitops\n")


if __name__ == "__main__":
    main()
