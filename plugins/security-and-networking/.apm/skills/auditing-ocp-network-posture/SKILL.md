---
name: auditing-ocp-network-posture
description: OpenShift container network posture auditing across multi-namespace groups — collecting NetworkPolicy, Service, Route, Deployment, and ConfigMap/env egress data, classifying wide-open cross-namespace and stale NPs, auditing Route TLS and admin UI exposure, classifying third-party egress, and rendering 6-section Markdown/PDF posture reports. Use when auditing OCP network security posture or preparing Emerald migration baselines.
compatibility: OpenShift 4.x (Silver, Gold, Emerald); requires oc CLI (logged in), jq, pandoc, Chrome headless.
---

# Auditing OCP Network Posture

Produces evidence-based, 6-section network posture reports for any group of OpenShift namespaces.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

1. **Data before analysis**: never generate findings until Phase 1 collection completes; if commands fail or return empty, note the gap and never fabricate NP names, hostnames, or egress targets.
2. **Evidence-backed findings**: every finding must cite the specific namespace, NetworkPolicy name, Route name, or ConfigMap/env key from collected artifacts.
3. **Never leave egress `Unknown`**: classify every entry in `egress-candidates.txt` before finalising the report.
4. **Versioned outputs**: save reports with `-v<N>` suffixes (`<LABEL>-Network-Report-v1.md` and `.pdf`); copy `v(N-1)` to `v(N)` before editing (see `doc-versioning`).
5. **Cross-skill alignment**: use `designing-bc-gov-networks` for scoped NP remediation YAML and `mapping-data-lineage` for PIA/FOIPPA triggers on cloud egress.

## Quick start

1. Log in to the target OpenShift cluster (`oc login`) and set `OUTPUT` and `LABEL` environment variables.
2. Run Phase 1 collection commands from [collection-commands.md](references/collection-commands.md) for each target namespace.
3. Classify findings and generate `<LABEL>-Network-Report-v1.md` and `.pdf`.

## Workflow

1. **Phase 1 — Collect**: Run the per-namespace `oc` + `jq` commands in [collection-commands.md](references/collection-commands.md) to populate `<OUTPUT>/<namespace>/` (`networkpolicies.yaml`, `cross-namespace-nps.txt`, `stale-nps.txt`, `route-summary.txt`, `egress-candidates.txt`, `deployment-summary.txt`, `summary.md`) and `cross-namespace-matrix.md`.
2. **Phase 2 — Gap analysis**: Classify cross-namespace NPs, cross-reference stale NPs against `deployment-summary.txt` (especially after Patroni-to-CloudNativePG or Redis migrations), audit Route TLS and admin UI exposure, and classify egress destinations per [gap-analysis-rubrics.md](references/gap-analysis-rubrics.md).
3. **Phase 3 — Draft report**: Author the 6-section report with RAG ratings and `NET-NN` tasks sorted `CRITICAL → HIGH → MEDIUM → LOW` per [report-and-pdf-rendering.md](references/report-and-pdf-rendering.md).
4. **Phase 4 — Render PDF**: Compile HTML via `pandoc` and PDF via headless Chrome per [report-and-pdf-rendering.md](references/report-and-pdf-rendering.md).

## Verification

- All target namespaces have a `summary.md` and collected YAML/text artifacts.
- Every wide-open cross-namespace NP and plaintext HTTP Route appears in Section 1 (Executive Summary) with a 🔴 RED RAG rating.
- Both `<LABEL>-Network-Report-v<N>.md` and `<LABEL>-Network-Report-v<N>.pdf` exist and are non-empty.

## References

- [collection-commands.md](references/collection-commands.md) — Phase 1 `oc` and `jq` commands for NPs, Services, Routes, Workloads, Egress candidates, `summary.md`, and `cross-namespace-matrix.md`.
- [gap-analysis-rubrics.md](references/gap-analysis-rubrics.md) — Cross-namespace NP risk tiers, stale/orphaned NP detection, Route TLS & admin UI rubrics, and egress classification table.
- [report-and-pdf-rendering.md](references/report-and-pdf-rendering.md) — 6-section report specification, RAG criteria, `NET-NN` task format, `pandoc` + Chrome headless PDF rendering, and toolkit invocation.
- [Acceptance Criteria](references/acceptance-criteria.md) — Observable pass/fail criteria for Phase 1 collection, gap analysis, and report/PDF deliverables.
