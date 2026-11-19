# `ag-helm` and Policy-as-Code Gate

Helm chart structure, `ag-helm-templates` OCI library usage, four-tool policy-as-code gate, and ArgoCD GitOps Application CRD.

## Contents

- [`ag-helm` Helm Library Chart](#ag-helm-helm-library-chart)
- [Helm Chart Requirements](#helm-chart-requirements)
- [Policy-as-Code Gate](#policy-as-code-gate)
- [Internet Egress Approval Annotations](#internet-egress-approval-annotations)
- [ArgoCD Application CRD](#argocd-application-crd)
- [Deployment Checklist](#deployment-checklist)
- [Sanitized Platform Knowledge](#sanitized-platform-knowledge)

---

## `ag-helm` Helm Library Chart

`ag-helm-templates` is a shared Helm library consumed via OCI in `Chart.yaml`:

```yaml
# gitops-repo/charts/<app>/Chart.yaml
dependencies:
  - name: ag-helm-templates
    version: "<released-version>"
    repository: "oci://ghcr.io/<org>/helm"
```

If the registry requires auth:

```bash
echo $GITHUB_TOKEN | helm registry login ghcr.io -u <github-user> --password-stdin
helm dependency update ./charts/<app>
```

### Templates provided by `ag-helm`

| Template | Description |
|---|---|
| `ag-template.deployment` | Deployment with OpenShift SCC awareness |
| `ag-template.statefulset` | StatefulSet |
| `ag-template.job` | Job with TTL |
| `ag-template.service` | Service |
| `ag-template.serviceaccount` | ServiceAccount |
| `ag-template.route.openshift` | OpenShift Route with AVI annotation enforcement |
| `ag-template.networkpolicy` | Intent-based NetworkPolicy (recommended) |
| `ag-template.hpa` | HPA (`autoscaling/v2`) |
| `ag-template.pdb` | PodDisruptionBudget |
| `ag-template.pvc` | PersistentVolumeClaim |

### Required `values.yaml` root keys

```yaml
global:
  openshift: true    # enables OpenShift SCC mode — do NOT omit on Emerald

project: <app-name>  # becomes ApplicationGroup label prefix
registry: artifacts.developer.gov.bc.ca
```

When NOT using `ag-helm`, manually include `global.openshift: true` in `values.yaml` and omit `runAsUser`/`runAsGroup` from pod `securityContext`.

---

## Helm Chart Requirements

Every service needs a Helm chart in `charts/<service>/`:

```text
charts/<service>/
  Chart.yaml
  values.yaml              ← per-service defaults
  values-dev.yaml          ← dev environment overrides
  values-test.yaml
  values-prod.yaml
  templates/
    deployment.yaml
    service.yaml
    route.yaml
    networkpolicy.yaml     ← required; see networkpolicy-patterns.md
    _helpers.tpl
```

Minimum `Chart.yaml`:

```yaml
apiVersion: v2
name: <service>
description: <description>
type: application
version: 0.1.0
appVersion: "1.0.0"
```

---

## Policy-as-Code Gate

Before deploying to **any** environment, render Helm output into a single YAML file and pass all four tools. Failing any tool blocks the pipeline.

```bash
# 1. Render Helm to a single YAML file (cross-resource checks need all resources together)
helm template myapp ./charts/<app> --values ./deploy/dev_values.yaml --debug > rendered.yaml

# 2. Run all four policy checks — all must pass before deploy
datree test rendered.yaml --policy-config cd/policies/datree-policies.yaml
polaris audit --config cd/policies/polaris.yaml --format pretty rendered.yaml
kube-linter lint rendered.yaml --config cd/policies/kube-linter.yaml
conftest test rendered.yaml --policy cd/policies --all-namespaces --fail-on-warn
```

### GitHub Actions Step

```yaml
      - name: Render Helm templates
        run: |
          helm dependency update ./charts/${{ env.APP_NAME }}
          helm template ${{ env.APP_NAME }} ./charts/${{ env.APP_NAME }} \
            --values ./deploy/${{ env.ENVIRONMENT }}_values.yaml \
            --debug > rendered.yaml

      - name: Policy-as-code gate
        run: |
          datree test rendered.yaml --policy-config cd/policies/datree-policies.yaml
          polaris audit --config cd/policies/polaris.yaml --format pretty rendered.yaml
          kube-linter lint rendered.yaml --config cd/policies/kube-linter.yaml
          conftest test rendered.yaml --policy cd/policies --all-namespaces --fail-on-warn
```

### What each tool checks

| Tool | Key checks relevant to Emerald workloads |
|---|---|
| **Datree** | `DataClass` label present (`Low\|Medium\|High`); `owner` label required; `environment` label (`production\|test\|development`); Route has `aviinfrasetting.ako.vmware.com/name`; image tag required; resource requests/limits required; probes required; `imagePullPolicy: Always` |
| **Polaris** | `hostIPC/PID/Network: false`; `allowPrivilegeEscalation: false`; `runAsNonRoot: true`; `readOnlyRootFilesystem: true`; no secrets in env vars or ConfigMaps; `missingNetworkPolicy`; `deploymentMissingReplicas`; `priorityClassNotSet`; `dataClassLabelRequired`; `routeAviAnnotationRequired` |
| **kube-linter** | `run-as-non-root`; `privilege-escalation-container`; `default-service-account`; `latest-tag`; `env-var-secret`; selector mismatches; PDB min/max |
| **Conftest (OPA/Rego)** | Hard-deny: Deployment without matching NetworkPolicy; Deployment without `DataClass`; NP without `policyTypes`; NP empty `podSelector: {}`; allow-all ingress/egress (`- {}`); missing `from/to`; missing `ports`; internet egress without `justification` + `approvedBy` annotations; edge-terminated Route without `app.kubernetes.io/component=frontend` label or `isb.gov.bc.ca/edge-termination-approval` annotation |

---

## Internet Egress Approval Annotations

If a NetworkPolicy has egress to `0.0.0.0/0` or `::/0`, Conftest **denies** it unless both annotations are present:

```yaml
metadata:
  annotations:
    justification: "Why this service requires internet-wide egress"
    approvedBy: "Ticket reference or approver name"
```

Prefer specific CIDRs (`ipBlock.cidr`) over internet-wide egress — specific CIDRs do not require these annotations.

---

## ArgoCD Application CRD

With **Apps in Any Namespace** enabled on the shared Argo CD instances, place `Application` manifests in `<license-plate>-tools` (or any namespace in your `<license-plate>-{dev,test,prod,tools}` project set) and set `spec.project` to your `<license-plate>` (never `openshift-gitops` / `default`):

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: <service>-<env>
  namespace: <license-plate>-tools
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: <license-plate>
  source:
    repoURL: https://github.com/bcgov-c/tenant-gitops-<license-plate>.git
    targetRevision: HEAD
    path: environments/<env>/<service>
    helm:
      valueFiles:
        - values.yaml
        - values-<env>.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: <license-plate>-<env>
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=false
```

---

## Deployment Checklist

- [ ] Containerfile at `src/<service>/Containerfile` exposes port `8080` and runs as non-root `appuser`
- [ ] Health probes configured (`/health/live`, `/health/ready`)
- [ ] AVI InfraSettings annotation on every Route (`aviinfrasetting.ako.vmware.com/name`)
- [ ] Pod labels: `DataClass`, `owner`, `environment` on every Deployment/StatefulSet
- [ ] `Internet-Ingress: DENY` label on all internal workloads
- [ ] PriorityClass defined and referenced in every Deployment/StatefulSet
- [ ] NetworkPolicy: intent-based via `ag-template.networkpolicy` — no allow-all shapes
- [ ] Policy-as-code gate passes: Datree + Polaris + kube-linter + Conftest (`rendered.yaml`)
- [ ] Image pinned by tag or digest (no floating `latest`) and `imagePullPolicy: Always`
- [ ] Artifactory secrets in namespace; ArgoCD Application CRD syncing

---

## Sanitized Platform Knowledge

- 2026-04-16: Conftest hard-denies Deployments without a matching NetworkPolicy — render all resources into one YAML file so cross-resource checks work.
- 2026-04-16: Required pod labels are `DataClass` + `owner` + `environment` (all three enforced by Datree/Conftest). `owner` = team name or ticket; `environment` = `production|test|development`.
- 2026-04-16: Polaris `priorityClassNotSet` check requires every Deployment/StatefulSet to set `spec.template.spec.priorityClassName`.
- 2026-04-16: Edge-terminated Routes need label `app.kubernetes.io/component=frontend` OR annotation `isb.gov.bc.ca/edge-termination-approval` — else Conftest denies.
- 2026-04-16: Internet-wide egress (`0.0.0.0/0`) in NetworkPolicy requires `justification` + `approvedBy` annotations or Conftest denies. Prefer specific CIDRs.
