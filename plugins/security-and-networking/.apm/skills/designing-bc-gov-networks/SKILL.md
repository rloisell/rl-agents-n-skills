---
name: designing-bc-gov-networks
description: BC Government network architecture, SDN zone classification (Low/Medium/High), IMIT 6.13/6.28/5.08 compliance, Third Party Gateway (3PG) / Forward Proxy egress, and OpenShift NetworkPolicy authoring. Use when classifying DataClass, designing cross-zone or cross-cluster (Silver/Emerald) connectivity, writing NetworkPolicy YAML or ag-helm intent rules, or debugging Emerald default-deny failures.
compatibility: BC Gov OpenShift Private Cloud (Silver, Gold, Emerald); IMIT 6.13, 6.18, 6.28, 5.08; OCIO SDN Security Classification Model v1.0.
---

# Designing BC Gov Networks

Synthesises BC Gov SDN zone classification, IMIT standards, and OpenShift NetworkPolicy authoring into a single connectivity design workflow.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

1. **Classify by data at rest**: assign `DataClass` (`Low` / `Medium` / `High`) based on ISCF classification of data the workload stores, not data it passes through in memory.
2. **No zone-hopping**: only adjacent zones may communicate (`Low ↔ Medium ↔ High`; `DMZ ↔ Zone B ↔ Zone A`). Zone C is the Trusted Client Zone (workstations), never `DataClass: High`.
3. **Two-policy rule**: every OpenShift traffic flow requires an **Egress** NetworkPolicy on the sender pod AND an **Ingress** NetworkPolicy on the receiver pod.
4. **DNS egress first**: Emerald default-denies egress; every pod needs `allow-egress-dns` targeting `openshift-dns` (UDP/TCP 53).
5. **No direct internet egress**: Medium/High workloads must use the SDN Forward Proxy (whitelist) or 3PG CIDR (for external partners); CIDR policies to `0.0.0.0/0` are silently dropped at the SDN guardrail unless explicitly approved.
6. **Least-privilege NetworkPolicies**: never omit `podSelector` or `ports` on cross-namespace rules; Conftest hard-denies allow-all `{}` rules. For Emerald AVI/pod-label mechanics, see `bc-gov-emerald`.

## Quick start

1. Classify the workload's data at rest (`Low` / `Medium` / `High`) and map it to an IMIT 6.13 SDN zone (`DMZ`, `Zone B`, or `Zone A`).
2. Copy `allow-egress-dns.yaml` and the matching flow template from `assets/templates/`, then tailor pod labels and ports.
3. Verify both sender Egress and receiver Ingress policies with `oc describe networkpolicy`.

## Workflow

1. **Classify data & assign SDN zone**: Map ISCF class to `DataClass` (`Low`/`Medium`/`High`) and IMIT 6.13 zone (`DMZ`/`Zone B`/`Zone A`), then validate zone adjacency and egress path (Forward Proxy vs 3PG) per [sdn-zones-and-imit-standards.md](references/sdn-zones-and-imit-standards.md).
2. **Author NetworkPolicy manifests**: Implement DNS egress, two-policy intra/inter-namespace flows, router ingress, or `ag-helm` intent API rules per [networkpolicy-patterns.md](references/networkpolicy-patterns.md).
3. **Validate cross-cluster & Emerald enforcement**: Treat Silver ↔ Emerald flows as external egress via public Routes; confirm `DataClass`, `owner`, `environment` pod labels and AVI InfraSettings annotations match.

## Verification

- Every flow has both sender Egress and receiver Ingress policies, plus `allow-egress-dns`.
- Validate selectors and live reachability with `oc describe networkpolicy`, `oc get pod --show-labels`, and `oc exec ... -- curl -v <dest>:<port>` (or `auditing-ocp-network-posture` for multi-namespace audits).

## References

- [sdn-zones-and-imit-standards.md](references/sdn-zones-and-imit-standards.md) — ISCF-to-SDN mapping, IMIT 6.13 v5 & 5.08 (3PG) controls, SDN guardrails, Forward Proxy egress, and multi-segment vs single-segment patterns.
- [networkpolicy-patterns.md](references/networkpolicy-patterns.md) — Two-policy rule, DNS egress, same/cross-namespace YAML, `ag-helm` intent API, common ports, and debugging checklist.
- [Hosting Tiers & Porter TCP](references/hosting-tiers-and-porter-tcp.md) — Silver/Gold/Emerald tier comparison, SDN vs NSX-T vs OVN-Kubernetes, and Porter `TransportServerClaim` (`NodePort` requirement).
- [Acceptance Criteria](references/acceptance-criteria.md) — Observable pass/fail criteria for SDN zone classification, NetworkPolicy manifests, and Emerald verification.
- Templates: [allow-egress-dns.yaml](assets/templates/allow-egress-dns.yaml) • [allow-frontend-to-api.yaml](assets/templates/allow-frontend-to-api.yaml) • [allow-ingress-from-router.yaml](assets/templates/allow-ingress-from-router.yaml) • [allow-egress-external-cidr.yaml](assets/templates/allow-egress-external-cidr.yaml) • [allow-cross-namespace.yaml](assets/templates/allow-cross-namespace.yaml)
