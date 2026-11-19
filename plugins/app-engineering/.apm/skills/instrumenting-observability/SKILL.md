---
name: instrumenting-observability
description: Instruments BC Government .NET, React, and OpenShift applications with Serilog structured JSON logging, health checks, Prometheus metrics, OpenTelemetry tracing, and PII-free log auditing. Use when configuring logging, adding metrics or tracing, setting up liveness/readiness probes, or auditing logs for PII.
---

# Instrumenting Observability

Standardises structured JSON logging, health checks, Prometheus metrics, OpenTelemetry tracing, and PII-in-logs auditing across BC Gov applications.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- **Structured JSON to stdout:** Use Serilog with `CompactJsonFormatter` so OpenShift log aggregation ingests single-line JSON.
- **EF Core SQL level:** Keep `Microsoft.EntityFrameworkCore.Database.Command` at `Warning` in production so query parameters containing PII are never logged.
- **PII-free logs:** Never log names, emails, SIN/DL/health numbers, BCeID/IDIR usernames, tokens, connection strings, or full request/response bodies. Log opaque `sub`/GUIDs only.
- **Static Prometheus counters:** Declare `Metrics.CreateCounter` as `static readonly` at class level; call `MapMetrics()` with `UseHttpMetrics()` cleanly.
- **Health endpoints:** Expose `/api/health` (liveness) and `/api/health/details` (readiness with DB check).

## Quick start

1. Bootstrap Serilog with `CompactJsonFormatter` in `Program.cs` and set `Microsoft.EntityFrameworkCore.Database.Command` to `Warning`.
2. Map `/api/health`, `/api/health/details`, and Prometheus `/metrics`, then run the PII-free log audit.

## Workflow

1. **Configure Serilog & Health Checks:** Wire `CompactJsonFormatter`, log-level overrides, structured property logging, and `/api/health` + `/api/health/details` in `Program.cs` and `Containerfile`. See [serilog-and-health-checks.md](references/serilog-and-health-checks.md).
2. **Add Prometheus & OpenTelemetry:** Add Emerald pod annotations, `prometheus-net.AspNetCore` `/metrics`, OpenTelemetry tracing (`AspNetCore`, `HttpClient`, `EntityFrameworkCore`), and alert thresholds. See [prometheus-and-opentelemetry.md](references/prometheus-and-opentelemetry.md).
3. **Configure Sysdig, OCP Monitoring, Loki & Uptime.com:** Provision `SysdigTeam` in `<license>-tools`, add `ServiceMonitor`/`PrometheusRule`/`AlertmanagerConfig` with `NetworkPolicy`, follow Loki 14-day logging rules (`X-Forwarded-For`), and set 30-day SLOs. See [sysdig-and-loki-monitoring.md](references/sysdig-and-loki-monitoring.md), [sysdigteam.tpl.yaml](assets/templates/sysdigteam.tpl.yaml), and [servicemonitor.tpl.yaml](assets/templates/servicemonitor.tpl.yaml).
4. **Standardise Errors & Diagnostics:** Configure RFC 9457 `ProblemDetails` (`IExceptionHandler`, `UseStatusCodePages`, `Cache-Control: no-store`), W3C `traceId`/`supportId` contracts, UI error surfaces, SPA error reporting, safe log stand-ins, and `ExpiresUtc`-gated escape hatches. See [application-diagnostics-and-errors.md](references/application-diagnostics-and-errors.md).
5. **Audit for PII in Logs:** Run the PII-free logging checklist and `grep` scans across Python, Go, Node.js, and .NET services. See [pii-in-logs-audit.md](references/pii-in-logs-audit.md).
6. **Check Known Pitfalls:** Review confirmed facts and common pitfalls in [observability-knowledge.md](references/observability-knowledge.md).

## Verification

- Confirm stdout emits single-line JSON logs and no interpolated `$"..."` log strings or PII fields appear.
- Verify `GET /api/health`, `GET /api/health/details`, and `GET /metrics` return HTTP 200.
- Run the PII `grep` audit commands and justify or fix every match.

## References

- [Serilog & Health Checks](references/serilog-and-health-checks.md) — packages, `Program.cs` bootstrap, log levels, structured logging, and health probes.
- [Prometheus & OpenTelemetry](references/prometheus-and-opentelemetry.md) — Emerald pod annotations, `/metrics`, OTel tracing, and alert baseline.
- [Sysdig, OCP Monitoring, Loki & Uptime.com](references/sysdig-and-loki-monitoring.md) — `SysdigTeam` CR, `ServiceMonitor`/`AlertmanagerConfig`, Loki 14-day logging, and 30-day SLOs.
- [`SysdigTeam` Template](assets/templates/sysdigteam.tpl.yaml) — `ops.gov.bc.ca/v1alpha1` team manifest for `<license>-tools`.
- [`ServiceMonitor` Template](assets/templates/servicemonitor.tpl.yaml) — `monitoring.coreos.com/v1` scrape config for OCP User-Defined Monitoring.
- [Application Diagnostics & Errors](references/application-diagnostics-and-errors.md) — RFC 9457 `ProblemDetails`, `traceId`/`supportId` contract, UI error surface matrix, SPA reporting, safe stand-ins, and `ExpiresUtc` escape hatches.
- [PII-in-Logs Audit](references/pii-in-logs-audit.md) — PII-free rules, Python/Go/Node.js checklists, and `grep` scan commands.
- [Observability Knowledge](references/observability-knowledge.md) — confirmed facts and common pitfalls.
- [Acceptance Criteria](references/acceptance-criteria.md) — observable pass/fail criteria for logging, health checks, metrics, and PII audits.
