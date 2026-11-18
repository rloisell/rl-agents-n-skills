# Acceptance Criteria — Designing BC Gov Networks

Observable pass/fail criteria for BC Gov SDN zone classification, IMIT alignment, and OpenShift NetworkPolicy design.

## Zone Classification & IMIT Alignment

| Criterion | Pass | Fail |
|---|---|---|
| Data-at-rest `DataClass` | `DataClass` (`Low` / `Medium` / `High`) is assigned from the ISCF classification of data stored at rest by the workload. | Classification based on transient in-memory passthrough data or left unassigned. |
| Zone adjacency | Traffic flows only between adjacent IMIT 6.13 zones (`DMZ <-> Zone B <-> Zone A`); Zone C is never `DataClass: High`. | Direct `DMZ <-> Zone A` zone-hopping or `High` workloads placed in Zone C. |
| Egress path compliance | Medium/High external egress uses the SDN Forward Proxy (whitelist) or Third Party Gateway (3PG) CIDR per IMIT 5.08; no unapproved `0.0.0.0/0` CIDR rules. | Direct internet egress from Medium/High workloads or `0.0.0.0/0` rules without documented exemption. |

## NetworkPolicy Manifests

| Criterion | Pass | Fail |
|---|---|---|
| DNS egress present | Every pod/namespace in Emerald has `allow-egress-dns` targeting `openshift-dns` on UDP/TCP 53. | Missing DNS egress policy (causing silent resolution failures under default-deny). |
| Two-policy rule | Every intra- and inter-namespace flow has both a sender **Egress** NetworkPolicy and a receiver **Ingress** NetworkPolicy. | Only Ingress or only Egress policy defined for a flow. |
| Least-privilege selectors | Cross-namespace rules specify explicit `namespaceSelector`, `podSelector` (non-empty), and `ports`; zero `{}` allow-all rules. | Empty `podSelector: {}` or omitted `ports` on cross-namespace policies (Conftest hard-deny). |

## Cross-Cluster & Emerald Verification

| Criterion | Pass | Fail |
|---|---|---|
| Cross-cluster routing | Silver <-> Emerald traffic is designed as external egress via public Routes (not internal cluster DNS). | Assuming direct pod/service DNS across Silver and Emerald clusters. |
| Emerald labels & AVI | Pod labels (`DataClass`, `owner`, `environment`) and AVI `InfraSettings` annotations are consistent and verified. | Mismatched `DataClass` labels or missing AVI annotations on Emerald Routes. |
| Live verification | Selectors and reachability are confirmed with `oc describe networkpolicy`, `oc get pod --show-labels`, and `oc exec ... -- curl -v <dest>:<port>`. | Policies declared complete without verifying label matching and live traffic path. |
