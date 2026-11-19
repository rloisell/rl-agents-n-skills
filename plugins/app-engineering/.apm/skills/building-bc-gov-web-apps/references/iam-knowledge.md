# IAM Knowledge

```yaml
confirmed_facts:
  - "Common SSO 'standard' realm brokers IDIR, BCeID Basic, and BCeID Business"
  - "PKCE with S256 is mandatory for public clients — implicit flow is disabled on Common SSO"
  - "automaticSilentRenew uses a hidden iframe; may fail in Safari with ITP — use refresh_token_grant as fallback"
  - "Keycloak sub claim = user's UUID in the realm — use as the canonical user identifier"
  - "DIAM adds a ministry-specific brokering layer on top of Common SSO for ministry projects"
  - "Vault structure for OIDC client secrets: namespace 'platform-services', engine '<license-plate>-nonprod' (tools/dev/test) or '<license-plate>-prod' (prod), e.g., <license-plate>-nonprod/<app-secret-dev> (avoid hyphens in secret keys)"
common_pitfalls:
  - "do NOT store access_token in localStorage — use oidc-client-ts in-memory store"
  - "ClockSkew must be set to at least 30s to tolerate server timing differences with Keycloak"
  - "Post logout redirect URI must be registered in Keycloak or the logout will fail silently"
  - "Bearer token audience validation: Keycloak issues 'account' audience by default — configure 'Add Audience' mapper"
```
