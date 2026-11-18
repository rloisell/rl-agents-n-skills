---
name: securing-bc-gov-workloads
description: Security architecture, secrets management, and database/container hardening for BC Gov .NET, React, and OpenShift workloads. Use when designing OWASP Top 10 controls, configuring HashiCorp Vault / External Secrets Operator, auditing OpenShift RBAC and container image provenance, implementing OIDC PKCE, or applying the 23 BC Gov Database Security Standard controls and STRA/PIA gates.
compatibility: .NET 10 / ASP.NET Core, React / Vite, OpenShift 4.x (Silver/Gold/Emerald), HashiCorp Vault, External Secrets Operator v0.9+.
---

# Securing BC Gov Workloads

Drives application security architecture, secrets management, database security compliance, and OpenShift workload auditing for BC Government projects.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

1. **Parameterised queries only**: never use `FromSqlRaw` in EF Core; use LINQ or `FromSqlInterpolated`.
2. **OIDC PKCE only**: never use implicit flow; implement backchannel logout and token rotation.
3. **No secrets in source or Helm values**: store secrets in HashiCorp Vault (`secret/<license-plate>/<env>/<key>`) and sync via External Secrets Operator (ESO) or Vault Agent Injector (annotations on Pod template `metadata`, not Deployment `metadata`).
4. **Container security baseline**: non-root user, `allowPrivilegeEscalation: false`, `drop: [ALL]`, `readOnlyRootFilesystem: true`, port `8080`, SHA-pinned internal/Artifactory images in non-dev environments.
5. **Database Security Standard (23 MUST controls)**: segregate prod from non-prod, sanitise test data (Medium/High), enforce TLS in transit, test backups, and audit privileged/bulk access.
6. **STRA/PIA gate**: workloads storing Protected B+ or Medium/High data require a STRA before TEST and a PIA if collecting/disclosing personal information.

## Quick start

1. Confirm the workload's ISCF classification and STRA/PIA status before designing controls.
2. Apply OWASP Top 10, OIDC PKCE, Vault/ESO secrets, and BC Gov Database Security Standard controls from `references/`.
3. Run static/CI security gates and OpenShift RBAC/image provenance checks before promoting to non-dev environments.

## Workflow

1. **Classify & gate**: Determine ISCF data classification and whether STRA/PIA triggers apply (see `mapping-data-lineage` for data flow ledgers and FOIPPA residency).
2. **Harden app & auth**: Apply OWASP Top 10 controls, DTO data annotations, EF Core `AuditInterceptor`, OIDC PKCE (`oidc-client-ts`), and named CORS policies per [owasp-dotnet-react-oidc.md](references/owasp-dotnet-react-oidc.md).
3. **Configure secrets**: Provision Vault paths, ESO `SecretStore`/`ExternalSecret` (or Pod-template Vault Agent annotations), and shape-only Helm `secret.yaml` per [vault-secrets.md](references/vault-secrets.md).
4. **Apply database controls**: Map all 23 controls from the BC Gov Database Security Standard to the System Security Plan or documented OCIO exemptions per [database-security-standard.md](references/database-security-standard.md).
5. **Audit cluster posture**: Run RBAC least-privilege, ServiceAccount, and image provenance checks per [ocp-rbac-and-image-audit.md](references/ocp-rbac-and-image-audit.md); remediate any public `:latest` admin UI routes immediately.

## Verification

- Static/CI gates: CodeQL, Trivy FS/Image (`exit-code 1` on CRITICAL/HIGH), Dependency Review, and Gitleaks pass on PRs.
- Cluster checks: zero `cluster-admin` namespace SA bindings, zero pods on `default` SA, and zero unmirrored DockerHub `:latest` images in `oc get deployments,statefulsets`.

## References

- [owasp-dotnet-react-oidc.md](references/owasp-dotnet-react-oidc.md) — OWASP Top 10 (.NET/React), input validation, EF Core `AuditInterceptor`, container security baseline, SAST/DAST toolchain, OIDC PKCE, and STRA/PIA checklists.
- [vault-secrets.md](references/vault-secrets.md) — Vault path conventions, ESO `SecretStore`/`ExternalSecret` CRDs, Vault Agent Injector annotations, shape-only Helm Secrets, and GitHub Actions integration.
- [database-security-standard.md](references/database-security-standard.md) — BC Gov Database Security Standard (23 mandatory controls), Emerald/EF Core application notes, and companion IMIT standards.
- [ocp-rbac-and-image-audit.md](references/ocp-rbac-and-image-audit.md) — OpenShift RBAC least-privilege audit commands, CronJob anti-pattern, image provenance risk tiers, and remediation steps.
- [Acceptance Criteria](references/acceptance-criteria.md) — Observable pass/fail criteria for STRA/PIA gates, app/auth/container hardening, Vault/ESO, DB controls, and CI/cluster checks.
- Templates: [secretstore.yaml](assets/templates/secretstore.yaml) • [externalsecret.yaml](assets/templates/externalsecret.yaml)
