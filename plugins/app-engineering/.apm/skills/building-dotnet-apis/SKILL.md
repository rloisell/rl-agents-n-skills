---
name: building-dotnet-apis
description: Builds BC Government .NET 10 APIs with Entity Framework Core (Pomelo MariaDB) and enforces the BC Gov REST API Development Standard. Use when setting up DbContext, writing migrations, structuring service layers, diagnosing Linux LINQ issues, or designing RESTful endpoints.
---

# Building .NET APIs

Guides EF Core data-layer implementation with Pomelo MariaDB and conformance to the BC Government REST API Development Standard.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- **Startup migrations:** Always call `db.Database.Migrate()` on startup; never call `EnsureCreated()`.
- **Parameterised queries:** Use EF Core LINQ queries; never pass raw user input to `FromSqlRaw`.
- **Service layer:** Keep controllers thin; place business logic and `DbContext` access in scoped services using primary constructors behind interfaces.
- **Linux LINQ compatibility:** Always declare collections for `.Contains()` as `List<string>`, never `string[]` (avoids the Linux `ReadOnlySpan` runtime overload bug).
- **REST API compliance:** Public APIs must follow all 8 BC Gov REST API mandates (RESTful resources, RFC 7231 verbs, single-resource URLs, response metadata with ISO 8601 timestamp + licence, HTTP status errors, and versioning).

## Quick start

1. Register `ApplicationDbContext` with `UseMySql(..., ServerVersion.AutoDetect(connStr))` and call `db.Database.Migrate()` during startup.
2. Add a migration with `dotnet ef migrations add InitialCreate`, preview with `--idempotent`, and expose versioned REST endpoints.

## Workflow

1. **Configure EF Core & Service Layer:** Set up `ApplicationDbContext` with `UseMySql` and `ServerVersion.AutoDetect`, define entities, and implement scoped services mapping domain exceptions to RFC 7807 `ProblemDetails`. See [ef-core-pomelo-patterns.md](references/ef-core-pomelo-patterns.md).
2. **Manage Migrations:** Add, preview (`--idempotent`), and apply migrations using `dotnet ef`, and configure startup `Migrate()`. See [ef-core-migrations.md](references/ef-core-migrations.md).
3. **Design REST Endpoints:** Validate routes, HTTP verbs, content negotiation, metadata wrappers, error responses, and versioning against the standard. See [bc-gov-rest-api-standard.md](references/bc-gov-rest-api-standard.md).
4. **Check Known Pitfalls:** Review project discoveries and MariaDB/Quartz notes in [ef-knowledge.md](references/ef-knowledge.md).

## Verification

- Build and run unit tests with the EF Core in-memory provider (`dotnet test`).
- Preview generated SQL before applying schema changes (`dotnet ef migrations script --idempotent`).
- Confirm all public endpoints return versioned routes, proper HTTP status codes, and `metadata` (`createdAt` ISO 8601 + `license`).

## References

- [EF Core & Pomelo Patterns](references/ef-core-pomelo-patterns.md) — provider setup, primary constructors, Linux LINQ `List<string>` rule, service layer, domain exceptions, and in-memory testing.
- [EF Core Migrations](references/ef-core-migrations.md) — `dotnet ef` commands, naming conventions, and startup `Migrate()` pattern.
- [BC Gov REST API Standard](references/bc-gov-rest-api-standard.md) — 8 mandated minimums, verb conformance, metadata template, anti-patterns, and OCIO compliance links.
- [EF Knowledge](references/ef-knowledge.md) — recorded EF Core and MariaDB discoveries.
- [.NET CI Automation](references/dotnet-ci-automation.md) — GitHub Actions CI patterns for vulnerability scanning, `dotnet format`, EF SQL script artifacts, merged Coverlet gating, gRPC `protoc` builds, and NuGet pack/deploy.
- [Acceptance Criteria](references/acceptance-criteria.md) — observable pass/fail criteria for EF Core, migrations, and REST API compliance.
