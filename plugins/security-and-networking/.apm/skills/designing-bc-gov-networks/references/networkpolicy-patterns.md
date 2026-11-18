# OpenShift NetworkPolicy Patterns for BC Gov

## Contents

- [The Two-Policy Rule](#the-two-policy-rule)
- [DNS Egress — Required on Every Pod](#dns-egress--required-on-every-pod)
- [Common Flow Patterns](#common-flow-patterns)
- [Cross-Namespace & Cross-Cluster Flows](#cross-namespace--cross-cluster-flows)
- [ag-helm Intent API (Preferred Authoring)](#ag-helm-intent-api-preferred-authoring)
- [Common Port Reference](#common-port-reference)
- [Debugging Checklist](#debugging-checklist)

## The Two-Policy Rule

Every traffic flow requires **two NetworkPolicy objects**: an **Egress** policy on the sender pod in the sender's namespace, and an **Ingress** policy on the receiver pod in the receiver's namespace. Defining only one causes a silent TCP timeout.

## DNS Egress — Required on Every Pod

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-egress-dns
  namespace: <license-plate>-dev
spec:
  podSelector: {}
  policyTypes: [Egress]
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: openshift-dns
      ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
```

> The `to: namespaceSelector` targeting `openshift-dns` is required — Conftest hard-denies egress rules without a `to:` peer selector.

## Common Flow Patterns

### Frontend → API (same namespace)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-egress-frontend-to-api
spec:
  podSelector:
    matchLabels:
      app: frontend
  policyTypes: [Egress]
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: api
      ports:
        - protocol: TCP
          port: 8080
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-ingress-api-from-frontend
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes: [Ingress]
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend
      ports:
        - protocol: TCP
          port: 8080
```

### Router → Pod (inbound from OpenShift router)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-ingress-from-router
spec:
  podSelector:
    matchLabels:
      app: frontend
  policyTypes: [Ingress]
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              network.openshift.io/policy-group: ingress
```

### Egress to External IP / CIDR (on-prem DB, external API, or 3PG)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-egress-api-to-oracle
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes: [Egress]
  egress:
    - to:
        - ipBlock:
            cidr: 198.51.100.0/24
      ports:
        - protocol: TCP
          port: 1521
```

## Cross-Namespace & Cross-Cluster Flows

### Scoped Cross-Namespace Ingress Pattern

Never use `namespaceSelector` alone without `podSelector` and `ports`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-<source-app>-api
  namespace: <target-ns>-dev
spec:
  podSelector:
    matchLabels:
      app: <target-app>-api
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: <source-ns>-dev
          podSelector:
            matchLabels:
              app: <source-app>-api
      ports:
        - protocol: TCP
          port: 8080
```

### Cross-Cluster Flows (Silver ↔ Emerald)

There is **no direct cluster-to-cluster Kubernetes networking** between Silver and Emerald. All cross-cluster calls route via **public Routes** with TLS and should be treated as external egress (Forward Proxy / FWCR as applicable).

## ag-helm Intent API (Preferred Authoring)

When using `ag-helm-templates`, use `ag-template.networkpolicy` with `AllowIngressFrom` and `AllowEgressTo` so generated manifests pass `ag-devops` Conftest gates:

```yaml
{{- $np := dict "Values" .Values -}}
{{- $_ := set $np "ApplicationGroup" .Values.project -}}
{{- $_ := set $np "Name" "<app-name>" -}}
{{- $_ := set $np "Namespace" $.Release.Namespace -}}
{{- $_ := set $np "PolicyTypes" (list "Ingress" "Egress") -}}

{{- $_ := set $np "AllowIngressFrom" (dict
  "ports" (list 8080)
  "apps" (list (dict "name" "rabbitmq"))
) -}}

{{- $_ := set $np "AllowEgressTo" (dict
  "ipBlocks" (list (dict
    "cidr" "198.51.100.0/24"
    "ports" (list 443)
  ))
) -}}

{{ include "ag-template.networkpolicy" $np }}
```

If `0.0.0.0/0` egress is unavoidable, Conftest requires `Annotations` with `justification` and `approvedBy`.

## Common Port Reference

| Service | Protocol | Port |
| --- | --- | --- |
| Oracle Database | TCP | 1521 |
| SQL Server (MSSQL) | TCP | 1433 |
| PostgreSQL | TCP | 5432 |
| MySQL / MariaDB | TCP | 3306 |
| LDAP / LDAPS | TCP | 389 / 636 |
| SMTP | TCP | 25 / 587 |
| NTP | UDP | 123 |
| DNS | UDP + TCP | 53 |
| HTTP / HTTPS | TCP | 80 / 443 |
| Kubernetes API / OCP App | TCP | 6443 / 8080 |

## Debugging Checklist

1. **Two-policy rule**: sender has Egress AND receiver has Ingress?
2. **DNS egress**: `allow-egress-dns` present on sender?
3. **Label match**: `podSelector.matchLabels` matches running pod labels?
4. **Namespace scope**: `namespaceSelector` present for cross-namespace flows?
5. **Port match**: policy port matches listening container port?
6. **SDN guardrail**: destination on internet from Medium/High workload? (NP cannot override guardrail.)

```bash
oc get networkpolicy -n <ns-prefix>-dev
oc describe networkpolicy <name> -n <ns-prefix>-dev
oc exec <pod> -n <ns-prefix>-dev -- curl -v <destination>:<port>
oc debug -n <ns-prefix>-dev deployment/<name> -- curl -v <destination>:<port>
oc get pod <pod> -n <ns-prefix>-dev --show-labels
```
