# rl-agents-n-skills

**Author**: Ryan Loiselle — Developer / Architect  
**AI tool**: GitHub Copilot — AI pair programmer / code generation  
**Updated**: April 2026

Shared **Claude Code plugin** containing persona agents, reusable skills, and
Claude Code subagents for rloisell BC Gov .NET/React/OpenShift projects.

This repo serves two toolchains from a single source:

| Toolchain | How it consumes this repo | Discovery path |
| --- | --- | --- |
| **VS Code / GitHub Copilot** | Git submodule at `.github/agents/` | `.github/agents/*/SKILL.md` |
| **Claude Code** | Plugin via `.claude/settings.json` | `agents/` subagents in plugin root |

---

## Agents (20) — VS Code SKILL.md + Claude Code subagent

Each agent has two artefacts: a VS Code `SKILL.md` at the repo root (auto-discovered when
this repo is a submodule at `.github/agents/`) and a Claude Code subagent in `agents/`.

| Directory | Scope |
| --- | --- |
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
| --- | --- |
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
| --- | --- | --- |
| [NousResearch Hermes Agent](https://github.com/NousResearch/hermes-function-calling) (MIT) | `agent-evolution` | Retain/recall/reflect pattern — mid-session knowledge capture, pre-session retrieval, USER_MODEL section |
| [GitHub Spec-Kit](https://github.com/github/spec-kit) (MIT) | `spec-kit` | Spec-Driven Development lifecycle — specify-cli commands, extensions/presets model, SDD phases |
| [NIST SP 800-207 — Zero Trust Architecture](https://csrc.nist.gov/publications/detail/sp/800-207/final) | `zero-trust-architect` | Authoritative ZTA definition and design principles |
| [OWASP Top 10](https://owasp.org/Top10/) | `security-architect`, `ocp-migration-analyst` | Web application security risk taxonomy |
| [RFC 1918 — Private Address Space](https://datatracker.ietf.org/doc/html/rfc1918) | `network-architect`, `network-security`, `dns-tools` | Private IPv4 address range conventions |
| [RFC 5798 — VRRP](https://datatracker.ietf.org/doc/html/rfc5798) | `network-architect` | Virtual Router Redundancy Protocol |
| [RFC 7807 — Problem Details for HTTP APIs](https://datatracker.ietf.org/doc/html/rfc7807) | `ef-core` | Standard error response envelope for domain exceptions |
| [BC Gov IMIT 6.13 — Network Security Zones Standard (v5) + Specifications (v1)](https://intranet.gov.bc.ca/assets/intranet/mtics/ocio/es/enterprise-services-division/information-security-branch/information-security-standards-and-guidelines/imit_613_network_security_zones_standard_v5.pdf) | `bc-gov-sdn-zones`, `bc-gov-network-architect`, `bc-gov-emerald`, `bc-gov-devops`, `network-security`, `network-architect`, `zero-trust-architect`, `security-architect` | Zone model (DMZ / Zone A/B/C; SDN Low/Medium/High); zone adjacency; SPAN. Intranet-only. |
| [BC Gov IMIT 6.28 — Network and Communications Security Standard (v5.0, 2022)](https://www2.gov.bc.ca/assets/gov/government/services-for-government-and-broader-public-sector/information-technology-services/standards-files/09_-_communications_security_standard_v10.pdf) · [Specifications (v1.0, 2024)](https://www2.gov.bc.ca/assets/gov/government/services-for-government-and-broader-public-sector/information-technology-services/standards-files/imit_628_netowrk_and_communications_security_specifications.pdf) | `bc-gov-sdn-zones`, `bc-gov-networkpolicy`, `bc-gov-emerald`, `bc-gov-network-architect`, `bc-gov-devops`, `network-security`, `network-architect`, `zero-trust-architect`, `security-architect` | Network controls, segregation (§3.5), routing controls (§3.6), logging (§3.3), communication security (§3.7), exchange agreements (§3.9). Includes retired IMIT 5.09 WLAN requirements. |
| [BC Gov IMIT 5.08 — Network-to-Network Connectivity Security Standard (v2.0, 2022)](https://www2.gov.bc.ca/assets/gov/government/services-for-government-and-broader-public-sector/information-technology-services/standards-files/imit_508_network_to_network_connectivity_standard.pdf) · [Specifications (v1.0, 2022)](https://www2.gov.bc.ca/assets/gov/government/services-for-government-and-broader-public-sector/information-technology-services/standards-files/imit_508_network-to-network_connectivity_specifications.pdf) | `bc-gov-sdn-zones`, `bc-gov-networkpolicy`, `bc-gov-network-architect`, `bc-gov-devops`, `network-security`, `network-architect`, `zero-trust-architect`, `security-architect` | Third-Party Gateway (3PG) standard. Stateful firewall + IPS/IDS at security transit point; default-deny; encryption per IMIT 6.10; PCI traffic requires separate physical router per circuit; raw log retention ≥ 13 months. |

---

## Contributing

All changes go through PRs on `main`. After merging, consuming projects update
their submodule reference.

### Contributing BC Gov skills upstream

This repo is the **primary development home** — all work happens here first.

Selected BC Gov platform skills are candidates for upstream contribution to
[`bcgov/copilot-instructions`](https://github.com/bcgov/copilot-instructions),
which is the org-level shared skills library used across BC Gov projects.

**Candidate skills for bcgov/copilot-instructions:**

| Skill | Notes |
| --- | --- |
| `bc-gov-devops/` | Emerald deployment patterns — broadly applicable |
| `bc-gov-iam/` | DIAM / Common SSO OIDC — applicable to all BC Gov apps |
| `bc-gov-emerald/` | Emerald platform mechanics |
| `bc-gov-networkpolicy/` | NetworkPolicy patterns — applicable to all OCP clusters |
| `bc-gov-sdn-zones/` | SDN zone model — org-wide reference |
| `bc-gov-network-architect/` | BC Gov network architecture reasoning |
| `ocp-migration-analyst/` | OCP migration analysis pipeline |
| `ocp-resilience-analyst/` | Namespace resilience posture reporting |

**Skills that stay in this repo only** (personal workflow, project-specific):
`session-workflow`, `agent-evolution`, `spec-kitty`, `spec-kit`, `ef-core`,
`doc-versioning`, `solaris`, `cisco-ios`, `local-dev`, `dns-tools`.

**Contribution process:**

1. Develop and validate the skill here as normal
2. Fork `bcgov/copilot-instructions`
3. Copy the skill to `.github/skills/<name>/SKILL.md` — strip personal
   references (`metadata.author`, project-specific `compatibility` notes,
   cross-refs to personal skills)

4. Submit PR with a clear description of what the skill does and what it targets

Sources in this repo and `bcgov/copilot-instructions` are intentionally separate.
The BCGov version is a trimmed, generic copy — not a symlink.
