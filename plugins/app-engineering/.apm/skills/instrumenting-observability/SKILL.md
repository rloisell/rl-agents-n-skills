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
3. **Audit for PII in Logs:** Run the PII-free logging checklist and `grep` scans across Python, Go, Node.js, and .NET services. See [pii-in-logs-audit.md](references/pii-in-logs-audit.md).
4. **Check Known Pitfalls:** Review confirmed facts and common pitfalls in [observability-knowledge.md](references/observability-knowledge.md).

## Verification

- Confirm stdout emits single-line JSON logs and no interpolated `$"..."` log strings or PII fields appear.
- Verify `GET /api/health`, `GET /api/health/details`, and `GET /metrics` return HTTP 200.
- Run the PII `grep` audit commands and justify or fix every match.

## References

- [Serilog & Health Checks](references/serilog-and-health-checks.md) — packages, `Program.cs` bootstrap, log levels, structured logging, and health probes.
- [Prometheus & OpenTelemetry](references/prometheus-and-opentelemetry.md) — Emerald pod annotations, `/metrics`, OTel tracing, and alert baseline.
- [PII-in-Logs Audit](references/pii-in-logs-audit.md) — PII-free rules, Python/Go/Node.js checklists, and `grep` scan commands.
- [Observability Knowledge](references/observability-knowledge.md) — confirmed facts and common pitfalls.
- [Acceptance Criteria](references/acceptance-criteria.md) — observable pass/fail criteria for logging, health checks, metrics, and PII audits.
