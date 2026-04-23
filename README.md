# rl-agents-n-skills

**Author**: Ryan Loiselle — Developer / Architect  
**AI tool**: GitHub Copilot — AI pair programmer / code generation  
**Updated**: April 2026

Shared **Claude Code plugin** containing persona agents, reusable skills, and
Claude Code subagents for rloisell BC Gov .NET/React/OpenShift projects.

This repo serves two toolchains from a single source:

| Toolchain | How it consumes this repo | Discovery path |
|-----------|--------------------------|----------------|
| **VS Code / GitHub Copilot** | Git submodule at `.github/agents/` | `.github/agents/*/SKILL.md` |
| **Claude Code** | Plugin via `.claude/settings.json` | `agents/` subagents in plugin root |

---

## Agents (20) — VS Code SKILL.md + Claude Code subagent

Each agent has two artefacts: a VS Code `SKILL.md` at the repo root (auto-discovered when
this repo is a submodule at `.github/agents/`) and a Claude Code subagent in `agents/`.

| Directory | Scope |
|-----------|-------|
| `session-workflow/` | Session startup/shutdown, AI file maintenance (WORKLOG/CHANGES/COMMANDS/COMMIT_INFO) |
| `github-workflow/` | Branch naming, PR lifecycle, CI diagnosis, gh CLI, rulesets |
| `diagram-generation/` | draw.io + PlantUML + Mermaid, 10-diagram UML suite, folder structure, export |
| `ci-cd-pipeline/` | 5-workflow pattern, ISB EA Option 2, image tags, yq GitOps, Trivy, failure triage |
| `local-dev/` | podman-compose, EF Core migration commands, MariaDB, port conventions, troubleshooting |
| `spec-kitty/` | Spec-first development, WP YAML format, spec.md/plan.md sections, validate-tasks |
| `spec-kit/` | GitHub Spec-Kit SDD lifecycle — constitution→specify→plan→tasks→implement, extensions, presets |
| `ef-core/` | Pomelo/MariaDB patterns, migration workflow, startup Migrate(), Linux LINQ gotcha, service layer |
| `bc-gov-devops/` | Emerald OpenShift, Artifactory, Helm, health checks, Common SSO, oc commands, ArgoCD |
| `agent-evolution/` | Self-learning — monitors sessions, updates KNOWLEDGE sections, promotes shared skills |
| `security-architect/` | OWASP Top 10, SAST/DAST toolchain, input validation, audit logging, container security, STRA/PIA |
| `bc-gov-iam/` | DIAM/Keycloak OIDC PKCE, realm selection, React oidc-client-ts, token lifecycle, backchannel logout |
| `observability/` | Serilog structured logging, health checks, Prometheus pod annotations, OpenTelemetry .NET SDK |
| `zero-trust-architect/` | ZTA design, SASE architecture, ZTNA/CASB/SWG evaluation |
| `network-architect/` | Routing/switching design, WAN, BGP/OSPF, topology review |
| `cisco-ios/` | Cisco IOS/IOS-XE/NX-OS config, home lab, troubleshooting, password recovery |
| `sysadmin/` | *nix admin, Solaris 9/10/11 SPARC (LDoms), RHEL, storage, boot issues |
| `bc-gov-network-architect/` | BC Gov workload connectivity, NetworkPolicy authoring, SDN zone classification, cross-zone failure diagnosis |
| `ocp-migration-analyst/` | Full OCP migration analysis pipeline — namespace discovery, gap analysis, network mapping, report generation |
| `ocp-resilience-analyst/` | OpenShift namespace resilience posture — R01–R15 grading, PDB/HPA/replica analysis, prioritised remediation |

---

## Shared Skills (15) — reusable reference libraries

| Directory | Consumed by |
|-----------|-------------|
| `ai-session-files/` | session-workflow, github-workflow |
| `git-conventions/` | session-workflow, github-workflow, ci-cd-pipeline |
| `bc-gov-emerald/` | bc-gov-devops, ci-cd-pipeline |
| `containerfile-standards/` | bc-gov-devops, ci-cd-pipeline |
| `vault-secrets/` | security-architect, bc-gov-devops, ci-cd-pipeline |
| `bc-gov-networkpolicy/` | bc-gov-network-architect, bc-gov-devops |
| `bc-gov-sdn-zones/` | bc-gov-network-architect |
| `bc-gov-design-system/` | bc-gov-devops, local-dev |
| `network-security/` | security-architect, network-architect, zero-trust-architect |
| `dns-tools/` | network-architect, sysadmin |
| `solaris/` | sysadmin |
| `linux-rhel/` | sysadmin |
| `bc-migrate-service/` | ocp-migration-analyst |
| `bc-resilience-service/` | ocp-resilience-analyst |
| `doc-versioning/` | session-workflow, any agent working with versioned documents/reports |

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

## References

Standards, frameworks, and projects that shaped the skills in this library:

| Reference | Used in | Notes |
|-----------|---------|-------|
| [NousResearch Hermes Agent](https://github.com/NousResearch/hermes-function-calling) (MIT) | `agent-evolution` | Retain/recall/reflect pattern — mid-session knowledge capture, pre-session retrieval, USER_MODEL section |
| [GitHub Spec-Kit](https://github.com/github/spec-kit) (MIT) | `spec-kit` | Spec-Driven Development lifecycle — specify-cli commands, extensions/presets model, SDD phases |
| [NIST SP 800-207 — Zero Trust Architecture](https://csrc.nist.gov/publications/detail/sp/800-207/final) | `zero-trust-architect` | Authoritative ZTA definition and design principles |
| [OWASP Top 10](https://owasp.org/Top10/) | `security-architect`, `ocp-migration-analyst` | Web application security risk taxonomy |
| [RFC 1918 — Private Address Space](https://datatracker.ietf.org/doc/html/rfc1918) | `network-architect`, `network-security`, `dns-tools` | Private IPv4 address range conventions |
| [RFC 5798 — VRRP](https://datatracker.ietf.org/doc/html/rfc5798) | `network-architect` | Virtual Router Redundancy Protocol |
| [RFC 7807 — Problem Details for HTTP APIs](https://datatracker.ietf.org/doc/html/rfc7807) | `ef-core` | Standard error response envelope for domain exceptions |
| [BC Gov IMIT Standard 6.13 — Network Security Zones (2012)](https://www2.gov.bc.ca/gov/content/governments/services-for-government/policies-procedures/im-it-standards) | `bc-gov-sdn-zones` | BC Government SDN zone classification and connectivity rules |
| [BC Gov N2N Connectivity Standard (2008)](https://www2.gov.bc.ca/gov/content/governments/services-for-government/policies-procedures/im-it-standards) | `bc-gov-sdn-zones` | Node-to-node connectivity rules within BC Gov SDN |

---

## Contributing

All changes go through PRs on `main`. After merging, consuming projects update
their submodule reference.

