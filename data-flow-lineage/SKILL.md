---
name: data-flow-lineage
description: Data classification and cross-service data flow analysis — ISCF classification quick reference, data flow ledger template, cross-boundary risk matrix, Azure data residency pattern, collection commands, and PIA trigger checklist. Use when mapping data flows for STRA/PIA, assessing cloud data residency risk, or generating a data flow ledger.
tools: Read, Grep, Glob, Bash
user-invocable: false
metadata:
  author: Ryan Loiselle
  version: "1.0"
compatibility: >
  BC Gov OCP Silver/Gold/Emerald. BC Gov FOIPPA and Privacy Act framework.
  References bc-gov-sdn-zones for zone-to-classification mapping.
---

# Data Flow Lineage

Maps personal information movement across services, namespaces, clusters, and cloud boundaries for STRA/PIA compliance.

**Reference implementation:** `rloisell/FOI-analysis` — `report/cross-cutting/FOI-security-rollup-v1.md` §6 Azure Data Residency.

---

## ISCF Classification Quick Reference

| Classification | SDN Zone | Typical Content | Examples |
|---|---|---|---|
| Unclassified | Low | Public information | Public website content, open data |
| Protected A | Medium | Limited personal info | Employee names, work contact info |
| Protected B | Medium/High | Significant personal info | Names + addresses + request content, health records, financial records |
| Protected C | High | National security / law enforcement | Court orders, informant data, witness protection |

BC Gov FOI-specific classifications:
- **FOI request metadata** (requester name, contact, subject): **Protected B**
- **FOI request content / documents**: **Protected B or higher** (medical, legal, financial documents may be Protected C)
- **FOI processing workflow data** (status, assignee, timeline): **Protected A**

---

## Data Flow Ledger Template

Use this table in STRA/PIA submissions and security rollup reports. One row per significant data flow.

| Source Service | Target Service | Data Elements | Classification | Direction | Protocol/Port | Cross-Boundary? | PIA Covered? |
|---|---|---|---|---|---|---|---|
| foi-requests | foi-flow | Requestor name, contact, request content | Protected B | → | HTTPS/443 | Cross-namespace | TBD |
| foi-flow | foi-docreviewer | Document bytes + metadata | Protected B | → | HTTPS/443 | Cross-namespace | TBD |
| foi-docreviewer | Azure Document Intelligence | Document content (text extraction) | Protected B | → External | HTTPS/443 | Cross-cloud 🔴 | Required |

---

## Cross-Boundary Risk Matrix

| Boundary Type | Classification | Risk | Required Controls |
|---|---|---|---|
| Same namespace, same classification | Any | ✅ No additional controls | Standard NP |
| Cross-namespace, same classification | Any | 🟡 MEDIUM | Scoped NetworkPolicy (namespaceSelector + podSelector + ports) |
| Cross-namespace with wide-open NP | Protected B+ | 🔴 HIGH | Remediate NP — add podSelector + ports |
| Cross-cluster (Silver↔Emerald) | Any | 🟡 MEDIUM | Public Route + TLS; treat as external egress |
| Cross-cloud to Canadian data centre | Protected B | 🟡 MEDIUM | MISA Data Processing Agreement required |
| Cross-cloud to non-specified region | Protected B+ | 🔴 HIGH | PIA required; FOIPPA s.30.1 disclosure notice required |
| Cross-border (non-Canadian cloud region) | Protected B+ | 🔴 CRITICAL | FOIPPA s.30.1 applies; ministerial approval required; explicit privacy notice to affected individuals |

---

## Azure Document Intelligence Pattern

This is the canonical Protected B cross-cloud data flow from the FOI-analysis engagement.

### What was found

`foi-docreviewer` sends document content (scanned PDFs, images) to **Azure Cognitive Services / Document Intelligence** for OCR and text extraction. These documents contain Protected B personal information (names, addresses, financial records, medical information).

### Legal risk

Under **FOIPPA s.30.1**, personal information stored outside Canada must be:
1. Disclosed in the public body's privacy notice
2. Covered by a written agreement with the service provider
3. Subject to Canadian law protections where reasonably possible

Azure data centres outside Canada East / Canada Central would trigger a FOIPPA s.30.1 disclosure obligation and require a **MISA Data Processing Agreement (DPA)**.

### Mitigation options

| Option | Pros | Cons |
|---|---|---|
| **Azure Canada Central/East region + MISA DPA** | Keeps Azure; maintains data residency in Canada | DPA must be in place before go-live; ongoing compliance obligation |
| **On-premise OCR (Tesseract)** | No cross-cloud boundary; no DPA required | Lower accuracy than Azure; infrastructure overhead |
| **Data scrubbing before submission** | Can use any Azure region | Complex; risk of incomplete scrubbing; still may require DPA |

**Recommended:** Confirm Azure region in the deployment config (`AZURE_ENDPOINT` env var) → if Canada Central/East, obtain MISA DPA → document in STRA → add to privacy notice.

---

## Collection Commands — Building a Data Flow Ledger

```bash
# Find all cross-service URL references in ConfigMaps
oc get configmaps -n <ns> -o json | \
  jq '.items[] | .data | to_entries[] | select(.value | test("https?://")) | {key, value}'

# Find all external hostname references in environment variables
oc get deployments -n <ns> -o json | \
  jq '.items[].spec.template.spec.containers[].env[]? |
      select(.value? | test("https?://|smtp:|redis://")) |
      {name, value}'

# Find Redis stream keys (PII carrier risk — streams may carry Protected B data)
oc get configmaps -n <ns> -o json | \
  jq '.items[] | .data | to_entries[] |
      select(.key | test("STREAM|TOPIC|QUEUE")) | {key, value}'

# Find Azure or external cloud endpoints
oc get deployments,configmaps -n <ns> -o json | \
  jq '.. | strings | select(test("azure|amazonaws|googleapis|cognitive"))'
```

---

## PIA Trigger Checklist

A Privacy Impact Assessment (PIA) is required when:

- [ ] **New cross-cloud data flow** involving personal information (any cloud provider)
- [ ] **New third-party data processor** where personal data is shared or processed
- [ ] **Change to data retention periods** for personal information
- [ ] **New AI/ML processing** of personal data — Azure Document Intelligence, OpenAI, etc. all qualify
- [ ] **New automated decision** supported by personal data (algorithmic decision-making)
- [ ] **New collection of personal information** not covered by an existing PIA
- [ ] **Significant change** to an existing system that handles personal information

When a PIA trigger is identified:
1. Document in `AI/securityNextSteps.md` under "PIA Status"
2. Engage the Ministry Privacy Officer
3. Do not deploy to production until PIA is reviewed
4. Capture accepted residual risks in the STRA

---

## DATA_FLOW_LINEAGE_KNOWLEDGE

<!-- agent-evolution appends discoveries here -->
<!-- Format: - YYYY-MM-DD: [Project] <imperative statement> -->
- 2026-06-05: [FOI-analysis] foi-docreviewer sends Protected B document content to Azure Document Intelligence — confirm Azure Canada Central/East region + obtain MISA DPA before production
- 2026-06-05: [FOI-analysis] AZURE_ENDPOINT env var in foi-docreviewer ConfigMap is the authoritative source for data residency determination — always check this first
- 2026-06-05: [FOI-analysis] Redis streams are a PII carrier — stream keys in ConfigMaps indicate cross-namespace Protected B data flows that must be in the data flow ledger
