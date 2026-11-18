---
name: auditing-cicd-governance
description: >-
  Audits SaaS, container, and hybrid CI/CD deployment pipelines against BC Gov
  governance intent, producing evidence-mapped control matrices, severity-ranked
  findings, phased remediation roadmaps, and executive briefs. Use when assessing
  GitHub Actions, Bitbucket Pipelines, Azure DevOps, or GitLab CI delivery
  controls. Not for single-command pipeline fixes or feature code reviews.
---

# Auditing CI/CD Governance

Platform-agnostic, evidence-traceable governance assessment workflow for SaaS, container, and hybrid delivery pipelines.

## Contents

- [Constraints](#constraints) • [Quick start](#quick-start) • [Workflow](#workflow) • [Verification](#verification) • [References](#references)

## Constraints

1. **Evidence first**: Collect and map machine-readable evidence with line-level references before mapping controls or recommending actions.
2. **Intent-based mapping for SaaS**: For non-OpenShift SaaS environments (e.g., Salesforce `force.com`), map BC Gov standards (`IMIT 6.28`, `IMIT 5.08`, `IMIT 6.13`) by control intent rather than Kubernetes implementation details.
3. **Actionable Critical/High findings**: Every Critical or High finding must include a concrete remediation action and an owner suggestion.
4. **Explicit assumptions**: Document boundary conditions and assumption gaps (e.g., missing branch-protection exports) and mark affected findings as provisional.
5. **Edge-case handling**: Require OCR or machine-readable exports for image-only PDFs; split findings by platform context for mixed delivery models.

## Quick start

1. Confirm delivery model (SaaS, OpenShift, or hybrid) and scope boundaries (pipeline/process vs. application code).
2. Extract machine-readable pipeline configs and governance docs into a line-referenced evidence map.
3. Evaluate controls against `CM-01..CM-05` in [control-matrix-and-deliverables.md](references/control-matrix-and-deliverables.md).

## Workflow

1. **Intake & Scope**: Confirm scope boundaries (pipeline/process vs. application code), target delivery model (SaaS, OpenShift, hybrid), and required audience deliverables.
2. **Evidence Capture**: Extract machine-readable source content from pipeline configs and docs, build a line-referenced evidence map, and cite any verified external platform behavior.
3. **Control Analysis**: Evaluate release integrity, determinism, segregation, quality gates, secrets lifecycle, governance approvals, supply chain, audit retention, and rollback readiness ([control-matrix-and-deliverables.md](references/control-matrix-and-deliverables.md)).
4. **Findings & Roadmap**: Rank findings (`Critical`, `High`, `Medium`, `Low`), assign concrete recommendations and domain owners, and build a phased roadmap (`0-30`, `31-90`, `90+` days).
5. **Package Deliverables**: Produce the technical report, executive summary, one-page brief, control matrix, and process artifacts ([control-matrix-and-deliverables.md](references/control-matrix-and-deliverables.md)).

## Verification

Before finalizing the assessment package:
- Confirm every finding links to direct line-level or artifact-level evidence.
- Confirm all Critical/High findings specify a remediation action, phased timeline, and owner candidate.
- Confirm assumptions and provisional findings are explicitly labeled.

## References

- [control-matrix-and-deliverables.md](references/control-matrix-and-deliverables.md) — Control domains (`CM-01..CM-05`), standard output filenames, examples, and IMIT/security references
- [Acceptance Criteria](references/acceptance-criteria.md) — Observable pass/fail criteria for evidence mapping, control coverage, findings, and deliverables
