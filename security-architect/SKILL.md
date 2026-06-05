---
name: security-architect
description: Security architecture and analysis for BC Gov .NET / React / OpenShift projects — OWASP Top 10 mitigations, SAST/DAST toolchain, secrets management with Vault, container security baseline, input validation, audit logging, OIDC session management, STRA/PIA process, and security hardening roadmap. Use when designing security controls, reviewing code for vulnerabilities, setting up scanning workflows, or completing the AI/securityNextSteps.md hardening plan.
tools: Read, Grep, Glob
user-invocable: false
metadata:
  author: Ryan Loiselle
  version: "1.0"
compatibility: .NET 10 / ASP.NET Core. React / Vite. Emerald OpenShift 4.x. BC Gov STRA/PIA process. References vault-secrets shared skill.
---

# Security Architect Agent

Drives security design, threat modelling, and hardening activities for BC Government projects.

**Shared skills referenced by this agent:**
- Vault path conventions, ESO CRD, CI secrets → [`../vault-secrets/SKILL.md`](../vault-secrets/SKILL.md)
- BC Gov platform constraints → [`../bc-gov-emerald/SKILL.md`](../bc-gov-emerald/SKILL.md)

---

## OWASP Top 10 — .NET 10 / React Controls

| # | Risk | .NET Control | React Control |
|---|------|-------------|---------------|
| A01 | Broken Access Control | `[Authorize]`, `ForbiddenException` service guard, role claims | Route guards in React Router; API response drives visibility |
| A02 | Cryptographic Failures | `PasswordHasher<T>` only; never store plain text; TLS edge on Route | HTTPS enforced at OpenShift Route; no secrets in JS bundle |
| A03 | Injection | EF Core parameterised queries only; prohibit `FromSqlRaw`; validate with data annotations | No `dangerouslySetInnerHTML`; parameterise API calls |
| A04 | Insecure Design | STRA before first environment; threat model per epic | Spec-kitty workflow captures assumptions; security review step |
| A05 | Security Misconfiguration | Remove default endpoints; CORS named policies only (`ProdCors` explicit origins) | CSP headers via nginx `add_header`; no wildcard origins |
| A06 | Vulnerable Components | Dependabot + `dependency-review.yml` + Trivy FS scan in CI | Same; `package-lock.json` committed |
| A07 | Auth Failures | OIDC PKCE only (no implicit); short-lived access tokens; silent refresh via refresh token rotation | `oidc-client-ts`; `onSigninCallback` normalises URL; backchannel logout endpoint |
| A08 | Data Integrity | Cosign image signing (future); Helm chart values pinned to SHA tags in prod | `integrity` attribute on CDN assets |
| A09 | Logging/Monitoring | Structured Serilog + no PII in logs; EF Core interceptor for change audit | No sensitive data in browser console |
| A10 | SSRF | Prohibit user-controlled URLs in `HttpClient`; allowlist outbound hosts | API proxies all external calls; no direct browser-to-third-party sensitive calls |

---

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
// POST /api/items — create a new work item
[HttpPost]
public async Task<IActionResult> Create([FromBody] CreateItemRequest request)
{
    if (!ModelState.IsValid) return BadRequest(ModelState);
    var result = await _service.CreateAsync(request);
    return CreatedAtAction(nameof(GetById), new { id = result.Id }, result);
}
```

### SQL injection prevention
- **NEVER use `FromSqlRaw`** — use EF Core LINQ operators exclusively
- If raw SQL is unavoidable: use `FromSqlInterpolated` with `$`-string params
- Log a warning and add to `securityNextSteps.md` review column whenever raw SQL is introduced

### Output encoding
- Razor: `@Html.Encode()` / default encoding is sufficient
- React: JSX auto-escapes; never use `dangerouslySetInnerHTML`
- JSON responses: `System.Text.Json` default serialiser; no custom formatters

---

## Audit Logging

### Purpose
Every state-changing action on data classified Medium or above must produce a tamper-evident audit record: **who** did **what** to **which record** at **when**.

### EF Core SaveChanges interceptor
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

Register in `Program.cs`:
```csharp
builder.Services.AddDbContext<AppDbContext>(opt =>
    opt.UseMySql(connectionString, serverVersion)
       .AddInterceptors(new AuditInterceptor(sp.GetRequiredService<IHttpContextAccessor>())));
```

---

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

---

## SAST / DAST Toolchain

### SAST (Static Analysis)
| Tool | Workflow | Gate |
|------|----------|------|
| CodeQL | `.github/workflows/codeql.yml` | Blocks PR on CRITICAL/HIGH (requires GHAS) |
| Trivy FS | `.github/workflows/trivy-scan.yml` (fs job) | Blocks PR on CRITICAL/HIGH CVE |
| Trivy Image | `.github/workflows/trivy-scan.yml` (image job) | Scans post-push image on develop |
| Dependency Review | `.github/workflows/dependency-review.yml` | Blocks PR if new CRITICAL/HIGH dependency introduced |
| Gitleaks | `.github/workflows/secrets-scan.yml` | Blocks push/PR on detected secrets |

### DAST (Dynamic Analysis — future roadmap)
- OWASP ZAP baseline scan against dev environment on schedule
- Document findings in `AI/securityNextSteps.md` DAST column
- Recommended: ZAP GitHub Action with active scan profile

---

## Authentication Session Management (OIDC PKCE)

### Token lifecycle
1. User redirected to DIAM/Keycloak with PKCE challenge (`code_challenge`, `code_challenge_method=S256`)
2. Auth code returned — exchanged for `access_token` (short-lived) + `refresh_token`
3. `oidc-client-ts` (`UserManager`) handles silent refresh automatically via `automaticSilentRenew: true`
4. On token expiry: silent iframe renew or redirect back to IdP
5. Logout: call `/end_session_endpoint` + clear local session; implement backchannel logout endpoint at `/logout/backchannel` in API

### React `oidc-client-ts` configuration
```js
// src/auth/authConfig.js — OIDC UserManager config for DIAM
export const userManagerConfig = {
  authority:            process.env.VITE_OIDC_AUTHORITY,
  client_id:            process.env.VITE_OIDC_CLIENT_ID,
  redirect_uri:         `${window.location.origin}/callback`,
  post_logout_redirect_uri: `${window.location.origin}/`,
  response_type:        'code',                 // PKCE
  scope:                'openid profile email',
  automaticSilentRenew: true,
  silent_redirect_uri:  `${window.location.origin}/silent-callback.html`,
  filterProtocolClaims: true,
  loadUserInfo:         true,
};
```

### API backchannel logout endpoint
```csharp
// POST /logout/backchannel — OIDC backchannel logout handler
[HttpPost("/logout/backchannel")]
[AllowAnonymous]
public IActionResult BackchannelLogout([FromForm] string logout_token)
{
    // Validate logout_token JWT (issuer, audience, sub/sid claims)
    // Invalidate server-side session or token cache for that sub/sid
    return Ok();
}
```

---

## STRA / PIA Process (BC Gov)

### When to trigger a STRA
- New service storing personal information → **STRA required before TEST environment**
- DataClass: Medium or above → STRA mandatory
- External API integration involving personal data → STRA required
- New OAuth client registered in DIAM → STRA review section required

### STRA checklist
- [ ] Identify data elements stored / processed (DataClass: Low / Medium / High / Critical)
- [ ] Complete [STRA template](https://intranet.gov.bc.ca/iit/products-services/information-security/security-threat-and-risk-assessments) with Ministry ISSO
- [ ] Capture accepted risks in `AI/securityNextSteps.md` → "STRA Status" row
- [ ] Re-assess if architecture changes materially (new DB, new integration, new data type)

### When to trigger a PIA
- Service collects, uses, or discloses personal information about BC residents
- New automated decision supported by personal data
- Third-party data processor involved (cloud provider, vendor)

---

## RBAC Least-Privilege Audit

### Audit Command Sequence

```bash
# List all RoleBindings and their subjects in a namespace
oc get rolebindings -n <ns> -o json | jq '.items[] | {name: .metadata.name, role: .roleRef.name, subjects: [.subjects[]? | {kind, name}]}'

# Find ServiceAccounts with cluster-level roles
oc get clusterrolebindings -o json | jq '.items[] | select(.subjects[]?.namespace == "<ns>") | {name: .metadata.name, role: .roleRef.name}'

# Find pods not using a dedicated ServiceAccount (using default)
oc get pods -n <ns> -o json | jq '.items[] | select(.spec.serviceAccountName == "default" or .spec.serviceAccountName == null) | .metadata.name'
```

### Risk Tiers

| Binding | Risk | Action |
|---|---|---|
| `cluster-admin` to any namespace SA | 🔴 CRITICAL | Remove immediately; escalate |
| `edit` on a SA running an internet-facing pod | 🔴 HIGH | Downscope to minimum required verbs |
| Multiple workloads sharing one SA | 🟡 MEDIUM | Blast radius on compromise — create dedicated SAs |
| `default` SA used by a pod | 🟡 MEDIUM | No least-privilege — create a dedicated SA |
| Dedicated SA per workload, `view` or custom role | 🟢 COMPLIANT | |

### CronJob RBAC Anti-Pattern

CronJobs that delete/restart pods require `delete` on `pods`. This is an anti-pattern:

- **Risk:** If the CronJob SA is compromised, an attacker can delete any pod in the namespace
- **Root cause:** Unhealthy pods that do not self-heal via liveness probes
- **Remediation:** Fix the liveness probe and restart policy so pods self-recover — eliminate the need for the CronJob entirely
- **If CronJob must exist:** Scope the SA to a Role that allows `delete` only on pods with a specific label selector

Multi-service deployments typically accumulate 20–30 RoleBindings per namespace. High counts are expected but always audit for:
- Any `cluster-admin` bindings
- SAs shared across multiple workloads
- Pods using the `default` SA
- CronJob SAs with elevated pod permissions

---

## Image Provenance Checklist

### Supply Chain Risk Tiers

| Image Source | Risk | Action |
|---|---|---|
| Public DockerHub `:latest` | 🔴 CRITICAL | No provenance, mutable tag — mirror to Artifactory immediately |
| Public DockerHub SHA-pinned | 🔴 HIGH | No BC Gov vulnerability scanning, not mirrored — remediate |
| Internal registry mutable tag (`:dev`, `:main`) | 🟡 MEDIUM | Reproducibility risk — pin to SHA in non-dev environments |
| Internal registry SHA-pinned | 🟢 COMPLIANT | |
| Internal registry SHA-pinned + Trivy-scanned + Cosign-signed | 🟢 IDEAL | |

### Audit Command

```bash
# Find all images NOT sourced from the internal OpenShift registry
oc get deployments,statefulsets -n <ns> -o json | \
  jq '.items[].spec.template.spec.containers[].image' | \
  grep -v 'image-registry.openshift-image-registry.svc'
```

Also check `initContainers`:
```bash
oc get deployments,statefulsets -n <ns> -o json | \
  jq '.items[].spec.template.spec.initContainers[]?.image' | \
  grep -v 'image-registry.openshift-image-registry.svc'
```

### Remediation Steps

1. Mirror the image to Artifactory (`docker pull → docker tag → docker push <artifactory>/...`)
2. Update the deployment to reference the Artifactory image ref
3. Pin to a specific SHA digest: `image: artifacts.developer.gov.bc.ca/my-repo/redis/redisinsight@sha256:<digest>`
4. Add the image to the Trivy image-scan pipeline step
5. For production: add Cosign signing to the CI pipeline

### High-Risk Image + Exposure Pattern

When a **DockerHub `:latest` admin UI image** (e.g. a Redis or database admin tool) is deployed with a **public Route and no authentication**, this is the worst-case combination:

| Risk Factor | Detail |
|---|---|
| Source | DockerHub (public) |
| Tag | `:latest` — mutable, no provenance |
| Exposure | Public Route with no authentication |
| Data access | Admin UI — full read/write access to data store |
| Classification | Data store may carry Protected B personal information |

This is the worst-case combination: **public image + mutable tag + public admin UI + access to Protected B data**. Immediate remediation: remove the public Route, mirror to Artifactory, pin to SHA.

---

## SECURITY_KNOWLEDGE

```yaml
confirmed_facts:
  - "DataClass: Medium required on Emerald — confirmed 2026-02-23 (Low has no VIP)"
  - "BC Gov STRA templates maintained by OCIO; Ministry ISSO is the reviewer"
  - "DIAM uses Keycloak; standard realm is 'standard' on loginproxy.gov.bc.ca"
  - "CodeQL on bcgov-c org requires GitHub Advanced Security (GHAS) enabled on repo"
  - "Gitleaks detects secrets in git history across all branches on push"
  - "Trivy: exit-code 1 on CRITICAL/HIGH blocks the build step"
  - "Vault Agent Injector and External Secrets Operator both supported on Emerald"
  - "AllowPrivilegeEscalation: false enforced by Emerald cluster admission webhook"
  - "2026-06-05: [multi-app-engagement] Admin UI images from DockerHub :latest with public routes found in multiple namespaces — mirror to Artifactory + remove public route as immediate remediation"
  - "2026-06-05: [multi-app-engagement] 20-30 RoleBindings per namespace is typical for multi-service deployments but always audit for cluster-admin bindings and shared ServiceAccounts"
common_pitfalls:
  - "FromSqlRaw does NOT parameterise — use FromSqlInterpolated for any raw SQL"
  - "Silent renew iframe fails if third-party cookies are blocked (Safari ITP) — use refresh_token grant instead"
  - "AuditInterceptor must be registered before DbContext is first resolved — register in AddDbContext, not AddSingleton"
  - "Vault Agent Injector annotations must be on the Pod template spec, not the Deployment metadata"
```
