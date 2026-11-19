# rl-agents-n-skills

**Author**: Ryan Loiselle — Developer / Architect  
**AI tool**: GitHub Copilot / Claude Code / APM  
**Updated**: November 2026

Domain-organized [APM](https://github.com/microsoft/apm)-native collection of reusable agent skills and justified subagents for BC Gov .NET/React/OpenShift DevOps, security & networking, and systems infrastructure.

## Documentation

- [AGENTS.md](AGENTS.md) — Canonical repository rules, confidentiality baseline, coding standards, and subagent registry
- [CLAUDE.md](CLAUDE.md) — Thin bridge to `AGENTS.md`
- [architecture.md](architecture.md) — APM topology, plugins, skills, references, and subagents
- [install.md](install.md) — APM installation, target harnesses, update, and troubleshooting guide
- [migration-map.md](migration-map.md) — Transition guide: legacy 41 skills & 24 agents → new plugin paths
- [docs/SKILL-STRUCTURE-STANDARD.md](docs/SKILL-STRUCTURE-STANDARD.md) — Agent Skills Open Standard & `authoring-skills` contract

---

## Domain Plugins (`plugins/`)

Consolidates the original 21 agents and 17 shared skills into 5 APM-native domain plugins (19 skills, 5 justified subagents):

| Plugin | Scope | Skills | Subagents |
| --- | --- | --- | --- |
| [dev-workflow](plugins/dev-workflow/README.md) | Sessions, GitHub PRs/rulesets, spec-driven dev, diagrams/versioning, skill evolution | 5 | 1 (`agent-evolution`) |
| [app-engineering](plugins/app-engineering/README.md) | .NET 10 / EF Core / REST APIs, BC Gov Design System, DIAM/OIDC IAM, observability, local dev | 4 | 0 |
| [openshift-devops](plugins/openshift-devops/README.md) | Emerald OpenShift, Option 2 CI/CD, migration & resilience analysis, CI/CD governance | 3 | 2 (`ocp-migration-analyst`, `ocp-resilience-analyst`) |
| [security-and-networking](plugins/security-and-networking/README.md) | AppSec, Vault, DB security, data lineage/STRA/PIA, Zero Trust, enterprise & OCP networking | 5 | 2 (`security-architect`, `container-network-analyst`) |
| [systems-infrastructure](plugins/systems-infrastructure/README.md) | Unix/RHEL/Solaris administration, DNS diagnostics, Cisco IOS/NX-OS networking | 2 | 0 |

---

## Using in a project (APM)

Install all 5 domain plugins globally across target harnesses:

```bash
apm install https://github.com/rloisell/rl-agents-n-skills --global --target claude,copilot,codex,agy
```

See [install.md](install.md) for per-plugin installs, project-local installs, Windows flags, updating, and troubleshooting.

### Project-specific agents

Project-specific Claude Code subagents belong in `.claude/agents/` within the
consuming project — not in this repo.

---

## References & Acknowledgments

Standards, frameworks, and projects that shaped the skills in this library:

| Reference | Scope / Domain | Notes |
| --- | --- | --- |
| [bcgov/platform-developer-docs](https://github.com/bcgov/platform-developer-docs) (Apache-2.0) | `openshift-devops`, `app-engineering` | BC Gov OpenShift Emerald, Argo CD, Vault, and resiliency references |
| [bcgov/crow](https://github.com/bcgov/crow) (MIT, Copyright (c) 2026 Christian Baerike) | `openshift-devops`, `security-and-networking`, `app-engineering` | CI/CD quality gates, HA application continuity, security/Sonar review, `.NET`/Unicode, and UX patterns |
| [richfrem/bc-gov-design-system](https://github.com/richfrem/bc-gov-design-system) | `app-engineering` | Companion APM skill owning official BC Gov Design System components, BC Sans, and v5 tokens |
| [NousResearch Hermes Agent](https://github.com/NousResearch/hermes-function-calling) (MIT) | `evolving-agent-skills` | Retain/recall/reflect pattern — mid-session knowledge capture, pre-session retrieval, USER_MODEL section |
| [GitHub Spec-Kit](https://github.com/github/spec-kit) (MIT) | `driving-spec-development` | Spec-Driven Development lifecycle — specify-cli commands, extensions/presets model, SDD phases |
| [NIST SP 800-207 — Zero Trust Architecture](https://csrc.nist.gov/publications/detail/sp/800-207/final) | `designing-enterprise-networks` | Authoritative ZTA definition and design principles |
| [OWASP Top 10](https://owasp.org/Top10/) | `securing-bc-gov-workloads`, `analyzing-ocp-platforms` | Web application security risk taxonomy |
| [RFC 1918 — Private Address Space](https://datatracker.ietf.org/doc/html/rfc1918) | `designing-enterprise-networks`, `administering-unix-systems` | Private IPv4 address range conventions |
| [RFC 5798 — VRRP](https://datatracker.ietf.org/doc/html/rfc5798) | `designing-enterprise-networks` | Virtual Router Redundancy Protocol |
| [RFC 7807 — Problem Details for HTTP APIs](https://datatracker.ietf.org/doc/html/rfc7807) | `building-dotnet-apis` | Standard error response envelope for domain exceptions |
| [BC Gov IMIT 6.13 — Network Security Zones Standard (v5) + Specifications (v1)](https://intranet.gov.bc.ca/assets/intranet/mtics/ocio/es/enterprise-services-division/information-security-branch/information-security-standards-and-guidelines/imit_613_network_security_zones_standard_v5.pdf) | `designing-bc-gov-networks`, `deploying-bc-gov-workloads`, `designing-enterprise-networks`, `securing-bc-gov-workloads` | Zone model (DMZ / Zone A/B/C; SDN Low/Medium/High); zone adjacency; SPAN. Intranet-only. |
| [BC Gov IMIT 6.28 — Network and Communications Security Standard (v5.0, 2022)](https://www2.gov.bc.ca/assets/gov/government/services-for-government-and-broader-public-sector/information-technology-services/standards-files/09_-_communications_security_standard_v10.pdf) · [Specifications (v1.0, 2024)](https://www2.gov.bc.ca/assets/gov/government/services-for-government-and-broader-public-sector/information-technology-services/standards-files/imit_628_netowrk_and_communications_security_specifications.pdf) | `designing-bc-gov-networks`, `deploying-bc-gov-workloads`, `designing-enterprise-networks`, `securing-bc-gov-workloads` | Network controls, segregation (3.5), routing controls (3.6), logging (3.3), communication security (3.7), exchange agreements (3.9). Includes retired IMIT 5.09 WLAN requirements. |
| [BC Gov IMIT 5.08 — Network-to-Network Connectivity Security Standard (v2.0, 2022)](https://www2.gov.bc.ca/assets/gov/government/services-for-government-and-broader-public-sector/information-technology-services/standards-files/imit_508_network_to_network_connectivity_standard.pdf) · [Specifications (v1.0, 2022)](https://www2.gov.bc.ca/assets/gov/government/services-for-government-and-broader-public-sector/information-technology-services/standards-files/imit_508_network-to-network_connectivity_specifications.pdf) | `designing-bc-gov-networks`, `designing-enterprise-networks`, `securing-bc-gov-workloads` | Third-Party Gateway (3PG) standard. Stateful firewall + IPS/IDS at security transit point; default-deny; encryption per IMIT 6.10; PCI traffic requires separate physical router per circuit; raw log retention >= 13 months. |
| [BC Gov Network-to-Network Connectivity Technical and Product Standard](https://www2.gov.bc.ca/assets/gov/government/services-for-government-and-broader-public-sector/information-technology-services/standards-files/network_to_network_connectivity_technical_and_product_standard.pdf) | `designing-bc-gov-networks` | Companion to IMIT 5.08 — approved technical implementations and certified products. |
| [BC Gov OCIO SDN Security Classification Model v1.0 (June 2022)](https://www2.gov.bc.ca/assets/gov/government/services-for-government-and-broader-public-sector/information-technology-services/standards-files/sdn_security_classification_model.pdf) | `designing-bc-gov-networks`, `deploying-bc-gov-workloads` | Workload-centric Low/Medium/High classification; guardrails vs security policies; Public VIP rules; Forward Proxy supported protocols. |
| [BC Gov Database Security Standard for Information Protection v1.0 (Apr 2018)](https://www2.gov.bc.ca/assets/gov/government/services-for-government-and-broader-public-sector/information-technology-services/standards-files/database_security_standards_for_information_protection_-_2018-04_version_1.pdf) | `securing-bc-gov-workloads`, `building-dotnet-apis`, `deploying-bc-gov-workloads` | 23 mandatory database controls (data classification, encryption decisions, separation of duties, env segregation, vulnerability assessment, change mgmt, patching, audit). |
| [BC Gov Security Standard for Application and Web Development and Deployment v1.3 (Apr 2015)](https://www2.gov.bc.ca/assets/gov/government/services-for-government-and-broader-public-sector/information-technology-services/standards-files/security_standard_application_web_development_deployment.pdf) | `securing-bc-gov-workloads`, `deploying-bc-gov-workloads` | Patch & vulnerability mgmt; prod/non-prod segregation; code review; secure coding (OWASP); 45-day dormant accounts; no creds in source; WAF for public-facing web apps. |
| [BC Gov Development Standards for Information Systems and Services v3.0 (May 2015)](https://www2.gov.bc.ca/assets/gov/government/services-for-government-and-broader-public-sector/information-technology-services/standards-files/development_standards_for_information_systems_and_services.pdf) | `managing-github-workflows`, `driving-spec-development`, `deploying-bc-gov-workloads`, `securing-bc-gov-workloads` | Requirements management practices; github.com/bcgov mandate; 2FA on repo admins; approved licenses; Content Approval Checklist. |
| [BC Gov REST API Development Standard (2015-04-01)](https://www2.gov.bc.ca/assets/gov/government/services-for-government-and-broader-public-sector/information-technology-services/standards-files/api-standard.pdf) | `building-dotnet-apis`, `deploying-bc-gov-workloads` | 8 mandated minimums: REST for public APIs, HTTP verbs per RFC, single-resource URLs, JSON/XML, response metadata (ISO 8601 + license), error messaging, version number. |
| [BC Gov Guidelines on the Use of Open Source Software (R1.0, Apr 2012)](https://www2.gov.bc.ca/assets/gov/government/services-for-government-and-broader-public-sector/information-technology-services/standards-files/guidelines_on_the_use_of_open_source_software_2016.pdf) | `deploying-bc-gov-workloads`, `securing-bc-gov-workloads`, `managing-github-workflows` | OSS adoption guidance — license review, business value + TCO, due diligence (guideline, not mandate). |

---

## Contributing

All changes go through PRs on `main`. After merging, consuming projects update
their installed APM packages (`apm update`).

### Contributing BC Gov skills upstream

This repo is the **primary development home** — all work happens here first.

Selected BC Gov platform skills are candidates for upstream contribution to
[`bcgov/copilot-instructions`](https://github.com/bcgov/copilot-instructions),
which is the org-level shared skills library used across BC Gov projects:

- `deploying-bc-gov-workloads` (`openshift-devops`) — Emerald deployment patterns, scaffolding & policy-gate scripts
- `building-bc-gov-web-apps` & `building-dotnet-apis` (`app-engineering`) — DIAM / Common SSO OIDC & REST API standards
- `designing-bc-gov-networks` & `auditing-ocp-network-posture` (`security-and-networking`) — SDN zones & NetworkPolicy patterns
- `securing-bc-gov-workloads` (`security-and-networking`) — Database Security Standard & AppSec controls
- `analyzing-ocp-platforms` & `auditing-cicd-governance` (`openshift-devops`) — OCP migration/resilience & CI/CD governance

**Contribution process:**

1. Develop and validate the skill here as normal
2. Fork `bcgov/copilot-instructions`
3. Copy the skill to `.github/skills/<name>/SKILL.md` — strip personal references (`metadata.author`, project-specific `compatibility` notes, cross-refs to personal skills)
4. Submit PR with a clear description of what the skill does and what it targets

Sources in this repo and `bcgov/copilot-instructions` are intentionally separate.
The BCGov version is a trimmed, generic copy — not a symlink.
