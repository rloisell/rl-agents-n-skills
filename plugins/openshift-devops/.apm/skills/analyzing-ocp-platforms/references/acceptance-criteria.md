# Acceptance Criteria — Analyzing OpenShift Platforms

Observable pass/fail criteria for verifying OpenShift migration gap analyses (G1–G12), resilience posture assessments (R01–R15), multi-app coupling orchestrations, and versioned PDF deliverables.

## 1. Pre-Flight & Collection Integrity

| Criterion | Pass Condition | Fail Condition |
|---|---|---|
| Read-only posture | Zero mutating `oc` commands (`apply`, `patch`, `delete`, `scale`, `rollout`) or target-repo edits executed | Any cluster workload, deployment, or target repo modified during collection or analysis |
| Secret value exclusion | Secrets collected via `oc get secret --no-headers` (names/types only); no base64 secret values or tokens stored in artifacts | `oc get secret -o yaml` dumped or any secret value/token present in captured files or reports |
| Subagent context isolation | Raw `workloads.yaml`, `pdbs.yaml`, and `pods.yaml` parsed by `ocp-migration-analyst` or `ocp-resilience-analyst` | Raw multi-hundred-line YAML dumps loaded directly into the main conversation thread |

## 2. Analysis Mode Completeness

| Mode | Pass Condition | Fail Condition |
|---|---|---|
| **Migration (G1–G12)** | All 12 gap checks (`G1`–`G12`) evaluated with status, evidence, network flow mapping, and `HELM-XX` remediation tasks | Any G1–G12 check omitted without explicit N/A justification, or network flows missing |
| **Resilience (R01–R15)** | All 15 checks (`R01`–`R15`) scored with letter grades (`A`–`F`), affected workloads, and `RES-NN` remediation tasks | Any R01–R15 check omitted, ungraded, or missing affected workload names |
| **Multi-App (2+ apps)** | `coupling-matrix.md` completed and upstream-first migration sequence established before per-app deep-dives | Per-app deep-dives or sequencing drafted without a completed cross-namespace coupling matrix |

## 3. Traceability & Confidentiality

- **Pass**: Every G1–G12 gap, R01–R15 finding, and `HELM-XX`/`RES-NN` task row cites at least one valid standard ID (`PS-*`, `AD-*`, `ISB-*`, `OCP-*`, `K8S-*`, `SEC-*`) from [standards-catalog.md](standards-catalog.md).
- **Fail**: Any finding or task row lacks a `Standard` citation or cites an invented/non-catalog ID.
- **Pass**: Public/shared skill examples and templates contain only generic placeholders (`<ns-prefix>-dev`, `<APP-NAME>`, `<license-plate>`).
- **Fail**: Unredacted client names, real OCP namespace IDs, tokens, or internal IPs appear in non-private outputs.

## 4. Report Formatting & PDF Parity

- **Pass**: Report uses versioned naming (`<APP-NAME>-Resilience-Report-v<N>.md` / `<APP-NAME>-Migration-Analysis.md`), never overwrites `v(N-1)`, ends every metadata header line with two trailing spaces (`  `), includes a numbered `## Table of Contents` and footer, and has a matching `.pdf` rendered with `report-style.css` where all diagram images resolve.
- **Fail**: Prior version overwritten, missing `.pdf` counterpart, broken diagram images in PDF, or collapsed single-line metadata header due to missing trailing spaces.
