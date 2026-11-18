## Contents

- [Provider Setup](#provider-setup)
- [Entity Conventions & DbContext](#entity-conventions--dbcontext)
- [Linux LINQ ReadOnlySpan Gotcha](#linux-linq-readonlyspan-gotcha)
- [Service Layer Pattern](#service-layer-pattern)
- [Domain Exceptions (RFC 7807 ProblemDetails)](#domain-exceptions-rfc-7807-problemdetails)
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

## Service Layer Pattern

Controllers are thin — no business logic or direct `DbContext` in controllers. Place all logic in scoped services behind interfaces using primary constructors, and use EF Core parameterised queries only (never `FromSqlRaw` with user input).

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

## Domain Exceptions (RFC 7807 ProblemDetails)

A global exception handler maps domain exceptions to RFC 7807 `ProblemDetails`:

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
