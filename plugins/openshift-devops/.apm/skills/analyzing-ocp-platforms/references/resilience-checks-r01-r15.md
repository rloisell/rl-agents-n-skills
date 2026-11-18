# Resilience Checks (R01–R15) & Patterns

Workload resilience assessment criteria (R01–R15), A–F grading rubric, Kubernetes resilience patterns, and disruption simulation rules.

## Contents

- [Resilience Check Categories (R01–R15)](#resilience-check-categories-r01r15)
- [Gap Scoring](#gap-scoring)
- [PodDisruptionBudget Patterns](#poddisruptionbudget-patterns)
- [Pod Anti-Affinity & TopologySpreadConstraints](#pod-anti-affinity--topologyspreadconstraints)
- [Graceful Termination & RollingUpdate](#graceful-termination--rollingupdate)
- [QoS Class Determination](#qos-class-determination)
- [Disruption Simulation Rules](#disruption-simulation-rules)

---

## Resilience Check Categories (R01–R15)

Assess each workload against R01–R15. Assign a grade (`A`/`B`/`C`/`D`/`F`) and severity (`⛔ CRITICAL` / `⚠ HIGH` / `ℹ LOW`). Cite standards from [standards-catalog.md](standards-catalog.md).

| ID | Category | Failing Condition | Severity | Standard / Source |
|---|---|---|---|---|
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

---

## Gap Scoring

- **Grade A**: 0 CRITICAL, 0 HIGH
- **Grade B**: 0 CRITICAL, ≤ 2 HIGH
- **Grade C**: 0 CRITICAL, > 2 HIGH
- **Grade D**: 1 CRITICAL
- **Grade F**: 2+ CRITICAL

Use `RES-NN` task numbering (e.g., `RES-01`, `RES-02`) for remediation tasks.

---

## PodDisruptionBudget Patterns

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

---

## Pod Anti-Affinity & TopologySpreadConstraints

### Pod anti-affinity (spread across nodes)

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

---

## Graceful Termination & RollingUpdate

### Graceful termination with `preStop` hook

```yaml
containers:
  - name: myapp
    lifecycle:
      preStop:
        exec:
          command: ["/bin/sh", "-c", "sleep 5"]
    terminationGracePeriodSeconds: 30
```

### RollingUpdate strategy (zero-downtime)

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 0    # never take a pod down before new one is Ready
    maxSurge: 1          # allow one extra pod during update
```

---

## QoS Class Determination

| QoS Class | Condition | Eviction priority |
|---|---|---|
| Guaranteed | `requests == limits` for all containers | Last evicted |
| Burstable | `requests` set but `!= limits` | Middle |
| BestEffort | No `requests` set | First evicted |

---

## Disruption Simulation Rules

- **Node drain (e.g., OCP node upgrade)**: All pods on the drained node are evicted. PDB `disruptionsAllowed` controls whether eviction proceeds; if `0`, the drain hangs indefinitely (**upgrade blocker**).
- **Zone failure**: All pods on nodes in that zone are lost simultaneously. Anti-affinity and `topologySpreadConstraints` determine if pods exist in other zones; readiness probes gate traffic routing.
- **Rolling OCP upgrade (4.x minor version)**: Machine Config Operator drains nodes one at a time. Each drain is a PDB checkpoint; workloads without PDBs are evicted without constraint.
