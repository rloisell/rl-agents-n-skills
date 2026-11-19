## Contents

- [Provider Setup](#provider-setup)
- [Entity Conventions & DbContext](#entity-conventions--dbcontext)
- [Linux LINQ ReadOnlySpan Gotcha](#linux-linq-readonlyspan-gotcha)
- [Service Layer & Persistence Boundaries](#service-layer--persistence-boundaries)
- [Startup, Middleware Ordering & Resilience](#startup-middleware-ordering--resilience)
- [Domain Exceptions (RFC 9457 ProblemDetails)](#domain-exceptions-rfc-9457-problemdetails)
- [Testing](#testing)

# EF Core & Pomelo MariaDB Patterns

## Provider Setup

Required NuGet packages:

- `Microsoft.EntityFrameworkCore`
- `Pomelo.EntityFrameworkCore.MySql`
- `Microsoft.EntityFrameworkCore.Design` (local dev only; exclude from runtime image)

```json
// appsettings.json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=localhost;Port=3306;Database=<project>_dev;User=<user>;Password=<pass>;AllowPublicKeyRetrieval=true;"
  }
}
```

```csharp
// Program.cs
builder.Services.AddDbContext<ApplicationDbContext>(options =>
    options.UseMySql(
        builder.Configuration.GetConnectionString("DefaultConnection"),
        ServerVersion.AutoDetect(builder.Configuration.GetConnectionString("DefaultConnection")),
        mySqlOptions => mySqlOptions.MigrationsAssembly("<Project>.Api")
    )
);
```

## Entity Conventions & DbContext

```csharp
public class MyEntity
{
    public Guid Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
    public DateTime? UpdatedAt { get; set; }
}
```

Use primary constructors for `DbContext`:

```csharp
public class ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
    : DbContext(options)
{
    public DbSet<MyEntity> MyEntities => Set<MyEntity>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);
    }
}
```

## Linux LINQ ReadOnlySpan Gotcha

**Silent bug on Linux that does not appear on macOS development.**

```csharp
// BROKEN on Linux — compiles, throws at EF Core runtime
var results = db.Entities
    .Where(e => new[] { "active", "pending" }.Contains(e.Status))
    .ToList();

// CORRECT — declare as List<string> explicitly
var statuses = new List<string> { "active", "pending" };
var results = db.Entities
    .Where(e => statuses.Contains(e.Status))
    .ToList();
```

**Rule:** Always use `List<string>` (not `string[]`) for collections used in LINQ `.Contains()` against EF Core queries.

## Service Layer & Persistence Boundaries

Controllers are thin — no business logic or direct `DbContext` in controllers. Place all logic in scoped services behind interfaces using primary constructors, and use EF Core parameterised queries only (never `FromSqlRaw` with user input).

- **Avoid generic repository wrappers over EF Core:** `DbContext` and `DbSet<T>` already implement unit-of-work and repository semantics. Adding a generic `IRepository<T>` wrapper hides projection (`Select`), `AsNoTracking()`, explicit transactions, and batching without adding domain policy. Put use-case-specific queries directly in scoped services or focused query objects.

```csharp
// IMyService.cs
public interface IMyService
{
    Task<MyDto[]> GetAllAsync();
    Task<MyDto> GetByIdAsync(Guid id);       // throws NotFoundException
    Task<MyDto> CreateAsync(CreateRequest r);
    Task<MyDto> UpdateAsync(Guid id, UpdateRequest r);
    Task DeleteAsync(Guid id);
}

// MyService.cs
public class MyService(ApplicationDbContext db) : IMyService
{
    // returns all entities sorted by name
    public async Task<MyDto[]> GetAllAsync() =>
        await db.MyEntities
            .OrderBy(e => e.Name)
            .Select(e => new MyDto { Id = e.Id, Name = e.Name })
            .ToArrayAsync();

    // throws NotFoundException if not found
    public async Task<MyDto> GetByIdAsync(Guid id) =>
        await db.MyEntities
            .Where(e => e.Id == id)
            .Select(e => new MyDto { Id = e.Id, Name = e.Name })
            .FirstOrDefaultAsync()
        ?? throw new NotFoundException($"MyEntity {id} not found");
}

// Program.cs registration
builder.Services.AddScoped<IMyService, MyService>();
```

## Startup, Middleware Ordering & Resilience

- **Startup Options validation:** Bind cohesive settings to strongly typed options classes and validate at startup (`AddOptions<T>().BindConfiguration(...).ValidateDataAnnotations().ValidateOnStart()` or `IValidateOptions<T>`) so missing issuer, audience, allowed origins, or external endpoints fail fast outside development.
- **Polly v8 outbound HTTP resilience:** Register typed/named `HttpClient` instances via `IHttpClientFactory` and use `Microsoft.Extensions.Resilience` / `Microsoft.Extensions.Http.Resilience` (Polly v8) instead of the deprecated `Microsoft.Extensions.Http.Polly`. Design retries only for transient, idempotent operations.
- **API versioning:** For externally consumed APIs requiring framework versioning and versioned OpenAPI, use the maintained `Asp.Versioning` family (`Asp.Versioning.Http` / `Asp.Versioning.Mvc`) instead of legacy `Microsoft.AspNetCore.Mvc.Versioning`.
- **Explicit `Program.cs` middleware ordering:** Keep ordering-sensitive middleware visible in `Program.cs`:
  1. `UseForwardedHeaders()` (configured with explicit `KnownProxies`/`KnownNetworks`; never clear trust lists just to make redirects work)
  2. Exception handling (`UseExceptionHandler()` / `UseStatusCodePages()`) and security headers / HSTS / HTTPS redirection
  3. `UseRouting()` (before rate limiting and auth when endpoint metadata drives those policies)
  4. `UseRateLimiter()` and CORS (`UseCors(...)`)
  5. `UseAuthentication()` -> `UseAuthorization()`
  6. Endpoints (`MapControllers()`, `MapGroup(...)`, health endpoints)

## Domain Exceptions (RFC 9457 ProblemDetails)

A global exception handler (`IExceptionHandler` + `AddProblemDetails()`) maps domain exceptions to **RFC 9457** `ProblemDetails` (superseding RFC 7807):

| Exception | HTTP Status | Use when |
|---|---|---|
| `NotFoundException` | 404 | Entity not found |
| `ForbiddenException` | 403 | Requester doesn't own item and isn't Admin/Manager |
| `BadRequestException` | 400 | Invalid input that passed model validation |
| `UnauthorizedException` | 401 | No valid identity in token |

## Testing

Use the in-memory database provider for unit tests rather than real MariaDB for CI portability:

```csharp
services.AddDbContext<ApplicationDbContext>(o =>
    o.UseInMemoryDatabase("TestDb_" + Guid.NewGuid()));
```
