# Troubleshooting & Local Dev Knowledge

## Common Issues

| Symptom | Cause | Fix |
|---|---|---|
| `Auth plugin 'caching_sha2_password' not supported` | Wrong MariaDB auth plugin | Add `AllowPublicKeyRetrieval=true;` or recreate user with `mysql_native_password` |
| `Unable to connect to database` | MariaDB not running | `brew services start mariadb` or `podman-compose up db` |
| `Migration has already been applied` | DB ahead of code | Reset: `dotnet ef database update 0` then `update` |
| CORS error in browser | Vite port not in allowlist | Add `http://localhost:<vite-port>` to `Cors:AllowedOrigins` |
| `EACCES` on `npm run dev` | Port 5173 in use | `lsof -ti:5173 \| xargs kill` |
| `dotnet run` fails — port bound | API port in use | `lsof -ti:5005 \| xargs kill` |
| `Model backing the context has changed` | Unapplied migration | `dotnet ef database update` |

## Local Dev Knowledge

- **2026-02-27 (`[engagement]`):** macOS Homebrew MariaDB uses socket auth for `root`. Created dedicated `<project>_dev` DB with password-auth user. Connection string: `Server=localhost;Port=3306;Database=<project>_dev;User=<project>_user;Password=...;`.
- **2026-02-27 (`[engagement]`):** API on port 5200, Vite on 5175 (non-default). After EF Core `InitialCreate` migration, full CRUD verified via `curl`. Quartz.NET background scheduler starts on API boot.
- **2026-04-13:** `dev-ctl` consolidated multi-project dev manager introduced. All projects declare a `.dev-env`; shared services (MariaDB) start once and run per-project DB setup. `crontab` monitors every 5 min with macOS notifications. Source: `<dev-tools>/dev-ctl`. macOS `launchd` TCC blocks scripts in `~/Documents` — `crontab` used instead.
