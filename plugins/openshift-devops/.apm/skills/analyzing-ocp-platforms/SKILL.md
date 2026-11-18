---
name: analyzing-ocp-platforms
description: >-
  Conducts OpenShift platform migration gap analysis (G1-G12), workload
  resilience posture assessments (R01-R15), multi-app coupling orchestration,
  and versioned PDF report generation. Use when evaluating OCP Silver/Gold/Emerald
  namespaces for migration readiness, PodDisruptionBudget and HA resilience, or
  inter-app dependencies across a program area.
---

# Analyzing OpenShift Platforms

Structured, evidence-based analysis for OpenShift platform migrations, workload resilience posture, and multi-application portfolios.

## Contents

- [Constraints](#constraints) • [Quick start](#quick-start) • [Modes](#modes) • [Workflow](#workflow) • [Verification](#verification) • [References](#references)

## Constraints

1. **Read-only analysis**: Never modify cluster workloads, deployments, or target repositories during collection or assessment.
2. **No secret values**: Collect `oc get secret --no-headers` names/types only; never dump secret data.
3. **Context isolation**: Offload raw `workloads.yaml`, `pdbs.yaml`, and `pods.yaml` parsing to `ocp-migration-analyst` or `ocp-resilience-analyst` subagents so large manifests do not bloat the main thread.
4. **Traceable standards**: Every G1–G12 gap, R01–R15 check, and remediation task must cite its standard ID from [standards-catalog.md](references/standards-catalog.md).
5. **Versioned report + PDF parity**: Never overwrite prior report versions; every `v<N>.md` must have a matching `v<N>.pdf` rendered with `report-style.css`.
6. **Coupling matrix first**: For 2+ interconnected apps, complete the coupling matrix before per-app deep-dives or migration sequencing.

## Quick start

1. Confirm cluster and GitHub access: `oc whoami && gh auth status`.
2. Select an analysis mode from the table below and capture namespace YAML manifests without secret values.
3. Offload raw `workloads.yaml`, `pdbs.yaml`, and `pods.yaml` parsing to `ocp-migration-analyst` or `ocp-resilience-analyst`.

## Modes

| Mode | Scope | Key Outputs | Reference |
|---|---|---|---|
| **Migration** | Single-app Silver/Gold → Emerald | G1–G12 gaps, network flows, `<APP>-Migration-Analysis.md/.pdf` | [migration-gaps-g1-g12.md](references/migration-gaps-g1-g12.md) |
| **Resilience** | Per-namespace HA & disruption | R01–R15 scorecard (A–F), `<APP>-Resilience-Report-v<N>.md/.pdf` | [resilience-checks-r01-r15.md](references/resilience-checks-r01-r15.md) |
| **Multi-App** | 2+ interconnected apps | `coupling-matrix.md`, deep-dives, cross-cutting rollups | [multi-app-orchestration.md](references/multi-app-orchestration.md) |

## Workflow

1. **Pre-flight & Collection**: Verify `oc whoami` and `gh auth status`, then run manual `oc` commands or toolkit scripts to capture namespace manifests and repo structure ([oc-collection-and-toolkits.md](references/oc-collection-and-toolkits.md)).
2. **Coupling Matrix (multi-app only)**: Map cross-namespace NetworkPolicies, HTTP calls, shared Redis/S3/Keycloak/DBs, and determine upstream-first migration order ([multi-app-orchestration.md](references/multi-app-orchestration.md)).
3. **Evaluate Gaps & Resilience**: Assess collected manifests against G1–G12 migration checks ([migration-gaps-g1-g12.md](references/migration-gaps-g1-g12.md)) and R01–R15 resilience checks ([resilience-checks-r01-r15.md](references/resilience-checks-r01-r15.md)).
4. **Draft Report**: Assemble the required sections, metadata header (two trailing spaces per line), standards columns, and `HELM-XX`/`RES-NN` task tables ([report-format-and-pdf.md](references/report-format-and-pdf.md)).
5. **Render PDF**: Run `pandoc` with `report-style.css` and headless Chrome from the report directory so relative diagram paths resolve ([report-format-and-pdf.md](references/report-format-and-pdf.md)).

## Verification

Before delivering any report:
- Confirm all findings and task rows cite valid standard IDs from [standards-catalog.md](references/standards-catalog.md).
- Confirm metadata header lines end with two trailing spaces and `v<N>.md` / `v<N>.pdf` both exist.
- Confirm no client secrets, tokens, or unredacted sensitive values appear in outputs.

## References

- [oc-collection-and-toolkits.md](references/oc-collection-and-toolkits.md) — `oc` CLI capture commands, repo inspection, automated toolkits
- [migration-gaps-g1-g12.md](references/migration-gaps-g1-g12.md) — G1–G12 gap matrix, network flow mapping, task numbering
- [resilience-checks-r01-r15.md](references/resilience-checks-r01-r15.md) — R01–R15 checks, A–F grading, PDB/anti-affinity/QoS/drain patterns
- [multi-app-orchestration.md](references/multi-app-orchestration.md) — Phases 0–5, coupling matrix, sequencing rules, cross-cutting rollups
- [report-format-and-pdf.md](references/report-format-and-pdf.md) — Versioning, headers, section templates, `report-style.css`, Pandoc + Chrome PDF
- [standards-catalog.md](references/standards-catalog.md) — Authoritative `PS-*`, `AD-*`, `ISB-*`, `OCP-*`, `K8S-*`, `SEC-*` catalog
- [Acceptance Criteria](references/acceptance-criteria.md) — Observable pass/fail criteria for migration, resilience, multi-app, and PDF outputs
