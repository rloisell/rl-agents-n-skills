# Acceptance Criteria — Deploying BC Gov Workloads

Observable pass/fail criteria for verifying Containerfiles, ISB EA Option 2 GitHub Actions workflows, Emerald OpenShift manifests, zero-trust NetworkPolicies, and policy-as-code gates.

## 1. Containerfile & Image Standards

| Criterion | Pass Condition | Fail Condition |
|---|---|---|
| Non-root port `8080` | Containerfile exposes `8080`, runs as non-root (`USER appuser`), and defines a `HEALTHCHECK` (`/health/live` or `/nginx-health`) | Container listens on privileged port (`80`/`443`), runs as `root`, or omits `HEALTHCHECK` |
| Runtime frontend config | Frontend containers serve environment config via runtime `/config.json` rather than baking env vars at build time | Environment URLs or OIDC client IDs hardcoded into build-time bundle |
| Immutable image references | Non-dev deployments pin images by immutable tag or `sha256:` digest; zero hardcoded secrets | `:latest` tag used in prod/test manifests or secrets committed to Containerfile/values |

## 2. CI/CD (ISB EA Option 2)

- **Pass**: Five-workflow GitHub Actions pattern configured to build, Trivy-scan, push to Artifactory, and update the GitOps Helm image tag via `yq` without manual cluster credentials in feature branches.
- **Fail**: Pipeline pushes `:latest`, skips Trivy vulnerability scanning, or applies manifests directly with `oc apply` bypassing GitOps.

## 3. Emerald Platform Manifests & NetworkPolicies

| Criterion | Pass Condition | Fail Condition |
|---|---|---|
| OpenShift SCC mode | `global.openshift: true` set in Helm `values.yaml`; `runAsUser` and `runAsGroup` omitted | Fixed numeric `runAsUser`/`runAsGroup` breaks restricted-v2 SCC |
| AVI & DataClass alignment | Every Route has `aviinfrasetting.ako.vmware.com/name` (`dataclass-medium` default, never `dataclass-low`) matching pod `DataClass: Medium` | Route uses `dataclass-low`, omits AVI annotation, or mismatches pod `DataClass` |
| Required pod metadata | Every Deployment/StatefulSet defines `DataClass`, `owner`, `environment` (`production\|test\|development`), and `priorityClassName` | Any required label or `priorityClassName` missing |
| Zero-trust NetworkPolicy | Explicit allow rules via `ag-template.networkpolicy` or explicit `podSelector`/`namespaceSelector` + `ports` | Empty `podSelector: {}` peers or missing `ports` in Ingress/Egress rules |

## 4. Policy-as-Code Gate & Rollout Verification

- **Pass**: Single `rendered.yaml` generated via `helm template` passes all four checks with exit code `0`:
  1. `datree test rendered.yaml --policy-config cd/policies/datree-policies.yaml`
  2. `polaris audit --config cd/policies/polaris.yaml --format pretty rendered.yaml`
  3. `kube-linter lint rendered.yaml --config cd/policies/kube-linter.yaml`
  4. `conftest test rendered.yaml --policy cd/policies --all-namespaces --fail-on-warn`
- **Pass**: `oc rollout status deployment/<name> -n <ns-prefix>-<env>` completes with all pods `Ready`.
- **Fail**: Any of the four policy-as-code tools reports an error/warning failure, or pods fail readiness/liveness probes after rollout.
