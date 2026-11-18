# Prometheus & OpenTelemetry

## Metrics — Prometheus

Emerald OpenShift uses a Prometheus pull model. Annotate pods in Helm `values.yaml` so Prometheus discovers the metrics endpoint:

```yaml
podAnnotations:
  prometheus.io/scrape: "true"
  prometheus.io/path:   "/metrics"
  prometheus.io/port:   "8080"
```

```bash
dotnet add package prometheus-net.AspNetCore
```

```csharp
// METRICS — expose /metrics for Prometheus scrape
app.UseHttpMetrics();  // request duration, count, in-flight
app.MapMetrics();      // GET /metrics
```

Declare custom metrics as `static readonly` at class level:

```csharp
// create once at class level (static) — Prometheus counters are global
private static readonly Counter _itemsCreated =
    Metrics.CreateCounter("app_items_created_total", "Number of work items created.",
        labelNames: ["project_id"]);

// in service method — increment counter when an item is created
_itemsCreated.WithLabels(projectId.ToString()).Inc();
```

## Tracing — OpenTelemetry

```bash
dotnet add package OpenTelemetry.Extensions.Hosting
dotnet add package OpenTelemetry.Instrumentation.AspNetCore
dotnet add package OpenTelemetry.Instrumentation.Http
dotnet add package OpenTelemetry.Exporter.Console   # dev only
```

```csharp
// TRACING — OpenTelemetry with OTLP export (or console in dev)
builder.Services.AddOpenTelemetry()
    .WithTracing(tracing =>
    {
        tracing
            .SetResourceBuilder(ResourceBuilder.CreateDefault()
                .AddService(serviceName: "my-app-api"))
            .AddAspNetCoreInstrumentation()
            .AddHttpClientInstrumentation()
            .AddEntityFrameworkCoreInstrumentation();

        if (builder.Environment.IsDevelopment())
            tracing.AddConsoleExporter();
        else
            tracing.AddOtlpExporter(opt =>
                opt.Endpoint = new Uri(builder.Configuration["Otlp:Endpoint"]!));
    });
```

## Alert Baseline (document in `securityNextSteps.md`)

| Signal | Threshold | Action |
|---|---|---|
| HTTP 5xx rate | > 5% of requests over 5 min | Alert on-call |
| DB health check failing | > 2 consecutive failures | Alert on-call |
| Pod restart count | > 3 in 10 min | Alert on-call |
| High memory / CPU | > 90% of request limit for 5 min | Alert + scale |
| Auth failures (401/403) | Spike > 10x baseline | Security alert |
