# Migration Gaps (G1–G12) & Network Flow Mapping

Gap analysis framework, G1–G12 evaluation matrix, network flow mapping, task numbering, and AI-assist indicators for OpenShift platform migrations.

## Contents

- [Cross-Skill Interpretation Matrix](#cross-skill-interpretation-matrix)
- [Critical Gap Categories (G1–G12)](#critical-gap-categories-g1g12)
- [Platform Policy & Legacy Tooling Checks](#platform-policy--legacy-tooling-checks)
- [Network Flow Mapping](#network-flow-mapping)
- [Task Numbering & AI Assist Indicators](#task-numbering--ai-assist-indicators)
- [Sanitized Migration Knowledge](#sanitized-migration-knowledge)

---

## Cross-Skill Interpretation Matrix

Apply these domain lenses when interpreting collected manifests and repo artifacts:

| Area | Domain / Skill | Key checks |
|---|---|---|
| Platform requirements | `deploying-bc-gov-workloads` | AVI InfraSettings, `DataClass`/`owner`/`environment` labels, `StorageClass`, `PriorityClass`, edge Route |
| NetworkPolicy | `deploying-bc-gov-workloads` | Default-deny egress, DNS policy, CIDR-based external flows, `ag-template` intent API |
| CI/CD and Helm | `deploying-bc-gov-workloads` | Policy-as-code gate, `ag-helm-templates`, Artifactory, ArgoCD, deployment checklist |
| Secrets | `vault-secrets` | Vault + ESO `ExternalSecret`, no plain Secrets for sensitive values |
| Observability | `observability` | Structured logging, health probes, Prometheus annotations, OpenTelemetry |
| Security | `security-architect` | Pod security contexts, OWASP, image CVE scanning, action SHA pinning |
| SDN / Zone flows | `bc-gov-sdn-zones` | Zone A/B/C egress constraints, CSBC FWCR requirements, MCCS |

---

## Critical Gap Categories (G1–G12)

Every gap maps to one or more standards in [standards-catalog.md](standards-catalog.md).

| # | Category | Source indicator | Gap test | Standard / Source |
|---|---|---|---|---|
| G1 | No egress NetworkPolicies | `networkpolicies.yaml` has no egress rules | Emerald default-denies all egress | PS-01 |
| G2 | DeploymentConfig used | `workloads.yaml` has `kind: DeploymentConfig` | DC deprecated in OCP 4.14+; must convert | OCP-01 |
| G3 | No Helm charts | No `Chart.yaml` in repo | `ag-helm-templates` required on Emerald | AD-01 |
| G4 | Internal image registry / ImageStreams | `image-refs.txt` shows `image-registry.openshift-image-registry.svc` or `build-objects.yaml` has cluster-local `ImageStream`s | Must migrate images to Artifactory | ISB-03; PS-03 |
| G5 | No health probes | No `livenessProbe`/`readinessProbe` in workload YAML | Required on Emerald for proper rollout | K8S-01; PS-04 |
| G6 | Plain Secrets | `secret-names.txt` shows non-system secrets | Must migrate to Vault + ESO | ISB-01 |
| G7 | Missing pod labels | No `DataClass`/`owner`/`environment` in pod templates | Datree/Conftest enforced on Emerald | AD-02 |
| G8 | Wrong StorageClass | `pvcs.yaml` shows `netapp-file-standard` for database PVCs | Should be `netapp-block-standard` | PS-02 |
| G9 | No PriorityClass | No `kind: PriorityClass` in repo | Polaris `priorityClassNotSet` check | AD-04 |
| G10 | Legacy Jenkins or third-party CI workflows | `tools` namespace runs Jenkins or workflow imports vendor reusable workflows | Replace with first-party GitOps (GitHub Actions + ArgoCD) | ISB-02 |
| G11 | No policy-as-code gate | No Datree/Polaris/kube-linter/Conftest in CI | Required by `ag-devops` standard | AD-03 |
| G12 | Image tag not pinned | `latest` or mutable tag in image refs | Use digest pinning in prod | SEC-01; SEC-02 |

---

## Platform Policy & Legacy Tooling Checks

Evaluate these additional platform-enforced and legacy-tooling checks from `workloads.yaml`, `build-objects.yaml`, and `prometheus-rules.yaml`:

- **CronJob Schedule & Timezone Policy (`PS-06`, Kyverno `validate-cron-schedule`)**:
  - Flag CronJobs scheduled faster than every **5 minutes** (`<5m`) — blocked by `no-fast-cronjob`.
  - Flag CronJobs with a **PVC mounted** scheduled faster than every **hour** (`<1h`) — blocked to reduce API and storage mount/unmount load; convert to an always-running `Deployment` with `go-crond --allow-unprivileged`.
  - Flag `CRON_TZ=` in `spec.schedule` — blocked by `no-unsupported-timezone`; use `spec.timeZone` instead.
- **Deprecated Jenkins Pipelines (`ISB-02`)**:
  - Flag Jenkins `Deployment` / `DeploymentConfig` instances in `tools` namespaces. Platform Services recommends migrating to GitHub Actions, ArgoCD, or OpenShift Pipelines; if temporarily retained, tune resources (`requests.cpu: 100m`, no `limits.cpu`, `requests.memory: 512Mi`).
- **Cluster-Local ImageStreams (`ISB-03`, `PS-03`)**:
  - Flag `BuildConfig` / `ImageStream` objects in `build-objects.yaml` and `image-registry.openshift-image-registry.svc` or `:latest` references. Migrate builds to GitHub Actions pushing immutable tags/`sha256` digests to Artifactory.
- **AlertManager & `PrometheusRule` (`PS-08`)**:
  - Carry over custom `PrometheusRule` objects from `prometheus-rules.yaml`; never modify `platform-services-controlled-alert-rules` or `platform-services-controlled-alert-routing`.

---

## Network Flow Mapping

Build a flow table from the workload and service data. For each flow, determine:

| Column | How to find it |
|---|---|
| Source | Pod name from `workloads.yaml` |
| Destination | Service name, Route host, or external CIDR |
| Protocol | Port from service spec |
| External | Whether destination is outside the cluster |
| FWCR required | Whether destination is Zone B / behind a CSBC firewall |
| Status | Does a NetworkPolicy exist for this flow? |

---

## Task Numbering & AI Assist Indicators

### Task numbering convention

| Prefix | Category |
|---|---|
| `HELM-XX` | Helm chart authoring and configuration |
| `NP-XX` | NetworkPolicy suite |
| `CI-XX` | CI/CD pipeline updates |
| `APP-XX` | Application code changes |
| `VAULT-XX` | Secrets migration to Vault |
| `DATA-XX` | PVC / data migration |
| `ARCH-XX` | Architecture decisions (FWCRs, external connectivity) |

### AI assist level indicators

| Icon | Meaning |
|---|---|
| 🤖 | Fully Copilot-generated (boilerplate, no project context required) |
| 🤝 | Copilot drafts, developer verifies (project-specific details needed) |
| 💼 | Admin action (GitHub Secrets, Vault namespace, CSBC FWCR) |
| 🔎 | Investigation required before task can begin |

---

## Sanitized Migration Knowledge

- 2026-04-16: [migration-engagement] A structured collect-then-analyze approach reduces multi-session migration analysis to a single pass.
- 2026-04-16: [migration-engagement] The two most time-consuming gap areas are NetworkPolicy (external CIDR discovery requires firewall team input) and Helm authoring (when no charts exist). Flag these as `ARCH-XX` pre-tasks in every report.
- 2026-04-16: [migration-engagement] `DeploymentConfig` → `Deployment` conversion is always task `HELM-01` and is prerequisite for all other Helm tasks.
- 2026-04-16: [migration-engagement] Zone B external services (SFTP, ORDS) always require CSBC FWCRs — create `ARCH-01 CSBC FWCR request` as the first blocking task whenever these flows are present.
- 2026-04-16: Report PDF rendering must run from the report directory (not workspace root) so relative image paths in markdown resolve correctly.
- 2026-06-05: [multi-app-engagement] Cross-namespace NPs detected during analysis — coupling matrix is essential for multi-app migrations to identify sequencing dependencies and shared infrastructure.
