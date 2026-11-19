# SAST, Semantic Release, and Container Build/Scan CI

Reusable GitHub Actions patterns for static analysis, secrets scanning, semantic
releases, and Docker-in-Docker (DinD) container builds with Trivy vulnerability
scanning.

## Contents

- [Gitleaks and SonarQube SAST](#gitleaks-and-sonarqube-sast)
- [Fail-closed CI checks and test tiers](#fail-closed-ci-checks-and-test-tiers)
- [Semantic release with Release Please](#semantic-release-with-release-please)
- [DinD, Buildx, and Trivy container scanning](#dind-buildx-and-trivy-container-scanning)

## Gitleaks and SonarQube SAST

Run secrets detection and static code analysis in a composite action or job after
the test job uploads its Cobertura coverage artifact:

1. Check out with `fetch-depth: 0` so Gitleaks and SonarQube have full git history.
2. Run `gitleaks/gitleaks-action@v2` on `push` (branch refs) and `pull_request`
   events with `GITHUB_TOKEN` and `GITLEAKS_LICENSE`.
3. Download the `test-results` artifact produced by the test job into
   `TestResults/coverage`.
4. Run `SonarSource/sonarqube-scan-action@v5.3.0` passing `SONAR_TOKEN`,
   `SONAR_HOST_URL` (e.g., `https://<sonarqube-host>.apps.<cluster>.devops.gov.bc.ca/`),
   and Cobertura report path arguments.

```yaml
steps:
  - name: Checkout repository
    uses: actions/checkout@v4
    with:
      fetch-depth: 0

  - name: Run Gitleaks
    if: github.event_name == 'push' && startsWith(github.ref, 'refs/heads/') || github.event_name == 'pull_request'
    uses: gitleaks/gitleaks-action@v2
    env:
      GITHUB_TOKEN: ${{ inputs.github_token }}
      GITLEAKS_LICENSE: ${{ inputs.gitleaks_license }}

  - name: Download coverage report
    uses: actions/download-artifact@v4
    with:
      name: test-results
      path: TestResults/coverage

  - name: Run SonarQube Scan
    if: github.event_name == 'push' && startsWith(github.ref, 'refs/heads/') || github.event_name == 'pull_request'
    uses: SonarSource/sonarqube-scan-action@v5.3.0
    env:
      SONAR_TOKEN: ${{ inputs.sonar-token }}
      SONAR_HOST_URL: ${{ inputs.sonar-host-url }} # e.g. https://<sonarqube-host>.apps.<cluster>.devops.gov.bc.ca/
    with:
      args: >
        -Dsonar.projectKey=${{ inputs.project-key }}
        -Dsonar.sources=${{ inputs.sources }}
        -Dsonar.cs.vscoveragexml.reportsPaths=TestResults/coverage/coverage.cobertura.xml
        -Dsonar.qualitygate.wait=true
        -Dsonar.qualitygate.timeout=300
```

### SonarQube hardening rules

- **`projectVersion` resolution**: resolve `sonar.projectVersion` from build or package metadata (`version.txt`, `apm.yml`, `.csproj`/`AssemblyInfo.cs`, `pom.xml`/`gradle.properties`, or explicit `composer.json` `version`). Never pass literal `${...}`, `unspecified`, or per-build counters (which break Sonar's new-code baselines); omit `sonar.projectVersion` if no non-empty version can be verified.
- **`.gitignore` to `sonar.exclusions`**: read `.gitignore` and translate patterns to `sonar.exclusions` **only** when a pattern matches at least one file or directory present in the repository. Do not import unmatched generic `.gitignore` entries.
- **MSBuild multi-solution disambiguation**: when multiple `.slnx`, `.sln`, or project files exist, pass an explicit `solutionFile` target to SonarScanner for .NET; `testsDir` is ignored by the MSBuild workflow.
- **Quality-gate enforcement**: a successful scan upload is not a passed gate. Set `sonar.qualitygate.wait=true` with a bounded `sonar.qualitygate.timeout` (or a verified pinned quality-gate action) so failed or timed-out gates block the job.
- **Fork PR & cache-poisoning isolation**: use `pull_request` for untrusted contributions—never check out untrusted PR head code under `pull_request_target` or a privileged `workflow_run`. Never inject `SONAR_TOKEN` or internal SonarQube endpoints into untrusted fork builds, and scope caches with manifest-derived keys so untrusted PRs cannot poison caches consumed by privileged jobs.

## Fail-closed CI checks and test tiers

- **Fail closed on missing evidence**: fail the job on any missing expected report (test results, Cobertura/LCOV/Clover coverage, SARIF, or Trivy output) or when an expected test suite executes zero tests. Never treat missing reports as a success-shaped warning.
- **Workflow linting**: validate modified workflow files with `actionlint` before merging.
- **PR fast-iterations vs nightly deep-iterations**: run fast unit, lint, and targeted integration checks on every PR; schedule heavy integration suites, property-based/exhaustive runs, and full container/OS scans on nightly or pre-release workflows when they exceed PR feedback budgets.

## Semantic release with Release Please

Automate version bumps, `CHANGELOG.md` updates, and GitHub Releases from
conventional commits using `googleapis/release-please-action@v4`:

```yaml
steps:
  - name: Run Release Please
    id: release
    if: github.event_name == 'push' && startsWith(github.ref, 'refs/heads/') || github.event_name == 'pull_request'
    uses: googleapis/release-please-action@v4
    with:
      token: ${{ inputs.token }}
      release-type: ${{ inputs.release-type }} # e.g., simple, node, dotnet
      target-branch: ${{ inputs.target-branch }} # default: main
```

- Requires conventional commit messages (`feat:`, `fix:`, `feat!:`) on `main` to
  compute semver increments.
- Opens or updates a Release PR; merging that PR creates the GitHub Release and
  git tag.

### Approval-gated two-stage release hardening

For higher-assurance or artifact-producing releases alongside Release Please:

1. **Protected `release` environment**: gate tag creation and release publication behind a GitHub `release` environment with required maintainer reviewers.
2. **Rebuild from immutable SHA**: check out the exact validated `main` commit SHA in the protected job and rebuild the archive and checksum from source. Never trust uploaded workflow artifacts as the release source (compare against the rebuild only after verifying SHA-256 and source SHA).
3. **Annotated tag & checksum asset**: create or verify an annotated `v<version>` tag (fail closed if already present; never move tags implicitly), publish with `gh release create --verify-tag`, and attach a `.sha256` checksum asset alongside the release archive.
4. **Minimal credential persistence**: set `persist-credentials: false` on `actions/checkout` and pass a scoped token only to the tag/release step.
5. **Public-safe release-notes sanitization**: review release notes against the complete diff before publishing—strip internal URLs, credentials, environment-specific paths, private repository names, and raw commit-subject dumps; keep HTTP(S) configuration URLs in linked repository docs.

## DinD, Buildx, and Trivy container scanning

When building and scanning OCI images on GitHub-hosted runners using an isolated
Docker-in-Docker daemon:

1. **Start `docker:dind`**: launch `docker:28.3.3-dind` (pinned version) with
   `DOCKER_TLS_CERTDIR=` on `tcp://127.0.0.1:2375` and poll `docker version`
   until ready.
2. **Authenticate & configure Buildx**: log in to an explicit registry or default
   `ghcr.io` via `docker/login-action@v3`, then run
   `docker/setup-buildx-action@v3` and `docker/setup-qemu-action@v3`.
3. **Auto-tag**: on `release` events, tag with `release.tag_name`; on branch/PR
   builds, compose `latest`, `<branch>.build<run_number>`, and
   `<branch>.<short_sha>`.
4. **Build & push**: use `docker/build-push-action@v6` with GHA build cache
   (`cache-from: type=gha`, `cache-to: type=gha,mode=max`).
5. **Trivy scan & reporting**:
   - Set `DOCKER_HOST: ""` on the Trivy step so it does not conflict with the
     DinD TCP socket.
   - Fail the build on `CRITICAL,HIGH` (`exit-code: "1"`, `ignore-unfixed: "true"`).
   - Write table output to `trivy-results.txt`, upload it as the
     `trivy-sbom-report` artifact (`retention-days: 20`), and append the first 50
     lines to `$GITHUB_STEP_SUMMARY`.

```yaml
- name: Trivy vulnerability scan
  uses: aquasecurity/trivy-action@0.24.0
  env:
    DOCKER_HOST: ""
  with:
    image-ref: ${{ steps.compose.outputs.first_tag }}
    severity: "CRITICAL,HIGH"
    ignore-unfixed: "true"
    format: "table"
    output: "trivy-results.txt"
    exit-code: "1"
    github-pat: ${{ github.token }}

- name: Upload Trivy report as GitHub artifact
  if: ${{ success() }}
  uses: actions/upload-artifact@v4
  with:
    name: trivy-sbom-report
    path: trivy-results.txt
    retention-days: 20

- name: Add Trivy Scan Summary
  if: ${{ success() }}
  shell: bash
  run: |
    echo "🔎 Image Scan Summary" >> "$GITHUB_STEP_SUMMARY"
    echo "" >> "$GITHUB_STEP_SUMMARY"
    head -n 50 trivy-results.txt >> "$GITHUB_STEP_SUMMARY"
    echo "" >> "$GITHUB_STEP_SUMMARY"
    echo "_Full results available in uploaded artifact (trivy-sbom-report)_" >> "$GITHUB_STEP_SUMMARY"
```
