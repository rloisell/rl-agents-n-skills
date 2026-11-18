---
name: deploying-bc-gov-workloads
description: >-
  Deploys containerized applications to the BC Government Emerald OpenShift platform
  using standardized Containerfiles, GitHub Actions ISB EA Option 2 CI/CD pipelines,
  ag-helm charts, policy-as-code gates, and NetworkPolicies. Use when building
  images, configuring CI/CD workflows, authoring Helm charts or Routes, or
  troubleshooting deployments on Emerald OpenShift.
---

# Deploying BC Gov Workloads

End-to-end deployment workflow for BC Government Emerald OpenShift workloads, from container build through GitOps delivery.

## Contents

- [Constraints](#constraints) • [Quick start](#quick-start) • [Platform Reference](#platform-reference) • [Workflow](#workflow) • [Verification](#verification) • [References](#references)

## Constraints

1. **Container port 8080**: All application containers expose port `8080` as non-root (`USER appuser`); OpenShift Routes and AVI handle external TLS.
2. **OpenShift SCC mode**: Set `global.openshift: true` in Helm `values.yaml` and omit `runAsUser`/`runAsGroup` so OpenShift SCC assigns runtime UID/GID.
3. **AVI and DataClass alignment**: Every Route requires `aviinfrasetting.ako.vmware.com/name` (`dataclass-medium` default, never `dataclass-low`), matching the pod `DataClass` label (`Medium`).
4. **Required pod labels and PriorityClass**: Every Deployment/StatefulSet requires `DataClass`, `owner`, `environment` (`production|test|development`), and `priorityClassName`.
5. **Policy-as-code gate**: Render Helm to a single `rendered.yaml` and pass Datree, Polaris, kube-linter, and Conftest before deploying to any environment.
6. **Zero-trust NetworkPolicies**: Emerald default-denies both Ingress and Egress; use `ag-template.networkpolicy` or explicit allow rules (no empty `podSelector: {}` peers or missing `ports`).
7. **No hardcoded secrets or floating tags**: Store secrets in OpenShift Secrets; pin images by immutable tag or `sha256:` digest.

## Quick start

1. Expose port `8080` as non-root `appuser` in your Containerfile (see [Containerfile.dotnet](assets/templates/Containerfile.dotnet) / [Containerfile.react](assets/templates/Containerfile.react)).
2. Set `global.openshift: true`, `DataClass: Medium`, `owner`, `environment`, and `priorityClassName` in Helm values.
3. Render `rendered.yaml` with `helm template` and pass the policy-as-code gate before deploying to `<ns-prefix>-dev`.

## Platform Reference

| Cluster | API URL | OIDC Issuer |
|---|---|---|
| Gold | `https://api.gold.devops.gov.bc.ca:6443` | `https://loginproxy.gov.bc.ca/auth/realms/standard` |
| Gold DR | `https://api.golddr.devops.gov.bc.ca:6443` | `https://loginproxy.gov.bc.ca/auth/realms/standard` |
| Silver | `https://api.silver.devops.gov.bc.ca:6443` | `https://loginproxy.gov.bc.ca/auth/realms/standard` |

Namespace pattern: `<ns-prefix>-<env>` (`dev`, `test`, `prod`, `tools`).

## Workflow

1. **Standardize Containerfiles**: Expose port `8080`, add `HEALTHCHECK` (`/health/live` or `/nginx-health`), run as non-root `appuser`, and serve frontend config via runtime `/config.json` ([containerfile-standards.md](references/containerfile-standards.md)).
2. **Configure CI/CD (ISB EA Option 2)**: Set up the five-workflow GitHub Actions pattern to build, Trivy-scan, push to Artifactory, and update the GitOps Helm image tag via `yq` ([github-actions-option2.md](references/github-actions-option2.md)).
3. **Configure Emerald platform manifests**: Apply AVI Route annotations, `DataClass`/`owner`/`environment` pod labels, `Internet-Ingress: DENY`, `PriorityClass`, `StorageClass`, probes, and SSO OIDC settings ([emerald-platform-mechanics.md](references/emerald-platform-mechanics.md)).
4. **Author Helm chart & NetworkPolicies**: Consume `ag-helm-templates` or standard Helm templates, define intent-based NetworkPolicies ([networkpolicy-patterns.md](references/networkpolicy-patterns.md)), and configure ArgoCD Application CRDs ([ag-helm-and-policy-gate.md](references/ag-helm-and-policy-gate.md)).
5. **Run policy-as-code gate**: Execute `helm template` followed by Datree, Polaris, kube-linter, and Conftest before merging or syncing.

## Verification

Run the policy-as-code gate against rendered manifests and verify rollout in the target namespace:

```bash
helm template myapp ./charts/<app> --values ./deploy/dev_values.yaml --debug > rendered.yaml
datree test rendered.yaml --policy-config cd/policies/datree-policies.yaml
polaris audit --config cd/policies/polaris.yaml --format pretty rendered.yaml
kube-linter lint rendered.yaml --config cd/policies/kube-linter.yaml
conftest test rendered.yaml --policy cd/policies --all-namespaces --fail-on-warn
oc rollout status deployment/<name> -n <ns-prefix>-dev
```

## References

- [containerfile-standards.md](references/containerfile-standards.md) — Port 8080, .NET API & React/Vite Containerfiles, runtime `/config.json`
- [github-actions-option2.md](references/github-actions-option2.md) — Five-workflow pattern, Artifactory, Trivy, `yq` GitOps updates, triage
- [emerald-platform-mechanics.md](references/emerald-platform-mechanics.md) — AVI InfraSettings, DataClass, SCC, StorageClass, SSO, `oc` reference
- [ag-helm-and-policy-gate.md](references/ag-helm-and-policy-gate.md) — `ag-helm-templates`, Datree/Polaris/kube-linter/Conftest gate, ArgoCD CRD
- [networkpolicy-patterns.md](references/networkpolicy-patterns.md) — Intent-based `ag-template.networkpolicy` and raw NetworkPolicy YAML
- Templates: [Containerfile.dotnet](assets/templates/Containerfile.dotnet) • [Containerfile.react](assets/templates/Containerfile.react)
