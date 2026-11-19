# Standards & References Catalog

Authoritative standard IDs cited by G1–G12 migration gap findings, R01–R15 resilience checks, and remediation tasks.

## Contents

- [BC Gov Platform Services (`PS-*`)](#bc-gov-platform-services-ps-)
- [`ag-devops` Policy Standards (`AD-*`)](#ag-devops-policy-standards-ad-)
- [BC Gov Information Security & ISB EA (`ISB-*`)](#bc-gov-information-security--isb-ea-isb-)
- [OpenShift Platform (`OCP-*`)](#openshift-platform-ocp-)
- [Kubernetes Documentation (`K8S-*`)](#kubernetes-documentation-k8s-)
- [Security (`SEC-*`)](#security-sec-)

---

## BC Gov Platform Services (`PS-*`)

| ID | Standard | Reference |
|---|---|---|
| PS-01 | Emerald Landing Zone — default-deny egress NetworkPolicy requirement | `docs.developer.gov.bc.ca` |
| PS-02 | Platform Services — Storage Guide (`netapp-block-standard` for block storage workloads) | `docs.developer.gov.bc.ca` |
| PS-03 | Platform Services — Artifactory as mandatory image registry on Emerald / Health Probes | `docs.developer.gov.bc.ca` |
| PS-04 | Platform Services — Health Probes and Deployment Readiness requirements | `docs.developer.gov.bc.ca` |
| PS-05 | Platform Services — Application Resiliency Guidelines (Guaranteed QoS in `prod`, PDBs, 600s drain cap, `OpenShift-alerts`) | `app-resiliency-guidelines.md` |
| PS-06 | Platform Services — Kyverno ClusterPolicies (CronJob schedule/timezone rules, `DataClass` labels) | `kyverno.md` |
| PS-07 | Platform Services — Automated Scale-Down (Tuesday 8 PM: `Progressing.lastUpdateTime > 1 year` or `> 100` restarts) | `automated-scaling.md` |
| PS-08 | Platform Services — AlertManager & Per-Namespace Alerts (`platform-services-controlled-alert-rules`, custom `PrometheusRule`) | `alertmanager.md` |
| PS-09 | Platform Services — Project Resource Quotas, Auto-Approval & Tuning (`default-limits`, `compute-long-running-quota`, `compute-time-bound-quota`, `compute-best-effort-quota`, CPU ratios `3:1`/`2:1`/`1.5:1`) | `openshift-project-resource-quotas.md`, `request-quota-adjustment-for-openshift-project-set.md`, `application-resource-tuning.md` |

---

## `ag-devops` Policy Standards (`AD-*`)

| ID | Standard | Enforcement |
|---|---|---|
| AD-01 | `ag-helm-templates` — mandatory Helm scaffolding / PriorityClass requirement | Datree / Polaris `priorityClassNotSet` |
| AD-02 | Pod labels `DataClass`, `owner`, `environment` / Resource requests required | Datree + Conftest / Polaris `requestsNotSet` |
| AD-03 | Policy-as-code gate: Datree + Polaris + kube-linter + Conftest in every CI pipeline | CI workflow requirement |
| AD-04 | PriorityClass required on all workloads | Polaris `priorityClassNotSet` check |

---

## BC Gov Information Security & ISB EA (`ISB-*`)

| ID | Standard | Reference |
|---|---|---|
| ISB-01 | BC Gov Information Security Policy — plain Kubernetes Secrets prohibited for sensitive values; Vault + ESO mandatory | BC Gov IS Policy |
| ISB-02 | ISB Enterprise Architecture — Option 2 CI/CD standard (first-party GitOps pipelines) | Internal ISB EA documentation |
| ISB-03 | ISB Enterprise Architecture — Artifact Management (Artifactory as single source of truth for images) | Internal ISB EA documentation |

---

## OpenShift Platform (`OCP-*`)

| ID | Standard | Reference |
|---|---|---|
| OCP-01 | OpenShift 4.14 — `DeploymentConfig` deprecation / Node Management & OOMKill detection | OCP 4.14 Docs |
| OCP-02 | OpenShift — Machine Config Operator: rolling node upgrade drains pods one node at a time | OCP MCO Docs |
| OCP-03 | OpenShift — PodDisruptionBudget support during node drain | OCP PDB Docs |

---

## Kubernetes Documentation (`K8S-*`)

| ID | Standard | Reference |
|---|---|---|
| K8S-01 | Configure Pod Disruption Budgets / Probes (migration) | `kubernetes.io/docs/tasks/run-application/configure-pdb/` |
| K8S-02 | Configure Liveness, Readiness, and Startup Probes / PV Access Modes | `kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/` |
| K8S-03 | Horizontal Pod Autoscaling / Network Policies | `kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/` |
| K8S-04 | Assigning Pods to Nodes — Affinity and Anti-Affinity | `kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/` |
| K8S-05 | Pod Lifecycle — Termination and `preStop` hooks | `kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-termination` |
| K8S-06 | Pod Quality of Service Classes (Guaranteed / Burstable / BestEffort) | `kubernetes.io/docs/concepts/workloads/pods/pod-qos/` |
| K8S-07 | Persistent Volumes — Access Modes (RWO vs RWX) | `kubernetes.io/docs/concepts/storage/persistent-volumes/#access-modes` |
| K8S-08 | Pod Priority and Preemption | `kubernetes.io/docs/concepts/scheduling-eviction/pod-priority-preemption/` |
| K8S-09 | Deployment Update Strategy (RollingUpdate vs Recreate) | `kubernetes.io/docs/concepts/workloads/controllers/deployment/#strategy` |
| K8S-10 | Topology Spread Constraints (zone-level HA) | `kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/` |

---

## Security (`SEC-*`)

| ID | Standard | Reference |
|---|---|---|
| SEC-01 | OWASP A06:2021 — Vulnerable and Outdated Components (mutable image tags allow silent dependency drift) | `owasp.org/Top10/A06_2021-Vulnerable_and_Outdated_Components/` |
| SEC-02 | GitHub Actions — SHA pinning for third-party actions | GitHub Security Hardening |
