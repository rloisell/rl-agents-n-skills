---
name: building-bc-gov-web-apps
description: Builds BC Government React/Vite web applications using the BC Gov Design System (@bcgov/* packages, BC Sans, design tokens) and DIAM/Common SSO OIDC PKCE authentication with .NET JWT validation. Use when building BC Gov React frontends, replacing manual header/footer markup, applying design tokens, or configuring Keycloak OIDC and backchannel logout.
---

# Building BC Gov Web Apps

Combines the BC Government Design System for React/Vite with DIAM and Common SSO Keycloak OIDC PKCE authentication and .NET JWT validation.

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

1. Install `@bcgov/design-system-react-components`, `@bcgov/bc-sans`, `@bcgov/design-tokens`, `oidc-client-ts`, and `react-oidc-context`.
2. Import CSS in `main.jsx` (`BC_Sans.css` -> `variables.css` -> `./index.css`), wrap the app in `<AuthProvider>`, and render `<Header>` / `<Footer>`.

## Workflow

1. **Install & Wire Design System:** Install `@bcgov/design-system-react-components`, `@bcgov/bc-sans`, and `@bcgov/design-tokens`; configure `Header`, `Footer`, and `.app-nav` navigation. See [bc-gov-design-system.md](references/bc-gov-design-system.md) and [design-tokens.md](references/design-tokens.md).
2. **Select Realm & Register Client:** Choose Common SSO `standard` (or DIAM if ministry-specific brokering is required) and register public/confidential Keycloak clients. See [keycloak-realms-and-clients.md](references/keycloak-realms-and-clients.md).
3. **Configure React OIDC:** Set up `oidc-client-ts` and `react-oidc-context` with `/callback`, `/silent-callback.html`, and an API Bearer interceptor. See [react-oidc-client-ts.md](references/react-oidc-client-ts.md).
4. **Secure .NET API & Logout:** Configure `AddJwtBearer`, extract the `sub` claim, and implement `/logout/backchannel`. See [dotnet-jwt-and-backchannel-logout.md](references/dotnet-jwt-and-backchannel-logout.md).
5. **Review Pitfalls:** Check confirmed facts and common IAM pitfalls in [iam-knowledge.md](references/iam-knowledge.md).

## Verification

- Confirm no external `fonts2.gov.bc.ca` requests or hard-coded `#003366` / `#38598a` hex values exist in CSS.
- Verify `<FooterLinks>` receives React `<a>` elements (not plain objects).
- Test OIDC login, silent renew, API Bearer authorization, and logout redirect against the registered Keycloak client.

## References

- [BC Gov Design System](references/bc-gov-design-system.md) — npm packages, `main.jsx` order, `Header`, `Footer`, `.app-nav`, and anti-patterns.
- [Design Tokens](references/design-tokens.md) — colour and layout CSS custom properties.
- [Keycloak Realms & Clients](references/keycloak-realms-and-clients.md) — Common SSO vs DIAM, PKCE flow, and client registration.
- [React `oidc-client-ts`](references/react-oidc-client-ts.md) — `authConfig.js`, `AuthProvider`, callback/silent-renew, and axios interceptor.
- [.NET JWT & Backchannel Logout](references/dotnet-jwt-and-backchannel-logout.md) — `JwtBearer` setup, claims extraction, and `/logout/backchannel`.
- [IAM Knowledge](references/iam-knowledge.md) — confirmed facts and common OIDC pitfalls.
- [Acceptance Criteria](references/acceptance-criteria.md) — observable pass/fail criteria for Design System, OIDC, and JWT outputs.
