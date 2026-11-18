# Keycloak Realms & Clients (DIAM & Common SSO)

## Identity Provider Reference

| Provider | Base URL | Realm | Use When |
|---|---|---|---|
| Common SSO (IDIR + BCeID) | `https://loginproxy.gov.bc.ca` | `standard` | Internal staff / business users |
| DIAM | `https://diam-dev.gov.bc.ca` / `diam.gov.bc.ca` | Project-specific | Ministry-specific brokered identity |
| IDIR (direct) | `https://loginproxy.gov.bc.ca` | `idir` | IDIR only, no BCeID needed |
| BCeID (direct) | `https://loginproxy.gov.bc.ca` | `bceidbasic` / `bceidbusiness` | BCeID only |

DIAM brokers to Common SSO as a federation layer. Most new projects use **Common SSO `standard`** unless there is a specific requirement for DIAM's additional brokering or custom attribute mapping.

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
| `client_secret` | Store in Vault at `secret/<license>/<env>/oidc-client-secret` |
