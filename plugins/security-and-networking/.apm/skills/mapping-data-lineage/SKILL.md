---
name: mapping-data-lineage
description: Data classification and cross-service data flow lineage for BC Gov workloads — ISCF classification, data flow ledger templates, cross-boundary risk matrices, FOIPPA s.30.1 residency checks, OpenShift ConfigMap/env discovery commands, and PIA trigger checklists. Use when mapping personal information flows for STRA/PIA, assessing external AI/OCR cloud residency risk, or auditing cross-namespace/cross-cluster data movement.
compatibility: BC Gov OpenShift Private Cloud (Silver/Gold/Emerald), BC Gov FOIPPA and Privacy Act framework.
---

# Mapping Data Lineage

Maps personal information movement across services, namespaces, clusters, and cloud boundaries for STRA and PIA compliance.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

1. **Authoritative residency source**: always verify cloud region from the service endpoint URL in ConfigMaps or deployment environment variables before assuming Canadian residency.
2. **FOIPPA s.30.1 gate**: personal information (Protected B+) processed or stored outside Canada requires privacy notice disclosure, a written MISA Data Processing Agreement (DPA), and ministerial approval if cross-border.
3. **PIA before production**: any new cross-cloud flow, third-party processor, AI/ML processing (e.g., OCR/Document Intelligence), or automated decision-making involving personal data must not deploy to production until a PIA is reviewed.
4. **Stream/queue visibility**: message stream, topic, and queue keys in ConfigMaps indicate cross-namespace flows that must be recorded in the data flow ledger.
5. **Zone alignment**: map ISCF classifications to SDN zones using `designing-bc-gov-networks`.

## Quick start

1. Run the `oc` and `jq` discovery commands in [oc-discovery-commands.md](references/oc-discovery-commands.md) against the target namespaces.
2. Populate the Data Flow Ledger and Cross-Boundary Risk Matrix with each discovered endpoint and ISCF classification.
3. Check external AI/OCR or cross-cloud flows against FOIPPA s.30.1 and the PIA Trigger Checklist.

## Workflow

1. **Discover endpoints & streams**: Run the `oc` and `jq` queries in [oc-discovery-commands.md](references/oc-discovery-commands.md) against target namespaces to extract ConfigMap URLs, deployment env vars, stream/topic keys, and cloud endpoints.
2. **Classify & build ledger**: Assign ISCF classification (`Unclassified` / `Protected A` / `Protected B` / `Protected C`) and populate the Data Flow Ledger and Cross-Boundary Risk Matrix in [iscf-and-risk-matrix.md](references/iscf-and-risk-matrix.md).
3. **Evaluate residency & PIA triggers**: Check external AI/OCR and cloud flows against FOIPPA s.30.1 and the PIA Trigger Checklist in [foippa-residency-and-pia.md](references/foippa-residency-and-pia.md).
4. **Record & escalate**: Log triggered PIAs in `AI/securityNextSteps.md`, engage the Ministry Privacy Officer, and capture residual risks in the STRA.

## Verification

- Every external HTTPS/SMTP/Redis/AMQP/cloud endpoint found in ConfigMaps and deployments appears as a row in the Data Flow Ledger.
- Every Protected B+ external or cross-cloud flow has a confirmed Canadian region (or documented FOIPPA s.30.1 controls), MISA DPA status, and PIA coverage status.

## References

- [iscf-and-risk-matrix.md](references/iscf-and-risk-matrix.md) — ISCF classification quick reference, Data Flow Ledger template, and Cross-Boundary Risk Matrix.
- [foippa-residency-and-pia.md](references/foippa-residency-and-pia.md) — External AI/OCR service pattern, FOIPPA s.30.1 residency rules, and PIA Trigger Checklist.
- [oc-discovery-commands.md](references/oc-discovery-commands.md) — `oc` + `jq` commands to discover cross-service URLs, stream/queue keys, and cloud endpoints.
- [Acceptance Criteria](references/acceptance-criteria.md) — Observable pass/fail criteria for endpoint discovery, data flow ledgers, FOIPPA s.30.1 residency, and PIA gates.
