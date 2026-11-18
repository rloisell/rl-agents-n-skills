# Podman & MariaDB Setup

## Standard Port Conventions

| Service | Local Port | URL |
|---|---|---|
| .NET API (template default) | 5005 | `http://localhost:5005` |
| React/Vite dev server | 5173 | `http://localhost:5173` |
| MariaDB | 3306 | TCP or socket |
| `podman-compose` API | 8080 | `http://localhost:8080` |

Check `src/<Project>.Api/Properties/launchSettings.json` for the actual API port. The CORS policy in `appsettings.Development.json` must include the Vite port.

## Running Native (without `podman-compose`)

```bash
# API
cd src/<Project>.Api
dotnet run        # or: dotnet watch run (file-change reload)

# Frontend
cd src/<Project>.WebClient
npm run dev       # Vite proxies /api/* to the API port

# MariaDB (macOS Homebrew)
brew services start mariadb
```

## Running With `podman-compose`

```bash
podman-compose up --build   # build and start all services
podman-compose up           # start without rebuild
podman-compose down         # stop, keep volumes
podman-compose down -v      # stop and wipe volumes (clean slate)
podman-compose logs -f api  # tail API logs
```

`podman-compose.yml` lives in `containerization/` and mirrors the OpenShift layout: API on 8080, MariaDB on 3306, healthchecks on all services.

## Environment Configuration

```bash
cp src/<Project>.Api/appsettings.Development.json.example \
   src/<Project>.Api/appsettings.Development.json
```

`.Development.json` is in `.gitignore` — never commit it.

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=localhost;Port=3306;Database=<project>_dev;User=<user>;Password=<pass>;"
  },
  "Authentication": { "BypassAuth": true },
  "Admin": { "Token": "local-admin-token" }
}
```

## MariaDB Socket Auth (macOS Homebrew)

Homebrew MariaDB defaults to socket auth for `root`. Create a password-auth dev user:

```sql
-- Run as root: mariadb --skip-ssl
CREATE DATABASE <project>_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER '<user>'@'localhost' IDENTIFIED BY '<password>';
GRANT ALL PRIVILEGES ON <project>_dev.* TO '<user>'@'localhost';
FLUSH PRIVILEGES;
```

Use `Server=localhost;Port=3306;` (TCP) in the connection string with this user.

## EF Core Migrations

For `dotnet ef` migration commands, naming conventions, and startup `db.Database.Migrate()`, refer to the `building-dotnet-apis` skill (`ef-core-migrations.md`).

## Running Tests

```bash
dotnet test                            # all tests
dotnet test tests/<Project>.Tests/     # specific project
dotnet test --verbosity normal         # with output
cd src/<Project>.WebClient && npm test # Vitest frontend tests
```
