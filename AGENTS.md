# AGENTS.md — rl-agents-n-skills

Canonical governance and repository instructions for `rl-agents-n-skills`. All consumer projects and domain plugins inherit these rules.

## Repository Layout

This repository is an [APM](https://github.com/microsoft/apm)-native multi-plugin collection organized into five organizational domains under `plugins/`:

| Plugin | Domain Scope |
|---|---|
| [dev-workflow](plugins/dev-workflow/README.md) | Session management, GitHub workflows, spec-driven dev, diagrams/versioning, skill evolution |
| [app-engineering](plugins/app-engineering/README.md) | .NET 10 / EF Core / REST APIs, BC Gov Design System, DIAM/OIDC IAM, observability, local dev |
| [openshift-devops](plugins/openshift-devops/README.md) | Emerald OpenShift, Option 2 CI/CD, migration & resilience analysis, CI/CD governance |
| [security-and-networking](plugins/security-and-networking/README.md) | AppSec, Vault, DB security, data lineage/STRA/PIA, Zero Trust, enterprise & OCP networking |
| [systems-infrastructure](plugins/systems-infrastructure/README.md) | Unix/RHEL/Solaris administration, DNS diagnostics, Cisco IOS/NX-OS networking |

See [architecture.md](architecture.md) for the consolidation map and [install.md](install.md) for APM installation.

## Companion APM Skills (Reuse, Don't Duplicate)

This workbench augments — and intentionally avoids duplicating — companion APM skill packages when installed globally alongside `rl-agents-n-skills`:

- **BC Gov Design System** ([`richfrem/bc-gov-design-system`](https://github.com/richfrem/bc-gov-design-system)): Canonical source for BC Sans, v5 design tokens, `@bcgov/*` components, Blazor/PPTX/SharePoint modes, and WCAG rules (`building-bc-gov-web-apps` layers React/Vite + OIDC/JWT on top).
- **BC Gov CROW** ([`bcgov/crow`](https://github.com/bcgov/crow), MIT): Complementary standalone agents/skills for brownfield architecture, legacy/API modernization, framework & dependency updates, Sonar scanning, and executive reporting (`rl-agents-n-skills` folds only non-duplicated Emerald/OpenShift/Option-2 CI/CD, HA, security, and .NET/UX gaps into existing skills).
- **General Harness & Authoring Skills** (e.g., `agent-plugins-skills` / global `~/.gemini/antigravity-cli/skills/`): Skill/plugin authoring, workflow orchestration, GitHub issue/worktree workflows, and memory skills live in the global harness rather than being duplicated here.

## Non-Negotiable Rules

### Confidentiality and Privacy

1. **No client or engagement details in public repos**: Never include real client, ministry, or program-area names, real OCP namespace IDs, real application/repo names, or engagement-specific findings in committed skill, reference, or doc files. Use generic placeholders (`<ns-prefix>-dev`, `<app-a>`, `<license-plate>`, `<org>/<analysis-repo>`, `[engagement]`).
2. **Generic knowledge entries**: Appended `KNOWLEDGE` entries MUST capture generalisable patterns, not engagement case reports.
3. **Private analysis repos**: Repositories holding live cluster captures, analysis reports, or client deliverables MUST be created as private (`gh repo create --private`).
4. **Omit when uncertain**: If unsure whether a detail is client-specific, omit it or replace it with a generic placeholder.

## Universal Coding Standards

- **Bash**: `set -euo pipefail`; use `local` for function variables.
- **Python**: Type hints on public functions; no bare `except:`.
- **YAML**: 2-space indent; quote strings with special characters.
- **Markdown**: ATX headings (`#`, `##`); fenced code blocks with language tags.
- **Secrets & Images**: Never hardcode secrets (use Vault / ESO / OCP Secrets); pin container images to `sha256` digests in non-dev environments (never `:latest` in prod).

## Subagent Registry

Subagents are reserved strictly for context isolation or independent/adversarial review:

| Subagent | Plugin | Justification |
|---|---|---|
| `agent-evolution` | `dev-workflow` | Context isolation when scanning `AI/` logs and skills at session end |
| `ocp-migration-analyst` | `openshift-devops` | Context isolation for raw `oc get -o yaml` cluster dumps |
| `ocp-resilience-analyst` | `openshift-devops` | Context isolation for raw workload/PDB/pod YAML dumps |
| `security-architect` | `security-and-networking` | Independent/adversarial read-only security & STRA/PIA review |
| `container-network-analyst` | `security-and-networking` | Context isolation for multi-namespace NetworkPolicy/Route YAML dumps |
