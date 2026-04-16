# SKILL: bc-migrate-service

**Domain**: Tier 3 OCP Migration Analysis Service  
**Runtime**: Node.js 22 / TypeScript / Fastify — GitHub Copilot Extension on Emerald  
**Skill version**: 1.0  
**Updated**: April 2026

---

## Purpose

`bc-migrate-service` is a **GitHub Copilot Extension** deployed on Emerald OpenShift
(namespace `be808f`). It lets any BC Gov team run a full OpenShift migration analysis
directly from Copilot Chat using the `@bc-migrate` agent.

This skill documents how to:
- Invoke and test the extension
- Deploy and configure it on Emerald
- Register or update the GitHub App
- Manage secrets in Vault
- Debug common failures

---

## Usage (Copilot Chat)

Install the extension from the GitHub Marketplace (or via org settings), then:

```
# Generate a full migration analysis report
@bc-migrate analyze namespace:f1b263 repo:bcgov-c/justinrcc

# With optional parameters
@bc-migrate analyze namespace:f1b263 repo:bcgov-c/justinrcc target:emerald cluster:silver envs:dev,test,prod,tools

# Show help
@bc-migrate help
```

**Parameters**:

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `namespace` | ✅ | — | 6-char OCP license plate prefix (e.g. `f1b263`) |
| `repo` | ✅ | — | GitHub repo `owner/name` |
| `target` | ❌ | `emerald` | Target platform: `emerald` \| `aws-ecs` \| `aws-eks` |
| `cluster` | ❌ | `silver` | Source cluster: `silver` \| `gold` |
| `envs` | ❌ | `dev,test,prod,tools` | Comma-separated environment suffixes |

**Analysis takes 3–8 minutes** depending on namespace size. The extension streams
progress updates in real time, then delivers a link to the PDF report uploaded as
a GitHub Release asset on the target repo.

---

## Architecture

```
Copilot Chat
    │  @bc-migrate analyze namespace:X repo:Y
    ▼
GitHub Copilot Extensions API (SSE)
    │  POST /api/v1/extension
    ▼
bc-migrate-service (be808f-{env}.apps.emerald.devops.gov.bc.ca)
    │
    ├─ Verify GitHub HMAC signature
    ├─ Verify caller repo access (Octokit)
    │
    ├─► Stage 1: collect.sh
    │     oc get workloads/svc/route/pvc/np/...
    │     gh clone + extract workflows/Helm/k8s
    │     → manifest-summary.md
    │
    ├─► Stage 2: GitHub Models API (gpt-4o, streaming)
    │     System: report-sections.md guide + bc-gov-* skills
    │     User:   manifest-summary.md + request params
    │     → full 12-section markdown report (streamed to chat)
    │
    └─► Stage 3: pandoc + chromium → PDF
          Upload as GitHub Release asset
          → Download link returned in chat
```

---

## Deployment on Emerald

### Prerequisites

1. Namespace `be808f-{dev,test,prod,tools}` provisioned
2. ArgoCD project `be808f` configured
3. Vault path `secret/data/be808f-<env>/bc-migrate-service` populated (see Secrets below)
4. KEDA HTTP Add-on installed in the cluster
5. External Secrets Operator + `ClusterSecretStore: vault-secret-store` installed

### Deploy (GitOps)

```bash
# Apply ArgoCD Application CRDs (one-time setup per environment)
kubectl apply -f gitops/applications/argocd/app-dev.yaml  -n be808f-tools
kubectl apply -f gitops/applications/argocd/app-test.yaml -n be808f-tools
kubectl apply -f gitops/applications/argocd/app-prod.yaml -n be808f-tools
```

ArgoCD will then manage all subsequent deployments via GitOps.
Image tag updates are committed to the gitops repo by the CI workflow.

### CI/CD Flow (ISB EA Option 2)

```
develop branch  → build image → commit dev_values.yaml  → ArgoCD auto-syncs be808f-dev
test branch     → build image → commit test_values.yaml → ArgoCD auto-syncs be808f-test
main / v* tag   → build image → open PR on prod_values.yaml → human approves → ArgoCD syncs be808f-prod
```

---

## GitHub App Registration

The GitHub App is the identity of the extension. Create it once at the org level.

1. Go to **GitHub org Settings → Developer Settings → GitHub Apps → New GitHub App**
2. Set **App name**: `BC Migrate`
3. Set **Homepage URL**: `https://bc-migrate-service-be808f.apps.emerald.devops.gov.bc.ca`
4. Set **Callback URL** / **Webhook URL**:
   `https://bc-migrate-service-be808f.apps.emerald.devops.gov.bc.ca/api/v1/extension`
5. Set **Permissions**:
   - Repository: Contents (read), Metadata (read)
   - Organization: Members (read)
   - Copilot Chat: (all enabled)
6. Set **GitHub Copilot** section:
   - Copilot Extension Type: **Agent**
   - Inference Description: `On-demand OCP → Emerald migration analysis for BC Gov teams.`
7. Generate and download the **private key** PEM
8. Note the **App ID** and **Webhook Secret**
9. Install the app on each organization that will use it

---

## Secrets in Vault

Path: `secret/data/be808f-<env>/bc-migrate-service`

| Key | Description |
|-----|-------------|
| `GITHUB_APP_ID` | Numeric GitHub App ID |
| `GITHUB_APP_PRIVATE_KEY` | Full PEM private key (multi-line) |
| `GITHUB_APP_WEBHOOK_SECRET` | Webhook secret from App registration |
| `GITHUB_MODELS_API_KEY` | GitHub PAT with `models:read` scope |
| `OC_SILVER_TOKEN` | Service account token for Silver OCP API |
| `OC_GOLD_TOKEN` | Service account token for Gold OCP API |

The ExternalSecret in `gitops/charts/bc-migrate/templates/externalsecret.yaml`
syncs these into a Kubernetes Secret that is mounted as pod environment variables.

Write a secret:
```bash
vault kv put secret/be808f-dev/bc-migrate-service \
  GITHUB_APP_ID=12345 \
  GITHUB_APP_PRIVATE_KEY="$(cat /path/to/private-key.pem)" \
  GITHUB_APP_WEBHOOK_SECRET=<value> \
  GITHUB_MODELS_API_KEY=ghp_... \
  OC_SILVER_TOKEN=<service-account-token> \
  OC_GOLD_TOKEN=<service-account-token>
```

---

## FWCR Requirements

bc-migrate-service makes **internet egress** connections — CSBC Firewall Change Requests
are required per environment before the service can reach these endpoints:

| Endpoint | Protocol | Port | Purpose |
|----------|----------|------|---------|
| `api.github.com` | HTTPS | 443 | GitHub API (repo access verify, Release upload) |
| `models.inference.ai.azure.com` | HTTPS | 443 | GitHub Models API (LLM analysis) |
| `api.silver.devops.gov.bc.ca` | HTTPS | 6443 | Silver OCP API (namespace collection) |
| `api.gold.devops.gov.bc.ca` | HTTPS | 6443 | Gold OCP API (namespace collection) |

Submit a FWCR for each environment (`be808f-dev`, `be808f-test`, `be808f-prod`).
The NetworkPolicy `justification` annotations in `networkpolicies.yaml` document the business
justification for the Conftest policy gate.

---

## Local Development

```bash
# Prerequisites: Node.js 22, pandoc, chromium, oc CLI, gh CLI

# Clone with submodules
git clone --recurse-submodules https://github.com/rloisell/bc-migrate-service.git
cd bc-migrate-service

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your GitHub App credentials and OCP tokens

# Run in development mode (tsx watch — hot reload)
npm run dev

# Run the analysis manually (simulate Copilot Chat)
curl -X POST http://localhost:8080/api/v1/extension \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Token: ghp_..." \
  -d '{"messages":[{"role":"user","content":"@bc-migrate analyze namespace:f1b263 repo:bcgov-c/justinrcc"}]}'
```

---

## Debugging

**Pod not starting:**
```bash
oc logs -n be808f-dev deploy/bc-migrate-service --follow
oc describe pod -n be808f-dev -l app.kubernetes.io/name=bc-migrate-service
```

**ExternalSecret not syncing:**
```bash
oc get externalsecret -n be808f-dev
oc describe externalsecret bc-migrate-service-secrets -n be808f-dev
```

**Analysis failing (LLM errors):**
- Check `GITHUB_MODELS_API_KEY` is set and has `models:read` scope
- Check rate limits: GitHub Models free tier has token limits per hour

**Signature verification failing:**
- Ensure `GITHUB_APP_WEBHOOK_SECRET` in Vault matches the value in the GitHub App settings exactly
- Check the `X-Hub-Signature-256` header is present (GitHub sends this for all webhook deliveries)

**Collection failing (oc not found):**
- The `oc` CLI must be on the PATH in the container — add it to the Containerfile or mount via init container
- Verify `OC_SILVER_TOKEN` or `OC_GOLD_TOKEN` is populated for the target cluster

---

## Related Skills

- `ocp-migration-analyst` — orchestrator skill (Tier 1: VS Code)
- `bc-gov-devops` — Emerald deployment patterns + ag-devops policy gate
- `bc-gov-networkpolicy` — NetworkPolicy authoring with ag-helm intent API
- `bc-gov-emerald` — DataClass labels, PriorityClass, edge Route requirements
- `vault-secrets` — Vault + ESO patterns for BC Gov
- `bc-gov-iam` — GitHub App / OAuth2 patterns for BC Gov

---

## PLATFORM_KNOWLEDGE

```yaml
service:
  name: bc-migrate-service
  namespace_prefix: be808f
  cluster: emerald
  port: 8080
  image: artifacts.developer.gov.bc.ca/be808f-docker-local/bc-migrate-service
  gitops_repo: rloisell/bc-migrate-service-gitops
  argocd_project: be808f

github_app:
  name: BC Migrate
  webhook_path: /api/v1/extension
  extension_type: agent

llm:
  provider: github_models
  model: openai/gpt-4o
  base_url: https://models.inference.ai.azure.com

vault:
  path_pattern: "secret/data/be808f-{env}/bc-migrate-service"
  keys:
    - GITHUB_APP_ID
    - GITHUB_APP_PRIVATE_KEY
    - GITHUB_APP_WEBHOOK_SECRET
    - GITHUB_MODELS_API_KEY
    - OC_SILVER_TOKEN
    - OC_GOLD_TOKEN

keda:
  type: http-addon
  scale_to_zero: true
  cooldown_seconds: 300
```
