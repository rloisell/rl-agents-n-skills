# Acceptance Criteria — Mapping Data Lineage

Observable pass/fail criteria for BC Gov data classification, cross-service data flow ledgers, and FOIPPA/PIA compliance checks.

## Discovery & Data Flow Ledger

| Criterion | Pass | Fail |
|---|---|---|
| Authoritative endpoint discovery | All ConfigMap URLs, deployment environment variables, and cloud endpoints are extracted via `oc` + `jq` discovery commands. | Endpoints guessed from architecture diagrams without checking live ConfigMaps/env vars. |
| Complete ledger coverage | Every external HTTPS, SMTP, Redis, AMQP, and cloud endpoint found in cluster config appears as a row in the Data Flow Ledger. | Discovered endpoints omitted from the ledger. |
| Stream & queue visibility | Message stream, topic, and queue keys indicating cross-namespace flows are recorded in the ledger and Cross-Boundary Risk Matrix. | Async/event-driven cross-namespace flows omitted. |
| ISCF & zone alignment | Each flow is assigned an ISCF class (`Unclassified` / `Protected A` / `Protected B` / `Protected C`) aligned with `designing-bc-gov-networks` SDN zones. | Unclassified flows or ISCF classes contradicting stored data sensitivity. |

## Residency, FOIPPA s.30.1 & PIA Gates

| Criterion | Pass | Fail |
|---|---|---|
| Verified cloud residency | Cloud region is confirmed directly from the service endpoint URL in ConfigMaps or env vars (never assumed Canadian). | Canadian residency assumed from vendor marketing without checking the configured endpoint URL. |
| FOIPPA s.30.1 compliance | Any Protected B+ personal information processed or stored outside Canada has documented privacy notice disclosure, MISA DPA, and ministerial approval. | Cross-border Protected B+ flow lacking DPA, privacy notice, or ministerial approval. |
| PIA pre-production gate | New cross-cloud flows, third-party processors, AI/ML (e.g., OCR/Document Intelligence), or automated decision-making have PIA review before production deployment. | Triggered PIA flow promoted to production without Ministry Privacy Officer review. |
| Escalation & STRA capture | Triggered PIAs are logged in `AI/securityNextSteps.md`, Ministry Privacy Officer is engaged, and residual risks are recorded in the STRA. | Triggered PIAs left undocumented or omitted from STRA residual risk tracking. |
