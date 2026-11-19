## Contents

- [Indigenous-Language UTF-8, Unicode & ICU](#indigenous-language-utf-8-unicode--icu)
- [Resilience, Time & Cancellation](#resilience-time--cancellation)
- [Supply Chain & Deterministic Builds](#supply-chain--deterministic-builds)
- [Data Protection Across Replicas](#data-protection-across-replicas)
- [Integration Testing & Concurrency Invariants](#integration-testing--concurrency-invariants)

# .NET Engineering Standards

Engineering baselines for .NET backends supporting BC Gov web applications.

## Indigenous-Language UTF-8, Unicode & ICU

- **Preserve original text:** Use UTF-8 for HTTP/JSON/file interchange and Unicode-capable DB columns/collations. Do not strip diacritics, transliterate, force ASCII, or normalize destructively. Decode strictly at trust boundaries.
- **Grapheme-aware string handling:** Use `System.Globalization.StringInfo` and text-element APIs for user-visible length limits, truncation, and substrings (never index UTF-16 `char` directly). Use `Rune` for Unicode scalar values and explicit `StringComparison` (ordinal for IDs/security tokens; approved culture/collation for linguistic text).
- **Keep ICU enabled:** Never set `InvariantGlobalization=true` or use chiseled container images without ICU/locale/font assets when handling Indigenous-language or culture-sensitive text.
- **Round-trip corpus testing:** Maintain a test corpus covering combining marks (e.g., base Latin + `U+0313`), Unified Canadian Aboriginal Syllabics, canonically equivalent composed/decomposed sequences, and supplementary-plane characters across UI/API -> persistence -> retrieval/search -> export.

## Resilience, Time & Cancellation

- **Polly v8 via `Microsoft.Extensions.Http.Resilience`:** Register typed or named `HttpClient` instances through `IHttpClientFactory` and configure `Microsoft.Extensions.Resilience` / `Microsoft.Extensions.Http.Resilience` (Polly v8). Do not add the deprecated `Microsoft.Extensions.Http.Polly` package to new code. Design retries only for transient, idempotent operations.
- **Testable time & randomness:** Inject `TimeProvider` instead of calling `DateTimeOffset.UtcNow` / `DateTime.UtcNow` directly in business logic; use `RandomNumberGenerator` for security-sensitive randomness.
- **End-to-end `CancellationToken`:** Propagate `CancellationToken` through controllers/endpoints, application services, EF Core queries/saves, outbound `HttpClient` calls, and `BackgroundService` loops.

## Supply Chain & Deterministic Builds

- **Lock files in CI:** Keep `packages.lock.json` committed for deployable applications and restore with `dotnet restore --locked-mode` in CI (followed by `--no-restore` on build/test).
- **NuGetAudit:** Keep `NuGetAudit` enabled at repository level (including transitive dependencies) with an explicit severity policy. Suppress an advisory only with documented reachability evidence, owner, and review date.

## Data Protection Across Replicas

- **Shared key ring:** Persist ASP.NET Core Data Protection keys (`PersistKeysTo...`) to a protected shared store with a stable `SetApplicationName(...)` whenever multiple replicas validate the same auth cookies or antiforgery tokens.
- **Protect keys & minimize cookies:** Encrypt the key ring at rest (`ProtectKeysWith...`) and restrict access policy. Do not store unnecessary OIDC access or refresh tokens inside authentication cookies.

## Integration Testing & Concurrency Invariants

- **`WebApplicationFactory` integration tests:** Use `WebApplicationFactory<Program>` to test routing, middleware ordering, filters, authentication/authorization, wrong-owner/tenant isolation, serialization, RFC 9457 `ProblemDetails`, cancellation/timeouts, and dependency failures. Replace external services with controlled fakes or disposable test containers.
- **Atomic compare-and-swap & outbox invariants:**
  - Make state transitions and balance/quota updates atomic at the resource boundary using conditional updates (compare-and-swap with checked row count), effective locks, or database constraints within a single unit of work.
  - Bind tenant and actor to verified request/job context on every operation and fail closed when context or policy data is absent.
  - Deduplicate retried effects in the same transaction as the mutation, consume one-time tokens atomically, and use an outbox or idempotent calls with reconciliation for external side effects.
