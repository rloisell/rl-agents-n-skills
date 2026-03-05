# rl-agents-n-skills

**Author**: Ryan Loiselle — Developer / Architect  
**AI tool**: GitHub Copilot — AI pair programmer / code generation  
**Updated**: March 2026

Shared **Claude Code plugin** containing persona agents, reusable skills, and
Claude Code subagents for rloisell BC Gov .NET/React/OpenShift projects.

This repo serves two toolchains from a single source:

| Toolchain | How it consumes this repo | Discovery path |
|-----------|--------------------------|----------------|
| **VS Code / GitHub Copilot** | Git submodule at `.github/agents/` | `.github/agents/*/SKILL.md` |
| **Claude Code** | Plugin via `.claude/settings.json` | `agents/` subagents in plugin root |

---

## Personas (12) — VS Code SKILL.md + Claude Code subagent

Each persona has two artefacts: a VS Code `SKILL.md` at the repo root (auto-discovered when
this repo is a submodule at `.github/agents/`) and a Claude Code subagent in `agents/`.

| Directory | Scope |
|-----------|-------|
| `session-workflow/` | Session startup/shutdown, AI file maintenance (WORKLOG/CHANGES/COMMANDS/COMMIT_INFO) |
| `github-workflow/` | Branch naming, PR lifecycle, CI diagnosis, gh CLI, rulesets |
| `diagram-generation/` | draw.io + PlantUML + Mermaid, 10-diagram UML suite, folder structure, export |
| `ci-cd-pipeline/` | 5-workflow pattern, ISB EA Option 2, image tags, yq GitOps, Trivy, failure triage |
| `local-dev/` | podman-compose, EF Core migration commands, MariaDB, port conventions, troubleshooting |
| `spec-kitty/` | Spec-first development, WP YAML format, spec.md/plan.md sections, validate-tasks |
| `ef-core/` | Pomelo/MariaDB patterns, migration workflow, startup Migrate(), Linux LINQ gotcha, service layer |
| `bc-gov-devops/` | Emerald OpenShift, Artifactory, Helm, health checks, Common SSO, oc commands, ArgoCD |
| `agent-evolution/` | Self-learning — monitors sessions, updates KNOWLEDGE sections, promotes shared skills |
| `security-architect/` | OWASP Top 10, SAST/DAST toolchain, input validation, audit logging, container security, STRA/PIA |
| `bc-gov-iam/` | DIAM/Keycloak OIDC PKCE, realm selection, React oidc-client-ts, token lifecycle, backchannel logout |
| `observability/` | Serilog structured logging, health checks, Prometheus pod annotations, OpenTelemetry .NET SDK |

---

## Shared Skills (5) — reusable reference libraries

| Directory | Consumed by |
|-----------|-------------|
| `ai-session-files/` | session-workflow, github-workflow |
| `git-conventions/` | session-workflow, github-workflow, ci-cd-pipeline |
| `bc-gov-emerald/` | bc-gov-devops, ci-cd-pipeline |
| `containerfile-standards/` | bc-gov-devops, ci-cd-pipeline |
| `vault-secrets/` | security-architect, bc-gov-devops, ci-cd-pipeline |

---

## Using in a project

### VS Code / GitHub Copilot

Add as a git submodule at `.github/agents/`:

```bash
git submodule add https://github.com/rloisell/rl-agents-n-skills.git .github/agents
git submodule update --init --recursive
```

VS Code auto-discovers all `SKILL.md` files under `.github/agents/`.

### Claude Code plugin

Reference the submodule path in `.claude/settings.json`:

```json
{
  "plugins": [".github/agents"]
}
```

Run subagents explicitly:
```bash
Use the security-architect subagent to review this file for vulnerabilities
```

### Updating to latest

```bash
cd .github/agents && git pull origin main && cd ../..
git add .github/agents
git commit -m "chore: update rl-agents-n-skills submodule"
```

---

## Project-specific agents

Project-specific Claude Code subagents belong in `.claude/agents/` within the
consuming project — not in this repo.

---

## Contributing

All changes go through PRs on `main`. After merging, consuming projects update
their submodule reference.

