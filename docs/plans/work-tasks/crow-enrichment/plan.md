# Crow Enrichment Plan (`bcgov-devops-platform-workbench`)

## Objective

Augment existing skills and references across `dev-workflow`, `openshift-devops`, `security-and-networking`, and `app-engineering` with non-duplicated BC Gov CI/CD, HA continuity, security/Sonar/code-review, .NET 10/Unicode, diagnostics, and UX/accessibility gaps from `temp/repos/crow/.apm/skills/` (`bcgov/crow`, MIT License), without duplicating Crow skills or creating redundant skills.

## Nodes

1. **`dev-workflow-crow`**:
   - `managing-github-workflows`: Sonar `projectVersion`, `sonar.qualitygate.wait=true`, untrusted PR/cache-poisoning guards, fail-on-zero-tests, `actionlint`, PR fast vs nightly deep tests, approval-gated rebuild-from-immutable-SHA release, release-notes sanitization, runtime-vs-library dependency hygiene, GitHub PR pagination + steelman review method, `crow-debt:` marker.
   - `managing-dev-sessions`: `Verified / Inferred / Unknown` epistemic labeling and public-safe project-context manifest pattern.
2. **`openshift-devops-crow`**:
   - `auditing-cicd-governance`: `CM-01`–`CM-04` checks for upload-only vs blocking Sonar gate, Azure `pollingTimeoutSec` trap, Jenkins Groovy secret interpolation, cache poisoning, zero-test fail-closed, DB-migration packaging vs execution, immutable build-ID binding, rebuild-from-SHA release, release-notes sanitization.
   - `analyzing-ocp-platforms`: Application & Release Continuity (`designed-not-demonstrated` vs `demonstrated`, N-1 version/asset/session overlap, expand-contract DB evolution, worker/scheduler drain, shared `terminationGracePeriodSeconds` timeline budget).
   - `deploying-bc-gov-workloads`: DB-migration artifact packaging note in `github-actions-option2.md`.
3. **`security-crow`**:
   - `securing-bc-gov-workloads`: ASP.NET Core middleware order, `[Http*]` verb & antiforgery checks, `TokenValidationParameters` algorithm pinning, Data Protection key persistence, SPA `javascript:` URL / bundle `VITE_*` / client-guard / state-persistence checks, real-wiring integration test assurance, `ForwardedHeaders` allowlists, stateful invariants (`FSM-BYPASS`, `TOCTOU-RACE`, `TENANT-LEAK`, `FAIL-OPEN-AUTH`), plus `llm-and-markdown-security.md` (prompt injection, pre-retrieval authz, tool bounds, Markdown XSS/SSRF).
4. **`app-engineering-crow`**:
   - `building-dotnet-apis`: BC Gov Indigenous-language UTF-8/ICU readiness, Polly v8 (`Microsoft.Extensions.Http.Resilience`), `Asp.Versioning`, RFC 9457 `ProblemDetails`, `Program.cs` middleware ordering, startup Options validation, avoiding generic EF repositories, narrow-question APIs.
   - `building-bc-gov-web-apps`: WCAG 2.2 AA deltas, sensitive-identifier masking/reveal UX, consequential decision/degraded-state UX, structured UX finding format, Indigenous UTF-8/ICU & .NET 10 engineering defaults.
   - `instrumenting-observability`: Application diagnostics, RFC 9457 Problem Details + W3C `traceId` support ref, UI error surface matrix, SPA error reporting, safe diagnostic stand-ins.
5. **`docs-and-attribution`** (fan-in):
   - Update `README.md`, `architecture.md`, and `migration-map.md` to catalog all new references and credit `bcgov/crow` (MIT License).
