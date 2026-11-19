# OpenShift Collection & Toolkits

Manual `oc` CLI collection commands, repository inspection commands, and automated toolkit usage for migration and resilience analyses.

## Contents

- [Migration Namespace Collection](#migration-namespace-collection)
- [Resilience Namespace Collection](#resilience-namespace-collection)
- [Probe & Affinity JSON Extraction](#probe--affinity-json-extraction)
- [Generate `manifest-summary.md`](#generate-manifest-summarymd)
- [Repository Collection](#repository-collection)
- [Automated Toolkits](#automated-toolkits)
- [GitOps Migration Export (`get_ns_resources.sh` Pattern)](#gitops-migration-export-get_ns_resourcessh-pattern)

---

## Migration Namespace Collection

Run for each environment (`dev`, `test`, `prod`, `tools`) in the namespace prefix. Substitute `<NS>` with `<ns-prefix>-<env>`:

```bash
mkdir -p working/<NS>

# Workload inventory (dc covers DeploymentConfig still used on Silver/Gold; cronjob for Kyverno checks)
oc get dc,deployment,statefulset,daemonset,cronjob -n <NS> -o yaml > working/<NS>/workloads.yaml

# Services and Routes
oc get svc,route -n <NS> -o yaml > working/<NS>/network-svc-routes.yaml

# Persistent storage (storageclass is cluster-scoped — split from namespace-scoped pvc)
oc get pvc -n <NS> -o yaml > working/<NS>/pvcs.yaml
oc get storageclass -o yaml > working/<NS>/storageclasses.yaml  # omit if RBAC restricts

# Secret names (no values — security boundary)
oc get secret -n <NS> --no-headers | awk '{print $1, $2}' > working/<NS>/secret-names.txt

# ConfigMap names and sizes
oc get configmap -n <NS> --no-headers > working/<NS>/configmap-names.txt

# NetworkPolicies
oc get networkpolicy -n <NS> -o yaml > working/<NS>/networkpolicies.yaml

# Build objects (indicates old OCP S2I patterns)
oc get bc,is -n <NS> -o yaml > working/<NS>/build-objects.yaml

# Resource quotas and limits
oc get resourcequota,limitrange -n <NS> -o yaml > working/<NS>/resource-quotas.yaml

# PrometheusRules (AlertManager / custom alerting rules)
oc get prometheusrule -n <NS> -o yaml > working/<NS>/prometheus-rules.yaml 2>/dev/null || true

# Events (recent errors or warnings)
oc get events -n <NS> --sort-by='.lastTimestamp' | tail -30 > working/<NS>/events.txt

# Image digests for running pods
oc get pods -n <NS> -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{range .spec.containers[*]}{.image}{"\n"}{end}{end}' > working/<NS>/image-refs.txt
```

---

## Resilience Namespace Collection

Run against each environment suffix (`-dev`, `-test`, `-prod`, `-tools`). Store output in `<OUTPUT>/<ns-prefix>-<env>/`:

```bash
NS="<ns-prefix>-<env>"
OUT="<OUTPUT>/${NS}"
mkdir -p "${OUT}"

# Core workloads
oc get dc,deployment,statefulset,daemonset,cronjob -n "${NS}" -o yaml > "${OUT}/workloads.yaml"
oc get dc,deployment,statefulset,daemonset -n "${NS}" \
  -o custom-columns='NAME:.metadata.name,KIND:.kind,REPLICAS:.spec.replicas,STRATEGY:.spec.strategy.type,PROGRESSING:.status.conditions[?(@.type=="Progressing")].status' \
  > "${OUT}/workload-summary.txt"

# PodDisruptionBudgets — PRIMARY target
oc get pdb -n "${NS}" -o yaml > "${OUT}/pdbs.yaml"
oc get pdb -n "${NS}" \
  -o custom-columns='NAME:.metadata.name,MIN-AVAILABLE:.spec.minAvailable,MAX-UNAVAILABLE:.spec.maxUnavailable,CURRENT-HEALTHY:.status.currentHealthy,DESIRED-HEALTHY:.status.desiredHealthy,DISRUPTED:.status.disruptedPods,DISRUPTIONS-ALLOWED:.status.disruptionsAllowed' \
  > "${OUT}/pdb-summary.txt" 2>&1 || echo "No PDBs found" >> "${OUT}/pdb-summary.txt"

# Horizontal & Vertical Pod Autoscalers
oc get hpa -n "${NS}" -o yaml > "${OUT}/hpas.yaml"
oc get hpa -n "${NS}" \
  -o custom-columns='NAME:.metadata.name,TARGET:.spec.scaleTargetRef.name,MIN:.spec.minReplicas,MAX:.spec.maxReplicas,CURRENT:.status.currentReplicas,CPU-TARGET:.spec.metrics[0].resource.target.averageUtilization' \
  > "${OUT}/hpa-summary.txt" 2>&1 || echo "No HPAs found" >> "${OUT}/hpa-summary.txt"
oc get vpa -n "${NS}" -o yaml > "${OUT}/vpas.yaml" 2>/dev/null || echo "# VPA not available" > "${OUT}/vpas.yaml"

# Pod topology and scheduling
oc get pod -n "${NS}" -o wide > "${OUT}/pods-wide.txt"
oc get pod -n "${NS}" -o yaml > "${OUT}/pods.yaml"

# Resource quotas, PVCs, and Services
oc get resourcequota,limitrange -n "${NS}" -o yaml > "${OUT}/quota.yaml"
oc get pvc -n "${NS}" -o yaml > "${OUT}/pvcs.yaml"
oc get pvc -n "${NS}" \
  -o custom-columns='NAME:.metadata.name,STATUS:.status.phase,CAPACITY:.status.capacity.storage,ACCESS:.spec.accessModes,STORAGECLASS:.spec.storageClassName' \
  > "${OUT}/pvc-summary.txt" 2>&1 || echo "No PVCs" >> "${OUT}/pvc-summary.txt"
oc get svc -n "${NS}" -o yaml > "${OUT}/services.yaml"

# Disruption/eviction events
oc get events -n "${NS}" \
  --field-selector reason=Evicted,reason=OOMKilled,reason=BackOff,reason=Unhealthy \
  --sort-by='.lastTimestamp' > "${OUT}/disruption-events.txt" 2>&1 || true
oc get events -n "${NS}" --sort-by='.lastTimestamp' | tail -50 > "${OUT}/recent-events.txt"

# Priority classes, node distribution, and rollout history
oc get pod -n "${NS}" -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.priorityClassName}{"\n"}{end}' \
  > "${OUT}/priority-classes.txt"
oc get pod -n "${NS}" -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.nodeName}{"\t"}{.metadata.labels.app}{"\n"}{end}' \
  > "${OUT}/pod-node-distribution.txt"
oc rollout history deployment -n "${NS}" 2>/dev/null > "${OUT}/rollout-history.txt" || true
```

---

## Probe & Affinity JSON Extraction

```bash
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
```

---

## Generate `manifest-summary.md`

```bash
cat > "${OUT}/../manifest-summary.md" << EOF
# Resilience Collection Summary
Namespace prefix: <ns-prefix>
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

## Repository Collection

```bash
gh repo clone <OWNER/REPO> working/repo -- --depth=1

find working/repo/.github/workflows -name '*.yml' -o -name '*.yaml' | sort
find working/repo -name 'Containerfile' -o -name 'Dockerfile' | sort
find working/repo -maxdepth 4 \( -name 'pom.xml' -o -name 'build.gradle' \
  -o -name 'package.json' -o -name '*.csproj' -o -name '*.sln' \) | sort
find working/repo -name 'Chart.yaml' -o -name 'values.yaml' | sort
find working/repo -name '*.yaml' -print0 | xargs -0 grep -l 'kind: Deployment\|kind: DeploymentConfig' 2>/dev/null | head -20
grep -r 'livenessProbe\|readinessProbe\|startupProbe' working/repo --include='*.yaml' -l
find working/repo -name '*.yaml' -print0 | xargs -0 grep -l 'kind: NetworkPolicy' 2>/dev/null
```

---

## Automated Toolkits

### `ocp-migration-toolkit`

```bash
cd ocp-migration-toolkit
./collect/collect.sh \
  --namespace <ns-prefix> \
  --cluster silver \
  --repo <org>/<app-repo> \
  --target emerald \
  --output working/
```

GitHub Action invocation:

```yaml
- uses: <org>/ocp-migration-toolkit@main
  with:
    namespace: <ns-prefix>
    cluster: silver
    repo: <org>/<app-repo>
    target: emerald
    oc-token: ${{ secrets.OC_SA_TOKEN }}
    gh-token: ${{ secrets.GITHUB_TOKEN }}
```

### `ocp-resilience-toolkit`

```bash
./ocp-resilience-toolkit/collect/collect.sh --namespace <ns-prefix> --cluster silver --output ./data
```

---

## GitOps Migration Export (`get_ns_resources.sh` Pattern)

When migrating an existing namespace not yet managed by Kustomize/Helm into an Argo CD manifest repo, export `configmap`, `deployment`, `deploymentconfig`, `route`, `service`, and `statefulset` (excluding `Secret`s) using `oc` + `jq` + `yq` while stripping OpenShift-injected runtime metadata:

```bash
for resource in configmap deployment deploymentconfig route service statefulset; do
  for name in $(oc get "$resource" -n <NS> -o custom-columns=NAME:.metadata.name --no-headers); do
    oc get "$resource" "$name" -n <NS> -o json | jq '
      del(.metadata.annotations["kubectl.kubernetes.io/last-applied-configuration"],
          .metadata.creationTimestamp, .metadata.generation, .metadata.managedFields,
          .metadata.resourceVersion, .metadata.selfLink, .metadata.uid,
          .spec.clusterIP, .status)' | yq -P eval > "manifests/${resource}.${name}.yaml"
  done
done
```
