# Phase 1 — OpenShift Namespace Collection Commands

## Contents

- [1A — NetworkPolicy Collection](#1a--networkpolicy-collection)
- [1B — Service and Route Collection](#1b--service-and-route-collection)
- [1C — Workload Collection (Stale NP Cross-Reference)](#1c--workload-collection-stale-np-cross-reference)
- [1D — Egress Destination Scan](#1d--egress-destination-scan)
- [1E — Per-Namespace Summary](#1e--per-namespace-summary)
- [1F — Cross-Namespace Matrix](#1f--cross-namespace-matrix)

Run these commands for each namespace in the input list and store outputs in `<OUTPUT>/<namespace>/`.

## 1A — NetworkPolicy Collection

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

## 1B — Service and Route Collection

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

## 1C — Workload Collection (Stale NP Cross-Reference)

```bash
# Deployments and DeploymentConfigs — names, labels, replicas, images
oc get deployment,dc -n "${NS}" -o yaml > "${OUT}/deployments.yaml"
oc get deployment,dc -n "${NS}" \
  -o custom-columns='NAME:.metadata.name,KIND:.kind,LABELS:.metadata.labels,REPLICAS:.spec.replicas,IMAGE:.spec.template.spec.containers[0].image' \
  > "${OUT}/deployment-summary.txt" 2>&1 || echo "No Deployments found" > "${OUT}/deployment-summary.txt"
```

## 1D — Egress Destination Scan

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

## 1E — Per-Namespace Summary

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

## 1F — Cross-Namespace Matrix

Run after all namespaces are collected:

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
      echo "| ${NS} | ${name} | ${selector} | _see NP YAML_ | _see NP YAML_ | ${created} | Review |"
    done < "${NS_DIR}/cross-namespace-nps.txt"
  fi
done >> "${OUT_BASE}/cross-namespace-matrix.md"
```
