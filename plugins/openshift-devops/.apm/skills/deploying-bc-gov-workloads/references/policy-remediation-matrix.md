# Policy Gate Remediation Matrix

Tool-by-tool failure-to-fix guide for the four-tool policy-as-code gate (`datree`, `polaris`, `kube-linter`, `conftest`).

## Contents

- [Datree (`assets/policies/datree-policies.yaml`)](#datree-assetspoliciesdatree-policiesyaml)
- [Polaris (`assets/policies/polaris.yaml`)](#polaris-assetspoliciespolarisyaml)
- [kube-linter (`assets/policies/kube-linter.yaml`)](#kube-linter-assetspolicieskube-linteryaml)
- [Conftest / OPA (`assets/policies/*.rego`)](#conftest--opa-assetspoliciesrego)
- [Cross-Tool Nuances](#cross-tool-nuances)

---

## Datree (`assets/policies/datree-policies.yaml`)

| Rule / Failure | Cause | Fix |
|---|---|---|
| `CUSTOM_WORKLOAD_INCORRECT_DATACLASS_LABELS` | Missing or invalid `DataClass` on pod template | Set `DataClass: Medium` (allowed: `Low`, `Medium`, `High`) on `spec.template.metadata.labels` |
| `CUSTOM_WORKLOAD_INCORRECT_ROUTE_DATACLASS_LABELS` | Route/Ingress missing AVI annotation or invalid value | Set `metadata.annotations["aviinfrasetting.ako.vmware.com/name"]` to `dataclass-medium` (or `dataclass-high` / `dataclass-public`) |
| `CUSTOM_WORKLOAD_INCORRECT_ENVIRONMENT_LABELS` | Missing or invalid `metadata.labels.environment` | Set `environment` to `development`, `test`, or `production` |
| `CUSTOM_WORKLOAD_MISSING_LABEL_OWNER_VALUE` | Missing `metadata.labels.owner` | Add `owner: <team-name>` in `commonLabels` / `metadata.labels` |
| `CUSTOM_WORKLOAD_INVALID_LABELS_VALUE` | Label value >63 chars or invalid characters | Use RFC 1123-safe values (`^[A-Za-z0-9]([A-Za-z0-9_.-]*[A-Za-z0-9])?$`) |
| `CUSTOM_WORKLOAD_INCORRECT_NETWORK_POLICIES` | Empty `podSelector` or rule missing `from`/`to` | Add `podSelector.matchLabels` and non-empty `from`/`to` peers |
| `CUSTOM_REPLICA_COUNT_PROD` | `environment: production` with `< 2` replicas | Set `replicas >= 2` in `values-prod.yaml` |
| `ENSURE_IMAGE_PULL_POLICY_SET_TO_ALWAYS` | `imagePullPolicy` is not `Always` | Set `image.pullPolicy: Always` |
| `CONTAINERS_INCORRECT_RUNASUSER_VALUE_LOWUID` | `runAsUser` set to `< 10000` | Omit `runAsUser` when `global.openshift: true` (SCC assigns UID) |

---

## Polaris (`assets/policies/polaris.yaml`)

| Check | Cause | Fix |
|---|---|---|
| `runAsRootAllowed` / `privilegeEscalationAllowed` | Missing container securityContext hardening | Set `allowPrivilegeEscalation: false`, `runAsNonRoot: true`, `capabilities.drop: ["ALL"]` |
| `notReadOnlyRootFilesystem` | `readOnlyRootFilesystem` not `true` | Set `readOnlyRootFilesystem: true` and mount `emptyDir` for `/tmp` |
| `cpuRequestsMissing` / `cpuLimitsMissing` / `memory*` | Missing container resource requests or limits | Define `resources.requests` and `resources.limits` |
| `imageRegistry` | Image from unapproved registry | Use OpenShift internal registry, `ghcr.io`, `docker.io`, or Artifactory/JFrog |
| `tagNotSpecified` / `pullPolicyNotAlways` | Unpinned image or non-`Always` pull policy | Pin tag/digest and set `imagePullPolicy: Always` |
| `serviceTypeClusterIPOnly` | Service uses `NodePort` or `LoadBalancer` | Change `spec.type` to `ClusterIP` (use `Route` for external access) |
| `missingNetworkPolicy` | PodTemplate has no matching `NetworkPolicy` | Create a `NetworkPolicy` whose `podSelector.matchLabels` matches pod labels and has >= 1 `ingress` or `egress` rule |
| `statefulSetMissingReplicas` | StatefulSet omits `spec.replicas` | Set explicit `spec.replicas >= 1` |

---

## kube-linter (`assets/policies/kube-linter.yaml`)

| Check | Cause | Fix |
|---|---|---|
| `default-service-account` | Workload uses `default` ServiceAccount | Create dedicated ServiceAccount (`--type serviceaccount`) and set `serviceAccountName` |
| `required-annotation-email` | Missing contact email annotation | Add `email: <team-email>` under `metadata.annotations` |
| `required-label-owner` | Missing `owner` label | Add `owner: <team-name>` under `metadata.labels` |
| `latest-tag` | Container image uses `:latest` | Pin immutable release tag or `sha256:` digest |
| `no-read-only-root-fs` | `readOnlyRootFilesystem` not `true` | Set `readOnlyRootFilesystem: true` |
| `pdb-max-unavailable` / `pdb-min-available` | Invalid PDB budget relative to replicas | Ensure `maxUnavailable < replicas` or `minAvailable < replicas` |
| `dangling-service` / `mismatching-selector` | Service selector matches no workload labels | Align `Service.spec.selector` with pod template labels |

---

## Conftest / OPA (`assets/policies/*.rego`)

| Policy File | Denial Condition | Fix |
|---|---|---|
| `avi-infrasetting-annotation.rego` | `Route`/`Ingress` missing or invalid `aviinfrasetting.ako.vmware.com/name` | Set annotation to `dataclass-medium` (or `dataclass-high` / `dataclass-public`) |
| `routes-edge-termination.rego` | Edge-terminated `Route` without `app.kubernetes.io/component: frontend` | Remove Route for internal services, or add `isb.gov.bc.ca/edge-termination-approval: <ticket>` |
| `network-policies.rego` | `NetworkPolicy` missing `policyTypes`, empty `podSelector: {}` (non-default-deny), missing `from`/`to`/`ports`, or `podSelector: {}` peer | Scope `podSelector` with `matchLabels`; include both peers and `ports` in every rule |
| `network-policies.rego` | `podSelector` in `from` without `namespaceSelector` | Add `namespaceSelector` so ingress does not match all namespaces |
| `network-policies.rego` | `0.0.0.0/0` or `::/0` egress without approval | Add annotations `justification` and `approvedBy` on `NetworkPolicy.metadata.annotations` |

---

## Cross-Tool Nuances

- **`kube-linter` probes**: `no-liveness-probe` and `no-readiness-probe` are excluded in `kube-linter.yaml`, but **enforced as `danger` in `polaris.yaml`** — always define both probes.
- **`kube-linter` replicas**: `minimum-three-replicas` is excluded in `kube-linter.yaml`, while `datree-policies.yaml` enforces `replicas >= 2` when `environment: production`.
- **Single-file rendering**: `polaris` (`missingNetworkPolicy`) and `kube-linter` (`dangling-service`, `mismatching-selector`) cross-reference resources; always run the gate against a single combined `rendered.yaml`.
