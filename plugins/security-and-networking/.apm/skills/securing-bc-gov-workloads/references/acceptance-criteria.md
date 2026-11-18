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
| OIDC PKCE auth | Authentication uses OIDC Authorization Code + PKCE (`oidc-client-ts`), backchannel logout, and token rotation. | Implicit flow, tokens stored without rotation, or missing logout handling. |
| Container security baseline | Pods run non-root on port `8080` with `allowPrivilegeEscalation: false`, `drop: [ALL]`, `readOnlyRootFilesystem: true`, and SHA-pinned internal/Artifactory images in non-dev. | Root containers, writable root filesystem, or `:latest` tags in non-dev environments. |

## Secrets & Database Controls

| Criterion | Pass | Fail |
|---|---|---|
| Vault / ESO integration | Secrets live in Vault (`secret/<license-plate>/<env>/<key>`) synced via ESO or Pod-template Vault Agent annotations; Helm `secret.yaml` is shape-only. | Hardcoded secrets in source/Helm values, or Vault annotations placed on Deployment `metadata` instead of Pod template `metadata`. |
| Database Security Standard | All 23 BC Gov MUST controls (prod/non-prod segregation, Medium/High test data sanitisation, TLS in transit, backup testing, privileged/bulk audit) are mapped in the SSP or have documented OCIO exemptions. | Unmapped MUST controls, unsanitised prod data in non-prod, or unencrypted DB connections. |

## CI Gates & Cluster Posture

| Criterion | Pass | Fail |
|---|---|---|
| Static & supply-chain CI | CodeQL, Trivy FS/Image (`exit-code 1` on CRITICAL/HIGH), Dependency Review, and Gitleaks pass on PRs. | Bypassed CI security gates or unaddressed CRITICAL/HIGH CVEs. |
| RBAC & image provenance | Zero `cluster-admin` namespace SA bindings, zero pods on `default` SA, zero unmirrored DockerHub `:latest` images, and zero public `:latest` admin UI routes. | Over-privileged SAs, workloads on `default` SA, or exposed `:latest` admin UIs. |
