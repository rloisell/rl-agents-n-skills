# Acceptance Criteria — Building BC Gov Web Apps

Observable pass/fail criteria for verifying BC Gov React/Vite design-system and OIDC/JWT implementations.

## Pass/Fail Criteria

| Area | Pass Criteria | Fail Criteria |
|---|---|---|
| **BC Sans & CSS Order** | `@bcgov/bc-sans/css/BC_Sans.css`, `@bcgov/design-tokens/css/variables.css`, and `./index.css` are imported in that exact order in `main.jsx`. | Missing `BC_Sans.css`, wrong import order, or any reference/request to `fonts2.gov.bc.ca`. |
| **Design System & Tokens** | Uses official `@bcgov/design-system-react-components` `<Header>` and `<Footer>` (`<FooterLinks>` receives React `<a>` elements) and `var(--surface-color-*, fallback)` tokens. | Custom header/footer HTML, plain objects passed to `<FooterLinks>`, or hard-coded `#003366` / `#38598a` hex values in CSS. |
| **React OIDC & PKCE** | `oidc-client-ts` / `react-oidc-context` uses `response_type: "code"` with PKCE `S256`, in-memory token storage, `/callback`, `/silent-callback.html`, and an API Bearer interceptor. | Implicit flow enabled, tokens persisted to `localStorage`/`sessionStorage`, or missing silent-renew/callback routes. |
| **.NET JWT & Logout** | `AddJwtBearer` validates issuer, audience, and lifetime with `ClockSkew >= 30s` (60s recommended); `sub` claim is extracted; `/logout/backchannel` is implemented. | Disabled issuer/audience/lifetime validation, `ClockSkew < 30s`, or missing backchannel logout endpoint. |
| **Build & Flow Verification** | `npm run build` and `npm test` exit 0; OIDC login, silent renew, Bearer API call, and logout redirect succeed against the registered Keycloak client. | Build/test failures, 401 on authenticated API calls, or broken logout redirect. |
| **UX & WCAG 2.2 AA** | Reflows at 320px / 400% zoom, meets target-size and unobscured-focus rules, respects `prefers-reduced-motion`, updates SPA title/focus on route change, masks sensitive IDs by default with per-field `aria-pressed` reveal, and surfaces provenance/recourse on consequential/degraded states (see [ux-and-accessibility-patterns.md](ux-and-accessibility-patterns.md)). | Horizontal scroll on ordinary content, obscured focus, missing reveal/re-mask controls, sensitive values in live regions/DOM/logs, or failures hidden in spinners. |
| **.NET Engineering** | Preserves Indigenous-language UTF-8 with ICU enabled, uses `Microsoft.Extensions.Http.Resilience` (Polly v8), injects `TimeProvider`, propagates `CancellationToken`, restores `packages.lock.json --locked-mode` with `NuGetAudit`, persists Data Protection keys across replicas, and tests boundaries via `WebApplicationFactory` (see [dotnet-engineering-standards.md](dotnet-engineering-standards.md)). | `InvariantGlobalization=true`, deprecated `Microsoft.Extensions.Http.Polly`, missing lockfile/`NuGetAudit`, ephemeral local Data Protection keys in multi-replica deploys, or non-atomic state transitions. |
