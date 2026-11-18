# EF Core Migrations

## Migration Workflow

```bash
# Add migration
dotnet ef migrations add <MigrationName> --project src/<Project>.Api --startup-project src/<Project>.Api

# Apply locally
dotnet ef database update --project src/<Project>.Api --startup-project src/<Project>.Api

# Generate idempotent SQL preview
dotnet ef migrations script --idempotent --project src/<Project>.Api -o migrations-preview.sql

# List migration status
dotnet ef migrations list --project src/<Project>.Api

# Rollback to previous migration
dotnet ef database update <PreviousMigrationName> --project src/<Project>.Api

# Remove last un-applied migration file (does not touch DB)
dotnet ef migrations remove --project src/<Project>.Api

# Wipe schema (dangerous)
dotnet ef database update 0 --project src/<Project>.Api
```

## Naming Conventions

| Scenario | Name |
|---|---|
| Initial schema | `InitialCreate` |
| Add table | `Add<Entity>Table` |
| Add column | `Add<Column>To<Table>` |
| Remove column | `Remove<Column>From<Table>` |
| Add index | `Add<Field>IndexTo<Table>` |
| Refactor | `<Description>Refactor` |
| Seed change | `Seed<Entity>Data` |

## Startup Auto-Migrate

**ALWAYS `db.Database.Migrate()`. NEVER `EnsureCreated()`.**

`EnsureCreated()` creates the schema without the `__EFMigrationsHistory` table, permanently blocking future migrations on that database.

```csharp
// Program.cs — after app build, before app.Run()
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();
    db.Database.Migrate();
}
```
