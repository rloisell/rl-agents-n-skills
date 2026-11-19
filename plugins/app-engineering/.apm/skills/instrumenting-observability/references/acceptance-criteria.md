# Acceptance Criteria — Instrumenting Observability

Observable pass/fail criteria for verifying Serilog structured logging, health checks, Prometheus/OpenTelemetry instrumentation, and PII-free log audits.

## Pass/Fail Criteria

| Area | Pass Criteria | Fail Criteria |
|---|---|---|
| **Structured JSON Logs** | Serilog is configured with `CompactJsonFormatter` writing single-line JSON to `stdout`; log calls use structured property templates. | Multi-line plain-text logs or interpolated `$"..."` strings inside log calls. |
| **EF Core Log Level** | `Microsoft.EntityFrameworkCore.Database.Command` is set to `Warning` (or higher) in production configuration. | `Information` or `Debug` SQL command logging enabled in production (exposes query parameters). |
| **PII-Free Logging** | Logs contain only opaque `sub`/GUID identifiers; PII `grep` audit across `.NET`, Python, Go, and Node.js services has 0 unresolved matches. | Names, emails, SIN/DL/health numbers, BCeID/IDIR usernames, Bearer tokens, connection strings, or full bodies logged. |
| **Health Endpoints** | `/api/health` (liveness) and `/api/health/details` (readiness with DB check) are mapped and return HTTP `200 OK` when healthy. | Missing health endpoints, readiness check skipping DB connectivity, or non-200 response on healthy stack. |
| **Prometheus & OTel** | `Metrics.CreateCounter` fields are `static readonly` at class level; `UseHttpMetrics()` + `MapMetrics()` serve `/metrics` (HTTP `200`); OTel traces `AspNetCore`, `HttpClient`, and `EntityFrameworkCore`. | Per-request counter allocation, `/metrics` returning 404/500, or missing OTel/Emerald scrape annotations. |
| **Diagnostics & Error Contracts** | APIs/UI emit RFC 9457 `ProblemDetails` (`Cache-Control: no-store`) with W3C `traceId` or `supportId` + UTC timestamp, use the least-disruptive UI error surface, report SPA `error`/`unhandledrejection` without secrets, use safe log stand-ins, and gate any diagnostic escape hatch behind `ExpiresUtc` (see [application-diagnostics-and-errors.md](application-diagnostics-and-errors.md)). | Raw exception messages/stacks in responses, auto-dismissing reference alerts, tokens/form values in SPA error reports, or unexpiring secret-logging switches. |
