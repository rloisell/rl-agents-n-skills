---
name: local-dev
description: Sets up, runs, and troubleshoots the local development environment — dev-ctl consolidated multi-project manager, podman-compose multi-container stack, EF Core migrations, MariaDB socket and TCP connection patterns, port conventions, admin token seeding, and test execution. Use when setting up local dev, scaffolding a .dev-env for a new project, running migrations, debugging connection errors, or troubleshooting the local stack.
tools: Read, Grep, Glob
user-invocable: false
metadata:
  author: Ryan Loiselle
  version: "2.0"
---

# Local Development Agent

Helps set up, run, and troubleshoot the local development environment.

---

## dev-ctl — Consolidated Multi-Project Manager

All projects on this machine are managed by a single command: `dev-ctl`.

```
~/dev-tools/
  dev-ctl                 ← single control plane for all projects

~/Documents/developer/
  <project>/.dev-env      ← each project declares its services here
```

`dev-ctl` auto-discovers every `*/.dev-env` file under `~/Documents/developer/` —
no registration step needed. Shared services (e.g. MariaDB) are started once and
deduplicated across projects.

### Commands

```bash
dev-ctl status                   # health table — all projects at once
dev-ctl start                    # start all projects
dev-ctl start <project-id>       # start one project (e.g. hnw, dscmod, dsc)
dev-ctl stop  <project-id>       # stop non-shared services for a project
dev-ctl monitor                  # health check + macOS notification (used by cron)
dev-ctl install-monitor          # cron: every 5 min health check + alert
dev-ctl uninstall-monitor        # remove cron job
dev-ctl logs  [project|svc]      # tail service logs
```

### Monitor / alerting

```bash
dev-ctl install-monitor
# Registers: */5 * * * * dev-ctl monitor   in crontab
# Alert:     macOS notification (sound: Basso) when any service goes down or recovers
# Log:       /tmp/dev-ctl/monitor.log
```

### Adding a new project

1. Create `<project-root>/.dev-env` (copy the template from `rl-project-template/scripts/dev-env.template`)
2. Set `DEV_PROJECT_ID`, `DEV_PROJECT_LABEL`, `DEV_SERVICES`
3. For each service `FOO`, define:
   - `DEV_SVC_FOO_LABEL`   — display name
   - `DEV_SVC_FOO_CHECK`   — bash snippet returning 0 if up
   - `DEV_SVC_FOO_START`   — bash snippet to start the service
   - `DEV_SVC_FOO_STOP`    — bash snippet to stop (optional)
   - `DEV_SVC_FOO_SHARED`  — `"true"` if shared across projects (e.g. MariaDB)
   - `DEV_SVC_FOO_SETUP`   — per-project init after service is up (e.g. CREATE DATABASE)
   - `DEV_SVC_FOO_TIMEOUT` — seconds to wait for start (default 30)
4. Run `dev-ctl status` — the project appears immediately

### Thin project-level wrappers (optional)

Projects may keep convenience scripts in `scripts/` that delegate to `dev-ctl`:

```bash
# scripts/dev-start.sh
exec "$HOME/dev-tools/dev-ctl" start <project-id>
```

---

---

## Standard Port Conventions

| Service | Local Port | URL |
|---------|-----------|-----|
| .NET API (template default) | 5005 | `http://localhost:5005` |
| React/Vite dev server | 5173 | `http://localhost:5173` |
| MariaDB | 3306 | TCP or socket |
| podman-compose API | 8080 | `http://localhost:8080` |

> Check `src/<Project>.Api/Properties/launchSettings.json` for the actual API port.
> The CORS policy in `appsettings.Development.json` must include the Vite port.

---

## Running Native (without podman-compose)

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

---

## Running With podman-compose

```bash
podman-compose up --build   # build and start all services
podman-compose up           # start without rebuild
podman-compose down         # stop, keep volumes
podman-compose down -v      # stop and wipe volumes (clean slate)
podman-compose logs -f api  # tail API logs
```

`podman-compose.yml` lives in `containerization/`. Mirrors OpenShift layout:
API on 8080, MariaDB on 3306, healthchecks on all services.

---

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

### MariaDB Socket Auth (macOS Homebrew)

Homebrew MariaDB defaults to socket auth for root. Create a password-auth dev user:

```sql
-- Run as root: mariadb --skip-ssl
CREATE DATABASE <project>_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER '<user>'@'localhost' IDENTIFIED BY '<password>';
GRANT ALL PRIVILEGES ON <project>_dev.* TO '<user>'@'localhost';
FLUSH PRIVILEGES;
```

Use `Server=localhost;Port=3306;` (TCP) in the connection string with this user.

---

## EF Core Migrations

```bash
# Add migration
dotnet ef migrations add <MigrationName> \
  --project src/<Project>.Api --startup-project src/<Project>.Api

# Apply
dotnet ef database update \
  --project src/<Project>.Api --startup-project src/<Project>.Api

# List status
dotnet ef migrations list --project src/<Project>.Api

# Rollback
dotnet ef database update <PreviousMigrationName> --project src/<Project>.Api

# Remove last un-applied migration file
dotnet ef migrations remove --project src/<Project>.Api

# Wipe schema (dangerous)
dotnet ef database update 0 --project src/<Project>.Api
```

### Naming Conventions

| Scenario | Migration Name |
|----------|---------------|
| Initial schema | `InitialCreate` |
| Add table | `Add<Entity>Table` |
| Add column | `Add<Column>To<Table>` |
| Remove column | `Remove<Column>From<Table>` |
| Refactor | `<Description>Refactor` |

### Startup Auto-Migrate

```csharp
// Program.cs — always Migrate(), never EnsureCreated()
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();
    db.Database.Migrate();
}
```

---

## Running Tests

```bash
dotnet test                            # all tests
dotnet test tests/<Project>.Tests/    # specific project
dotnet test --verbosity normal         # with output
cd src/<Project>.WebClient && npm test # Vitest frontend tests
```

---

## Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Auth plugin 'caching_sha2_password' not supported` | Wrong MariaDB auth plugin | Add `AllowPublicKeyRetrieval=true;` or recreate user with `mysql_native_password` |
| `Unable to connect to database` | MariaDB not running | `brew services start mariadb` or `podman-compose up db` |
| `Migration has already been applied` | DB ahead of code | Reset: `dotnet ef database update 0` then `update` |
| CORS error in browser | Vite port not in allowlist | Add `http://localhost:<vite-port>` to `Cors:AllowedOrigins` |
| `EACCES` on `npm run dev` | Port 5173 in use | `lsof -ti:5173 \| xargs kill` |
| `dotnet run` fails — port bound | API port in use | `lsof -ti:5005 \| xargs kill` |
| `Model backing the context has changed` | Unapplied migration | `dotnet ef database update` |

---

## LOCAL_DEV_KNOWLEDGE

> Append new local dev discoveries here.
> Format: `YYYY-MM-DD: <discovery>`

- 2026-02-27: [HelloNetworkWorld] macOS Homebrew MariaDB uses socket auth for root. Created dedicated `hnw_dev` DB with password-auth user. Connection string: `Server=localhost;Port=3306;Database=hnw_dev;User=hnw_user;Password=...;`
- 2026-02-27: [HelloNetworkWorld] API on port 5200, Vite on 5175 (non-default). After EF Core InitialCreate migration, full CRUD verified via curl. Quartz.NET background scheduler starts on API boot.
- 2026-04-13: dev-ctl consolidated multi-project dev manager introduced. All projects declare a .dev-env; shared services (MariaDB) start once and run per-project DB setup. crontab monitors every 5 min with macOS notifications. Source: ~/dev-tools/dev-ctl. macOS launchd TCC blocks scripts in ~/Documents — crontab used instead.
