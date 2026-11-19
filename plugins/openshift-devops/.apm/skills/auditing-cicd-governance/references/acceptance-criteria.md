# Acceptance Criteria — Auditing CI/CD Governance

Observable pass/fail criteria for verifying platform-agnostic CI/CD governance audits, evidence maps, control matrices (`CM-01`–`CM-05`), severity-ranked findings, and executive deliverables.

## 1. Intake, Scope & Evidence Traceability

| Criterion | Pass Condition | Fail Condition |
|---|---|---|
| Scope & delivery model | Target delivery model (`SaaS`, `OpenShift`, or `hybrid`) and scope boundary (pipeline/process vs. app code) explicitly stated | Assessment mixes platform assumptions or omits scope boundaries |
| Machine-readable evidence | Pipeline configs and governance docs extracted into a line-referenced evidence map before control evaluation | Findings asserted without file path + line/section references, or drawn from un-OCR'd image-only PDFs |
| Provisional labeling | Missing governance exports (e.g., branch protection, approval logs) recorded as explicit assumption gaps with affected findings marked `Provisional` | Missing evidence silently assumed compliant/non-compliant without provisional status |

## 2. Control Matrix & Platform Context

| Criterion | Pass Condition | Fail Condition |
|---|---|---|
| Control coverage (`CM-01`–`CM-05`) | All five core domains (`CM-01` Release Integrity, `CM-02` Quality Gates, `CM-03` Secrets Lifecycle, `CM-04` Governance Approval, `CM-05` Audit Retention) plus determinism, segregation, supply chain, and rollback readiness evaluated | Any `CM-01`–`CM-05` domain omitted without explicit scope exclusion |
| SaaS intent-based mapping | Non-OpenShift SaaS targets (e.g., `force.com`) mapped to BC Gov standards (`IMIT 6.28`, `IMIT 5.08`, `IMIT 6.13`) by control intent | SaaS pipeline penalized for lacking Kubernetes-specific manifests (e.g., NetworkPolicies, SCC) |
| Hybrid context splitting | Mixed delivery models split findings by platform context with a cross-cutting control summary | Container and SaaS findings conflated into undifferentiated recommendations |

## 3. Findings & Remediation Roadmap

- **Pass**: Every finding is ranked (`Critical`, `High`, `Medium`, `Low`) and linked to direct evidence in the evidence map.
- **Pass**: Every `Critical` and `High` finding specifies a concrete remediation action, an owner role/team suggestion, and placement in the phased roadmap (`0-30`, `31-90`, `90+` days).
- **Fail**: Any `Critical` or `High` finding lacks a concrete action, owner candidate, or target phase.

## 4. Deliverable Package Completeness

- **Pass**: Standard output set produced with consistent versioning (`v1`, `v2`, ...): technical analysis report (`.md` + `.pdf`), executive summary, one-page brief, control matrix, and process log (`docs/process-log/YYYY-MM-DD-<title>.md`), with zero unredacted secrets or client identifiers in public templates.
- **Fail**: Executive brief contradicts technical report severity counts, or required deliverables are missing without user-agreed scope reduction.
