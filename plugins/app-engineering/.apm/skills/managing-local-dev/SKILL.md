---
name: managing-local-dev
description: Manages local development environments for BC Gov .NET, React, and MariaDB stacks using dev-ctl, podman-compose, native runners, and MariaDB password-auth setup. Use when setting up local dev, scaffolding a .dev-env, starting or stopping local stacks, running tests, or troubleshooting database and port errors.
---

# Managing Local Dev

Sets up, runs, and troubleshoots local development environments across native, `dev-ctl`, and `podman-compose` workflows.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- **Never commit `.Development.json`:** Copy `appsettings.Development.json.example` to `appsettings.Development.json` locally and keep it gitignored.
- **CORS matches Vite port:** Ensure `Cors:AllowedOrigins` in `appsettings.Development.json` includes the active Vite dev server port (default `5173`).
- **Password-auth dev user for MariaDB:** macOS Homebrew MariaDB defaults to socket auth for `root`; create a dedicated `<project>_dev` database and password-authenticated user for TCP `Server=localhost;Port=3306;`.
- **EF Core migrations:** Do not duplicate migration steps here — use the `building-dotnet-apis` skill (`ef-core-migrations.md`) for `dotnet ef` commands, naming conventions, and startup `Migrate()`.

## Quick start

1. Copy `appsettings.Development.json.example` to `appsettings.Development.json` and verify `Cors:AllowedOrigins` matches your Vite port.
2. Start the stack with `dev-ctl up` or `podman-compose up -d`, then check health via `dev-ctl status`.

## Workflow

1. **Manage Multi-Project Stacks (`dev-ctl`):** Check status, start/stop services, tail logs, or scaffold a new `.dev-env` file. See [dev-ctl-guide.md](references/dev-ctl-guide.md).
2. **Run Native or `podman-compose` + MariaDB:** Follow port conventions, configure `appsettings.Development.json`, provision MariaDB TCP users, and run `dotnet test` / `npm test`. See [podman-and-mariadb-setup.md](references/podman-and-mariadb-setup.md).
3. **Troubleshoot Issues:** Resolve `caching_sha2_password`, port conflicts, CORS errors, and migration mismatches. See [troubleshooting-and-knowledge.md](references/troubleshooting-and-knowledge.md).

## Verification

- Run `dev-ctl status` (or `podman-compose ps`) to confirm API, frontend, and MariaDB are healthy.
- Run `dotnet test` and `npm test` in the web client to verify tests pass locally.

## References

- [dev-ctl Guide](references/dev-ctl-guide.md) — `dev-ctl` commands, cron monitor, `.dev-env` scaffolding, and wrapper scripts.
- [Podman & MariaDB Setup](references/podman-and-mariadb-setup.md) — port conventions, native vs `podman-compose`, `.Development.json`, MariaDB user setup, and test commands.
- [Troubleshooting & Knowledge](references/troubleshooting-and-knowledge.md) — common local-dev issues and recorded environment discoveries.
- [Acceptance Criteria](references/acceptance-criteria.md) — observable pass/fail criteria for local stack, MariaDB auth, and test verification.
