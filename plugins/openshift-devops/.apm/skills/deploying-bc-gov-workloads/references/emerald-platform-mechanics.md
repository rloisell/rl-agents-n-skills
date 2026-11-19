# Emerald Platform Mechanics

Emerald-specific OpenShift mechanics, AVI routing, DataClass labels, StorageClass, SSO, and `oc` operational commands.

## Contents

- [Namespace Convention](#namespace-convention)
- [AVI InfraSettings — Route Annotation](#avi-infrasettings--route-annotation)
- [DataClass & Required Pod Labels](#dataclass--required-pod-labels)
- [NetworkPolicy Model](#networkpolicy-model)
- [Route Edge Termination](#route-edge-termination)
- [PriorityClass](#priorityclass)
- [OpenShift Mode in Helm (`global.openshift: true`)](#openshift-mode-in-helm-globalopenshift-true)
- [StorageClass](#storageclass)
- [DNS Split-Tunneling](#dns-split-tunneling)
- [Health Checks](#health-checks)
- [Common SSO Authentication](#common-sso-authentication)
- [OpenShift `oc` Command Reference](#openshift-oc-command-reference)
- [Secrets Management](#secrets-management)
- [Kyverno Cluster Policies](#kyverno-cluster-policies)
- [CPU Limits & Resource Guidance](#cpu-limits--resource-guidance)
- [Platform Product Registry, RBAC & Security Tooling](#platform-product-registry-rbac--security-tooling)
- [Cluster Pruning & ImageStream Hygiene](#cluster-pruning--imagestream-hygiene)
- [Load Testing Policy](#load-testing-policy)
- [Application Retirement Runbook](#application-retirement-runbook)

---

## Namespace Convention

```text
<ns-prefix>-dev     ← development
<ns-prefix>-test    ← staging / QA
<ns-prefix>-prod    ← production
<ns-prefix>-tools   ← CI/CD tooling, Artifactory, Vault
```

---

## AVI InfraSettings — Route Annotation

Controls which VIP pool handles the Route. **Get this wrong and traffic silently drops.**

| Annotation value | VIP | When to use |
|---|---|---|
| `dataclass-medium` | Private VIP — VPN only | All internal workloads (default) |
| `dataclass-high` | Private VIP — sensitive data | Higher-trust internal workloads |
| `dataclass-public` | Public internet VIP | Internet-facing routes with public exposure |
| `dataclass-low` | NO VIP on Emerald | **NEVER USE** — DNS resolves but `ERR_EMPTY_RESPONSE` |

```yaml
# Required on every OpenShift Route
metadata:
  annotations:
    aviinfrasetting.ako.vmware.com/name: "dataclass-medium"
```

AKO re-adds this annotation within ~15 seconds if removed — always keep it in Helm values.

---

## DataClass & Required Pod Labels

Pod `DataClass` label **must match** the AVI annotation suffix (`DataClass: Low` + `dataclass-medium` route causes SDN to silently drop traffic). On Emerald (NSX), a Kyverno policy automatically mutates any pod lacking `Low`, `Medium`, or `High` to **`DataClass: Invalid`**, causing NSX firewall rules to block all network traffic to/from that pod.

Every Deployment/StatefulSet pod template must carry **all three** labels (enforced by Datree + Conftest):

```yaml
podLabels:
  DataClass: "Medium"          # Low | Medium | High
  owner: "<team-or-ticket>"    # team name or Jira ticket reference
  environment: "development"   # production | test | development (exact values)
```

When using `ag-template.deployment`, set `ModuleValues.dataClass` (renders `DataClass`) and add `owner`/`environment` via a `LabelData` fragment:

```yaml
{{- define "myapp.labels" -}}
owner: <team-name>
environment: development
{{- end }}
# ... in dict: set $p "LabelData" "myapp.labels"
```

### Internet-Ingress label

```yaml
podLabels:
  Internet-Ingress: "DENY"    # default — correct for all internal services
  # Internet-Ingress: "ALLOW" # only if reachable from public internet via Public VIP
```

---

## NetworkPolicy Model

Emerald default-denies **both Ingress AND Egress**. Every namespace also has a platform-managed **`platform-services-controlled-default`** NetworkPolicy (auto-recreated if deleted) that enforces default-deny while permitting Web Terminal Operator access. See [networkpolicy-patterns.md](networkpolicy-patterns.md) for full YAML patterns.

| Flow | Policy needed |
|---|---|
| Router → Frontend | Ingress on Frontend |
| Router → API | Ingress on API |
| Frontend → API | Ingress on API **+** Egress from Frontend |
| API → DB | Ingress on DB **+** Egress from API |
| Any pod → DNS | Egress UDP+TCP 53 on every pod |

---

## Route Edge Termination

Conftest denies **edge-terminated** Routes unless the Route has either:

- Label `app.kubernetes.io/component: frontend`, **or**
- Annotation `isb.gov.bc.ca/edge-termination-approval: "<ticket>"`

Passthrough (`spec.tls.termination: passthrough`) and re-encrypt termination are not affected.

```yaml
# If edge termination is approved:
metadata:
  labels:
    app.kubernetes.io/component: frontend   # OR:
  annotations:
    isb.gov.bc.ca/edge-termination-approval: "ISB-12345"
```

---

## PriorityClass

Every Deployment and StatefulSet must reference a `PriorityClass` (Polaris `priorityClassNotSet` check):

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: <app>-priority
value: 1000000
globalDefault: false
description: "<app> workloads"
```

```yaml
spec:
  template:
    spec:
      priorityClassName: <app>-priority
```

---

## OpenShift Mode in Helm (`global.openshift: true`)

Set this in every Helm chart's `values.yaml` targeting Emerald:

```yaml
global:
  openshift: true
```

Effect:

- Deployment/Job pod `securityContext` does **not** pin `runAsUser`/`runAsGroup` — OpenShift SCC assigns runtime UID/GID
- Adds `checkov.io/skip999: CKV_K8S_40=...` annotation to suppress Checkov false-positive
- Still enforces `runAsNonRoot`, `allowPrivilegeEscalation: false`, `readOnlyRootFilesystem: true`, capabilities drop `ALL`

Omitting `global.openshift: true` when using `ag-helm` causes the deployment template to pin `runAsUser: 10001`, which may conflict with the namespace SCC.

---

## StorageClass

| StorageClass | Access mode | Best for |
|---|---|---|
| `netapp-file-standard` | RWX (multi-pod) | Default storage class; shared file storage, config mounts (no automated backup) |
| `netapp-block-standard` | RWO (single-pod) | Databases, stateful workloads requiring higher IOPS (supports VolumeSnapshots; no automated backup) |
| `netapp-file-backup` | RWX (multi-pod) | **Backup-only** CronJob targets; OCIO Backup (monthly full, daily incremental, 90-day retention). **Never mount to production workloads** |

- **PVC size bounds**: NetApp PVCs must be between **`20Mi` minimum** and **`512Gi` maximum** (matching the maximum Product Registry storage quota).
- **Large / unstructured data (`>100Gi`)**: Do not store large unstructured datasets (images, PDFs, archives) on NetApp PVCs. Use **OCIO S3 Object Storage (Dell EMC ECS)** (provisioned via your Ministry IMB) and optionally **COMS** (Common Object Management Service).
- **`netapp-file-backup` recovery**: Record the underlying PV name (`oc get pvc` → `pvc-...`). To restore, create a destination `netapp-file-backup` PVC on the same cluster and submit a restore issue in [`bcgov/devops-requests`](https://github.com/bcgov/devops-requests/issues/new/choose).
- `netapp-block-standard` is single-pod (RWO) — do not use for workloads that require concurrent access from multiple pods.

---

## DNS Split-Tunneling

Route hostnames (`*.apps.emerald.devops.gov.bc.ca`) resolve only via BC Gov VPN DNS. Local/home DNS returns `NXDOMAIN`. Ensure the VPN client routes this domain through VPN DNS before debugging route connectivity issues.

---

## Health Checks

Every deployment must include both probes:

```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 30
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 10
  failureThreshold: 3
```

**.NET health check setup:**

```csharp
builder.Services.AddHealthChecks()
    .AddDbContextCheck<ApplicationDbContext>("database");

app.MapHealthChecks("/health/live");
app.MapHealthChecks("/health/ready", new HealthCheckOptions
{
    Predicate = check => check.Tags.Contains("ready") || check.Name == "database"
});
```

---

## Common SSO Authentication

BC Gov uses DIAM/Keycloak via `loginproxy.gov.bc.ca`.

| Realm | Use |
|---|---|
| `standard` | Production services |
| `onestopauth` | Existing IDIR / BCeID |
| `onestopauth-basic` | BCeID Basic |
| `onestopauth-business` | BCeID Business |

**React frontend — OIDC PKCE config:**

```json
{
  "authority": "https://loginproxy.gov.bc.ca/auth/realms/standard",
  "client_id": "<client-id>",
  "redirect_uri": "https://<app-route>/callback",
  "response_type": "code",
  "scope": "openid profile email"
}
```

---

## OpenShift `oc` Command Reference

On OCP 4.14+, use `--web` for browser-based OIDC login without pasting tokens into the CLI. For **Emerald**, connect over **SPAN-BC** (`https://api.emerald.devops.gov.bc.ca:6443`):

```bash
oc login --server=https://<cluster-api>:6443 --web
oc project <ns-prefix>-<env>
oc get pods -n <namespace>
oc logs <pod-name> -n <namespace> --tail=100
oc describe pod <pod-name> -n <namespace>
oc exec -it <pod-name> -n <namespace> -- /bin/sh
oc rollout restart deployment/<name> -n <namespace>
oc rollout status deployment/<name> -n <namespace>
oc scale deployment/<name> --replicas=0 -n <namespace>
```

---

## Secrets Management

**Never commit secrets.** Store in OpenShift Secrets, reference via env vars:

```yaml
env:
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: <service>-db-secret
        key: password
  - name: KEYCLOAK_CLIENT_SECRET
    valueFrom:
      secretKeyRef:
        name: <service>-keycloak-secret
        key: client-secret
```

```bash
oc create secret generic <service>-db-secret \
  --from-literal=password=<value> \
  -n <namespace>
```

---

## Kyverno Cluster Policies

Platform Services enforces Kyverno `ClusterPolicy` rules at admission time (pre-check locally with `scripts/check_platform_rules.py`):

| Policy / Rule | Enforcement | Remediation |
|---|---|---|
| `DataClass: Invalid` mutation | Pods without `DataClass` (`Low\|Medium\|High`) are mutated to `DataClass: Invalid`, blocking NSX traffic | Always set `DataClass: Low\|Medium\|High` on pod templates |
| `no-fast-cronjob` | Denies CronJobs running faster than every **5 minutes** (`>=5m`), or faster than every **1 hour** (`>=1h`) when mounting a PVC | Widen `spec.schedule` or replace with a `go-crond` Deployment |
| `no-unsupported-timezone` | Denies `CRON_TZ=` / `TZ=` inside `spec.schedule` | Move timezone to `spec.timeZone` (e.g., `America/Vancouver`) |

**`go-crond` workaround (frequent schedule + PVC)**: Replace the `CronJob` with a `Deployment` (`restartPolicy: Always`, `replicas: 1`) running `go-crond --allow-unprivileged /etc/crontab` (required because OpenShift SCC assigns a random UID). See [go-crond-deployment.tpl.yaml](../assets/templates/go-crond-deployment.tpl.yaml).

---

## CPU Limits & Resource Guidance

Platform Services recommends **omitting `limits.cpu`** on containers to prevent Linux CFS CPU throttling (`container_cpu_cfs_throttled_periods_total`), while always setting `requests.cpu`, `requests.memory`, and `limits.memory`.

> **Datree / Polaris policy gate exception**: The bundled `assets/policies/datree-policies.yaml` (`CONTAINERS_MISSING_CPU_LIMIT_KEY`) and `assets/policies/polaris.yaml` (`cpuLimitsMissing`) check for `limits.cpu` by default. If your team omits `limits.cpu` per Platform Services guidance, disable or exempt those two rules in your repo's policy config rather than adding tight CPU limits that throttle multi-threaded apps.

- **Node drain / termination**: Keep `terminationGracePeriodSeconds` <= `600` (Platform Ops caps node drain grace periods at `600s` and force-kills pods after).
- **PodDisruptionBudget (PDB)**: Never set `maxUnavailable: 0` (or `minAvailable` equal to total replicas), and set `unhealthyPodEvictionPolicy: AlwaysAllow` so unhealthy pods do not block node drains.

---

## Platform Product Registry, RBAC & Security Tooling

- **Platform Product Registry** (`https://registry.developer.gov.bc.ca`): Source of truth for project sets, storage/quota requests, cluster web console links, and Product Owner / Technical Lead contacts (uses IDIR accounts).
- **Platform requests**: Submit volume restores (`netapp-file-backup`) and platform support requests via [`bcgov/devops-requests`](https://github.com/bcgov/devops-requests/issues/new/choose).
- **IDIR-first RBAC**: Prefer IDIR UPNs (`first.last@gov.bc.ca`) over `<github-id>@github` in `RoleBinding`s; all usernames are lowercase, and users must log in to the OpenShift console once with IDIR before `RoleBinding`s can be created.
- **RHEL base images**: Pull UBI/RHEL images via Artifactory proxy `artifacts.developer.gov.bc.ca/redhat-docker-remote` (`ubi8`, `openshift4/ose-cli`). For `yum`/`dnf` subscription builds, the platform operator maintains `platform-services-controlled-etc-pki-entitlement` in every `-tools` namespace — mount it via `BuildConfig` `spec.strategy.dockerStrategy.volumes` at `/etc/pki/entitlement` so entitlement certs are never baked into the output image (RHEL 7 only also requires `RUN rm /etc/rhsm-host` before `yum`).
- **Security pipelines & image scanning**: Leverage [`bcgov/security-pipeline-templates`](https://github.com/bcgov/security-pipeline-templates) for CI/CD SAST/DAST, **Red Hat ACS** (`https://acs.developer.gov.bc.ca`) for active cluster/runtime vulnerability & network policy scanning, and **JFrog Xray** (built into Artifactory) for artifact scanning.

---

## Cluster Pruning & ImageStream Hygiene

Platform CronJobs prune stale objects daily to protect shared etcd and internal registry storage:

- **`DeploymentConfig` / `ReplicationController`**: Keeps last **2** `Complete` (0-replica), last **1** `Failed` (0-replica), and any `< 48h`.
- **`Build`**: Keeps last **2** `Complete`, last **1** `Failed`/`Error`/`Canceled`, and any `< 48h`.
- **`ImageStream`**: Daily prune keeps revisions `< 48h`, revisions in use by running pods/deployments, and the most recent revision (tag pruning also retains the 3 most recent revisions < 96h). Weekly registry size warnings email teams with oversized streams. Hard prune of orphaned blobs runs **Sunday 6:00 AM** (registry set Read-Only).
- **`PipelineRun` / `TaskRun`**: Keeps the **5** most recent of each type per namespace.
- **Manual cleanup**: Delete an entire stream with `oc delete imagestream <name>` or a single tag with `oc tag -d <imagestream>:<tag>`. Avoid `latest` in prod; clean up per-PR tags after merge.

---

## Load Testing Policy

Before load testing on BC Gov OpenShift (Silver/Gold):

1. **Schedule window**: Run only **after 5:30 PM on weekdays** or on **weekends**.
2. **Concurrency cap**: Restrict to **<= 50,000 concurrent sessions** (two-thirds of the 3-node router capacity) and keep a namespace admin available during the test.
3. **Approval**: Submit a load test plan (duration, target namespaces, ramp-up, success/failure criteria, traffic origin, off-cluster dependencies) to `PlatformServicesTeam@gov.bc.ca` to reserve a non-conflicting window.

---

## Application Retirement Runbook

1. **Policy & Backups**: Consult MISO/MPO/MRO for data retention laws; cancel ServiceNow/iStore TLS cert renewals and vendor licenses. Export backups to off-cluster storage (e.g., OCIO S3) — deleting the project set permanently deletes all OpenShift secrets and the namespace Vault folder.
2. **Disable Automation & Scale Down**: Disable CI/CD and Argo CD auto-sync, delete all `PodDisruptionBudget`, `HPA`/`VPA`, and `CronJob` objects, then scale all workloads to `0`.
3. **Offboard Dependent Services**: Delete all repos in your Artifactory project, remove Sysdig notification channels, email `PlatformServicesTeam@gov.bc.ca` to remove non-PO/TL ACS access, archive GitHub repos (and explicitly disable GitHub Actions workflows — archiving does not stop them), and offboard SSO/S3/CHES/CHEFS integrations.
4. **Delete PVCs & Pods**: Manually delete **all PVCs and all Pods** across every namespace including `-tools` (the Product Registry blocks deletion if any PVC or pod remains).
5. **Delete in Product Registry**: In `https://registry.developer.gov.bc.ca`, delete the product (irreversible; removes namespaces, Vault role/accounts, Artifactory service accounts, Sysdig teams, and Argo CD project/apps).
