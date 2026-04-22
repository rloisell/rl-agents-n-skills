# SKILL: ocp-resilience-analyst

**Domain**: OpenShift Workload Resilience & Pod Disruption Analysis  
**Skill version**: 1.0  
**Updated**: April 2026

---

## Purpose

Produce a **full resilience posture report** for any OpenShift namespace.  
The report is platform-agnostic — useful for teams staying on Silver/Gold AND  
for teams preparing to migrate to Emerald (pre-migration baseline).

**This skill is Tier 1 of the OCP Resilience Toolkit:**

| Tier | Name | What it is |
|------|------|------------|
| 1 | ocp-resilience-analyst (this skill) | VS Code / Copilot Chat agent + skills — **primary method** |
| 2 | ocp-resilience-toolkit | CLI data collection + GitHub Composite Action + VS Code prompt template |

---

## Invocation

```
# In VS Code Copilot Chat (agent mode), use the prompt template:
# .github/prompts/ocp-resilience-analysis.prompt.md
#
# Via Copilot Extension:
@bc-resilience analyze namespace:f1b263 [repo:bcgov-c/myapp] [cluster:silver]
#
# Via CLI toolkit:
./ocp-resilience-toolkit/collect/collect.sh --namespace f1b263 --cluster silver --output ./data
```

---

## Phase 1 — Collect Namespace Data

Run these commands against each environment suffix (`-dev`, `-test`, `-prod`, `-tools`).  
Store all output in `<OUTPUT>/<namespace>-<env>/` directories.

### 1A — Workload resilience data

```bash
NS="<NAMESPACE>-<ENV>"
OUT="<OUTPUT>/${NS}"
mkdir -p "${OUT}"

# Core workloads
oc get deployment,statefulset,daemonset,cronjob -n "${NS}" -o yaml > "${OUT}/workloads.yaml"
oc get deployment,statefulset,daemonset -n "${NS}" \
  -o custom-columns='NAME:.metadata.name,KIND:.kind,REPLICAS:.spec.replicas,STRATEGY:.spec.strategy.type,PROGRESSING:.status.conditions[?(@.type=="Progressing")].status' \
  > "${OUT}/workload-summary.txt"

# PodDisruptionBudgets — PRIMARY target
oc get pdb -n "${NS}" -o yaml > "${OUT}/pdbs.yaml"
oc get pdb -n "${NS}" \
  -o custom-columns='NAME:.metadata.name,MIN-AVAILABLE:.spec.minAvailable,MAX-UNAVAILABLE:.spec.maxUnavailable,CURRENT-HEALTHY:.status.currentHealthy,DESIRED-HEALTHY:.status.desiredHealthy,DISRUPTED:.status.disruptedPods,DISRUPTIONS-ALLOWED:.status.disruptionsAllowed' \
  > "${OUT}/pdb-summary.txt" 2>&1 || echo "No PDBs found" >> "${OUT}/pdb-summary.txt"

# Horizontal Pod Autoscalers
oc get hpa -n "${NS}" -o yaml > "${OUT}/hpas.yaml"
oc get hpa -n "${NS}" \
  -o custom-columns='NAME:.metadata.name,TARGET:.spec.scaleTargetRef.name,MIN:.spec.minReplicas,MAX:.spec.maxReplicas,CURRENT:.status.currentReplicas,CPU-TARGET:.spec.metrics[0].resource.target.averageUtilization' \
  > "${OUT}/hpa-summary.txt" 2>&1 || echo "No HPAs found" >> "${OUT}/hpa-summary.txt"

# Vertical Pod Autoscalers (if VPA operator present)
oc get vpa -n "${NS}" -o yaml > "${OUT}/vpas.yaml" 2>/dev/null || echo "# VPA not available" > "${OUT}/vpas.yaml"

# Pod topology and scheduling
oc get pod -n "${NS}" -o wide > "${OUT}/pods-wide.txt"
oc get pod -n "${NS}" -o yaml > "${OUT}/pods.yaml"

# Resource quotas and limit ranges (QoS context)
oc get resourcequota,limitrange -n "${NS}" -o yaml > "${OUT}/quota.yaml"

# PVCs (storage resilience)
oc get pvc -n "${NS}" -o yaml > "${OUT}/pvcs.yaml"
oc get pvc -n "${NS}" \
  -o custom-columns='NAME:.metadata.name,STATUS:.status.phase,CAPACITY:.status.capacity.storage,ACCESS:.spec.accessModes,STORAGECLASS:.spec.storageClassName' \
  > "${OUT}/pvc-summary.txt" 2>&1 || echo "No PVCs" >> "${OUT}/pvc-summary.txt"

# Services (traffic resilience — session affinity, topology)
oc get svc -n "${NS}" -o yaml > "${OUT}/services.yaml"

# Events — surface recent disruption/eviction events
oc get events -n "${NS}" \
  --field-selector reason=Evicted,reason=OOMKilled,reason=BackOff,reason=Unhealthy \
  --sort-by='.lastTimestamp' > "${OUT}/disruption-events.txt" 2>&1 || true
oc get events -n "${NS}" --sort-by='.lastTimestamp' | tail -50 > "${OUT}/recent-events.txt"

# Priority classes referenced by pods
oc get pod -n "${NS}" -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.priorityClassName}{"\n"}{end}' \
  > "${OUT}/priority-classes.txt"

# Pod node distribution (for anti-affinity analysis)
oc get pod -n "${NS}" -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.nodeName}{"\t"}{.metadata.labels.app}{"\n"}{end}' \
  > "${OUT}/pod-node-distribution.txt"

# Deployment strategies + update history
oc rollout history deployment -n "${NS}" 2>/dev/null > "${OUT}/rollout-history.txt" || true

echo "Phase 1A complete for ${NS}" >&2
```

### 1B — Extract probe and affinity detail from workload YAML

```bash
# Health probes per container
oc get deployment,statefulset -n "${NS}" -o json \
  | jq '[.items[] | {
      name: .metadata.name,
      kind: .kind,
      replicas: .spec.replicas,
      strategy: .spec.strategy,
      terminationGracePeriodSeconds: .spec.template.spec.terminationGracePeriodSeconds,
      containers: [.spec.template.spec.containers[] | {
        name: .name,
        livenessProbe: .livenessProbe,
        readinessProbe: .readinessProbe,
        startupProbe: .startupProbe,
        resources: .resources,
        lifecycle: .lifecycle
      }],
      affinity: .spec.template.spec.affinity,
      topologySpreadConstraints: .spec.template.spec.topologySpreadConstraints,
      nodeSelector: .spec.template.spec.nodeSelector,
      tolerations: .spec.template.spec.tolerations,
      priorityClassName: .spec.template.spec.priorityClassName
    }]' > "${OUT}/workload-detail.json"

echo "Phase 1B complete for ${NS}" >&2
```

### 1C — Generate manifest-summary.md

```bash
cat > "${OUT}/../manifest-summary.md" << EOF
# Resilience Collection Summary
Namespace prefix: <NAMESPACE>
Environments: <ENVS>
Collection date: $(date -u +%Y-%m-%dT%H:%M:%SZ)
Cluster: <CLUSTER>

## Workload Inventory
$(oc get deployment,statefulset,daemonset,cronjob -n "${NS}" \
    --no-headers -o custom-columns='KIND:.kind,NAME:.metadata.name,REPLICAS:.spec.replicas' 2>/dev/null)

## PDB Coverage
$(cat "${OUT}/pdb-summary.txt")

## HPA Configuration
$(cat "${OUT}/hpa-summary.txt")

## PVC Summary
$(cat "${OUT}/pvc-summary.txt")

## Recent Disruption Events
$(cat "${OUT}/disruption-events.txt" | head -30)
EOF
```

---

## Phase 2 — Gap Analysis

Assess each workload against the **Resilience Check Categories** below.  
Assign a **grade (A/B/C/D/F)** and **severity (⛔ CRITICAL / ⚠ HIGH / ℹ LOW)** per category.

### Resilience Check Categories

Each check maps to one or more standards in the [Sources and References](#sources-and-references) section at the end of this file.

| ID | Category | Failing Condition | Severity | Standard / Source |
|----|----------|-------------------|----------|-------------------|
| R01 | PodDisruptionBudget missing | No PDB for a Deployment/StatefulSet with replicas > 1 | ⛔ CRITICAL | K8S-01; OCP-02 |
| R02 | PDB misconfigured | `minAvailable: 0` OR `maxUnavailable: 100%` OR PDB blocks ALL disruptions (`minAvailable == replicas`) | ⛔ CRITICAL | K8S-01 |
| R03 | Single replica | `replicas: 1` with no HPA min ≥ 2 | ⛔ CRITICAL | K8S-03 |
| R04 | No liveness probe | Missing `livenessProbe` on any container | ⚠ HIGH | K8S-02; PS-03 |
| R05 | No readiness probe | Missing `readinessProbe` on any container | ⚠ HIGH | K8S-02; PS-03 |
| R06 | No HPA / scaling | No HPA and `replicas` is static (not StatefulSet with known single-instance requirement) | ⚠ HIGH | K8S-03 |
| R07 | No pod anti-affinity | No `podAntiAffinity` or `topologySpreadConstraints` on multi-replica workloads | ⚠ HIGH | K8S-04; K8S-10 |
| R08 | No graceful termination | `terminationGracePeriodSeconds` < 10 OR no `preStop` hook where needed | ⚠ HIGH | K8S-05 |
| R09 | BestEffort QoS | Missing `resources.requests` → QoS class BestEffort → first evicted under pressure | ⚠ HIGH | K8S-06; AD-02 |
| R10 | RWO PVC on replicated workload | `ReadWriteOnce` PVC on a Deployment with `replicas > 1` (prevents multi-node scheduling) | ⛔ CRITICAL | K8S-07 |
| R11 | No startup probe | Long-starting container without `startupProbe` → killed by liveness before ready | ℹ LOW | K8S-02 |
| R12 | Recreate strategy | `strategy: Recreate` on a user-facing Deployment → full downtime on update | ⚠ HIGH | K8S-09 |
| R13 | No PriorityClass | Missing `priorityClassName` → random eviction order during node pressure | ℹ LOW | K8S-08; AD-01 |
| R14 | Recent OOMKill / Eviction events | Events show OOMKilled or Evicted in last 72h | ⚠ HIGH | OCP-01 |
| R15 | PDB disruption budgets violated | `disruptionsAllowed: 0` AND `currentHealthy < desiredHealthy` | ⛔ CRITICAL | K8S-01; OCP-02 |

### Gap scoring

- **Grade A**: 0 CRITICAL, 0 HIGH
- **Grade B**: 0 CRITICAL, ≤ 2 HIGH
- **Grade C**: 0 CRITICAL, > 2 HIGH
- **Grade D**: 1 CRITICAL
- **Grade F**: 2+ CRITICAL

---

## Phase 3 — Report Structure

Generate the following 10 sections. See `templates/report-sections.md` for detailed
generation instructions per section.

```
1.  Executive Summary & Resilience Scorecard
2.  Workload Inventory
3.  PodDisruptionBudget Analysis
4.  Scaling & Autoscaling Configuration
5.  Health Probe Analysis
6.  Pod Scheduling & Anti-Affinity
7.  Graceful Termination & Deployment Strategy
8.  Resource Quality of Service (QoS)
9.  Storage Resilience
10. Disruption Simulation (node drain / zone failure / upgrade)
11. Remediation Tasks (prioritized)
12. Appendix
```

**Task numbering**: Use `RES-NN` prefix (e.g. `RES-01`, `RES-02`).

---

## Phase 4 — Render PDF

```bash
# From the report directory
cd <REPORT_DIR>
bash <TOOLKIT_PATH>/render/render.sh \
  --input  "<REPORT_DIR>/<APP_NAME>-Resilience-Report.md" \
  --output "<REPORT_DIR>" \
  --css    "<TOOLKIT_PATH>/templates/style/report-style.css"
```

---

## PLATFORM_KNOWLEDGE

### PodDisruptionBudget patterns

```yaml
# CORRECT — minAvailable leaves 1 pod up during drain
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: myapp-pdb
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: myapp

# CORRECT — maxUnavailable allows 1 pod down at a time
spec:
  maxUnavailable: 1

# WRONG — blocks all disruptions (node drain will hang)
spec:
  minAvailable: 2   # when replicas == 2

# WRONG — allows total outage
spec:
  maxUnavailable: 100%
```

### Pod anti-affinity pattern (spread across nodes)

```yaml
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchLabels:
              app: myapp
          topologyKey: kubernetes.io/hostname
```

### TopologySpreadConstraints (spread across zones)

```yaml
topologySpreadConstraints:
  - maxSkew: 1
    topologyKey: topology.kubernetes.io/zone
    whenUnsatisfiable: DoNotSchedule
    labelSelector:
      matchLabels:
        app: myapp
```

### Graceful termination with preStop hook

```yaml
containers:
  - name: myapp
    lifecycle:
      preStop:
        exec:
          command: ["/bin/sh", "-c", "sleep 5"]
    terminationGracePeriodSeconds: 30
```

### QoS class determination

| QoS Class | Condition | Eviction priority |
|-----------|-----------|-------------------|
| Guaranteed | requests == limits for all containers | Last evicted |
| Burstable | requests set but != limits | Middle |
| BestEffort | No requests set | First evicted |

### RollingUpdate strategy (zero-downtime)

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 0    # never take a pod down before new one is Ready
    maxSurge: 1          # allow one extra pod during update
```

### Disruption simulation rules

During a **node drain** (e.g. OCP node upgrade):
- All pods on the drained node are evicted
- PDB `disruptionsAllowed` controls whether eviction is allowed
- If `disruptionsAllowed: 0`, the drain hangs indefinitely → **upgrade blocker**

During a **zone failure**:
- All pods on nodes in that zone are lost simultaneously
- Anti-affinity and topologySpreadConstraints determine if pods exist in other zones
- Services route traffic to surviving pods (readiness probe gates this)

During a **rolling OCP upgrade** (4.x minor version):
- Nodes are drained one at a time by the Machine Config Operator
- Each node drain is a PDB check point
- All workloads without PDBs are evicted without constraint

---

## Sources and References

Every check (R01–R15) and remediation recommendation must cite the applicable standard ID
so readers can trace guidance back to its authoritative source.

### Kubernetes Documentation

| ID | Standard | Reference |
|----|----------|-----------|
| K8S-01 | Configure Pod Disruption Budgets | [kubernetes.io](https://kubernetes.io/docs/tasks/run-application/configure-pdb/) |
| K8S-02 | Configure Liveness, Readiness, and Startup Probes | [kubernetes.io](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) |
| K8S-03 | Horizontal Pod Autoscaling | [kubernetes.io](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/) |
| K8S-04 | Assigning Pods to Nodes — Affinity and Anti-Affinity | [kubernetes.io](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/) |
| K8S-05 | Pod Lifecycle — Termination and preStop hooks | [kubernetes.io](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-termination) |
| K8S-06 | Pod Quality of Service Classes (Guaranteed / Burstable / BestEffort) | [kubernetes.io](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/) |
| K8S-07 | Persistent Volumes — Access Modes (RWO vs RWX) | [kubernetes.io](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#access-modes) |
| K8S-08 | Pod Priority and Preemption | [kubernetes.io](https://kubernetes.io/docs/concepts/scheduling-eviction/pod-priority-preemption/) |
| K8S-09 | Deployment Update Strategy (RollingUpdate vs Recreate) | [kubernetes.io](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#strategy) |
| K8S-10 | Topology Spread Constraints (zone-level HA) | [kubernetes.io](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/) |

### OpenShift Platform

| ID | Standard | Reference |
|----|----------|-----------|
| OCP-01 | OpenShift — Node Management, Events, and OOMKill detection | [OCP Node Docs](https://docs.openshift.com/container-platform/4.14/nodes/nodes/nodes-nodes-working.html) |
| OCP-02 | OpenShift — Machine Config Operator: rolling node upgrade drains pods one node at a time | [OCP MCO Docs](https://docs.openshift.com/container-platform/4.14/post_installation_configuration/machine-configuration-tasks.html) |
| OCP-03 | OpenShift — PodDisruptionBudget support during node drain | [OCP PDB Docs](https://docs.openshift.com/container-platform/4.14/nodes/pods/nodes-pods-configuring.html) |

### BC Gov Platform Services

| ID | Standard | Reference |
|----|----------|-----------|
| PS-01 | Platform Services — PriorityClass requirement | [docs.developer.gov.bc.ca](https://docs.developer.gov.bc.ca/) |
| PS-02 | Platform Services — Resource Requests (Burstable QoS minimum) | [docs.developer.gov.bc.ca](https://docs.developer.gov.bc.ca/) |
| PS-03 | Platform Services — Health Probes and Deployment Readiness | [docs.developer.gov.bc.ca](https://docs.developer.gov.bc.ca/) |

### ag-devops Policy Standards

| ID | Standard | Enforcement |
|----|----------|-------------|
| AD-01 | PriorityClass required on all workloads | Polaris `priorityClassNotSet` audit |
| AD-02 | Resource requests required on all containers | Polaris `requestsNotSet` audit |
