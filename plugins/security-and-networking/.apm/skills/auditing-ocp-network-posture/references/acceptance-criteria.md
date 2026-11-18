# Acceptance Criteria — Auditing OCP Network Posture

Observable pass/fail criteria for verifying an OpenShift multi-namespace network posture audit.

## Phase 1: Evidence Collection

| Criterion | Pass | Fail |
|---|---|---|
| Per-namespace artifacts | Every target namespace has `networkpolicies.yaml`, `cross-namespace-nps.txt`, `stale-nps.txt`, `route-summary.txt`, `egress-candidates.txt`, `deployment-summary.txt`, and `summary.md`. | Any target namespace is missing artifacts or relies on memory instead of `oc` output. |
| Cross-namespace matrix | `cross-namespace-matrix.md` exists and maps all discovered inter-namespace allow rules. | Matrix is missing or omits namespaces from the target scope. |
| Gap honesty | Failed or empty `oc` commands are explicitly noted as collection gaps. | NP names, hostnames, or egress targets are fabricated to fill empty outputs. |

## Phase 2: Gap Analysis & Classification

| Criterion | Pass | Fail |
|---|---|---|
| Evidence citations | Every finding cites the exact namespace, NetworkPolicy, Route, or ConfigMap/env key from Phase 1 artifacts. | Generic or unattributed findings without artifact references. |
| Cross-namespace & stale NPs | Wide-open cross-namespace NPs (omitted `podSelector` or `ports`) and stale NPs (cross-referenced against `deployment-summary.txt`) are classified by risk tier. | Stale NPs left unverified or wide-open rules omitted from high-severity tiers. |
| Route & admin UI audit | All Routes are audited for TLS termination (`edge`/`reencrypt`/`passthrough` vs plaintext HTTP) and exposed admin UIs. | Plaintext HTTP Routes or unauthenticated admin UIs are missed or under-rated. |
| Egress classification | Every entry in `egress-candidates.txt` is classified (e.g., Internal, BC Gov 3PG/Proxy, Cloud/SaaS, External API). | Any egress destination remains `Unknown` in the final report. |

## Phase 3 & 4: Report & PDF Deliverables

| Criterion | Pass | Fail |
|---|---|---|
| Versioned filenames | Outputs follow `<LABEL>-Network-Report-v<N>.md` and `.pdf`; `v(N-1)` copied to `v(N)` before editing. | Unversioned filenames or overwriting prior versions without incrementing `v<N>`. |
| 6-section structure | Report contains all 6 required sections; Section 1 includes 🔴 RED RAG ratings for wide-open cross-namespace NPs and plaintext HTTP Routes. | Missing sections or 🔴 RED findings omitted from Executive Summary. |
| Prioritised remediation | `NET-NN` tasks are sorted `CRITICAL -> HIGH -> MEDIUM -> LOW` and align with `designing-bc-gov-networks` and `mapping-data-lineage`. | Unsorted tasks or remediation YAML that violates two-policy/least-privilege rules. |
| PDF compilation | Both `.md` and `.pdf` files exist, are non-empty, and render cleanly via `pandoc` + headless Chrome. | Missing, empty, or broken PDF output. |
