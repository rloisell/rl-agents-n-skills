# bc-resilience-service/SKILL.md
# Ryan Loisell — Developer / Architect | GitHub Copilot | April 2026
#
# Tier 3 GitHub Copilot Extension — OCP Resilience Posture Analysis
# Deployed on Emerald OpenShift (be808f namespace)

## Overview

`bc-resilience-service` is a GitHub Copilot Extension that performs on-demand
OpenShift workload resilience analysis. Users invoke it from GitHub Copilot Chat:

```
@bc-resilience analyze namespace:f1b263 [repo:owner/name] [cluster:silver] [envs:dev,prod]
```

The service:
1. Collects live OCP resource data via `oc` CLI (PDBs, HPAs, Deployments, etc.)
2. Calls GitHub Models API (GPT-4o) to analyse 15 resilience gap categories
3. Streams a structured report (R01–R15, grade A–F) as SSE delta chunks
4. Renders the report to PDF and uploads it as a GitHub Release asset

---

## Architecture

```
GitHub Copilot Chat
        │  POST /api/v1/extension  (HMAC-SHA256)
        ▼
bc-resilience-service  ←  Emerald be808f-{dev,test,prod}
  Fastify 5 | Node 22 | TypeScript 5
        │
        ├── bash collect.sh  (ocp-resilience-toolkit submodule)
        │     └── oc CLI  →  OCP Silver/Gold APIs  (cluster-reader SA)
        │
        ├── GitHub Models API  openai/gpt-4o  (SSE streaming)
        │
        ├── pandoc + Chromium  →  PDF
        │
        └── Octokit  →  GitHub Releases  (PDF + markdown)  →  URL in chat
```

---

## 15 Resilience Check Categories

| ID  | Severity | Grade Impact | Description |
|-----|----------|-------------|-------------|
| R01 | ⛔ CRITICAL | D/F | PDB missing on multi-replica Deployment/StatefulSet |
| R02 | ⛔ CRITICAL | D/F | PDB misconfigured (minAvailable:0 or maxUnavailable:100%) |
| R03 | ⛔ CRITICAL | D/F | Single replica with no HPA minReplicas ≥ 2 |
| R04 | ⚠ HIGH | B/C | No liveness probe |
| R05 | ⚠ HIGH | B/C | No readiness probe |
| R06 | ⚠ HIGH | B/C | No HPA — static scaling only |
| R07 | ⚠ HIGH | B/C | No pod anti-affinity on multi-replica workloads |
| R08 | ⚠ HIGH | B/C | No graceful termination (terminationGracePeriodSeconds < 10 or no preStop) |
| R09 | ⚠ HIGH | B/C | BestEffort QoS — missing resources.requests |
| R10 | ⛔ CRITICAL | D/F | RWO PVC on Deployment with replicas > 1 |
| R11 | ℹ INFO | A | No startup probe on long-starting containers |
| R12 | ⚠ HIGH | B/C | Recreate update strategy on a user-facing Deployment |
| R13 | ℹ INFO | A | No PriorityClass assigned |
| R14 | ⚠ HIGH | B/C | Recent OOMKill or Eviction events |
| R15 | ⛔ CRITICAL | D/F | Live PDB violation (disruptionsAllowed:0, currentHealthy < desiredHealthy) |

### Grading Scale

| Grade | Criteria |
|-------|----------|
| A | 0 CRITICAL, 0 HIGH |
| B | 0 CRITICAL, ≤ 2 HIGH |
| C | 0 CRITICAL, > 2 HIGH |
| D | 1 CRITICAL |
| F | 2+ CRITICAL |

**Task ID format:** `RES-NN`

---

## GitHub App Registration

1. Go to **GitHub → Settings → Developer settings → GitHub Apps → New GitHub App**
2. **App name:** `BC Resilience Service`
3. **Webhook URL:** `https://bc-resilience-<env>.apps.silver.devops.gov.bc.ca/api/v1/extension`
4. **Webhook secret:** Generate random 32-char secret → store in Vault
5. **Permissions:**
   - Repository: Contents (read), Metadata (read)
   - Copilot Chat: `copilot_chat` (write)
6. **Subscribe to events:** `push` (optional, for repo cross-reference)
7. **Where can this app be installed?** Any account
8. After creation: note **App ID**, generate + download **private key** → store in Vault

---

## Vault Secrets

Path: `secret/data/be808f-<env>/bc-resilience-service`

| Secret Key | Description |
|------------|-------------|
| `GITHUB_APP_ID` | GitHub App numeric ID |
| `GITHUB_APP_PRIVATE_KEY` | GitHub App RSA private key (PEM, base64 or raw) |
| `GITHUB_APP_WEBHOOK_SECRET` | HMAC-SHA256 webhook secret |
| `GITHUB_MODELS_API_KEY` | GitHub PAT with `models:read` scope |
| `OC_SILVER_TOKEN` | OCP Silver service account token (cluster-reader role) |
| `OC_GOLD_TOKEN` | OCP Gold service account token (cluster-reader role) |

```bash
# Write secrets to Vault (example)
vault kv put secret/be808f-dev/bc-resilience-service \
  GITHUB_APP_ID=12345 \
  GITHUB_APP_PRIVATE_KEY="$(cat private-key.pem)" \
  GITHUB_APP_WEBHOOK_SECRET="$(openssl rand -hex 32)" \
  GITHUB_MODELS_API_KEY="ghp_..." \
  OC_SILVER_TOKEN="$(oc serviceaccounts get-token bc-resilience-reader -n be808f-dev)" \
  OC_GOLD_TOKEN="..."
```

---

## Firewall Change Requests (FWCRs)

All egress is NetworkPolicy-controlled. The following external destinations require FWCRs:

| Destination | Port | Protocol | Justification |
|-------------|------|----------|---------------|
| `api.github.com` | 443 | HTTPS | GitHub Copilot Extensions API, GitHub Releases upload |
| `models.inference.ai.azure.com` | 443 | HTTPS | GitHub Models API (GPT-4o inference) |
| `api.silver.devops.gov.bc.ca` | 6443 | HTTPS | OCP Silver cluster API (namespace data collection) |
| `api.gold.devops.gov.bc.ca` | 6443 | HTTPS | OCP Gold cluster API (namespace data collection) |

NetworkPolicy annotations:
```yaml
annotations:
  isb.gov.bc.ca/internet-egress:  "true"
  isb.gov.bc.ca/justification:    "<justification text>"
  isb.gov.bc.ca/approvedBy:       "Platform Services"
```

---

## Deployment

### Prerequisites

- Emerald OpenShift access (be808f namespace)
- ArgoCD configured with `rloisell/bc-resilience-service-gitops`
- Vault policy granting `be808f-<env>/bc-resilience-service` path
- GitHub App created (see above)

### Initial deploy

```bash
# 1. Write secrets to Vault (see above)

# 2. Apply ExternalSecret (ArgoCD will sync automatically)
# OR manually:
oc apply -f gitops/argocd/bc-resilience-service-dev.yaml -n openshift-gitops

# 3. Verify pods are running
oc get pods -n be808f-dev -l app=bc-resilience-service

# 4. Check health
oc exec -n be808f-dev deploy/bc-resilience-service -- curl -s http://localhost:8080/health/ready
```

### GitOps flow

```
develop branch push → CI build → push image → update gitops dev → ArgoCD auto-sync
test    branch push → CI build → push image → update gitops test → ArgoCD auto-sync
main    branch push → CI build → push image → create PR to gitops main (manual merge = prod deploy)
```

---

## Debug Guide

### Check pod logs

```bash
oc logs -n be808f-dev deploy/bc-resilience-service --tail=100
```

### Verify ExternalSecret sync

```bash
oc get externalsecret bc-resilience-service-secret -n be808f-dev -o jsonpath='{.status.conditions}'
```

### Test webhook signature locally

```bash
BODY='{"messages":[{"role":"user","content":"@bc-resilience help"}]}'
SIG=$(echo -n "${BODY}" | openssl dgst -sha256 -hmac "${GITHUB_APP_WEBHOOK_SECRET}" | awk '{print "sha256="$2}')
curl -X POST http://localhost:8080/api/v1/extension \
  -H "Content-Type: application/json" \
  -H "X-Hub-Signature-256: ${SIG}" \
  -d "${BODY}"
```

### Test OC token

```bash
oc whoami --token="${OC_SILVER_TOKEN}" --server=https://api.silver.devops.gov.bc.ca:6443
oc auth can-i get pods --namespace be808f-dev --token="${OC_SILVER_TOKEN}" \
  --server=https://api.silver.devops.gov.bc.ca:6443
```

---

## PLATFORM_KNOWLEDGE

```yaml
platform_knowledge:
  resilience_checks:
    pdb:
      description: >
        Every Deployment or StatefulSet with replicas > 1 MUST have a PodDisruptionBudget.
        minAvailable must be ≥ 1 (not 0). maxUnavailable must be < 100%.
      example: |
        apiVersion: policy/v1
        kind: PodDisruptionBudget
        metadata:
          name: my-app-pdb
        spec:
          minAvailable: 1
          selector:
            matchLabels:
              app: my-app

    anti_affinity:
      description: >
        Multi-replica Deployments should use preferredDuringSchedulingIgnoredDuringExecution
        podAntiAffinity to spread pods across nodes.
      example: |
        affinity:
          podAntiAffinity:
            preferredDuringSchedulingIgnoredDuringExecution:
              - weight: 100
                podAffinityTerm:
                  labelSelector:
                    matchLabels:
                      app: my-app
                  topologyKey: kubernetes.io/hostname

    graceful_termination:
      description: >
        terminationGracePeriodSeconds MUST be ≥ 10 (recommend 30 for prod).
        A preStop hook (sleep 5) ensures the load balancer drains the pod before SIGTERM.
      example: |
        terminationGracePeriodSeconds: 30
        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 5"]

    qos:
      description: >
        All containers must define resources.requests (CPU + memory) to achieve at least
        Burstable QoS. BestEffort pods are first evicted under node pressure.
      example: |
        resources:
          requests:
            cpu:    100m
            memory: 128Mi
          limits:
            cpu:    500m
            memory: 512Mi

    probes:
      description: >
        Liveness probe restarts unhealthy containers.
        Readiness probe removes pods from service endpoints during startup or overload.
        Startup probe prevents premature liveness kills on slow-starting apps.
      example: |
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8080
          initialDelaySeconds: 15
          periodSeconds: 20
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 10
        startupProbe:
          httpGet:
            path: /health/live
            port: 8080
          failureThreshold: 12
          periodSeconds: 5

    hpa:
      description: >
        Production workloads must have an HPA with minReplicas ≥ 2 and appropriate
        CPU/memory targets. Dev/tools may use KEDA HTTP Add-on for scale-to-zero.
      example: |
        apiVersion: autoscaling/v2
        kind: HorizontalPodAutoscaler
        spec:
          scaleTargetRef:
            apiVersion: apps/v1
            kind: Deployment
            name: my-app
          minReplicas: 2
          maxReplicas: 10
          metrics:
            - type: Resource
              resource:
                name: cpu
                target:
                  type: Utilization
                  averageUtilization: 70
```
