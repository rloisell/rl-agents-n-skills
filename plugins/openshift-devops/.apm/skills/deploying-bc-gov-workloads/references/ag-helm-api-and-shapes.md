# `ag-helm` Dict API and Fragment Shapes

Authoritative `$p` dictionary contract and `define` fragment output shapes for `ag-helm-templates` (`ag-template.*`).

## Contents

- [Calling Convention](#calling-convention)
- [Workload Templates](#workload-templates)
- [Networking & Routing Templates](#networking--routing-templates)
- [Scaling, Availability & Storage Templates](#scaling-availability--storage-templates)
- [Fragment Hook Output Shapes](#fragment-hook-output-shapes)
- [Router Ingress Selector Pattern](#router-ingress-selector-pattern)

---

## Calling Convention

Pass a dictionary `$p` to `include "ag-template.<type>" $p`:

```tpl
{{- $p := dict "Values" .Values -}}
{{- $_ := set $p "ApplicationGroup" .Values.project -}}
{{- $_ := set $p "Name" "web-api" -}}
{{- $_ := set $p "Namespace" $.Release.Namespace -}}
{{- $_ := set $p "Registry" .Values.registry -}}
{{- $_ := set $p "ModuleValues" .Values.webApi -}}
{{ include "ag-template.deployment" $p }}
```

- **Required keys** must be set or templating fails / emits invalid YAML.
- **Fragment hooks** (`Ports`, `Env`, `Probes`, `ServicePorts`, etc.) are string names of `define` blocks.
- Workloads default `dataClass` to `low` if omitted; explicitly set `dataClass: medium` (or `high`) in `values.yaml` for Emerald compliance.

---

## Workload Templates

| Template | Required `$p` Keys | Key Optional `$p` Keys | Fragment Hooks (`define`) |
|---|---|---|---|
| `ag-template.deployment` | `ApplicationGroup`, `Name`, `Registry`, `ModuleValues` (`image.digest` or `image.tag`) | `Values`, `Namespace`, `Lang`, `ServiceAccountName` | `Ports`, `Env`, `Probes`, `Volumes`, `VolumeMounts`, `InitContainers`, `Lifecycle`, `SecurityContext`, `SidecarContainers`, `Resources`, `AnnotationData`, `LabelData`, `PullSecret`, `Tolerations` |
| `ag-template.statefulset` | `ApplicationGroup`, `Name`, `Registry`, `ServiceName`, `ModuleValues` (`image.tag`) | `Values`, `Namespace` | `Ports`, `Env`, `Probes`, `Volumes`, `VolumeMounts`, `Resources`, `VolumeClaims` |
| `ag-template.job` | `ApplicationGroup`, `Name`, `Registry` | `Values`, `Namespace`, `ModuleValues`, `BackoffLimit` (6), `TTLSecondsAfterFinished` (86400), `RestartPolicy` (`Never`), `Command`, `Args`, `ServiceAccountName`, `Annotations` | `Env`, `VolumeMounts`, `Volumes`, `Resources`, `SecurityContext`, `InitContainers`, `SidecarContainers`, `AnnotationData`, `LabelData`, `PullSecret`, `Tolerations`, `PodAnnotationData` |

---

## Networking & Routing Templates

| Template | Required `$p` Keys | Key Optional `$p` Keys | Notes |
|---|---|---|---|
| `ag-template.service` | `ApplicationGroup`, `Name`, `ServicePorts` (`define`) | `Type` (`ClusterIP`), `Headless`, `IPFamilies` (`define`) | Never use `NodePort` or `LoadBalancer` |
| `ag-template.route.openshift` | `Values`, `ApplicationGroup`, `Name`, `Namespace` | `ModuleValues`, `LabelData`, `Labels` | Reads `ModuleValues.route` (fallback `Values.route`); renders only when `route.enabled: true`; requires `aviinfrasetting.ako.vmware.com/name` |
| `ag-template.ingress` | `Name`, `Capabilities`, `Hosts`, `ServiceName`, `ServicePort` | `Namespace`, `ClassName`, `Tls`, `Annotations`, `LabelData`, `Labels`, `Values` | Requires `aviinfrasetting.ako.vmware.com/name` annotation |
| `ag-template.networkpolicy` | `ApplicationGroup`, `Name` | `Namespace`, `PodSelector`, `PolicyTypes`, `AllowIngressFrom`, `AllowEgressTo`, `Ingress`, `Egress`, `IngressTemplate`, `EgressTemplate`, `Annotations`, `Labels` | Prefer `AllowIngressFrom` / `AllowEgressTo` intent maps |

---

## Scaling, Availability & Storage Templates

| Template | Required `$p` Keys | Key Optional `$p` Keys | Notes |
|---|---|---|---|
| `ag-template.hpa` | `ApplicationGroup`, `Name`, `MinReplicas`, `MaxReplicas` | `TargetAverageUtilizationCpu`, `TargetAverageUtilizationMemory` | Renders `autoscaling/v2` HPA |
| `ag-template.pdb` | `ApplicationGroup`, `Name` | `Values`, `Namespace`, `ModuleValues`, `Selector` (`define`), `AnnotationData`, `LabelData` | Reads `ModuleValues.pdb`; renders nothing if `pdb.disabled: true` |
| `ag-template.pvc` | `ApplicationGroup`, `Name`, `Storage` | `StorageClassName`, `AccessModes` (`[ReadWriteOnce]`), `VolumeMode`, `Selector` | Example `Storage`: `1Gi` |
| `ag-template.serviceaccount` | `ApplicationGroup`, `Name` | `AnnotationData` (`define`), `LabelData` (`define`), `Annotations` | Emits `v1` ServiceAccount |
| `ag-template.priorityclass` | `Name`, `Value` | `GlobalDefault`, `Description`, `PreemptionPolicy`, `LabelData`, `Labels`, `Values` | Emits `scheduling.k8s.io/v1` PriorityClass |

---

## Fragment Hook Output Shapes

Fragment `define` blocks must emit valid YAML using spaces (never tabs) and omit the parent key when the template already supplies it:

```tpl
{{- define "webapi.ports" -}}
- name: http
  containerPort: 8080
  protocol: TCP
{{- end -}}

{{- define "webapi.servicePorts" -}}
- name: http
  port: 8080
  targetPort: http
  protocol: TCP
{{- end -}}

{{- define "webapi.probes" -}}
livenessProbe:
  httpGet:
    path: /health/live
    port: http
readinessProbe:
  httpGet:
    path: /health/ready
    port: http
{{- end -}}
```

For `IngressTemplate` / `EgressTemplate` on `ag-template.networkpolicy`, emit list items starting with `-` (do **not** emit `ingress:` or `egress:` keys).

---

## Router Ingress Selector Pattern

When exposing a service via an OpenShift `Route`, restrict router ingress to the default ingress controller pods in `openshift-ingress` (verify labels on cluster with `oc -n openshift-ingress get pods --show-labels`):

```tpl
{{- $_ := set $np "AllowIngressFrom" (dict
  "ports" (list 8080)
  "namespaces" (list (dict
    "name" "openshift-ingress"
    "podSelector" (dict "matchLabels" (dict
      "ingresscontroller.operator.openshift.io/deployment-ingresscontroller" "default"
    ))
  ))
) -}}
```
