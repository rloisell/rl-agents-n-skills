# Phase 3 & 4 — Report Structure & PDF Rendering

## Contents

- [6-Section Report Structure](#6-section-report-structure)
- [RAG Criteria](#rag-criteria)
- [Phase 4 — PDF Rendering](#phase-4--pdf-rendering)
- [Toolkit & Report Naming Conventions](#toolkit--report-naming-conventions)

## 6-Section Report Structure

Every section must cite collected evidence files (`networkpolicies.yaml`, `route-summary.txt`, `egress-candidates.txt`, etc.).

1. **Section 1 — Executive Summary**:
   - Overall RAG (`RED` / `AMBER` / `GREEN`) per namespace with rationale.
   - RAG table: namespace × (NP count, stale NPs, wide-open NPs, external routes, egress risks, RAG).
   - Top CRITICAL findings (every wide-open cross-namespace NP, every plaintext route) prominently flagged.
   - Total `NET-NN` task count by severity: CRITICAL / HIGH / MEDIUM / LOW.
2. **Section 2 — Cross-Namespace Connectivity Matrix**:
   - Table from `cross-namespace-matrix.md` with risk classification applied.
   - Narrative for each wide-open NP (covered workloads, potential flows) + remediation YAML.
3. **Section 3 — NetworkPolicy Inventory**:
   - Per-namespace NP inventory table (name, pod selector, policy types, port restrictions, age, status).
   - Stale NP analysis (orphaned vs stale config, with `oc delete` commands for confirmed orphans).
   - Gap analysis: workloads with no NP coverage (default allow-all ingress if no NP targets them).
4. **Section 4 — Route and Ingress Audit**:
   - All routes table with TLS classification and public risk rating.
   - Admin UI / management tool route callouts (HIGH risk pattern).
   - Vanity hostname analysis: DNS, WAF, authentication layer.
5. **Section 5 — Egress Audit (Third-Party Flow Ledger)**:
   - Consolidated flow table: namespace × source (ConfigMap/env var) × destination × classification × TLS × port × risk.
   - SMTP relay audit with port risk; cloud AI/Azure egress check (egress NP present? FWCR submitted?).
   - Document any previously unknown destinations manually — never leave unresolved.
6. **Section 6 — Findings and Recommendations**:
   - `NET-NN` numbered task list sorted `CRITICAL → HIGH → MEDIUM → LOW` (`Effort` scale: `30m` / `1h` / `2h` / `4h` / `1d`).

## RAG Criteria

- **RED**: any wide-open NP (`namespaceSelector: {}`), any plaintext HTTP route, or SMTP port 25 detected.
- **AMBER**: stale NPs present, vanity routes unreviewed, or unknown egress destinations.
- **GREEN**: all NPs current and scoped, all routes TLS-terminated, and all egress classified.

## Phase 4 — PDF Rendering

```bash
# Render HTML intermediate (run from report directory so relative paths resolve)
cd <report-dir>
pandoc <LABEL>-Network-Report-v1.md \
  --from=markdown --to=html5 --standalone \
  --css=/tmp/report-style.css --embed-resources \
  --output=/tmp/report.html \
  --metadata title="<LABEL> — Container Network Posture Report"

# Render PDF via Chrome headless (macOS or Linux google-chrome-stable)
google-chrome-stable --headless --disable-gpu \
  --print-to-pdf=<LABEL>-Network-Report-v1.pdf \
  --print-to-pdf-no-header --no-pdf-header-footer \
  file:///tmp/report.html
```

## Toolkit & Report Naming Conventions

```text
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

Automated collection & GitHub Action reference: `<org>/container-network-analysis-toolkit`.
