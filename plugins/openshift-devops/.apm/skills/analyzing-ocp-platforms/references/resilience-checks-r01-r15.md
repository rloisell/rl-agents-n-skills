# Resilience Checks (R01–R15) & Patterns

Workload resilience assessment criteria (R01–R15), A–F grading rubric, Kubernetes resilience patterns, and disruption simulation rules.

## Contents

- [Resilience Check Categories (R01–R15)](#resilience-check-categories-r01r15)
- [Gap Scoring](#gap-scoring)
- [PodDisruptionBudget Patterns](#poddisruptionbudget-patterns)
- [Pod Anti-Affinity & TopologySpreadConstraints](#pod-anti-affinity--topologyspreadconstraints)
- [Graceful Termination & RollingUpdate](#graceful-termination--rollingupdate)
- [QoS Class Determination](#qos-class-determination)
- [Automated Scale-Down (Tuesday 8 PM)](#automated-scale-down-tuesday-8-pm)
- [3-Pod HA Database & PVC Headroom](#3-pod-ha-database--pvc-headroom)
- [Resource Quotas, Auto-Approval & CPU Tuning](#resource-quotas-auto-approval--cpu-tuning)
- [Defunct PIDs & PID 1 Reaper Check](#defunct-pids--pid-1-reaper-check)
- [Post-Outage Recovery Checklist](#post-outage-recovery-checklist)
- [Disruption Simulation Rules](#disruption-simulation-rules)

---

## Resilience Check Categories (R01–R15)

Assess each workload against R01–R15. Assign a grade (`A`/`B`/`C`/`D`/`F`) and severity (`⛔ CRITICAL` / `⚠ HIGH` / `ℹ LOW`). Cite standards from [standards-catalog.md](standards-catalog.md).

| ID | Category | Failing Condition | Severity | Standard / Source |
|---|---|---|---|---|
| R01 | PodDisruptionBudget missing | No PDB for a Deployment/StatefulSet with replicas > 1 | ⛔ CRITICAL | K8S-01; OCP-02 |
| R02 | PDB misconfigured | `minAvailable: 0` OR `maxUnavailable: 0` (overridden by Platform Ops) OR `maxUnavailable: 100%` OR PDB blocks ALL disruptions (`minAvailable == replicas`) OR PDB present on `<3` DB pods | ⛔ CRITICAL | K8S-01; PS-05 |
| R03 | Single replica | `replicas: 1` with no HPA min ≥ 2 | ⛔ CRITICAL | K8S-03 |
| R04 | No liveness probe | Missing `livenessProbe` on any container | ⚠ HIGH | K8S-02; PS-03 |
| R05 | No readiness probe | Missing `readinessProbe` on any container | ⚠ HIGH | K8S-02; PS-03 |
| R06 | No HPA / scaling | No HPA and `replicas` is static (not StatefulSet with known single-instance requirement) | ⚠ HIGH | K8S-03 |
| R07 | No pod anti-affinity | No `podAntiAffinity` or `topologySpreadConstraints` on multi-replica workloads | ⚠ HIGH | K8S-04; K8S-10 |
| R08 | No graceful termination | `terminationGracePeriodSeconds` `< 10` OR `> 600` (Platform Ops force-kill cap during node drain) OR no `preStop` hook where needed | ⚠ HIGH | K8S-05; PS-05 |
| R09 | Non-Guaranteed QoS / BestEffort | Missing `resources.requests` (`LimitRange` `default-limits` injects `50m`/`256Mi` + memory limit → **Burstable** QoS) or explicit `0` requests & limits (**BestEffort** QoS) → not Guaranteed QoS in `prod` | ⚠ HIGH | K8S-06; AD-02; PS-05; PS-09 |
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

- Always set `unhealthyPodEvictionPolicy: AlwaysAllow` so stuck/unhealthy pods do not block node drains.
- Never set `maxUnavailable: 0` (overridden by Platform Operations during patching/drains).
- **Databases**: Use `minAvailable: 2` for 3-pod HA Patroni/MongoDB clusters; **do not** create a PDB if a database has `< 3` pods.

```yaml
# CORRECT — minAvailable leaves 1 pod up during drain + AlwaysAllow
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: myapp-pdb
spec:
  minAvailable: 2   # e.g. for 3-pod HA DB or 3-replica app
  selector:
    matchLabels:
      app: myapp
  unhealthyPodEvictionPolicy: AlwaysAllow

# CORRECT — maxUnavailable allows 1 pod down at a time
spec:
  maxUnavailable: 1
  unhealthyPodEvictionPolicy: AlwaysAllow

# WRONG — blocks all disruptions (node drain hangs; maxUnavailable: 0 is overridden by Platform Ops)
spec:
  minAvailable: 2   # when replicas == 2
  # or maxUnavailable: 0

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

Ensure containers handle `SIGTERM` cleanly and keep `terminationGracePeriodSeconds` between `10` and `600` seconds. Platform Operations caps node-drain grace periods at `600s` and force-kills any pod still running past that limit (`PS-05`).

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
| BestEffort | Requests and limits explicitly set to `0` | First evicted |

- **Guaranteed QoS in `prod`**: Platform Services recommends Guaranteed QoS (`requests == limits`) for `prod` workloads requiring highest uptime (`PS-05`).
- **`limits.cpu` CFS throttling trade-off**: For general/non-prod workloads or latency-sensitive services, Platform Services resource-tuning guidance notes avoiding `limits.cpu` to prevent Linux CFS bandwidth throttling while still setting `requests.cpu`, `requests.memory`, and `limits.memory`. Document this trade-off explicitly when recommending Guaranteed QoS.
- **`LimitRange` (`default-limits`) behavior** (`PS-09`): Omitting `requests` or `limits` does **not** produce `BestEffort`; OpenShift injects `default-limits` (`defaultRequest: cpu 50m, memory 256Mi`; `default` memory limit = `min(namespace memory quota, 16Gi)`, no default CPU limit). `BestEffort` only occurs when `requests` and `limits` are explicitly `0` via CLI/manifest.

---

## Automated Scale-Down (Tuesday 8 PM)

Platform Services runs automated reclamation every **Tuesday at 8:00 PM** on production clusters (`PS-07`). Flag any workload matching:

1. **Stale image/deployment**: `status.conditions[?(@.type=="Progressing")].lastUpdateTime` older than **1 year** (note: `Available` only tracks pod restarts, not image/spec updates).
2. **Chronic crash looping**: Pod restart count **> 100** (or `CrashLoopBackOff` > 1 day, which Platform Ops may delete/scale down).

**Behavior**: Non-ArgoCD workloads are scaled to `replicas: 0` and Product Owner / Technical Leads receive email notifications from the Product Registry. ArgoCD-managed workloads receive warning emails (since ArgoCD would otherwise scale them back up). Remediation requires rebuilding/updating the image or fixing the crash root cause before scaling back up.

---

## 3-Pod HA Database & PVC Headroom

For stateful database clusters (Patroni or CrunchyDB Postgres Operator):

- **Topology**: 3 pods (`1` primary + `2` read-only secondaries), each with its own dedicated `ReadWriteOnce` (`RWO`) PVC using `netapp-block-standard` (`3x` DB size total), and all 3 pods sized for primary load.
  - **CrunchyDB (`PostgresCluster`)**: Deploys **3 StatefulSets × 1 pod** each (operator-managed Services, Secrets, PDBs, PVCs, `pgbouncer` connection pooling, `pgbackrest` PITR). Deploy via `bcgov/crunchy-postgres` Helm chart (if using **Helm v4**, pass `--server-side=false` to avoid version-mismatch errors).
  - **Standalone Patroni**: Deploys **1 StatefulSet × 3 pods** + 3 ConfigMaps for leader/failover tracking. Community Helm chart: `bcgov/nr-patroni-chart` (pair with `bcgov/backup-container` and a separate PDB).
- **PDB**: `minAvailable: 2` for 3-pod clusters; **no PDB** if running `< 3` DB pods.
- **Management Hierarchy (CRITICAL)**: **Never** run `patronictl` or manually edit Kubernetes objects on a CrunchyDB deployment — always manage via the `PostgresCluster` CR so the operator does not conflict or overwrite state. Use `patronictl` (`patronictl list`) only on standalone Patroni.
- **WAL / Timeline Lag & PVC Headroom (`>= 20%` free)**:
  - Patroni halts/refuses to start at **90%** disk usage (`<= 80%` alert threshold; AlertManager `KubePersistentVolumeFillingUp` fires at `97%` or 4-day fill prediction; `PS-08`).
  - Keep `>= 20%` PVC free for WAL growth. If a secondary lags too long and the primary purges needed WALs, `patronictl list` shows extreme lag and logs show missing WAL files or a **forked timeline**.
  - On CrunchyDB, WAL archives purge only when a backup completes — run backups or archive WALs more frequently (or offload to OCIO S3) if the repo volume fills up.
- **Storage Migration**: Use [`bcgov/StorageMigration`](https://github.com/bcgov/StorageMigration) to migrate data between PVCs, `StorageClass`es, or larger volumes.

---

## Resource Quotas, Auto-Approval & CPU Tuning

- **Default Project Set Quotas (`PS-09`)**: `0.5` CPU request, `2 GB` RAM request, `60` PVCs, `1 GB` storage (`521 MB` backup storage, `5` snapshots).
- **Quota Objects**: `compute-long-running-quota` (deployments/statefulsets), `compute-time-bound-quota` (jobs/builds/deployers), `compute-best-effort-quota` (`0` requests & limits).
- **Registry Auto-Approval Thresholds**:
  - **CPU / Memory**: `>= 35%` long-term utilization (`Template - Resources Quota Approve Dashboard` in Sysdig), `> 85%` of total memory limit (for memory requests), and increase `<= 50%` OR minimum step (`1 core` CPU / `2 GB` memory).
  - **Storage**: `> 80%` PVC limit utilization, and increase `<= 50%` OR `32 GB` minimum step.
  - **Decreases**: Always auto-approved.
- **CPU Ratios & CFS Throttling**: Target CPU request:utilization of **3:1** (good), **2:1** (great), or **1.5:1** (amazing). Omit `limits.cpu` to prevent Linux CFS throttling; diagnose throttling via PromQL:
  ```promql
  avg(container_cpu_cfs_throttled_periods_total / container_cpu_cfs_periods_total {namespace=~"<license-plate>-.*", pod=~".*", container_name!="POD", image!=""}) BY (namespace)
  ```

---

## Defunct PIDs & PID 1 Reaper Check

Containers running multiple processes or `exec` health probes without a PID 1 init reaper accumulate **defunct (zombie) PIDs**, threatening node kernel stability and triggering platform alert emails (`PS-05`). Flag containers lacking an init reaper (`Tini`, `dumb-init`, or `s6-overlay` as `ENTRYPOINT`); immediate relief is deleting the pod, permanent fix is adding an init reaper `ENTRYPOINT`.

---

## Post-Outage Recovery Checklist

Include this operational verification checklist in resilience reports for platform-wide outage readiness (`PS-05`, `PS-08`):

- **Status & Channels**: Monitor MS Teams `OpenShift-alerts` / `OpenShift-emergencyhelp` and the off-site status page (`https://status.developer.gov.bc.ca`).
- **Workloads**: Verify pods scaled back up and check for `CrashLoopBackOff` or `ImagePullBackOff` (verify image integrity in Artifactory/registry).
- **Stale Route → Pod Recovery**: If a Route exists and pods look healthy/Ready but traffic fails, delete the pod to force endpoint/Route re-attachment.
- **CI/CD & Messaging**: Restart `tools` namespace pipeline pods (e.g., Jenkins) and run a test pipeline; restart RabbitMQ pods if networking was disrupted.
- **Backups**: Run a manual backup recovery test to confirm the latest backup is intact and scheduled jobs resume.

---

## Disruption Simulation Rules

- **Node drain (e.g., OCP node upgrade)**: All pods on the drained node are evicted. PDB `disruptionsAllowed` controls whether eviction proceeds; if `0`, the drain hangs indefinitely (**upgrade blocker**).
- **Zone failure**: All pods on nodes in that zone are lost simultaneously. Anti-affinity and `topologySpreadConstraints` determine if pods exist in other zones; readiness probes gate traffic routing.
- **Rolling OCP upgrade (4.x minor version)**: Machine Config Operator drains nodes one at a time. Each drain is a PDB checkpoint; workloads without PDBs are evicted without constraint.

---

## Application & Release Continuity

Evaluating zero-downtime release and failover continuity requires separating operational state from architectural proof:

### 1. Three Separate Lifecycles

Never conflate deployment health with proven continuity:

- **Run status**: Point-in-time pod/rollout health (e.g., `Ready`, `Progressing`, recent deployment succeeded).
- **Design approval**: Governance/architecture sign-off on the intended HA, rollback, and failover design.
- **Continuity verdict**: Evidence-based assessment of actual release/disruption continuity:
  - `not-assessed`: Continuity behavior has not been evaluated.
  - `cannot-establish`: Missing manifests, telemetry, or test evidence prevents a conclusion.
  - `designed-not-demonstrated`: Probes, PDBs, and anti-affinity are configured, but live failover/rollout continuity has not been exercised. *(Probes and PDBs alone only establish `designed-not-demonstrated`.)*
  - `demonstrated`: Observed under controlled rollout, drain, or failover testing without dropped requests, corrupt state, or manual intervention.

### 2. N-1 Version Overlap

During rolling updates, old (`N-1`) and new (`N`) pod revisions serve traffic concurrently. Verify backward/forward compatibility across:

- **APIs & payloads**: Additive, backward-compatible request/response schemas.
- **Events & queues**: Consumers must tolerate both `N-1` and `N` message envelopes.
- **Background jobs**: Enqueued jobs from `N` must not fail if picked up by `N-1` workers (and vice versa).
- **Serialized sessions & caches**: Shared Redis/session formats and cache keys must remain mutually readable or version-prefixed.
- **Versioned SPA assets**: Serve hashed/versioned frontend bundles across overlapping revisions so clients hitting `N-1` index HTML do not 404 on `N` chunk requests.

### 3. Expand-Contract Database Evolution

Decouple schema changes from application rollouts across four distinct phases:

1. **Expansion**: Add nullable columns, new tables, or dual-write triggers compatible with `N-1`.
2. **Transition**: Deploy `N` application code that reads/writes the expanded schema while `N-1` still runs safely.
3. **Backfill & validation**: Populate and verify historical rows out-of-band before enforcing constraints.
4. **Contraction**: Drop legacy columns/constraints only after `N-1` is fully retired and rollback to `N-1` is no longer needed.

- **"Online" DDL caveat**: Database "online" DDL (e.g., `ALTER TABLE ... ALGORITHM=INPLACE` or `CONCURRENTLY`) is not automatically non-blocking—metadata locks and lock-wait queues can still stall concurrent queries.
- **DB restore is not zero-loss rollback**: Point-in-time recovery (PITR) or snapshot restore discards writes committed after the restore point; design application-level rollback around forward-compatible schemas.

### 4. Worker/Scheduler Drain & Shutdown Timeline Budget

- **Decouple job acquisition from HTTP routing**: Stop polling/claiming new queue or cron work immediately on `SIGTERM` (independently of readiness probe removal).
- **Bound drain to lease/visibility timeout**: Finish in-flight jobs within the queue's lease/visibility window so tasks are not redelivered mid-processing; if unable to finish, checkpoint or release the lease cleanly.
- **Singleton fencing**: Use distributed leases/fencing tokens for singleton schedulers so a terminating pod cannot overlap with a newly elected leader.
- **WebSocket/SSE bounded drain**: Close long-lived streams gracefully with a bounded drain window and client reconnect jitter rather than waiting indefinitely.
- **Single shared `terminationGracePeriodSeconds` budget**: Pre-stop hooks (`preStop`), readiness propagation delay, HTTP in-flight drain, worker lease drain, and `SIGKILL` all share **one** `terminationGracePeriodSeconds` clock. Size `terminationGracePeriodSeconds` strictly greater than `preStop + max(httpDrain, workerDrain)` so Kubernetes does not send `SIGKILL` mid-drain.
