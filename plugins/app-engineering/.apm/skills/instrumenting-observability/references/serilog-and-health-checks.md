## Contents

- [Serilog Setup](#serilog-setup)
- [Log Level Standards](#log-level-standards)
- [Structured Logging Pattern](#structured-logging-pattern)
- [Health Checks](#health-checks)

# Serilog & Health Checks

## Serilog Setup

```bash
dotnet add package Serilog.AspNetCore
dotnet add package Serilog.Formatting.Compact
dotnet add package Serilog.Sinks.Console
```

```csharp
// Program.cs — structured JSON to stdout (picked up by OpenShift log aggregation)
Log.Logger = new LoggerConfiguration()
    .ReadFrom.Configuration(builder.Configuration)
    .Enrich.FromLogContext()
    .Enrich.WithMachineName()
    .Enrich.WithEnvironmentName()
    .WriteTo.Console(new CompactJsonFormatter())
    .CreateLogger();

builder.Host.UseSerilog();
```

```json
// appsettings.json
{
  "Serilog": {
    "MinimumLevel": {
      "Default": "Information",
      "Override": {
        "Microsoft": "Warning",
        "Microsoft.EntityFrameworkCore.Database.Command": "Warning",
        "System": "Warning"
      }
    }
  }
}
```

Keep EF Core SQL command logging at `Warning` in production so query parameters containing PII are never exposed.

## Log Level Standards

| Level | Use |
|---|---|
| `Verbose` | Development only — detailed flow tracing |
| `Debug` | Diagnostic context helpful in test environments |
| `Information` | Normal application events (startup, user actions, state transitions) |
| `Warning` | Recoverable abnormal conditions (retry, missing optional config) |
| `Error` | Exceptions / failures that require attention |
| `Fatal` | Unrecoverable startup / crash events |

## Structured Logging Pattern

```csharp
// Use structured properties, not string interpolation
_logger.LogInformation("Created work item {WorkItemId} for project {ProjectId}",
    item.Id, item.ProjectId);

// NOT:
_logger.LogInformation($"Created work item {item.Id}");
```

## Health Checks

```bash
dotnet add package AspNetCore.HealthChecks.MySql
```

```csharp
// Program.cs — /api/health (liveness) and /api/health/details (readiness)
builder.Services.AddHealthChecks()
    .AddMySql(
        connectionString: builder.Configuration.GetConnectionString("DefaultConnection")!,
        name: "database",
        tags: ["ready"]);

// ...
app.MapHealthChecks("/api/health");
app.MapHealthChecks("/api/health/details", new HealthCheckOptions
{
    ResponseWriter = UIResponseWriter.WriteHealthCheckUIResponse,
    Predicate      = _ => true,
});
```

```dockerfile
# Containerfile health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- http://localhost:8080/api/health || exit 1
```
