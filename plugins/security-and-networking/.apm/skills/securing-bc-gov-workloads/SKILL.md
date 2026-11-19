---
name: securing-bc-gov-workloads
description: Security architecture, secrets management, and database/container hardening for BC Gov .NET, React, and OpenShift workloads. Use when designing OWASP Top 10 controls, configuring HashiCorp Vault / External Secrets Operator, auditing OpenShift RBAC and container image provenance, implementing OIDC PKCE, or applying the 23 BC Gov Database Security Standard controls and STRA/PIA gates.
compatibility: .NET 10 / ASP.NET Core, React / Vite, OpenShift 4.x (Silver/Gold/Emerald), HashiCorp Vault, External Secrets Operator v1.
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
3. **No secrets in source or Helm values**: store secrets in HashiCorp Vault (`<license-plate>-nonprod/<secret>` or `<license-plate>-prod/<secret>` under namespace `platform-services`; no hyphens in secret keys). Use **Vault Agent Injector** (KSA `<license-plate>-vault`, cluster `auth/k8s-<cluster>`, Pod template `metadata` annotations) for KSA-based BC Gov Vault access, or **ESO** (`external-secrets.io/v1`) with Azure Key Vault / AWS Secrets Manager (ESO with BC Gov Vault requires a 1-month manual OIDC `tokenSecretRef`).
4. **Container security baseline**: non-root user, `allowPrivilegeEscalation: false`, `drop: [ALL]`, `readOnlyRootFilesystem: true`, port `8080`, SHA-pinned internal/Artifactory images in non-dev environments.
5. **Database Security Standard (23 MUST controls)**: segregate prod from non-prod, sanitise test data (Medium/High), enforce TLS in transit, test backups, and audit privileged/bulk access.
6. **STRA/PIA gate**: workloads storing Protected B+ or Medium/High data require a STRA before TEST and a PIA if collecting/disclosing personal information.

## Quick start

1. Confirm the workload's ISCF classification and STRA/PIA status before designing controls.
2. Apply OWASP Top 10, OIDC PKCE, Vault/ESO secrets, and BC Gov Database Security Standard controls from `references/`.
3. Run static/CI security gates and OpenShift RBAC/image provenance checks before promoting to non-dev environments.

## Workflow

1. **Classify & gate**: Determine ISCF data classification and whether STRA/PIA triggers apply (see `mapping-data-lineage` for data flow ledgers and FOIPPA residency).
2. **Harden app & auth**: Apply OWASP Top 10 controls, DTO data annotations, ASP.NET Core middleware/anti-forgery/JWT/Data Protection/`ForwardedHeaders` hardening, SPA URL/bundle/storage hygiene, service/DB-level `AuditInterceptor`, OIDC PKCE (`oidc-client-ts`), and named CORS policies per [owasp-dotnet-react-oidc.md](references/owasp-dotnet-react-oidc.md).
3. **Harden LLM & Markdown pipelines**: Enforce pre-retrieval tenant/authz filtering, typed tool allowlists, strict model-output validation, and safe Markdown/frontmatter rendering when processing AI or contributor docs per [llm-and-markdown-security.md](references/llm-and-markdown-security.md).
4. **Configure secrets**: Provision Vault paths (`<license-plate>-nonprod|prod`), Pod-template Vault Agent Injector annotations (or ESO `SecretStore`/`ExternalSecret`), and shape-only Helm `secret.yaml` per [vault-secrets.md](references/vault-secrets.md).
5. **Apply database controls**: Map all 23 controls from the BC Gov Database Security Standard to the System Security Plan or documented OCIO exemptions per [database-security-standard.md](references/database-security-standard.md).
6. **Audit cluster posture**: Run RBAC least-privilege, ServiceAccount, and image provenance checks per [ocp-rbac-and-image-audit.md](references/ocp-rbac-and-image-audit.md); remediate any public `:latest` admin UI routes immediately.

## Verification

- Static/CI gates: CodeQL, Trivy FS/Image (`exit-code 1` on CRITICAL/HIGH), Dependency Review, and Gitleaks pass on PRs.
- Assurance tests: Real-wiring integration tests (not direct controller or mocked-control tests) verify `401`/`403`, cross-tenant isolation, token/anti-forgery negative cases, audit emission, and stateful invariants (`FSM-BYPASS`, `TOCTOU-RACE`, `TENANT-LEAK`, `FAIL-OPEN-AUTH`).
- Cluster checks: zero `cluster-admin` namespace SA bindings, zero pods on `default` SA, and zero unmirrored DockerHub `:latest` images in `oc get deployments,statefulsets`.

## References

- [owasp-dotnet-react-oidc.md](references/owasp-dotnet-react-oidc.md) — OWASP Top 10 (.NET/React), ASP.NET Core/SPA blind spots, EF Core `AuditInterceptor` & control assurance, container security baseline, SAST/DAST toolchain, OIDC PKCE, and STRA/PIA checklists.
- [llm-and-markdown-security.md](references/llm-and-markdown-security.md) — Direct/second-order prompt injection, pre-retrieval authz, tool allowlists, untrusted model output, and Markdown/frontmatter XSS/SSRF/unicode checks.
- [vault-secrets.md](references/vault-secrets.md) — Vault path conventions, ESO `SecretStore`/`ExternalSecret` CRDs, Vault Agent Injector annotations, shape-only Helm Secrets, and GitHub Actions integration.
- [database-security-standard.md](references/database-security-standard.md) — BC Gov Database Security Standard (23 mandatory controls), Emerald/EF Core application notes, and companion IMIT standards.
- [ocp-rbac-and-image-audit.md](references/ocp-rbac-and-image-audit.md) — OpenShift RBAC least-privilege audit commands, CronJob anti-pattern, image provenance risk tiers, and remediation steps.
- [Acceptance Criteria](references/acceptance-criteria.md) — Observable pass/fail criteria for STRA/PIA gates, app/auth/container hardening, Vault/ESO, DB controls, and CI/cluster checks.
- Templates: [secretstore.yaml](assets/templates/secretstore.yaml) • [externalsecret.yaml](assets/templates/externalsecret.yaml) • [vault-agent-injector.tpl.yaml](assets/templates/vault-agent-injector.tpl.yaml) • [azure-keyvault-secretstore.tpl.yaml](assets/templates/azure-keyvault-secretstore.tpl.yaml)
