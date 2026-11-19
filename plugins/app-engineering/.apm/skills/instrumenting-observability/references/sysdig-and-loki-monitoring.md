# Sysdig Monitor, OCP User-Defined Monitoring, Loki & Uptime.com

Platform-level monitoring, alerting, centralized logging, and synthetic SLI/SLO practices for BC Gov Private Cloud OpenShift applications.

## Contents

- [Sysdig Monitor](#sysdig-monitor)
- [OCP User-Defined Monitoring](#ocp-user-defined-monitoring)
- [Loki Centralized Logging](#loki-centralized-logging)
- [Uptime.com & SLI/SLO Error Budgets](#uptimecom--slislo-error-budgets)

## Sysdig Monitor

### OIDC Login & User Provisioning

1. Every team member must sign in once before being added to a team:
   - Direct OIDC URL: `https://app.sysdigcloud.com/api/oauth/openid/bcdevops` (IDIR or GitHub account).
   - Alternatively, go to `https://app.sysdigcloud.com`, select **OpenID**, enter company `BCDevOps`, and select the **US East** region.
2. Check your exact email in **Sysdig User Profile** (`https://app.sysdigcloud.com/#/settings/user`); Sysdig identifies users by email address.

### `SysdigTeam` Custom Resource

Create **exactly one** `SysdigTeam` (`ops.gov.bc.ca/v1alpha1`) per project set, **only** in `<license>-tools` (and on **Gold only** if your project set spans Gold and GoldDR — the operator provisions dashboards across both clusters).

- **Do not edit team roles in the Sysdig UI:** Operator reconciliation overwrites UI changes. Manage all role assignments in the `<license>-tools` CR.
- **Remove duplicates:** Delete any accidental `SysdigTeam` CRs in `dev`, `test`, or `prod` namespaces (`oc -n <namespace> delete sysdig-team <name>`).
- **Available roles:**
  - `ROLE_TEAM_EDIT` (Advanced User): Read/write; create, edit, and delete dashboards and alerts (admins/leads).
  - `ROLE_TEAM_STANDARD` (Standard User): Same as Advanced without **Explore** page access (developers).
  - `ROLE_TEAM_READ` (View-only): Read-only access within team scope (product owners/business).

See [sysdigteam.tpl.yaml](../assets/templates/sysdigteam.tpl.yaml). Verify reconciliation with:

```bash
oc -n <license>-tools describe sysdig-team <license>-sysdigteam
# Expect: Message: Awaiting next reconciliation | Reason: Successful
```

### Dashboards, PromQL & API Backup

- **Default templates:** Start from Sysdig's Dashboard Library (`Pod Rightsizing & Workload Capacity Optimization`, `Template - Resource Allocation Dashboard`, `Pod/Workload Status & Performance`) or the Platform Services templates in `https://github.com/bcgov/platform-services-sysdig/tree/main/dashboard-template`.
- **Dashboard backup via Sysdig API:** Dashboards are tied to user/team ownership — if a user or team is deleted from Sysdig or `SysdigTeam`, all associated dashboards are permanently deleted. Export and version-control custom dashboards as code manifests using the [Sysdig REST API](https://docs.sysdig.com/en/docs/developer-tools/sysdig-rest-api-conventions/).
- **Pod `/metrics` scraping (Promscrape):** Add `prometheus.io/scrape: "true"`, `prometheus.io/port`, and `prometheus.io/path` (`"/metrics"`) to `deployment.spec.template.metadata.annotations` so Sysdig's Promscrape agent imports app metrics (relabelled as native Sysdig metrics).
- **Resource quota & PVC PromQL examples (for Explore / quota increase evidence / alerts):**

```promql
# Namespace CPU & Memory limit utilization %
sum by(kube_cluster_name, kube_namespace_name, kube_workload_name)(
  kube_resourcequota_sysdig_limits_cpu_used{cluster=~$cluster,namespace=~$namespace}
  / kube_resourcequota_sysdig_limits_cpu_hard{cluster=~$cluster,namespace=~$namespace} * 100
)
sum by(kube_cluster_name, kube_namespace_name, kube_workload_name)(
  kube_resourcequota_sysdig_limits_memory_used{cluster=~$cluster,namespace=~$namespace}
  / kube_resourcequota_sysdig_limits_memory_hard{cluster=~$cluster,namespace=~$namespace} * 100
)

# Total namespace storage quota usage %
kube_resourcequota_sysdig_requests_storage_used{kube_cluster_name=~$cluster,namespace=~$namespace}
  / kube_resourcequota_sysdig_requests_storage_hard{kube_cluster_name=~$cluster,namespace=~$namespace} * 100

# Top 25 PVCs by disk usage ratio
topk(25, kubelet_volume_stats_used_bytes{kube_cluster_name=~$cluster,namespace=~$namespace}
  / kubelet_volume_stats_capacity_bytes{kube_cluster_name=~$cluster,namespace=~$namespace})

# Alert rule: any PVC >= 80% full
((avg(kubelet_volume_stats_used_bytes / kubelet_volume_stats_capacity_bytes) by (persistentvolumeclaim)) * 100) >= 80
```

## OCP User-Defined Monitoring

OpenShift User-Defined Monitoring stores namespace metrics in Prometheus for **15 days**.

1. **Expose `/metrics` & create `ServiceMonitor`:** Use [servicemonitor.tpl.yaml](../assets/templates/servicemonitor.tpl.yaml) (`monitoring.coreos.com/v1`) matching your app `Service` port `metrics`.
2. **Mandatory `NetworkPolicy`:** Allow Prometheus scraping from `openshift-user-workload-monitoring`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-openshift-monitoring
  namespace: <license>-dev
spec:
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: openshift-user-workload-monitoring
  podSelector: {}
  policyTypes:
    - Ingress
```

3. **Custom alerts (`PrometheusRule`):** Define PromQL alert rules (`monitoring.coreos.com/v1`) in your target namespace with `for`, `expr`, `labels.severity`, and `annotations.message`.
4. **Platform AlertManager defaults & cadences:**
   - **1-hour persistence trigger:** Platform-controlled alerts fire only if the condition persists for **1 hour** (reducing noise during rollouts).
   - **Non-prod business-hours window:** Alerts in `tools`, `dev`, and `test` are sent only Monday–Friday **16:00–00:00 UTC** (8am–4pm PST / 9am–5pm PDT).
   - **Contacts:** Technical Leads receive all alerts; `critical` alerts in `-prod` are also forwarded to the Product Owner.
   - **Resend cadences for unresolved alerts:**

| Severity | `tools` | `dev` | `test` | `prod` |
|---|---|---|---|---|
| `critical` | Every 48h | Every 24h | Every 12h | Every 1h |
| `warning` / `info` | Every 5d | Every 4d | Every 2d | Every 1d |

5. **Alert routing (`AlertmanagerConfig`):** Each namespace includes a non-editable `AlertmanagerConfig` (`platform-services-controlled-alert-routing`) and `PrometheusRule` (`platform-services-controlled-alert-rules`). Add a separate `AlertmanagerConfig` (`monitoring.coreos.com/v1beta1`) for additional email receivers, keeping `groupBy: [severity, namespace]` and the cluster email templates (`email_subject`, `display_name`, `email_html`) intact:

```yaml
apiVersion: monitoring.coreos.com/v1beta1
kind: AlertmanagerConfig
metadata:
  name: custom-alert-routing
  namespace: <license>-dev
spec:
  receivers:
    - name: CustomContacts
      emailConfigs:
        - from: Cluster AlertManager <PlatformServicesTeam@gov.bc.ca>
          headers:
            - key: Subject
              value: '{{ template "email_subject" . }}'
          html: '{{ define "display_name" }}<app-display-name>{{ end }}{{ template "email_html" . }}'
          sendResolved: true
          smarthost: apps.smtp.gov.bc.ca:25
          tlsConfig:
            ca: {}
            cert: {}
            insecureSkipVerify: true
          to: team-alerts@example.com
  route:
    activeTimeIntervals:
      - business-hours
    groupBy:
      - severity
      - namespace
    groupInterval: 5m
    groupWait: 30s
    receiver: CustomContacts
    repeatInterval: 1h
  timeIntervals:
    - name: business-hours
      timeIntervals:
        - times: # UTC; 08:00-16:00 PST / 09:00-17:00 PDT
            - startTime: "16:00"
              endTime: "23:59"
          weekdays:
            - monday:friday
```

## Loki Centralized Logging

OpenShift collects container `stdout`/`stderr` into **Loki**, accessible in the OCP Web Console under **Observe -> Logs**.

- **14-day retention:** Loki retains console logs for **14 days**. Container restarts wipe ephemeral local container logs, so always log to `stdout`/`stderr`.
- **Shared resource — avoid `DEBUG` in prod:** Loki storage is shared across the platform. Keep production log levels at `Information`/`Warning` (never `DEBUG` continuously).
- **Long-term archival:** For audit logs or retention > 14 days, archive logs to **OCIO Object Storage (S3)** (or deploy a team-scoped log stack).
- **Plaintext transport & `view`-role access:** Logs are transmitted in **plaintext** to Loki and SIEM systems, and **anyone with `view` role in the namespace** can read them. Never log secrets, keys, tokens, or PII.
- **Log `X-Forwarded-For`:** Web requests entering pods show the OpenShift Router pod as the source IP. Extract and log the `X-Forwarded-For` HTTP header to record the true client IP for security auditing.

## Uptime.com & SLI/SLO Error Budgets

- **Uptime.com:** Configure synthetic availability checks, latency/performance checks, **SSL certificate & domain health** monitoring, and multi-step **transactional tests** (e.g., login/dashboard load) from external locations.
- **30-day rolling window:** Measure SLIs, SLOs, and SLAs over a continuous **30-day** rolling window for consistency and fair assessment.
- **Error budget calculation:**

```text
Error Budget = 1 - SLO
Example (99.5% daily SLO): 0.5% of 1,440 min = 7 min 12 sec/day allowed downtime
Example (95.0% 30-day SLO): 5.0% of 43,200 min = 2,160 min/month allowed downtime
```

- **Golden signals:** Track **Latency**, **Traffic**, **Errors** (e.g., 99.95% availability target), and **Saturation** (CPU/memory utilization; target >= 80% utilization without breaching SLOs).
