# NetworkPolicy Patterns

Reference NetworkPolicy patterns for BC Government Emerald OpenShift deployments.

## Contents

- [Recommended: `ag-helm` Intent-Based API](#recommended-ag-helm-intent-based-api)
- [Alternative: Raw NetworkPolicy YAML](#alternative-raw-networkpolicy-yaml)
- [Default Deny](#default-deny-apply-first-to-every-namespace)
- [Allow Ingress from OpenShift Router](#allow-ingress-from-openshift-router)
- [Allow Frontend → API](#allow-frontend--api)
- [Allow API → Database](#allow-api--database)
- [Allow Egress to External (HTTPS only)](#allow-egress-to-external-https-only)
- [Allow DNS Resolution](#allow-dns-resolution)
- [Allow User Workload Monitoring (Prometheus)](#allow-user-workload-monitoring-prometheus)
- [Complete Minimal Policy Set](#complete-minimal-policy-set)

---

## Recommended: `ag-helm` Intent-Based API

When consuming `ag-helm-templates`, create NetworkPolicies using the intent-based API to avoid accidental allow-all shapes rejected by the Rego policy gate.

### Frontend policy (ingress from router + egress to backend)

```tpl
{{- $np := dict "Values" .Values -}}
{{- $_ := set $np "ApplicationGroup" .Values.project -}}
{{- $_ := set $np "Name" "frontend" -}}
{{- $_ := set $np "Namespace" $.Release.Namespace -}}

{{- $_ := set $np "PolicyTypes" (list "Ingress" "Egress") -}}

{{- $_ := set $np "AllowIngressFrom" (dict
  "ports" (list 8080)
  "namespaces" (list (dict
    "name" "openshift-ingress"
    "podSelector" (dict "matchLabels" (dict
      "ingresscontroller.operator.openshift.io/deployment-ingresscontroller" "default"
    ))
  ))
) -}}

{{- $_ := set $np "AllowEgressTo" (dict
  "apps" (list (dict
    "name" "web-api"
    "ports" (list (dict "port" 8080 "protocol" "TCP"))
  ))
) -}}

{{ include "ag-template.networkpolicy" $np }}
```

### API / Backend policy (ingress from frontend + router; egress to DB)

```tpl
{{- $np := dict "Values" .Values -}}
{{- $_ := set $np "ApplicationGroup" .Values.project -}}
{{- $_ := set $np "Name" "web-api" -}}
{{- $_ := set $np "Namespace" $.Release.Namespace -}}

{{- $_ := set $np "PolicyTypes" (list "Ingress" "Egress") -}}

{{- $_ := set $np "AllowIngressFrom" (dict
  "ports" (list 8080)
  "apps" (list (dict "name" "frontend"))
  "namespaces" (list (dict
    "name" "openshift-ingress"
    "podSelector" (dict "matchLabels" (dict
      "ingresscontroller.operator.openshift.io/deployment-ingresscontroller" "default"
    ))
  ))
) -}}

{{- $_ := set $np "AllowEgressTo" (dict
  "apps" (list (dict
    "name" "postgresql"
    "ports" (list (dict "port" 3306 "protocol" "TCP"))
  ))
) -}}

{{ include "ag-template.networkpolicy" $np }}
```

### Database policy (ingress from API only)

```tpl
{{- $np := dict "Values" .Values -}}
{{- $_ := set $np "ApplicationGroup" .Values.project -}}
{{- $_ := set $np "Name" "postgresql" -}}
{{- $_ := set $np "Namespace" $.Release.Namespace -}}

{{- $_ := set $np "PolicyTypes" (list "Ingress") -}}

{{- $_ := set $np "AllowIngressFrom" (dict
  "ports" (list 3306)
  "apps" (list (dict "name" "web-api"))
) -}}

{{ include "ag-template.networkpolicy" $np }}
```

> **Rego & Intent API rules**: `assets/policies/network-policies.rego` denies egress rules without `to` (allow-all destination), rules without `ports`, wildcard peers (`podSelector: {}`), and ingress `podSelector` peers without a `namespaceSelector` (which would match pods in all namespaces).
>
> - **`AllowIngressFrom.namespaces`**: Pass `name: <ns>` alongside `podSelector` (as shown for `openshift-ingress` above) so the rendered rule includes both `namespaceSelector` and `podSelector` — scoping cross-namespace traffic to a single namespace and specific pods.
> - **`AllowIngressFrom.apps`**: Targets sibling pods by app label; verify the rendered rule includes `namespaceSelector` (or use `AllowIngressFrom.namespaces` with `name: $.Release.Namespace` and `podSelector`) so `network-policies.rego` does not flag a missing `namespaceSelector`.

---

## Alternative: Raw NetworkPolicy YAML

Use raw YAML when not consuming `ag-helm-templates`. Apply as Helm templates in `charts/<service>/templates/networkpolicy.yaml`.

---

## Default Deny (apply first to every namespace)

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: {{ .Values.namespace }}
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
```

Apply `default-deny-all` **before** any pod-specific allow policies.

---

## Allow Ingress from OpenShift Router

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-openshift-ingress
  namespace: {{ .Values.namespace }}
spec:
  podSelector:
    matchLabels:
      app: {{ include "<chart>.fullname" . }}-frontend
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: openshift-ingress
          podSelector:
            matchLabels:
              # Confirm with: oc -n openshift-ingress get pods --show-labels
              ingresscontroller.operator.openshift.io/deployment-ingresscontroller: default
  policyTypes:
    - Ingress
```

---

## Allow Frontend → API

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-api
  namespace: {{ .Values.namespace }}
spec:
  podSelector:
    matchLabels:
      app: {{ include "<chart>.fullname" . }}-api
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: {{ include "<chart>.fullname" . }}-frontend
      ports:
        - protocol: TCP
          port: 8080
  policyTypes:
    - Ingress
```

---

## Allow API → Database

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-api-to-database
  namespace: {{ .Values.namespace }}
spec:
  podSelector:
    matchLabels:
      app: {{ include "<chart>.fullname" . }}-database
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: {{ include "<chart>.fullname" . }}-api
      ports:
        - protocol: TCP
          port: 3306
  policyTypes:
    - Ingress
```

---

## Allow Egress to External (HTTPS only)

> When targeting `0.0.0.0/0`, `network-policies.rego` requires `justification` and `approvedBy` annotations. Prefer specific destination CIDRs (`ipBlock.cidr`) whenever possible.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-egress-https
  namespace: {{ .Values.namespace }}
  annotations:
    justification: "Outbound HTTPS to external API"
    approvedBy: "<ticket-or-approver>"
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/part-of: {{ .Values.project }}
  egress:
    - to:
        - ipBlock:
            cidr: 0.0.0.0/0
            except:
              - 10.0.0.0/8
              - 172.16.0.0/12
              - 192.168.0.0/16
      ports:
        - protocol: TCP
          port: 443
  policyTypes:
    - Egress
```

---

## Allow DNS Resolution

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
  namespace: {{ .Values.namespace }}
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/part-of: {{ .Values.project }}
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: openshift-dns
          podSelector:
            matchLabels:
              dns.operator.openshift.io/daemonset-dns: default
      ports:
        - protocol: UDP
          port: 5353
        - protocol: TCP
          port: 5353
  policyTypes:
    - Egress
```

---

## Allow User Workload Monitoring (Prometheus)

Allow OpenShift User Workload Monitoring to scrape `/metrics` endpoints from your pods (template: [allow-user-workload-monitoring.yaml](../assets/templates/allow-user-workload-monitoring.yaml)):

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-openshift-monitoring
  namespace: <license-plate>-<env>
spec:
  podSelector: {}
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: openshift-user-workload-monitoring
```

> **Conftest note**: If enforcing `assets/policies/network-policies.rego`, scope `podSelector.matchLabels` to your metrics-exposing pods and add explicit `ports` (e.g., `8080` or `8000`) rather than leaving `podSelector: {}`. You can also use **Red Hat ACS** (`https://acs.developer.gov.bc.ca`) to visualize pod-to-pod network flows and generate NetworkPolicy baselines.

---

## Complete Minimal Policy Set

For most two-tier (frontend + API) services, apply ALL of the following:

1. `default-deny-all`
2. `allow-from-openshift-ingress`
3. `allow-frontend-to-api`
4. `allow-api-to-database` (if DB in same namespace)
5. `allow-egress-https`
6. `allow-dns`

For API-only services, omit (2) and (3), and add a direct ingress-from-router rule targeting the API pods.
