# app-engineering Plugin

## Purpose

BC Gov .NET 10, EF Core, React, Design System, DIAM/OIDC IAM, observability, and local development.

## Plugin Components

APM and Claude Code auto-discover primitives under `.apm/`.

### Skills

| Skill | Description |
|---|---|
| [`building-dotnet-apis`](.apm/skills/building-dotnet-apis/SKILL.md) | .NET 10 APIs with EF Core (Pomelo MariaDB), migrations, service-layer patterns, and BC Gov REST API Development Standard compliance. |
| [`building-bc-gov-web-apps`](.apm/skills/building-bc-gov-web-apps/SKILL.md) | React/Vite app wiring, DIAM/Common SSO OIDC PKCE, and .NET JWT validation layered on top of [`richfrem/bc-gov-design-system`](https://github.com/richfrem/bc-gov-design-system). |
| [`instrumenting-observability`](.apm/skills/instrumenting-observability/SKILL.md) | Serilog JSON logging, health checks, Prometheus metrics, OpenTelemetry tracing, and PII-in-logs auditing. |
| [`managing-local-dev`](.apm/skills/managing-local-dev/SKILL.md) | Local development with `dev-ctl`, `podman-compose`, native runners, MariaDB TCP setup, and troubleshooting. |

### Sub-Agents

None.

### Hooks

None.

## Directory Structure

```text
app-engineering/
├── .apm/
│   └── skills/
│       ├── building-dotnet-apis/
│       ├── building-bc-gov-web-apps/
│       ├── instrumenting-observability/
│       └── managing-local-dev/
├── .claude-plugin/
│   └── plugin.json
├── apm.yml
└── README.md
```
