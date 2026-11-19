# Acceptance Criteria — Securing BC Gov Workloads

Observable pass/fail criteria for BC Gov .NET, React, and OpenShift application security, secrets management, database controls, and cluster posture.

## Governance & Data Gates

| Criterion | Pass | Fail |
|---|---|---|
| STRA / PIA gates | ISCF classification is confirmed; STRA is completed before TEST for Protected B+ / Medium+ data; PIA is initiated if collecting/disclosing personal information. | Protected B+ workload promoted to TEST without STRA or personal data flow without PIA. |

## Application, Auth & Container Hardening

| Criterion | Pass | Fail |
|---|---|---|
| Query & input safety | EF Core uses LINQ or `FromSqlInterpolated` (zero `FromSqlRaw`); DTOs enforce validation annotations; `AuditInterceptor` and named CORS policies are configured. | Raw SQL string concatenation (`FromSqlRaw`), wildcard CORS (`*`), or missing input validation. |
| ASP.NET Core pipeline & authz | `UseAuthentication()`/`UseAuthorization()` precede endpoints; `[AutoValidateAntiforgeryToken]` protects cookie/session actions; every action has an explicit `[Http*]` verb; `TokenValidationParameters` pins `iss`, `aud`, `exp`, and `ValidAlgorithms`; Data Protection keys persist across replicas; `ForwardedHeaders` uses explicit `KnownProxies`/`KnownNetworks`. | Auth middleware after endpoints, missing `[Http*]` catch-all or `[AcceptVerbs("GET","POST")]`, `alg: none`/unpinned JWT algorithms, ephemeral pod Data Protection keys, or cleared `KnownNetworks`/`KnownProxies`. |
| SPA security | URLs (`href`, `window.location`) validate against safe scheme allowlists; zero secrets in `VITE_*`/`REACT_APP_*`/`NEXT_PUBLIC_*`; protected routes return backend `401`/`403`; tokens/PII are never persisted in `localStorage`/`zustand`/`redux-persist`. | `javascript:` URL injection, secrets in client bundle env vars, UX-only route guards without backend `401`/`403`, or tokens persisted in `localStorage`. |
| Audit & control assurance | Authoritative audit logs emit at service/DB level with actor + correlation IDs; any diagnostic switch is time-boxed, off by default, and excludes passwords/MFA codes; real-wiring integration tests cover negative auth/tenant/token paths and stateful invariants (`FSM-BYPASS`, `TOCTOU-RACE`, `TENANT-LEAK`, `FAIL-OPEN-AUTH`). | Controller-only audit logs, unredacted passwords/MFA in diagnostics, direct controller instantiation or mocked-control tests as security proof, or fail-open null-scope/race paths. |
| LLM & Markdown security | RAG enforces pre-retrieval authz/tenant filtering; tools use allowlists, typed schemas, and server-side authz; model output is schema-validated before sinks; Markdown disables `html: true`/`javascript:` links/unsafe YAML loaders and strips hidden bidi/zero-width unicode. | Second-order prompt injection into privileged tools, post-retrieval-only filtering, raw HTML/MDX execution on untrusted Markdown, or `yaml.load()` without safe schema. |
| OIDC PKCE auth | Authentication uses OIDC Authorization Code + PKCE (`oidc-client-ts`), backchannel logout, and token rotation. | Implicit flow, tokens stored without rotation, or missing logout handling. |
| Container security baseline | Pods run non-root on port `8080` with `allowPrivilegeEscalation: false`, `drop: [ALL]`, `readOnlyRootFilesystem: true`, and SHA-pinned internal/Artifactory images in non-dev. | Root containers, writable root filesystem, or `:latest` tags in non-dev environments. |

## Secrets & Database Controls

| Criterion | Pass | Fail |
|---|---|---|
| Vault / ESO integration | Secrets live in Vault (`<license-plate>-nonprod/<secret>` or `<license-plate>-prod/<secret>`, namespace `platform-services`, no hyphens in keys) via Pod-template Vault Agent Injector (KSA `<license-plate>-vault`, cluster `auth/k8s-<cluster>`) or ESO `external-secrets.io/v1` (Azure Key Vault/AWS SM, or `tokenSecretRef` for BC Gov Vault); Helm `secret.yaml` is shape-only. | Hardcoded secrets in source/Helm values, hyphens in secret keys, missing `platform-services` namespace, or Vault annotations placed on Deployment `metadata` instead of Pod template `metadata`. |
| Database Security Standard | All 23 BC Gov MUST controls (prod/non-prod segregation, Medium/High test data sanitisation, TLS in transit, backup testing, privileged/bulk audit) are mapped in the SSP or have documented OCIO exemptions. | Unmapped MUST controls, unsanitised prod data in non-prod, or unencrypted DB connections. |

## CI Gates & Cluster Posture

| Criterion | Pass | Fail |
|---|---|---|
| Static & supply-chain CI | CodeQL, Trivy FS/Image (`exit-code 1` on CRITICAL/HIGH), Dependency Review, and Gitleaks pass on PRs. | Bypassed CI security gates or unaddressed CRITICAL/HIGH CVEs. |
| RBAC & image provenance | Zero `cluster-admin` namespace SA bindings, zero pods on `default` SA, zero unmirrored DockerHub `:latest` images, and zero public `:latest` admin UI routes. | Over-privileged SAs, workloads on `default` SA, or exposed `:latest` admin UIs. |
