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
2. Bootstrap a new Emerald repo with [init.py](scripts/init.py) or scaffold individual Helm/CI resources from [assets/templates/](assets/templates/) using `scripts/scaffold.py`:
   ```bash
   python scripts/init.py --project my-app --registry ghcr.io/<org>
   python scripts/scaffold.py --type deployment --name web-api --port 8080
   python scripts/scaffold.py --type networkpolicy --name web-api --ingress-from-router --egress-to-apps postgresql:5432
   ```
3. Validate rendered manifests against [assets/policies/](assets/policies/) with `scripts/validate.py` before deploying to `<ns-prefix>-dev`.

## Platform Reference

| Cluster | API URL | OIDC Issuer |
|---|---|---|
| Emerald | `https://api.emerald.devops.gov.bc.ca:6443` (SPAN-BC) | `https://loginproxy.gov.bc.ca/auth/realms/standard` |
| Gold | `https://api.gold.devops.gov.bc.ca:6443` | `https://loginproxy.gov.bc.ca/auth/realms/standard` |
| Gold DR | `https://api.golddr.devops.gov.bc.ca:6443` | `https://loginproxy.gov.bc.ca/auth/realms/standard` |
| Silver | `https://api.silver.devops.gov.bc.ca:6443` | `https://loginproxy.gov.bc.ca/auth/realms/standard` |

Namespace pattern: `<ns-prefix>-<env>` (`dev`, `test`, `prod`, `tools`).

## Workflow

1. **Standardize Containerfiles**: Expose port `8080`, add `HEALTHCHECK` (`/health/live` or `/nginx-health`), run as non-root `appuser`, and serve frontend config via runtime `/config.json` ([containerfile-standards.md](references/containerfile-standards.md)).
2. **Configure CI/CD (ISB EA Option 2)**: Set up the five-workflow GitHub Actions pattern or scaffold from [assets/templates/](assets/templates/) ([github-actions-option2.md](references/github-actions-option2.md)).
3. **Configure Emerald platform manifests**: Apply AVI Route annotations, `DataClass`/`owner`/`environment` pod labels, `Internet-Ingress: DENY`, `PriorityClass`, `StorageClass`, probes, and SSO OIDC settings ([emerald-platform-mechanics.md](references/emerald-platform-mechanics.md)).
4. **Author Helm chart & NetworkPolicies**: Scaffold with [scaffold.py](scripts/scaffold.py), use the `$p` dict API ([ag-helm-api-and-shapes.md](references/ag-helm-api-and-shapes.md)), and define intent-based NetworkPolicies ([networkpolicy-patterns.md](references/networkpolicy-patterns.md)).
5. **Run policy-as-code gate**: Execute [validate.py](scripts/validate.py) against [assets/policies/](assets/policies/) and remediate failures with [policy-remediation-matrix.md](references/policy-remediation-matrix.md).

## Verification

Run the four-tool policy-as-code gate plus BC Gov platform rules (`check_platform_rules.py`, integrated as `--tool platform-rules`) and verify rollout in the target namespace:

```bash
python scripts/validate.py --chart-dir ./charts/<app> --values ./deploy/values.yaml --values ./deploy/dev_values.yaml
oc rollout status deployment/<name> -n <ns-prefix>-dev
```

## References

- [ag-helm-api-and-shapes.md](references/ag-helm-api-and-shapes.md) — `$p` dict API, fragment hook shapes, router ingress selector
- [policy-remediation-matrix.md](references/policy-remediation-matrix.md) — Datree, Polaris, kube-linter, and Conftest failure-to-fix table
- [containerfile-standards.md](references/containerfile-standards.md) — Port 8080, .NET API & React/Vite Containerfiles, runtime `/config.json`
- [github-actions-option2.md](references/github-actions-option2.md) — Five-workflow pattern, Artifactory, Trivy, `yq` GitOps updates, triage
- [artifactory-argocd-gitops.md](references/artifactory-argocd-gitops.md) — Two-repo GitOps, umbrella charts, release-tag vs. retag promotion, Apicurio, ArgoCD gating
- [emerald-platform-mechanics.md](references/emerald-platform-mechanics.md) — AVI InfraSettings, DataClass, SCC, StorageClass, SSO, `oc` reference
- [ag-helm-and-policy-gate.md](references/ag-helm-and-policy-gate.md) — `ag-helm-templates`, four-tool gate, ArgoCD CRD
- [networkpolicy-patterns.md](references/networkpolicy-patterns.md) — Intent-based `ag-template.networkpolicy` and raw NetworkPolicy YAML
- [Acceptance Criteria](references/acceptance-criteria.md) — Observable pass/fail criteria across all layers
- Scripts & Assets: [init.py](scripts/init.py) • [scaffold.py](scripts/scaffold.py) • [validate.py](scripts/validate.py) • [check_platform_rules.py](scripts/check_platform_rules.py) • [assets/policies/](assets/policies/) • [argocd-application.tpl.yaml](assets/templates/argocd-application.tpl.yaml) • [promote-retag.tpl.yml](assets/templates/promote-retag.tpl.yml) • [assets/templates/](assets/templates/)
