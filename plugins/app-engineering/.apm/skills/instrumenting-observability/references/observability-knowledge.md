# Observability Knowledge

```yaml
confirmed_facts:
  - "CompactJsonFormatter writes single-line JSON to stdout — required for OpenShift log aggregation"
  - "Prometheus on Emerald uses pod annotations to discover /metrics endpoints"
  - "EF Core SQL logging at Information level may expose query parameters — use Warning"
  - "OpenTelemetry AddEntityFrameworkCoreInstrumentation requires EFCore instrumentation package"
  - "Health check at /api/health is used by OpenShift liveness probe; /api/health/details for readiness"
  - "2026-06-05: [multi-app-engagement] Python services using LOG_SQLALCHEMY=ERROR is correct but structured log format must be confirmed — validate JSON output in all Python/Go services"
common_pitfalls:
  - "Never log PII — user emails, names, or identifying numbers in structured properties"
  - "Metrics.CreateCounter must be static — creating per-request instances causes memory leaks"
  - "prometheus-net endpoint conflicts with ASP.NET Core minimal API route if MapMetrics() called after MapControllers()"
```
