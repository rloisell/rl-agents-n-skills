---
name: building-bc-gov-web-apps
description: Builds BC Government React/Vite web applications with DIAM/Common SSO OIDC PKCE authentication and .NET JWT validation, layering on top of the external bc-gov-design-system skill (richfrem/bc-gov-design-system). Use when building BC Gov React frontends, wiring OIDC/Header auth, or configuring Keycloak OIDC and backchannel logout.
---

# Building BC Gov Web Apps

Layers React/Vite app wiring, DIAM/Common SSO Keycloak OIDC PKCE (`oidc-client-ts`), `.NET` JWT validation, and BC Gov reusable services on top of the external [`bc-gov-design-system`](https://github.com/richfrem/bc-gov-design-system) skill (`react` mode).

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- **Self-hosted BC Sans:** Always import `@bcgov/bc-sans/css/BC_Sans.css` from npm; never import fonts from `fonts2.gov.bc.ca`.
- **Import order in `main.jsx`:** Import `BC_Sans.css`, then `@bcgov/design-tokens/css/variables.css`, then app `./index.css` last.
- **Official components & tokens:** Use `<Header>`, `<Footer>`, and `var(--surface-color-*, fallback)` tokens instead of manual header/footer markup or hard-coded hex values.
- **PKCE S256 mandatory:** Public SPA clients must use Authorization Code + PKCE (`S256`); implicit flow is disabled and tokens must stay in `oidc-client-ts` memory (never `localStorage`).
- **JwtBearer validation:** Validate issuer, audience, lifetime, and `ClockSkew >= 30s` (60s recommended) on the .NET API.

## Quick start

1. Ensure the [`bc-gov-design-system`](https://github.com/richfrem/bc-gov-design-system) skill is installed (`apm install richfrem/bc-gov-design-system`) and use its **`react` mode** for `@bcgov/*` components, BC Sans, and v5 design tokens.
2. Wrap the React/Vite app in `<AuthProvider>` (`oidc-client-ts` / `react-oidc-context`) and wire login/logout controls into the Design System `<Header>`.

## Workflow

1. **Delegate Design System (`bc-gov-design-system`):** Invoke `bc-gov-design-system` (`react` mode) from [`richfrem/bc-gov-design-system`](https://github.com/richfrem/bc-gov-design-system) for `@bcgov/design-system-react-components`, BC Sans, tokens, and WCAG rules; apply the Vite + OIDC wiring in [bc-gov-design-system.md](references/bc-gov-design-system.md).
2. **Select Realm & Register Client:** Choose Common SSO `standard` (or DIAM if ministry-specific brokering is required) and register public/confidential Keycloak clients. See [keycloak-realms-and-clients.md](references/keycloak-realms-and-clients.md).
3. **Configure React OIDC:** Set up `oidc-client-ts` and `react-oidc-context` with `/callback`, `/silent-callback.html`, and an API Bearer interceptor. See [react-oidc-client-ts.md](references/react-oidc-client-ts.md).
4. **Secure .NET API & Logout:** Configure `AddJwtBearer`, extract the `sub` claim, and implement `/logout/backchannel`. See [dotnet-jwt-and-backchannel-logout.md](references/dotnet-jwt-and-backchannel-logout.md).
5. **Integrate Reusable BC Gov Services:** Reuse CHES, CDOGS, COMS, GETOK, `bcgov/docker-weasyprint`, BC Address Geocoder, Fathom/Matomo, and `bcgov/owasp-zap-openshift` where applicable. See [bc-gov-reusable-services.md](references/bc-gov-reusable-services.md).
6. **Apply UX/Accessibility & .NET Engineering Baselines:** Verify WCAG 2.2 AA deltas, sensitive-identifier masking, and consequential-state UX in [ux-and-accessibility-patterns.md](references/ux-and-accessibility-patterns.md); apply UTF-8/ICU, Polly v8, Data Protection, and concurrency invariants in [dotnet-engineering-standards.md](references/dotnet-engineering-standards.md).
7. **Review Pitfalls:** Check confirmed facts and common IAM pitfalls in [iam-knowledge.md](references/iam-knowledge.md).

## Verification

- Confirm no external `fonts2.gov.bc.ca` requests or hard-coded `#003366` / `#38598a` hex values exist in CSS.
- Verify `<FooterLinks>` receives React `<a>` elements (not plain objects).
- Test OIDC login, silent renew, API Bearer authorization, and logout redirect against the registered Keycloak client.

## References

- [BC Gov Design System Integration](references/bc-gov-design-system.md) — thin layer consuming `richfrem/bc-gov-design-system` (`react` mode) with Vite + OIDC `<Header>` wiring.
- [Design Tokens Pointer](references/design-tokens.md) — delegates v5 design tokens to `richfrem/bc-gov-design-system`.
- [Keycloak Realms & Clients](references/keycloak-realms-and-clients.md) — Common SSO vs DIAM, PKCE flow, and client registration.
- [React `oidc-client-ts`](references/react-oidc-client-ts.md) — `authConfig.js`, `AuthProvider`, callback/silent-renew, and axios interceptor.
- [.NET JWT & Backchannel Logout](references/dotnet-jwt-and-backchannel-logout.md) — `JwtBearer` setup, claims extraction, and `/logout/backchannel`.
- [BC Gov Reusable Services](references/bc-gov-reusable-services.md) — CHES, CDOGS, COMS, GETOK, WeasyPrint, BC Address Geocoder, Fathom/Matomo, and OWASP ZAP.
- [UX & Accessibility Patterns](references/ux-and-accessibility-patterns.md) — WCAG 2.2 AA deltas, sensitive-ID masking/reveal, decision/degraded-state UX, and finding schema.
- [.NET Engineering Standards](references/dotnet-engineering-standards.md) — Indigenous UTF-8/ICU, Polly v8, `TimeProvider`, `CancellationToken`, lockfiles/`NuGetAudit`, Data Protection, and concurrency invariants.
- [IAM Knowledge](references/iam-knowledge.md) — confirmed facts and common OIDC pitfalls.
- [Acceptance Criteria](references/acceptance-criteria.md) — observable pass/fail criteria for Design System, OIDC, and JWT outputs.
