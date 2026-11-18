# ISCF Classification, Data Flow Ledger & Risk Matrix

## Contents

- [ISCF Classification Quick Reference](#iscf-classification-quick-reference)
- [Data Flow Ledger Template](#data-flow-ledger-template)
- [Cross-Boundary Risk Matrix](#cross-boundary-risk-matrix)

## ISCF Classification Quick Reference

| Classification | SDN Zone | Typical Content | Examples |
|---|---|---|---|
| Unclassified | Low | Public information | Public website content, open data |
| Protected A | Medium | Limited personal info | Employee names, work contact info |
| Protected B | Medium/High | Significant personal info | Names + addresses + request content, health records, financial records |
| Protected C | High | National security / law enforcement | Court orders, informant data, witness protection |

BC Gov `<program-area>` classifications (example — verify against the current PIA for your engagement):
- **Request metadata** (requester name, contact, subject): typically **Protected B**
- **Request content / documents**: typically **Protected B or higher** (medical, legal, financial documents may be Protected C)
- **Processing workflow data** (status, assignee, timeline): typically **Protected A**

## Data Flow Ledger Template

Use this table in STRA/PIA submissions and security rollup reports. One row per significant data flow.

| Source Service | Target Service | Data Elements | Classification | Direction | Protocol/Port | Cross-Boundary? | PIA Covered? |
|---|---|---|---|---|---|---|---|
| `<app-a>` | `<app-b>` | Requestor name, contact, request content | Protected B | → | HTTPS/443 | Cross-namespace | TBD |
| `<app-b>` | `<app-c>` | Document bytes + metadata | Protected B | → | HTTPS/443 | Cross-namespace | TBD |
| `<app-c>` | External AI/OCR service | Document content (text extraction) | Protected B | → External | HTTPS/443 | Cross-cloud (Review) | Required |

## Cross-Boundary Risk Matrix

| Boundary Type | Classification | Risk | Required Controls |
|---|---|---|---|
| Same namespace, same classification | Any | COMPLIANT | Standard NetworkPolicy |
| Cross-namespace, same classification | Any | MEDIUM | Scoped NetworkPolicy (`namespaceSelector` + `podSelector` + `ports`) |
| Cross-namespace with wide-open NP | Protected B+ | HIGH | Remediate NP — add `podSelector` + `ports` |
| Cross-cluster (Silver ↔ Emerald) | Any | MEDIUM | Public Route + TLS; treat as external egress |
| Cross-cloud to Canadian data centre | Protected B | MEDIUM | MISA Data Processing Agreement required |
| Cross-cloud to non-specified region | Protected B+ | HIGH | PIA required; FOIPPA s.30.1 disclosure notice required |
| Cross-border (non-Canadian cloud region) | Protected B+ | CRITICAL | FOIPPA s.30.1 applies; ministerial approval required; explicit privacy notice to affected individuals |
