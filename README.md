# rl-agents-n-skills

Domain-organized [APM](https://github.com/microsoft/apm)-native collection of reusable agent skills and justified subagents for software engineering, BC Gov .NET/React/OpenShift DevOps, security & networking, and systems infrastructure.

## Documentation

- [AGENTS.md](AGENTS.md) — Canonical repository rules, confidentiality baseline, coding standards, and subagent registry
- [CLAUDE.md](CLAUDE.md) — Thin bridge to `AGENTS.md`
- [architecture.md](architecture.md) — Future-state APM topology, plugins, skills, references, and subagents
- [install.md](install.md) — APM installation, target harnesses, update, and troubleshooting guide
- [migration-map.md](migration-map.md) — Transition guide: legacy 41 skills & 24 agents → new plugin paths
- [docs/SKILL-STRUCTURE-STANDARD.md](docs/SKILL-STRUCTURE-STANDARD.md) — Agent Skills Open Standard & `authoring-skills` contract

## Domain Plugins (`plugins/`)

| Plugin | Scope | Skills | Subagents |
|---|---|---|---|
| [dev-workflow](plugins/dev-workflow/README.md) | Sessions, GitHub PRs/rulesets, spec-driven dev, diagrams/versioning, skill evolution | 5 | 1 (`agent-evolution`) |
| [app-engineering](plugins/app-engineering/README.md) | .NET 10 / EF Core / REST APIs, BC Gov Design System, DIAM/OIDC IAM, observability, local dev | 4 | 0 |
| [openshift-devops](plugins/openshift-devops/README.md) | Emerald OpenShift, Option 2 CI/CD, migration & resilience analysis, CI/CD governance | 3 | 2 (`ocp-migration-analyst`, `ocp-resilience-analyst`) |
| [security-and-networking](plugins/security-and-networking/README.md) | AppSec, Vault, DB security, data lineage/STRA/PIA, Zero Trust, enterprise & OCP networking | 5 | 2 (`security-architect`, `container-network-analyst`) |
| [systems-infrastructure](plugins/systems-infrastructure/README.md) | Unix/RHEL/Solaris administration, DNS diagnostics, Cisco IOS/NX-OS networking | 2 | 0 |

## Quick Install

```bash
# Install all 5 domain plugins globally via APM
apm install https://github.com/rloisell/rl-agents-n-skills --global --target claude,copilot,codex,agy
```

See [install.md](install.md) for per-plugin installs, project-local installs, Windows flags, and troubleshooting.
