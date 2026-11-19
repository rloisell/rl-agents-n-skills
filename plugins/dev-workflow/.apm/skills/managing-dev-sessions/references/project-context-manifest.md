# Project Context Manifest

Public-safe repository-root project memory (`.workbench/project.config.yaml` or
`crow.config`) for Sonar settings, provider-neutral CI/CD, work tracking, and
security issue routing.

## Contents

- [Public-safe boundary](#public-safe-boundary)
- [Manifest structure](#manifest-structure)
- [Security issue routing](#security-issue-routing)
- [Provenance and user-confirmation gate](#provenance-and-user-confirmation-gate)

## Public-safe boundary

Treat the committed manifest as **public project memory**:

- **Allowed**: provider names (`github`, `azure-devops`, `discover`), public
  repository `owner/name`, repository-relative paths (`workflow_path`), Sonar
  project keys/exclusions, and symbolic `connection_ref` / `resource_ref`
  identifiers (e.g., `raven:github`, `<app>:ci:primary`).
- **Forbidden**: credentials, tokens, passwords, internal hostnames or base
  URLs, absolute filesystem paths, and raw provider API responses.
- **Private overlays**: store private locators and credentials in protected
  user-scoped storage (e.g., `~/.crow/crow.config.local` or platform keychain),
  never in the repository manifest.

## Manifest structure

```yaml
spec_version: "1.0"

project:
  id: "<app-name>"
  name: "<App Display Name>"
  repository:
    provider: "github"
    owner: "<org>"
    name: "<repo>"
    visibility: "public"

sonar:
  projectKey: "<app-name>"
  projectName: "<App Display Name>"
  exclusions:
    - "**/build/**"
    - "**/.scannerwork/**"
  useMsBuild: false
  runTests: false

ci_cd:
  - id: "primary"
    provider: "github"
    workflow_path: ".github/workflows/build-and-test.yml"
    lookup:
      mode: "local-then-provider"
      connection_ref: "raven:github"
      resource_ref: "<app-name>:ci:primary"
    discovered:
      source: "repository"
      recorded_by: "session"
      recorded_on: "YYYY-MM-DD"

work_tracking:
  - id: "primary"
    provider: "discover"
    lookup:
      mode: "provider"
      connection_ref: "raven:work-tracking"
      resource_ref: "<app-name>:work-tracking:primary"
```

Resolve `connection_ref` and `resource_ref` only when the active agent has a
matching read-only provider tool; otherwise leave private references unresolved
and report which lookup is needed rather than guessing an endpoint.

## Security issue routing

Resolve ticketing destinations from verified `work_tracking` entries rather than
assuming a GitHub repository is the ticketing system:

```yaml
security_issue_routing:
  destinations: [ghas, work_tracking]
  work_tracking_id: "primary"
  routes:
    - application_id: "api"
      service_path: "src/api"
      destinations: [ghas, work_tracking]
      work_tracking_id: "api-board"
```

- `ghas` is valid only when `project.repository.provider` is `github`.
- `work_tracking_id` must match an existing, verified `work_tracking` entry.
- Multi-app repositories require one route per inventoried app unless the user
  explicitly keeps an app local-only.

## Provenance and user-confirmation gate

1. **Read before external lookup**: check `.workbench/project.config.yaml` or
   `crow.config` at startup before querying external providers. If absent,
   continue with normal discovery and report that project memory is absent.
2. **User-confirmation gate**: never create or mutate the manifest without
   explicit user confirmation. A locator supplied for a one-off lookup is not
   authorization to persist it.
3. **Preserve provenance and unknown fields**: record `discovered.source`,
   `discovered.recorded_by`, and `discovered.recorded_on` on learned entries,
   and preserve existing entries and unknown fields.
4. **Fail closed**: stop and surface an error on malformed YAML, conflicting
   resource identities, an unverified provider lookup, or any attempted write of
   a secret, internal URL, or raw API response.
