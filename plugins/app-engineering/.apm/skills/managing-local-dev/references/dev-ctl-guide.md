# `dev-ctl` — Consolidated Multi-Project Manager

All local projects can be managed by a single command: `dev-ctl`.

```text
<dev-tools>/
  dev-ctl                 # single control plane for all projects

<workspace>/
  <project>/.dev-env      # each project declares its services here
```

`dev-ctl` auto-discovers every `*/.dev-env` file under `<workspace>/` — no registration step needed. Shared services (e.g. MariaDB) are started once and deduplicated across projects.

## Commands

```bash
dev-ctl status                   # health table — all projects at once
dev-ctl start                    # start all projects
dev-ctl start <project-id>       # start one project (e.g. app-a, app-b)
dev-ctl stop  <project-id>       # stop non-shared services for a project
dev-ctl monitor                  # health check + macOS notification (used by cron)
dev-ctl install-monitor          # cron: every 5 min health check + alert
dev-ctl uninstall-monitor        # remove cron job
dev-ctl logs  [project|svc]      # tail service logs
```

## Monitor / Alerting

```bash
dev-ctl install-monitor
# Registers: */5 * * * * dev-ctl monitor   in crontab
# Alert:     macOS notification (sound: Basso) when any service goes down or recovers
# Log:       /tmp/dev-ctl/monitor.log
```

## Adding a New Project

1. Create `<project-root>/.dev-env` (copy the template from `<project-template>/scripts/dev-env.template`).
2. Set `DEV_PROJECT_ID`, `DEV_PROJECT_LABEL`, and `DEV_SERVICES`.
3. For each service `FOO`, define:
   - `DEV_SVC_FOO_LABEL`   — display name
   - `DEV_SVC_FOO_CHECK`   — bash snippet returning 0 if up
   - `DEV_SVC_FOO_START`   — bash snippet to start the service
   - `DEV_SVC_FOO_STOP`    — bash snippet to stop (optional)
   - `DEV_SVC_FOO_SHARED`  — `"true"` if shared across projects (e.g. MariaDB)
   - `DEV_SVC_FOO_SETUP`   — per-project init after service is up (e.g. `CREATE DATABASE`)
   - `DEV_SVC_FOO_TIMEOUT` — seconds to wait for start (default 30)
4. Run `dev-ctl status` — the project appears immediately.

## Thin Project-Level Wrappers (Optional)

Projects may keep convenience scripts in `scripts/` that delegate to `dev-ctl`:

```bash
# scripts/dev-start.sh
exec "<dev-tools>/dev-ctl" start <project-id>
```
