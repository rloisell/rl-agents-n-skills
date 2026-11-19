# GitHub Actions ISB EA Option 2

Manages GitHub Actions workflows for BC Government projects on the Emerald OpenShift platform.

## Contents

- [Architecture](#architecture-isb-ea-option-2)
- [Five-Workflow Pattern](#five-workflow-pattern)
- [Image Tag Strategy](#image-tag-strategy)
- [Artifactory Setup](#artifactory-setup)
- [Build Workflow Steps](#build-workflow-steps)
- [GitOps Image Tag Update (yq)](#gitops-image-tag-update-yq)
- [Secrets Required](#secrets-required)
- [Placeholder Substitution & Path Filters](#placeholder-substitution--path-filters)
- [Status Check Configuration & PR Review](#status-check-configuration--pr-review)
- [Trivy Scan](#trivy-scan)
- [Failure Patterns](#failure-patterns)
- [Sanitized CI/CD Knowledge](#sanitized-cicd-knowledge)

---

## Architecture: ISB EA Option 2

```text
GitHub (source) ──build──> Artifactory (images) ──gitops──> OpenShift (runtime)
                        ArgoCD (GitOps) polls a gitops-<license-plate> repo and applies Helm
```

Environments: `dev` → `test` → `prod`.
Promotion is controlled by updating the image tag in the GitOps Helm values YAML.

---

## Five-Workflow Pattern

| File | Trigger | Purpose |
|---|---|---|
| `pr-checks.yml` | `pull_request` | Lint, unit tests, Trivy scan |
| `build-dev.yml` | `push: branches: [develop]` | Build + push image → deploy dev |
| `build-test.yml` | `push: branches: [test]` | Build + push image → deploy test |
| `build-prod.yml` | `push: tags: v*` | Build + push image → deploy prod |
| `dependency-review.yml` | `pull_request` | OSSF dependency-review action |

---

## Image Tag Strategy

```text
<registry>/<org>/<project>/<service>:<tag>

Tags:
  PR:    pr-<number>-<sha7>      e.g. pr-42-abc1234
  Dev:   dev-<sha7>-<run>        e.g. dev-abc1234-87
  Test:  test-<sha7>-<run>       e.g. test-abc1234-87
  Prod:  <semver>                e.g. 1.2.3
```

---

## Artifactory Setup

1. Request an Artifactory service account via BC Gov DevExchange platform docs.
2. Store credentials as GitHub Actions secrets:
   - `ARTIFACTORY_URL` = `artifacts.developer.gov.bc.ca`
   - `ARTIFACTORY_SERVICE_ACCOUNT` = service account name
   - `ARTIFACTORY_SERVICE_ACCOUNT_TOKEN` = token

---

## Build Workflow Steps

```yaml
jobs:
  build:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4

      - name: Set image tag
        id: tag
        run: echo "tag=dev-${GITHUB_SHA::7}-${{ github.run_number }}" >> "$GITHUB_OUTPUT"

      - name: Login to Artifactory
        uses: docker/login-action@v3
        with:
          registry: ${{ secrets.ARTIFACTORY_URL }}
          username: ${{ secrets.ARTIFACTORY_SERVICE_ACCOUNT }}
          password: ${{ secrets.ARTIFACTORY_SERVICE_ACCOUNT_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          file: src/<project>/Containerfile
          push: true
          tags: ${{ secrets.ARTIFACTORY_URL }}/<org>/<project>/<service>:${{ steps.tag.outputs.tag }}

      - name: Trivy image scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ secrets.ARTIFACTORY_URL }}/<org>/<project>/<service>:${{ steps.tag.outputs.tag }}
          format: table
          exit-code: 1
          vuln-type: os,library
          severity: CRITICAL,HIGH
```

---

## GitOps Image Tag Update (`yq`)

After a successful build, update the GitOps Helm values file and push:

```yaml
      - name: Update GitOps image tag
        run: |
          git clone https://x-access-token:${{ secrets.GITOPS_TOKEN }}@github.com/<org>/gitops-<license-plate>.git gitops
          cd gitops
          yq -i '.image.tag = "${{ steps.tag.outputs.tag }}"' \
            environments/dev/<service>/values.yaml
          git config user.email "ci@<project>"
          git config user.name "GitHub Actions"
          git commit -am "ci: update <service> image tag to ${{ steps.tag.outputs.tag }}"
          git push
```

---

## Secrets Required

| Secret | Description |
|---|---|
| `ARTIFACTORY_URL` | Registry base URL |
| `ARTIFACTORY_SERVICE_ACCOUNT` | Robot account name |
| `ARTIFACTORY_SERVICE_ACCOUNT_TOKEN` | Robot account token |
| `GITOPS_TOKEN` | PAT — `repo` + `workflow` scopes only |
| `OC_SERVER` | OpenShift cluster API URL (optional for direct `oc` deploy) |
| `OC_TOKEN` | Service account token for direct `oc` (optional) |

---

## Placeholder Substitution & Path Filters

Replace all `<placeholder>` values when starting from a template:

```bash
grep -r "<" .github/workflows/ | grep -v ".git"
```

When workflows use `paths:` filters that do not match changed files, the workflow never triggers:

```bash
# Find all paths filters in workflows
grep -r "paths:" .github/workflows/

# Verify the actual paths that exist
find . -name "Containerfile" -not -path "./.git/*"
```

Align `paths:` filters with the real directory tree.

---

## Status Check Configuration & PR Review

**Branch protection must list the EXACT workflow job name.**

```bash
# List all job names across all workflows
grep -h "^  [a-z].*:$" .github/workflows/*.yml | sed 's/://g' | sort -u
```

In GitHub: Settings → Branches → Require status checks → paste each job name.

In `.github/workflows/pr-checks.yml`:

```yaml
      - name: Copilot code review
        uses: github/copilot-code-review@main
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

Only runs on pull requests — no `GITHUB_TOKEN` permissions needed beyond default.

---

## Trivy Scan

```yaml
      - name: Trivy scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: '<image>:<tag>'
          format: table
          exit-code: 1
          vuln-type: os,library
          severity: CRITICAL,HIGH
```

`CRITICAL`/`HIGH` findings fail the pipeline. Patch OS packages first (update base image), then review library versions.

---

## Packaging Database Migrations

Package database migrations (EF Core migration bundles, Flyway SQL scripts, or versioned SQL) into verified, immutable build artifacts or container images during CI—**never execute schema migrations directly from CI runners** against target environments.

- Exclude database credentials, connection strings, SQL dumps, and real/production data from migration artifacts.
- Run migrations inside the target OpenShift namespace via a controlled release hook (e.g., an ArgoCD `PreSync` Job or init/migration Job) using cluster-injected secrets.

---

## Failure Patterns

| Symptom | Cause | Fix |
|---|---|---|
| Workflow never triggers | `paths:` filter mismatch | Fix paths or remove filter |
| Artifactory auth denied | Token not in secrets | Add/rotate secret |
| Trivy CRITICAL found | Stale base image | Update base image tag in Containerfile |
| `yq` update silently no-ops | Wrong YAML key path | `yq '.'` to inspect actual key path |
| GitOps push rejected | Token lacks `Contents: write` | Add to PAT or use fine-grained PAT |
| Status check not required | Job name mismatch in branch protection | Run grep; update protection rule |

---

## Sanitized CI/CD Knowledge

- 2026-02-27: [ci-cd-engagement] Paths filter fix — workflows targeting wrong directories silently fail to trigger; verify `paths:` against actual `Containerfile` paths.
- 2026-02-27: [ci-cd-engagement] Status checks must use exact job ID strings from workflow YAML, not display names.
- 2026-02-28: `ag-helm` OCI chart at `oci://ghcr.io/<org>/helm` requires `helm registry login ghcr.io` before `helm dependency update` — add as a step before template render.
- 2026-02-28: Policy-as-code gate must run on the output of `helm template`; `conftest` requires `--all-namespaces --fail-on-warn`; `kube-linter` config path is `cd/policies/kube-linter.yaml`.
- 2026-02-28: Prod image reference should prefer `image.digest: sha256:...` over mutable tag — use `docker inspect --format='{{index .RepoDigests 0}}' <image>:<tag>` to obtain digest after build.
