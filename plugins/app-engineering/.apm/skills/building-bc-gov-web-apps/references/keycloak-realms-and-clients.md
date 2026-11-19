# Keycloak Realms & Clients (DIAM & Common SSO)

## Identity Provider Reference

| Provider | Base URL | Realm | Use When |
|---|---|---|---|
| Common SSO (IDIR + BCeID) | `https://loginproxy.gov.bc.ca` | `standard` | Internal staff / business users |
| DIAM | `https://diam-dev.gov.bc.ca` / `diam.gov.bc.ca` | Project-specific | Ministry-specific brokered identity |
| IDIR / AzureAD IDIR | `https://loginproxy.gov.bc.ca` | `idir` | IDIR only, no BCeID needed |
| BCeID (Basic / Business) | `https://loginproxy.gov.bc.ca` | `bceidbasic` / `bceidbusiness` | BCeID Basic, Business, or both |
| GitHub (BC Gov Org) | `https://loginproxy.gov.bc.ca` | `standard` (CSS IdP) | GitHub BC Gov Org member login |

> **Pathfinder CSS IdP aliases vs legacy naming:** On Pathfinder CSS (`standard` realm), use the standard IdP aliases `idir`, `bceidbasic`, and `bceidbusiness` (or `kc_idp_hint` values matching your CSS integration). Legacy Silver/Emerald Keycloak deployments used `onestopauth`, `onestopauth-basic`, `onestopauth-business`, and `onestopauth-both` terminology — migrate to Pathfinder CSS `standard` realm aliases for new and modernized apps.

DIAM brokers to Common SSO as a federation layer. Most new projects use **Common SSO `standard`** via the **Pathfinder Common Hosted Single Sign-On (CSS)** self-service portal unless there is a specific requirement for DIAM's additional brokering or custom attribute mapping.

### Pathfinder CSS Self-Service & High Availability

- **Self-service portal:** Request and manage OIDC clients at [Pathfinder CSS (`sso-requests`)](https://bcgov.github.io/sso-requests/) (`https://github.com/bcgov/sso-requests`).
- **Platform foundation:** Built on Red Hat SSO / Keycloak ([`bcgov/sso-keycloak` wiki](https://github.com/bcgov/sso-keycloak/wiki)), supporting IDIR, AzureAD IDIR, BCeID Basic, BCeID Business, and **GitHub associated with BC Gov Org**.
- **Active-DR architecture (Gold / GoldDR):** Separate `dev`, `test`, and `prod` Keycloak instances run in Kamloops (**Gold**) with continuous data replication to Calgary (**GoldDR**) and automated **GSLB** failover (`bcgov/sso-switchover-agent`).

OIDC Discovery URL:
`https://loginproxy.gov.bc.ca/auth/realms/standard/.well-known/openid-configuration`

## PKCE Flow Summary

```text
Browser                   React App              Keycloak
   |                          |                      |
   |-- click Login -->        |                      |
   |                  generate code_verifier         |
   |                  hash -> code_challenge         |
   |                          |-- GET /auth?         |
   |                          |   client_id          |
   |                          |   code_challenge --> |
   |                          |              redirect_uri + auth_code
   |                          |<-- auth_code --------|
   |                          |-- POST /token        |
   |                          |   code + code_verifier
   |                          |--------------------->|
   |                          |<-- access_token      |
   |                          |    refresh_token ----|
```

No `client_secret` is required for public clients (SPA). The `code_verifier` / `code_challenge` pair replaces the implicit flow's reliance on a trusted origin.

## Keycloak Client Registration

### Public Client (React SPA)

| Setting | Value |
|---|---|
| Access type | `public` |
| Standard flow | `ON` |
| Implicit flow | `OFF` |
| Valid redirect URIs | `https://<app>-<license>-dev.apps.emerald.devops.gov.bc.ca/callback` |
| Post logout redirect URIs | `https://<app>-<license>-dev.apps.emerald.devops.gov.bc.ca/` |
| Web origins | Same as redirect (no `+` wildcard in prod) |
| PKCE method | `S256` |

### Confidential Client (API-to-API)

| Setting | Value |
|---|---|
| Access type | `confidential` |
| Service accounts | `ON` |
| `client_secret` | Store in BC Gov Vault (`https://vault.developer.gov.bc.ca/`, namespace `platform-services`): `<license-plate>-nonprod/<app-secret-dev>` (for `tools`/`dev`/`test`) or `<license-plate>-prod/<app-secret-prod>` (for `prod`), e.g. key `oidc_client_secret` (avoid hyphens in Vault secret keys) |
