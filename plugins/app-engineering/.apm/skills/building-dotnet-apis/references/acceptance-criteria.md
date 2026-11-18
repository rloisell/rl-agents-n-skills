# Acceptance Criteria — Building .NET APIs

Observable pass/fail criteria for verifying .NET 10 EF Core (Pomelo MariaDB) data layers and BC Gov REST API compliance.

## Pass/Fail Criteria

| Area | Pass Criteria | Fail Criteria |
|---|---|---|
| **DbContext & Startup** | `ApplicationDbContext` uses `UseMySql(..., ServerVersion.AutoDetect(connStr))` and startup calls `db.Database.Migrate()`. | `EnsureCreated()` is called, or `ServerVersion` is omitted/hardcoded inconsistently. |
| **Query Safety & Linux LINQ** | Queries use parameterised EF Core LINQ; collections passed to `.Contains()` are typed as `List<string>`. | Raw user input interpolated into `FromSqlRaw`, or `string[]` passed to `.Contains()` (triggers Linux `ReadOnlySpan` bug). |
| **Service Layer & Errors** | Controllers are thin; business logic and `DbContext` live in scoped services (primary constructors behind interfaces); domain exceptions map to RFC 7807 `ProblemDetails`. | `DbContext` injected directly into controllers, or unhandled exceptions leaking stack traces. |
| **Migrations** | Migrations are added via `dotnet ef migrations add <Name>` and previewed with `dotnet ef migrations script --idempotent` before applying. | Manual ad-hoc schema edits or unpreviewed destructive migrations. |
| **BC Gov REST Standard** | Public endpoints satisfy all 8 mandates: RESTful resource nouns, RFC 7231 verbs, single-resource URLs, versioned routes, `metadata` (`createdAt` ISO 8601 + `license`), and standard HTTP error statuses. | Unversioned public routes, verbs in URLs, missing `metadata` fields, or non-standard error payloads. |
| **Build & Test Verification** | `dotnet build`, `dotnet test` (EF Core in-memory provider), and `dotnet ef migrations script --idempotent` exit 0. | Compilation errors, failing unit tests, or migration script generation errors. |
