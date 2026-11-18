# Phase 2 — Gap Analysis Rubrics

## Contents

- [Cross-Namespace NP Risk Classification](#cross-namespace-np-risk-classification)
- [Stale & Orphaned NP Detection](#stale--orphaned-np-detection)
- [Route TLS & Admin UI Audit](#route-tls--admin-ui-audit)
- [Egress Classification](#egress-classification)

## Cross-Namespace NP Risk Classification

Load the full NP YAML from `networkpolicies.yaml` for every NP listed in `cross-namespace-nps.txt` and classify:

| Pattern | Risk | Classification |
|---------|------|----------------|
| `namespaceSelector: {}` (empty), no `podSelector`, no `ports` | CRITICAL | Wide-open — any pod in cluster can reach any pod in target NS |
| `namespaceSelector` with label, no `podSelector`, no `ports` | HIGH | Namespace-scoped but unrestricted — all pods and all ports |
| `namespaceSelector` with label, `podSelector` defined, no `ports` | MEDIUM | Pod-scoped but all ports unrestricted |
| `namespaceSelector` + `podSelector` + `ports` | COMPLIANT | Fully scoped |

For wide-open NPs, generate remediation YAML scoped with `namespaceSelector`, `podSelector`, and explicit `ports` (see `designing-bc-gov-networks`).

## Stale & Orphaned NP Detection

For each NP in `stale-nps.txt`:
1. Extract `podSelector.matchLabels` from `networkpolicies.yaml`.
2. Check `deployment-summary.txt` (and live pods if needed) for any workload with matching labels.
3. If no matching workload is found → **Orphaned** (recommend `oc delete networkpolicy <name> -n <ns>`).
4. If matching workload exists but NP is >2 years old → **Stale config** (review and validate).

> Stale NPs are especially common after Patroni-to-CloudNativePG migrations and Redis topology changes.

## Route TLS & Admin UI Audit

| TLS Termination | Risk | Notes |
|----------------|------|-------|
| `edge` | Standard | TLS at HAProxy; plaintext inside cluster |
| `reencrypt` | Preferred | End-to-end TLS; use for sensitive backends |
| `passthrough` | Review | TLS at pod; HAProxy cannot inspect; cert management shifts to app |
| missing / `none` | CRITICAL | Plaintext HTTP — immediate remediation required |

**Admin UI route detection**: Flag any route whose name or target service matches: `admin`, `console`, `insight`, `dashboard`, `manager`, `management`, `flower`, `rabbitmq`, `redis`, `pgadmin`, `kibana`, `grafana` (unless protected by SSO).

## Egress Classification

For each entry in `egress-candidates.txt`, classify the destination:

| Pattern | Classification | Risk |
|---------|---------------|------|
| `sso.gov.bc.ca`, `common-logon.gov.bc.ca`, `*.auth.*` | OIDC | Standard — verify port 443 |
| `*.amazonaws.com`, `*.s3.*`, `s3.gov.bc.ca` | S3 | Cloud egress — FWCR check |
| `*.azure.com`, `*.microsoft.com`, `cognitiveservices` | Azure | Cloud egress — FWCR + PIA check |
| SMTP/mail + port 25 | SMTP | HIGH — unencrypted relay |
| SMTP/mail + port 587/465 | SMTP | Encrypted relay |
| `*.gov.bc.ca` (non-SSO) | BC Gov Internal | Verify FWCR scope |
| Internal document management systems (`<internal-dms>`) | Internal DMS | Verify FWCR scope |
| Anything else | Unknown | Must classify before report is final |
