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

Pod `DataClass` label **must match** the AVI annotation suffix (`DataClass: Low` + `dataclass-medium` route causes SDN to silently drop traffic).

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

Emerald default-denies **both Ingress AND Egress**. See [networkpolicy-patterns.md](networkpolicy-patterns.md) for full YAML patterns.

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
| `netapp-file-standard` | RWX (multi-pod) | Shared file storage, build artefacts, config mounts |
| `netapp-block-standard` | RWO (single-pod) | Databases, stateful workloads requiring higher IOPS |

`netapp-block-standard` is single-pod (RWO) — do not use for workloads that require concurrent access from multiple pods.

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

```bash
oc login --token=<token> --server=https://api.gold.devops.gov.bc.ca:6443
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
