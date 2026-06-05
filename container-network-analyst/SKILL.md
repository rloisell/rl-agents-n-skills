# SKILL: container-network-analyst

**Domain**: OpenShift Container Network Posture & Cross-Namespace Flow Analysis  
**Skill version**: 1.0  
**Updated**: June 2026 (v1.0 — initial skill, extracted from multi-app analysis engagement)

---

## Purpose

Produce a **full network posture report** for any group of OpenShift namespaces.  
The report is cluster-agnostic — useful for teams on Silver/Gold and for teams
preparing Emerald migrations (network readiness baseline).

**This skill is Tier 1 of the Container Network Analysis Toolkit:**

| Tier | Name | What it is |
|------|------|------------|
| 1 | container-network-analyst (this skill) | VS Code / Copilot Chat agent + skills — **primary method** |
| 2 | container-network-analysis-toolkit | CLI data collection + GitHub Composite Action + VS Code prompt template |

---

## Invocation

```
# In VS Code Copilot Chat (agent mode), use the prompt template:
# .github/prompts/network-analysis.prompt.md (in container-network-analysis-toolkit)
#
# Via Copilot Extension:
@container-network analyse namespaces:abc123-dev,def456-dev [cluster:silver]
#
# Via CLI toolkit:
./container-network-analysis-toolkit/collect/collect.sh \
  --namespaces abc123-dev,def456-dev \
  --cluster silver \
  --output ./working
```

---

## Phase 1 — Collect Namespace Data

Run these commands for each namespace in the input list.
Store all output in `<OUTPUT>/<namespace>/` directories.

### 1A — NetworkPolicy collection

```bash
NS="<NAMESPACE>"
OUT="<OUTPUT>/${NS}"
mkdir -p "${OUT}"

# Full NetworkPolicy YAML — primary analysis source
oc get networkpolicies -n "${NS}" -o yaml > "${OUT}/networkpolicies.yaml"

# NP summary: name, pod selector, policy types, port restrictions
oc get networkpolicies -n "${NS}" \
  -o custom-columns='NAME:.metadata.name,POD-SELECTOR:.spec.podSelector,INGRESS-RULES:.spec.ingress,EGRESS-RULES:.spec.egress,TYPES:.spec.policyTypes,CREATED:.metadata.creationTimestamp' \
  > "${OUT}/np-summary.txt" 2>&1 || echo "No NetworkPolicies found" > "${OUT}/np-summary.txt"

# Cross-namespace NPs — any NP with namespaceSelector in ingress or egress rules
oc get networkpolicies -n "${NS}" -o json | \
  jq -r '.items[] | select(
    (.spec.ingress[]?.from[]?.namespaceSelector != null) or
    (.spec.egress[]?.to[]?.namespaceSelector != null)
  ) | "\(.metadata.name)\t\(.metadata.creationTimestamp)\t\(.spec.podSelector)"' \
  > "${OUT}/cross-namespace-nps.txt" 2>/dev/null || echo "None detected" > "${OUT}/cross-namespace-nps.txt"

# Egress-type NPs — NPs with Egress in policyTypes
oc get networkpolicies -n "${NS}" -o json | \
  jq -r '.items[] | select(.spec.policyTypes[]? == "Egress") | .metadata.name' \
  > "${OUT}/egress-nps.txt" 2>/dev/null || echo "None detected" > "${OUT}/egress-nps.txt"

# Stale NPs — created more than 365 days ago
CUTOFF=$(date -d '365 days ago' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -v-365d +%Y-%m-%dT%H:%M:%SZ)
oc get networkpolicies -n "${NS}" -o json | \
  jq -r --arg cutoff "${CUTOFF}" \
  '.items[] | select(.metadata.creationTimestamp < $cutoff) | "\(.metadata.name)\t\(.metadata.creationTimestamp)\t\(.spec.podSelector)"' \
  > "${OUT}/stale-nps.txt" 2>/dev/null || echo "None detected" > "${OUT}/stale-nps.txt"
```

### 1B — Service and Route collection

```bash
# Services — names, selectors, ports
oc get svc -n "${NS}" -o yaml > "${OUT}/services.yaml"
oc get svc -n "${NS}" \
  -o custom-columns='NAME:.metadata.name,SELECTOR:.spec.selector,PORTS:.spec.ports,TYPE:.spec.type' \
  > "${OUT}/svc-summary.txt"

# Routes — hostnames, TLS, target services
oc get route -n "${NS}" -o yaml > "${OUT}/routes.yaml"
oc get route -n "${NS}" \
  -o custom-columns='NAME:.metadata.name,HOST:.spec.host,TLS-TERMINATION:.spec.tls.termination,TARGET:.spec.to.name,CREATED:.metadata.creationTimestamp' \
  > "${OUT}/route-summary.txt" 2>&1 || echo "No Routes found" > "${OUT}/route-summary.txt"

# External (vanity) routes — hostnames NOT matching the cluster default pattern
oc get route -n "${NS}" -o json | \
  jq -r '.items[] | select(.spec.host | test("apps\\.silver\\.devops\\.gov\\.bc\\.ca|apps\\.gold\\.devops\\.gov\\.bc\\.ca|apps\\.emerald\\.devops\\.gov\\.bc\\.ca") | not) | "\(.metadata.name)\t\(.spec.host)"' \
  > "${OUT}/external-routes.txt" 2>/dev/null || echo "None detected" > "${OUT}/external-routes.txt"
```

### 1C — Workload collection (for stale NP cross-reference)

```bash
# Deployments and DeploymentConfigs — names, labels, replicas, images
oc get deployment,dc -n "${NS}" -o yaml > "${OUT}/deployments.yaml"
oc get deployment,dc -n "${NS}" \
  -o custom-columns='NAME:.metadata.name,KIND:.kind,LABELS:.metadata.labels,REPLICAS:.spec.replicas,IMAGE:.spec.template.spec.containers[0].image' \
  > "${OUT}/deployment-summary.txt" 2>&1 || echo "No Deployments found" > "${OUT}/deployment-summary.txt"
```

### 1D — Egress destination scan

```bash
# ConfigMap values containing URL/endpoint patterns
oc get configmaps -n "${NS}" -o json | \
  jq -r '.items[] | .metadata.name as $cm | .data // {} | to_entries[] |
    select(.value | type == "string") |
    select(.value | test("https?://|smtp:|redis://|amqp://|s3\\.|azure|oidc|sso"; "i")) |
    "\($cm)\t\(.key)\t\(.value)"' \
  > "${OUT}/egress-candidates.txt" 2>/dev/null || echo "No URL patterns found" > "${OUT}/egress-candidates.txt"

# Deployment env vars containing URL/endpoint patterns
oc get deployments,dc -n "${NS}" -o json | \
  jq -r '.items[] | .metadata.name as $dep |
    .spec.template.spec.containers[]? | .env[]? |
    select(.value? | strings | test("https?://|smtp:|redis://|amqp://|s3\\.|azure|oidc|sso"; "i")) |
    "\($dep)\t\(.name)\t\(.value)"' \
  >> "${OUT}/egress-candidates.txt" 2>/dev/null
```

### 1E — Per-namespace summary

Generate `<OUTPUT>/<namespace>/summary.md` as the AI analysis entry point:

```bash
cat > "${OUT}/summary.md" << EOF
# Network Posture Summary — ${NS}

**Collected:** $(date -u +%Y-%m-%dT%H:%M:%SZ)
**Namespace:** ${NS}

## Counts
- Total NetworkPolicies: $(oc get networkpolicies -n "${NS}" --no-headers 2>/dev/null | wc -l | tr -d ' ')
- Cross-namespace NPs: $(wc -l < "${OUT}/cross-namespace-nps.txt")
- Egress-type NPs: $(wc -l < "${OUT}/egress-nps.txt")
- Stale NPs (>365d): $(wc -l < "${OUT}/stale-nps.txt")
- Total Routes: $(oc get route -n "${NS}" --no-headers 2>/dev/null | wc -l | tr -d ' ')
- Vanity/external routes: $(wc -l < "${OUT}/external-routes.txt")
- Egress candidates: $(wc -l < "${OUT}/egress-candidates.txt")

## Files for AI analysis
- networkpolicies.yaml — full NP YAML
- np-summary.txt — NP table
- cross-namespace-nps.txt — cross-namespace NPs
- stale-nps.txt — NPs older than 365 days
- route-summary.txt — route table
- external-routes.txt — vanity hostnames
- egress-candidates.txt — URL/endpoint patterns from ConfigMaps and env vars
- deployment-summary.txt — workload labels (for stale NP cross-reference)
EOF
```

### 1F — Cross-namespace matrix (run after all namespaces collected)

```bash
OUT_BASE="<OUTPUT>"

cat > "${OUT_BASE}/cross-namespace-matrix.md" << 'HEADER'
# Cross-Namespace Connectivity Matrix

| Source Namespace | NP Name | Pod Selector | Namespace Selector | Ports | Age | Risk |
|-----------------|---------|-------------|-------------------|-------|-----|------|
HEADER

for NS_DIR in "${OUT_BASE}"/*/; do
  NS=$(basename "${NS_DIR}")
  if [[ -s "${NS_DIR}/cross-namespace-nps.txt" ]] && \
     ! grep -q "None detected" "${NS_DIR}/cross-namespace-nps.txt"; then
    while IFS=$'\t' read -r name created selector; do
      echo "| ${NS} | ${name} | ${selector} | _see NP YAML_ | _see NP YAML_ | ${created} | 🔴 Review |"
    done < "${NS_DIR}/cross-namespace-nps.txt"
  fi
done >> "${OUT_BASE}/cross-namespace-matrix.md"
```

---

## Phase 2 — Gap Analysis

### Cross-Namespace NP Risk Classification

For each cross-namespace NP found:

| Pattern | Risk | Classification |
|---------|------|----------------|
| `namespaceSelector: {}` (empty), no `podSelector`, no `ports` | 🔴 CRITICAL | Wide-open — any pod in cluster can reach any pod in target NS |
| `namespaceSelector` with label, no `podSelector`, no `ports` | 🔴 HIGH | Namespace-scoped but unrestricted — all pods and all ports |
| `namespaceSelector` with label, `podSelector` defined, no `ports` | 🟡 MEDIUM | Pod-scoped but all ports unrestricted |
| `namespaceSelector` + `podSelector` + `ports` | ✅ COMPLIANT | Fully scoped |

**Key check:** Load the full NP YAML from `networkpolicies.yaml` for every NP listed in
`cross-namespace-nps.txt` and classify against the table above.

### Stale NP Detection

For each NP in `stale-nps.txt`:
1. Extract the `podSelector.matchLabels` from `networkpolicies.yaml`
2. Check `deployment-summary.txt` for any workload with matching labels
3. If no matching workload found → **Orphaned** (recommend: `oc delete networkpolicy <name> -n <ns>`)
4. If matching workload exists but NP is >2 years old → **Stale config** (review and validate)

### Route TLS Audit

| TLS Termination | Risk | Notes |
|----------------|------|-------|
| `edge` | ✅ Standard | TLS at HAProxy; plaintext inside cluster |
| `reencrypt` | ✅ Preferred | End-to-end TLS; use for sensitive backends |
| `passthrough` | 🟡 Review | TLS at pod; HAProxy cannot inspect; cert management responsibility shifts to app |
| missing/`none` | 🔴 CRITICAL | Plaintext HTTP — immediate remediation required |

**Admin UI route detection:** Flag any route whose name or target service matches:
`admin`, `console`, `insight`, `dashboard`, `manager`, `management`, `flower`,
`rabbitmq`, `redis`, `pgadmin`, `kibana`, `grafana` (unless protected by SSO).

### Egress Classification

For each entry in `egress-candidates.txt`, classify the destination:

| Pattern | Classification | Risk |
|---------|---------------|------|
| `sso.gov.bc.ca`, `common-logon.gov.bc.ca`, `*.auth.*` | OIDC | ✅ Standard — verify port 443 |
| `*.amazonaws.com`, `*.s3.*`, `s3.gov.bc.ca` | S3 | 🟡 Cloud egress — FWCR check |
| `*.azure.com`, `*.microsoft.com`, `cognitiveservices` | Azure | 🟡 Cloud egress — FWCR + PIA check |
| SMTP/mail + port 25 | SMTP | 🔴 HIGH — unencrypted relay |
| SMTP/mail + port 587/465 | SMTP | ✅ Encrypted relay |
| `*.gov.bc.ca` (non-SSO) | BC Gov Internal | 🟡 Verify FWCR scope |
| axis, ediva, AXIS | AXIS | 🟡 BC Gov document management — FWCR scope |
| Anything else | Unknown | 🔴 Must classify before report is final |

---

## Phase 3 — Report Structure

Produce a 6-section markdown report. Every section must cite collected evidence files.

### Section 1 — Executive Summary

- Overall RAG (🔴/🟡/🟢) per namespace with rationale
- RAG table: namespace × (NP count, stale NPs, wide-open NPs, external routes, egress risks, RAG)
- Top CRITICAL findings (every wide-open cross-namespace NP, every plaintext route) prominently flagged ⛔
- Total `NET-NN` task count by severity: CRITICAL / HIGH / MEDIUM / LOW

**RAG criteria:**
- 🔴 RED — any wide-open NP (`namespaceSelector: {}`), any plaintext HTTP route, SMTP port 25 detected
- 🟡 AMBER — stale NPs present, vanity routes unreviewed, unknown egress destinations
- 🟢 GREEN — all NPs current and scoped, all routes TLS-terminated, all egress classified

### Section 2 — Cross-Namespace Connectivity Matrix

- Table from `cross-namespace-matrix.md` with risk classification applied
- Narrative for each wide-open NP: what workloads it covers, what flows could occur
- Remediation YAML for each wide-open NP (namespaceSelector + podSelector + ports)

### Section 3 — NetworkPolicy Inventory

For each namespace:
- Per-namespace NP inventory table (name, pod selector, policy types, port restrictions, age, status)
- Stale NP analysis: orphaned vs stale config, with `oc delete` commands for confirmed orphans
- Gap analysis: workloads with no NP coverage (default allow-all ingress if no NP targets them)

### Section 4 — Route and Ingress Audit

- All routes table with TLS classification and public risk rating
- Admin UI / management tool route callouts (HIGH risk pattern)
- Vanity hostname analysis: DNS, WAF, authentication layer

### Section 5 — Egress Audit (Third-Party Flow Ledger)

- Consolidated flow table: namespace × source (ConfigMap/env var) × destination × classification × TLS × port × risk
- SMTP relay audit with port risk
- Cloud AI / Azure egress check: egress NP present? FWCR submitted?
- Unknown classification: document manually, never leave unresolved

### Section 6 — Findings and Recommendations

`NET-NN` numbered task list, sorted CRITICAL → HIGH → MEDIUM → LOW.

| Task | Priority | Category | Description | Effort |
|------|----------|----------|-------------|--------|
| NET-01 | ⛔ CRITICAL | ... | ... | ... |

**Effort scale:** 30m / 1h / 2h / 4h / 1d

---

## Phase 4 — PDF Rendering

```bash
# Render HTML intermediate (run from report directory so relative paths resolve)
cd <report-dir>
/opt/homebrew/bin/pandoc <LABEL>-Network-Report.md \
  --from=markdown --to=html5 --standalone \
  --css=/tmp/report-style.css --embed-resources \
  --output=/tmp/report.html \
  --metadata title="<LABEL> — Container Network Posture Report"

# Render PDF via Chrome headless
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu \
  --print-to-pdf=<LABEL>-Network-Report.pdf \
  --print-to-pdf-no-header --no-pdf-header-footer \
  file:///tmp/report.html 2>/dev/null

echo "PDF: $(ls -lh <LABEL>-Network-Report.pdf)"
```

On Linux (GitHub Actions / container):
```bash
google-chrome-stable --headless --disable-gpu \
  --print-to-pdf=report.pdf \
  --print-to-pdf-no-header --no-pdf-header-footer \
  file:///tmp/report.html
```

CSS template: `container-network-analysis-toolkit/render/render.sh` handles this automatically.

---

## Invocation Patterns

### Via VS Code / GitHub Copilot

```
Use the container-network-analyst skill to generate a full network posture report for
namespaces abc123-dev,def456-dev on Silver cluster. Output to ./working/report.
```

### Via container-network-analysis-toolkit (automated)

```bash
# Step 1: collect data
./collect/collect.sh \
  --namespaces abc123-dev,def456-dev \
  --cluster silver \
  --output working/

./collect/egress-audit.sh \
  --namespaces abc123-dev,def456-dev \
  --output working/

# Step 2: open VS Code, invoke AI analysis
# Copilot reads working/*/summary.md + cross-namespace-matrix.md + runs analysis

# Step 3: render PDF
./render/render.sh \
  --input working/report/<LABEL>-Network-Report.md \
  --output working/report/
```

### Via GitHub Action (any BC Gov project)

```yaml
- uses: rloisell/container-network-analysis-toolkit@main
  with:
    namespaces: abc123-dev,def456-dev
    cluster: silver
    oc-server-url: ${{ secrets.OC_SILVER_URL }}
    oc-token: ${{ secrets.OC_SILVER_SA_TOKEN }}
    llm-api-key: ${{ secrets.GITHUB_MODELS_API_KEY }}
```

---

## Report Naming Convention

```
<LABEL>-Network-Report-v1.md      # First analysis
<LABEL>-Network-Report-v1.pdf     # Rendered PDF
<LABEL>-Network-Report-v2.md      # Re-analysis after remediation
working/
  <namespace>/
    networkpolicies.yaml
    cross-namespace-nps.txt
    stale-nps.txt
    route-summary.txt
    egress-candidates.txt
    summary.md
  cross-namespace-matrix.md
  third-party-flow-ledger.md
```

---

## Relationship to sibling toolkits

| Toolkit / Skill | Focus | Scope |
|----------------|-------|-------|
| `ocp-resilience-analyst` + `ocp-resilience-toolkit` | Workload resilience (PDB, HPA, probes, R01–R15) | Single namespace prefix, all envs |
| `ocp-migration-analyst` + `ocp-migration-toolkit` | Platform migration gap analysis (Silver/Gold → Emerald) | Single namespace prefix + GitHub repo |
| **`container-network-analyst` + `container-network-analysis-toolkit`** | **Network security posture (NP, Routes, Egress, Cross-namespace)** | **Multiple namespaces, mixed license plates** |

Run all three toolkits together for a complete pre-migration baseline.

---

## KNOWLEDGE

<!-- agent-evolution appends discoveries here -->
<!-- Format: - YYYY-MM-DD: [Project] <imperative statement> -->
