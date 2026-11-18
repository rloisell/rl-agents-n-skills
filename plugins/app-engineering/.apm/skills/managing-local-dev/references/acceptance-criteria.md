# Acceptance Criteria — Managing Local Dev

Observable pass/fail criteria for verifying local development environment setup, MariaDB connectivity, and stack health.

## Pass/Fail Criteria

| Area | Pass Criteria | Fail Criteria |
|---|---|---|
| **Config & Secret Hygiene** | `appsettings.Development.json` is copied locally from `appsettings.Development.json.example` and remains gitignored (`git status` clean). | `appsettings.Development.json` or `.dev-env` secrets committed to git. |
| **CORS & Port Alignment** | `Cors:AllowedOrigins` in `appsettings.Development.json` includes the active Vite dev server origin/port (default `http://localhost:5173`). | Browser CORS errors due to mismatched Vite port or missing origin entry. |
| **MariaDB TCP Auth** | A dedicated `<project>_dev` database and password-authenticated TCP user (`Server=localhost;Port=3306;`) are provisioned and reachable. | Reliance on macOS Homebrew `root` socket auth or `caching_sha2_password` connection failures. |
| **Stack & Migration Scope** | Stack starts cleanly via `dev-ctl up` or `podman-compose up -d`; EF Core migrations defer to `building-dotnet-apis` (`dotnet ef`). | Port collisions, unhealthy containers, or duplicated migration scripts in local-dev docs/wrappers. |
| **Health & Test Verification** | `dev-ctl status` (or `podman-compose ps`) shows API, frontend, and MariaDB healthy; `dotnet test` and `npm test` exit 0. | Unhealthy/exited services or failing local unit/integration tests. |
