## Contents

- [RFC 9457 ProblemDetails & Error Catalog (.NET 10+)](#rfc-9457-problemdetails--error-catalog-net-10)
- [Support Reference Contract](#support-reference-contract)
- [Least-Disruptive UI Error Surface Matrix](#least-disruptive-ui-error-surface-matrix)
- [SPA Client Error Reporting](#spa-client-error-reporting)
- [Safe Log Stand-Ins & Time-Boxed Escape Hatch](#safe-log-stand-ins--time-boxed-escape-hatch)

# Application Diagnostics & Error Contracts

Standardises RFC 9457 Problem Details, correlatable support references, least-disruptive UI error surfaces, safe SPA error reporting, and secret-free diagnostic stand-ins.

## RFC 9457 ProblemDetails & Error Catalog (.NET 10+)

Use built-in .NET 10 diagnostics primitives before adding custom middleware:

- **Core wiring:** Register `AddProblemDetails()` + `UseExceptionHandler()` + `UseStatusCodePages()` (and `AddValidation()` for minimal APIs) so both unhandled exceptions and non-exception error statuses emit RFC 9457 `ProblemDetails`.
- **`IExceptionHandler` & single-log rule:** Implement one `IExceptionHandler` mapping known domain/application exceptions to a central, localizable error catalog (`{ status, code, userMessageKey, retryable }`). When `IExceptionHandler` returns `true` (via `IProblemDetailsService.TryWriteAsync`), .NET 10 suppresses the default middleware error log — log the exception once with `ILogger.LogError(exception, ...)` and business context inside the handler. Unknown exceptions map to a generic `500` catalog entry; never expose `exception.Message`, exception type names, stack traces, SQL, or internal hostnames.
- **Caching & retry headers:** Exception middleware sets `Cache-Control: no-cache,no-store`; explicitly set `Cache-Control: no-store` on non-exception error responses (`400`, `403`, `404`, `429`, `503`) as well. Emit `Retry-After` on `429` and `503` when the wait is known.

## Support Reference Contract

Show one correlatable **support reference** on user-visible errors alongside a plain-language message, UTC `timestamp`, copyable reference control, next step, and application-owned contact channel:

- **Default to W3C `traceId`:** Use the 32-hex-character `Activity.Current.TraceId` (not the full `Activity.Id`) so UI/API references match log scopes. Fall back to a separately labeled `requestId` (`HttpContext.TraceIdentifier`) or a random `supportId` when no activity exists or when public callers can supply `traceparent`. Never label a host request ID as `traceId`.
- **Untrusted caller headers:** Treat caller-supplied correlation headers as untrusted — enforce length/character validation and log them in a separate `correlationId` field.
- **No server response:** If a browser request fails before reaching the server, show a client-generated attempt reference (or ask for UTC time and task) rather than fabricating a server reference.

```csharp
builder.Services.AddProblemDetails(o => o.CustomizeProblemDetails = ctx =>
{
    var naming = ctx.HttpContext.RequestServices
        .GetRequiredService<IOptions<Microsoft.AspNetCore.Http.Json.JsonOptions>>()
        .Value.SerializerOptions.PropertyNamingPolicy;
    var traceIdKey = naming?.ConvertName("traceId") ?? "traceId";
    if (Activity.Current is { } activity)
        ctx.ProblemDetails.Extensions[traceIdKey] = activity.TraceId.ToString();
    else
    {
        ctx.ProblemDetails.Extensions.Remove(traceIdKey);
        ctx.ProblemDetails.Extensions[naming?.ConvertName("requestId") ?? "requestId"] =
            ctx.HttpContext.TraceIdentifier;
    }
    ctx.ProblemDetails.Extensions["timestamp"] = DateTimeOffset.UtcNow;
});
```

## Least-Disruptive UI Error Surface Matrix

Choose the least disruptive surface that lets the user act; redirect to a full error page only when the user cannot continue:

| Situation | Surface | Requirements |
|---|---|---|
| Fixable input / validation (`400`/`422`) | Field-level errors + error summary | Preserve user input; usually no support reference needed. |
| Action failed, page still usable (`5xx`/conflict) | Persistent in-page alert (no auto-dismiss) | Preserve input, offer safe Retry, show copyable support reference + UTC time. |
| Partial widget/region failure | Inline region alert / `ErrorBoundary` | Keep the rest of the page interactive; reset boundary on retry. |
| Unauthenticated / expired session (`401`) | Redirect to sign-in, then return | Validate return URL as local-only; preserve or warn about unsaved work. |
| Forbidden (`403`) | Full access-denied page (in place) | Avoid redirect loops; explain how to request access and who to contact. |
| Not found (`404`/`410`) | Full not-found page | Provide navigation back (home, search, list). |
| Fatal route load / service down (`500`/`503`) | Full error page (`Cache-Control: no-store`) | Show catalog message, support reference, UTC time, next step, and contact. |

## SPA Client Error Reporting

- Attach a framework error boundary plus global `window` `error` and `unhandledrejection` handlers so client-only crashes are observable.
- Post a minimal structured report to an authenticated or strictly rate-limited server endpoint containing only: client attempt reference, route template, release version, browser metadata, error name, and stack.
- **Never** include form values, Bearer/session tokens, cookies, or `localStorage`/`sessionStorage` contents. The server logs the report under its own reference and treats all client fields as untrusted.

## Safe Log Stand-Ins & Time-Boxed Escape Hatch

Never log raw credentials, tokens, connection strings, or credential-bearing URLs. Use safe stand-ins first:

| Diagnostic Need | Safe Log Stand-In |
|---|---|
| Credential presence/type | Presence boolean, length, scheme (`Bearer`), config key name and provider source |
| Expected credential match | Non-secret `kid`, `X509Certificate2.Thumbprint`/subject/expiry, or keyed HMAC-SHA-256 fingerprint (never unkeyed hash or secret suffix) |
| Rejected JWT | Non-secret claims (`iss`, `aud`, `exp`, `nbf`, `iat`, scopes/roles, `azp`/`client_id`) and validation failure reason |
| Database / endpoint | Allowlisted `DataSource` and `InitialCatalog` extracted from `SqlConnectionStringBuilder` (never log the builder or connection string) |
| Outbound URL | Scheme, host, route template/path, and query **keys** with values redacted |

**Time-boxed diagnostic escape hatch (when stand-ins are insufficient):**

- Gate behind a configuration switch that is **off by default** and carries an explicit `ExpiresUtc` checked via `IOptionsMonitor<T>` on each application-controlled write (ignored automatically after expiry).
- Scope narrowly (one dependency, endpoint, or support reference) and write to a **dedicated `ILogger` category** routed only to a restricted-access, short-retention sink.
- Avoid process-wide switches like `DOTNET_SYSTEM_NET_HTTP_DISABLEURIREDACTION` or broad EF Core `EnableSensitiveDataLogging()` in production.
- Record who enabled it, incident/support reference, scope, and expiry; exclude end-user passwords and MFA/OTP codes; purge restricted logs and **rotate any logged credentials** once resolved.
