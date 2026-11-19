# OWASP Top 10, .NET/React Hardening, OIDC PKCE & STRA/PIA

## Contents

- [OWASP Top 10 — .NET 10 / React Controls](#owasp-top-10--net-10--react-controls)
- [Input Validation (.NET 10)](#input-validation-net-10)
- [ASP.NET Core Middleware & Authz Blind Spots](#aspnet-core-middleware--authz-blind-spots)
- [SPA Security Blind Spots](#spa-security-blind-spots)
- [Audit Logging (EF Core) & Control Assurance](#audit-logging-ef-core--control-assurance)
- [Container Security Baseline](#container-security-baseline)
- [SAST / DAST Toolchain](#sast--dast-toolchain)
- [Authentication Session Management (OIDC PKCE)](#authentication-session-management-oidc-pkce)
- [Application & Web Development Security Standard Rules](#application--web-development-security-standard-rules)
- [STRA / PIA Process (BC Gov)](#stra--pia-process-bc-gov)
- [Confirmed Facts & Pitfalls](#confirmed-facts--pitfalls)

## OWASP Top 10 — .NET 10 / React Controls

| # | Risk | .NET Control | React Control |
|---|------|-------------|---------------|
| A01 | Broken Access Control | `[Authorize]`, `ForbiddenException` service guard, role claims | Route guards in React Router; API response drives visibility |
| A02 | Cryptographic Failures | `PasswordHasher<T>` only; never store plain text; TLS edge on Route | HTTPS enforced at OpenShift Route; no secrets in JS bundle |
| A03 | Injection | EF Core parameterised queries only; prohibit `FromSqlRaw`; validate with data annotations | No `dangerouslySetInnerHTML`; parameterise API calls |
| A04 | Insecure Design | STRA before first environment; threat model per epic | Workflow captures assumptions; security review step |
| A05 | Security Misconfiguration | Remove default endpoints; CORS named policies only (`ProdCors` explicit origins) | CSP headers via nginx `add_header`; no wildcard origins |
| A06 | Vulnerable Components | Dependabot + `dependency-review.yml` + Trivy FS scan in CI | Same; `package-lock.json` committed |
| A07 | Auth Failures | OIDC PKCE only (no implicit); short-lived access tokens; silent refresh via refresh token rotation | `oidc-client-ts`; `onSigninCallback` normalises URL; backchannel logout endpoint |
| A08 | Data Integrity | Cosign image signing; Helm chart values pinned to SHA tags in prod | `integrity` attribute on CDN assets |
| A09 | Logging/Monitoring | Structured Serilog + no PII in logs; EF Core interceptor for change audit | No sensitive data in browser console |
| A10 | SSRF | Prohibit user-controlled URLs in `HttpClient`; allowlist outbound hosts | API proxies all external calls; no direct browser-to-third-party sensitive calls |

## Input Validation (.NET 10)

### Data Annotations (required on all incoming DTOs)

```csharp
public record CreateItemRequest(
    [Required, StringLength(200)] string Name,
    [Required, Range(1, int.MaxValue)] int ProjectId,
    [EmailAddress] string? ContactEmail
);
```

### Model-state gate in controller

```csharp
[HttpPost]
public async Task<IActionResult> Create([FromBody] CreateItemRequest request)
{
    if (!ModelState.IsValid) return BadRequest(ModelState);
    var result = await _service.CreateAsync(request);
    return CreatedAtAction(nameof(GetById), new { id = result.Id }, result);
}
```

### SQL injection prevention

- **NEVER use `FromSqlRaw`** — use EF Core LINQ operators exclusively.
- If raw SQL is unavoidable: use `FromSqlInterpolated` with `$`-string params.
- Log a warning and add to `AI/securityNextSteps.md` review column whenever raw SQL is introduced.

### Output encoding

- Razor: `@Html.Encode()` / default encoding is sufficient.
- React: JSX auto-escapes; never use `dangerouslySetInnerHTML`.
- JSON responses: `System.Text.Json` default serialiser; no custom formatters.

## ASP.NET Core Middleware & Authz Blind Spots

SAST tools inspect individual files and miss bootstrap ordering, host-wide proxy trust, and replica key state:

| Control | Required Pattern | Blind Spot / Failure Mode |
|---|---|---|
| Middleware ordering | Register `app.UseAuthentication()` and `app.UseAuthorization()` **before** `app.MapControllers()` / `app.UseEndpoints()`. | Auth registered after endpoints leaves routes unauthenticated. |
| Anti-forgery (cookie/session) | Register `builder.Services.AddAntiforgery()`; apply `[AutoValidateAntiforgeryToken]` on controllers (including `[ApiController]`) using cookie/session auth, or `[ValidateAntiForgeryToken]` on MVC state-changing actions. | `[IgnoreAntiforgeryToken]` on state-changing actions without compensating HMAC/token verification. |
| Explicit HTTP verbs | Decorate every action with `[HttpGet]`, `[HttpPost]`, `[HttpPut]`, `[HttpDelete]`, or `[HttpPatch]`. | Missing `[Http*]` (or bare `[Route]`) creates a catch-all accepting `GET` (CSRF/cache poisoning); `[AcceptVerbs("GET", "POST")]` mixes read and write semantics. |
| JWT `TokenValidationParameters` | Set `ValidateIssuer = true`, `ValidateAudience = true`, `ValidateLifetime = true`, and pin `ValidAlgorithms` (e.g., `["RS256"]`). | Accepting `alg: none` or RS256-to-HS256 key confusion; missing `iss`/`aud` validation allows cross-service token replay. |
| Data Protection keys | Persist keys across OpenShift replicas (`PersistKeysToDbContext<AppDbContext>()`, shared RWX PVC, or Redis) and protect keys at rest. | Ephemeral container-local keys invalidate anti-forgery tokens and auth cookies on pod restart or multi-replica routing. |
| `ForwardedHeaders` allowlist | Configure `ForwardedHeadersOptions` with explicit `KnownProxies` / `KnownNetworks` for the OpenShift router/HAProxy. | Calling `KnownNetworks.Clear()` and `KnownProxies.Clear()` trusts arbitrary `X-Forwarded-For` / `X-Forwarded-Proto` headers from clients. |

## SPA Security Blind Spots

- **URL scheme injection**: React/Vue auto-escape text, not URLs. Never pass unsanitized user input to `<a href={userInput}>`, `window.location`, or `window.open()` (`javascript:alert(1)`). Validate against an allowlist (`https:`, `http:`, `mailto:`, or relative `/`).
- **Client bundle secret leakage**: Environment variables prefixed with `VITE_*`, `REACT_APP_*`, or `NEXT_PUBLIC_*` are compiled into the public JS bundle. Never store write/admin API keys, DB strings, JWT secrets, or OAuth client secrets in them.
- **UX-only route guards**: `<PrivateRoute>` or `router.beforeEach()` only hide UI. Verify by deleting `localStorage`/cookies and calling protected API routes directly—the backend must return `401`/`403`.
- **Token & PII persistence**: Do not persist access/refresh tokens, session identifiers, or sensitive PII in `localStorage`, `redux-persist`, or `zustand` `persist` middleware (exposed to XSS). Keep tokens in memory or `HttpOnly; Secure; SameSite=Strict|Lax` cookies.

## Audit Logging (EF Core) & Control Assurance

Every state-changing action on data classified Medium or above must produce a tamper-evident audit record: **who** did **what** to **which record** at **when**.

```csharp
// AUDIT INTERCEPTOR — captures Insert/Update/Delete to audit table
public class AuditInterceptor : SaveChangesInterceptor
{
    public override InterceptionResult<int> SavingChanges(
        DbContextEventData eventData,
        InterceptionResult<int> result)
    {
        var entries = eventData.Context!.ChangeTracker.Entries()
            .Where(e => e.State is EntityState.Added
                             or EntityState.Modified
                             or EntityState.Deleted);
        foreach (var entry in entries)
        {
            var auditEntry = new AuditLog
            {
                TableName   = entry.Metadata.GetTableName()!,
                Action      = entry.State.ToString(),
                RecordId    = entry.Properties
                                   .FirstOrDefault(p => p.Metadata.IsPrimaryKey())
                                   ?.CurrentValue?.ToString(),
                ChangedBy   = _httpContextAccessor.HttpContext?
                                   .User.FindFirstValue(ClaimTypes.NameIdentifier),
                ChangedAt   = DateTime.UtcNow,
                OldValues   = entry.State == EntityState.Modified
                                   ? JsonSerializer.Serialize(
                                       entry.OriginalValues.ToObject())
                                   : null,
                NewValues   = entry.State != EntityState.Deleted
                                   ? JsonSerializer.Serialize(
                                       entry.CurrentValues.ToObject())
                                   : null,
            };
            eventData.Context.Set<AuditLog>().Add(auditEntry);
        }
        return result;
    }
}
```

Register in `Program.cs` (must be in `AddDbContext`, not `AddSingleton`):

```csharp
builder.Services.AddDbContext<AppDbContext>(opt =>
    opt.UseMySql(connectionString, serverVersion)
       .AddInterceptors(new AuditInterceptor(sp.GetRequiredService<IHttpContextAccessor>())));
```

### Authoritative Audit & Diagnostic Switches

- **Service/DB-level attribution**: Emit authoritative audit events at the service or persistence (`SaveChangesInterceptor`) boundary—not controllers alone (which background workers and alternate callers bypass). Propagate actor identity and correlation/trace IDs from the request or job context into the service/DB layer so events remain attributable without logging secrets or unnecessary PII.
- **Time-boxed diagnostic switches**: If temporary sensitive-diagnostic logging is needed when safe stand-ins (presence, length, key thumbprint) cannot resolve an issue, it must be **off by default**, **auto-expiring**, narrowly scoped, written to a restricted short-retention sink, audited (who enabled it and why), **strictly exclude end-user passwords and MFA/OTP codes**, and be followed by credential rotation.

### Real-Wiring Integration Tests & Stateful Invariants

- **No mocked-control or direct-controller tests as security proof**: Directly instantiating a controller or mocking the auth/policy/deletion logic in a unit test does not verify middleware ordering, `[Authorize]` policies, anti-forgery filters, or routing. Require `WebApplicationFactory` / real-host integration tests covering:
  - Unauthenticated (`401`) and unauthorized (`403`) denials, plus cross-user/cross-tenant isolation.
  - Expired, replayed, or malformed tokens and fail-closed dependency behavior.
  - Audit-event emission and secret redaction on both success and failure paths.
- **Stateful invariants**: Verify mutating workflows against four high-risk failure classes:
  - `FSM-BYPASS`: State transitions and terminal states enforced server-side (cannot skip approval/review steps or mutate terminal records).
  - `TOCTOU-RACE`: Concurrent writes, balance/quota updates, and idempotency enforced via atomic conditional updates, row-version/optimistic concurrency, or database constraints—not read-then-write checks.
  - `TENANT-LEAK`: Tenant/org scope enforced on every read, write, query filter, and pooled connection/cache key.
  - `FAIL-OPEN-AUTH`: Missing/null tenant context, policy evaluation errors, or fallback branches must deny by default, never expand scope.

## Container Security Baseline

All Containerfiles **must** satisfy:

| Control | Implementation |
|---------|---------------|
| Non-root user | `RUN addgroup -S appgroup && adduser -S appuser -G appgroup` → `USER appuser` |
| Drop all capabilities | `cap_drop: [ALL]` in compose / Pod `securityContext.capabilities.drop: [ALL]` |
| No privilege escalation | `securityContext.allowPrivilegeEscalation: false` |
| Read-only root FS | `readOnlyRootFilesystem: true`; mount writable `/tmp` as emptyDir |
| Port 8080 only | `EXPOSE 8080`; `ASPNETCORE_URLS=http://+:8080` |
| Pinned base images | Use SHA digest in prod Containerfiles: `FROM mcr.microsoft.com/dotnet/aspnet:10.0@sha256:<digest>` |

OpenShift Pod SecurityContext (apply in Helm `deployment.yaml`):

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1001
  fsGroup: 1001
  seccompProfile:
    type: RuntimeDefault
  capabilities:
    drop: [ALL]
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
```

## SAST / DAST Toolchain

### SAST (Static Analysis)

| Tool | Workflow | Gate |
|------|----------|------|
| CodeQL | `.github/workflows/codeql.yml` | Blocks PR on CRITICAL/HIGH (requires GHAS) |
| Trivy FS | `.github/workflows/trivy-scan.yml` (fs job) | Blocks PR on CRITICAL/HIGH CVE |
| Trivy Image | `.github/workflows/trivy-scan.yml` (image job) | Scans post-push image on develop |
| Dependency Review | `.github/workflows/dependency-review.yml` | Blocks PR if new CRITICAL/HIGH dependency introduced |
| Gitleaks | `.github/workflows/secrets-scan.yml` | Blocks push/PR on detected secrets |

### DAST (Dynamic Analysis)

- Use **`bcgov/owasp-zap-openshift`** (`https://github.com/bcgov/owasp-zap-openshift`) — the public DockerHub OWASP ZAP image requires privileged containers and is incompatible with OpenShift.
- Use **`bcgov/Security-pipeline-templates`** (`https://github.com/bcgov/Security-pipeline-templates/`) to integrate SAST (SonarQube/CodeQL), DAST (OWASP ZAP), and image scanning into CI pipelines.
- Document findings in `AI/securityNextSteps.md` DAST column.

### Container Scanning & SIEM Retention

- **Red Hat ACS (`https://acs.developer.gov.bc.ca`)**: Active registry/running-container scanning, build/deploy/runtime policies (crypto-mining, integrity monitoring), and network policy visualization. Scoped access is auto-granted to PO/Tech Lead in Platform Product Registry; developers request access with namespaces + PO approval.
- **JFrog Xray (`https://artifacts.developer.gov.bc.ca/ui/login/`)**: Passive vulnerability scanning on Artifactory images/artifacts (viewable in the Xray tab).
- **SIEM Log Retention**: Cluster logs ship to Security Operations SIEM — **2 months** for system/container logs, **13 months** for audit logs (request product log access via MISO).

## Authentication Session Management (OIDC PKCE)

### Token lifecycle

1. User redirected to DIAM/Keycloak with PKCE challenge (`code_challenge`, `code_challenge_method=S256`).
2. Auth code returned — exchanged for `access_token` (short-lived) + `refresh_token`.
3. `oidc-client-ts` (`UserManager`) handles silent refresh automatically via `automaticSilentRenew: true`.
4. On token expiry: silent iframe renew or redirect back to IdP (note: use `refresh_token` grant if third-party cookies are blocked, e.g. Safari ITP).
5. Logout: call `/end_session_endpoint` + clear local session; implement backchannel logout endpoint at `/logout/backchannel` in API.

### React `oidc-client-ts` configuration

```js
// src/auth/authConfig.js — OIDC UserManager config for DIAM
export const userManagerConfig = {
  authority:                process.env.VITE_OIDC_AUTHORITY,
  client_id:                process.env.VITE_OIDC_CLIENT_ID,
  redirect_uri:             `${window.location.origin}/callback`,
  post_logout_redirect_uri: `${window.location.origin}/`,
  response_type:            'code', // PKCE
  scope:                    'openid profile email',
  automaticSilentRenew:     true,
  silent_redirect_uri:      `${window.location.origin}/silent-callback.html`,
  filterProtocolClaims:     true,
  loadUserInfo:             true,
};
```

### API backchannel logout endpoint

```csharp
[HttpPost("/logout/backchannel")]
[AllowAnonymous]
public IActionResult BackchannelLogout([FromForm] string logout_token)
{
    // Validate logout_token JWT (issuer, audience, sub/sid claims)
    // Invalidate server-side session or token cache for that sub/sid
    return Ok();
}
```

## Application & Web Development Security Standard Rules

The OCIO Security Standard for Application and Web Development and Deployment (v1.3) mandates:

- **Patch management (§1.1)**: Risk-based prioritisation of security patches; log all patch activity in the System Security Plan.
- **Vulnerabilities management (§1.2)**: Maintain a record of known vulnerabilities impacting the software; application owner tracks remediation.
- **Production segregation (§1.3)**: Production MUST be segregated from dev/test (network + access controls). Test data containing MEDIUM/HIGH classified data MUST be sanitised.
- **Dormant accounts**: Accounts inactive for more than **45 days** MUST be considered dormant and removed or disabled.
- **No credentials in source**: Accounts, user IDs, and passwords MUST NOT be embedded in source code (use Vault/ESO).
- **Code review (§2.1)**: Custom code MUST be reviewed prior to production release by someone other than the original author.
- **Secure coding (§2.2)**: Custom code MUST be tested and remediated for common coding and web application interface vulnerabilities (OWASP).
- **Public-facing Web (§3.1)**: Public-facing web applications MUST be protected by an automated technical solution that detects and prevents web-based attacks (WAF or equivalent).
- **Dedicated Production TLS Certificate (ADMS / MyServiceCentre)**: OpenShift's default wildcard certificate is for dev/test only. Production workloads MUST obtain a dedicated TLS certificate from Access & Directory Management Services (ADMS): generate a `.csr`, submit order via **MyServiceCentre** (`https://ociomysc.service-now.com/sp/`) → Ministry Service Desk → EA approval → DXC fulfillment.
- **Non-PCI-DSS Warning**: BC Gov OpenShift Private Cloud is **NOT PCI-DSS compliant**. Applications accepting payment cards MUST use **PayBC** (e.g., Direct Sale with Bambora applet) or an external PCI-DSS proxy/cloud service to keep OpenShift out of PCI-DSS scope.

## STRA / PIA Process (BC Gov)

### When to trigger a STRA

- New service storing personal information → **STRA required before TEST environment**.
- DataClass: Medium or above → STRA mandatory.
- External API integration involving personal data → STRA required.
- New OAuth client registered in DIAM → STRA review section required.

### STRA checklist

- [ ] Identify data elements stored / processed (DataClass: Low / Medium / High / Critical)
- [ ] Complete STRA template (BC Gov OCIO intranet) with Ministry ISSO and **`cyber@gov.bc.ca`**
- [ ] Capture accepted risks in `AI/securityNextSteps.md` → "STRA Status" row
- [ ] Re-assess if architecture changes materially (new DB, new integration, new data type)

### When to trigger a PIA

- Service collects, uses, or discloses personal information about BC residents.
- New automated decision supported by personal data.
- Third-party data processor involved (cloud provider, vendor).

## Confirmed Facts & Pitfalls

```yaml
confirmed_facts:
  - "DataClass: Medium required on Emerald (Low has no VIP)"
  - "BC Gov STRA templates maintained by OCIO; Ministry ISSO is the reviewer"
  - "DIAM uses Keycloak; standard realm is 'standard' on loginproxy.gov.bc.ca"
  - "CodeQL on bcgov-c org requires GitHub Advanced Security (GHAS) enabled on repo"
  - "Gitleaks detects secrets in git history across all branches on push"
  - "Trivy: exit-code 1 on CRITICAL/HIGH blocks the build step"
  - "AllowPrivilegeEscalation: false enforced by Emerald cluster admission webhook"
common_pitfalls:
  - "FromSqlRaw does NOT parameterise — use FromSqlInterpolated for any raw SQL"
  - "Silent renew iframe fails if third-party cookies are blocked (Safari ITP) — use refresh_token grant instead"
  - "AuditInterceptor must be registered before DbContext is first resolved — register in AddDbContext, not AddSingleton"
```
