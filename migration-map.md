# Legacy-to-APM Migration Map

This document records the transition from the legacy flat repository layout (41 root skill directories and 24 root `agents/*.md` files) to the APM-native multi-plugin architecture under `plugins/`.

For the current future-state architecture, see [architecture.md](architecture.md).

## Transition Summary

- **41 legacy skills → 19 consolidated gerund-named skills** across **5 domain plugins** (`dev-workflow`, `app-engineering`, `openshift-devops`, `security-and-networking`, `systems-infrastructure`).
- **Pure reference libraries** were folded into `references/` directories inside their parent skills.
- **24 legacy `agents/*.md` files → 5 justified subagents** (retained only for context isolation or independent/adversarial review); the remaining 19 wrapper agents were retired into their consolidated skills.
- **2 deprecated service skills** (`bc-migrate-service`, `bc-resilience-service`) were retired.

---

## 1. Domain & Skill Consolidation Summary

### `plugins/dev-workflow`
| Consolidated Skill | Absorbed Legacy Skills / References |
|---|---|
| `managing-dev-sessions` | `session-workflow`, `ai-session-files` (moved to `references/`) |
| `managing-github-workflows` | `github-workflow`, `git-conventions` (moved to `references/`) |
| `driving-spec-development` | `spec-kit`, `spec-kitty` |
| `documenting-architecture` | `diagram-generation`, `doc-versioning` |
| `evolving-agent-skills` | `agent-evolution` |

### `plugins/app-engineering`
| Consolidated Skill | Absorbed Legacy Skills / References |
|---|---|
| `building-dotnet-apis` | `ef-core`, `bc-gov-rest-api` (moved to `references/`) |
| `building-bc-gov-web-apps` | `bc-gov-iam`, `bc-gov-design-system` (moved to `references/`) |
| `instrumenting-observability` | `observability` |
| `managing-local-dev` | `local-dev` (cross-references `building-dotnet-apis` for EF migrations) |

### `plugins/openshift-devops`
| Consolidated Skill | Absorbed Legacy Skills / References |
|---|---|
| `deploying-bc-gov-workloads` | `bc-gov-devops`, `ci-cd-pipeline`, `bc-gov-emerald`, `containerfile-standards` |
| `analyzing-ocp-platforms` | `ocp-migration-analyst`, `ocp-resilience-analyst`, `bc-gov-multi-app-analyst` (`bc-migrate-service` & `bc-resilience-service` retired) |
| `auditing-cicd-governance` | `bc-gov-deployment-cicd-analyst` (`UPSTREAM-ALIGNMENT.md` moved to `docs/`) |

### `plugins/security-and-networking`
| Consolidated Skill | Absorbed Legacy Skills / References |
|---|---|
| `securing-bc-gov-workloads` | `security-architect`, `vault-secrets`, `bc-gov-database-security` |
| `mapping-data-lineage` | `data-flow-lineage` (relocated from app-engineering to security/STRA-PIA) |
| `designing-enterprise-networks` | `zero-trust-architect`, `network-architect`, `network-security` |
| `designing-bc-gov-networks` | `bc-gov-network-architect`, `bc-gov-sdn-zones`, `bc-gov-networkpolicy` |
| `auditing-ocp-network-posture` | `container-network-analyst` + cross-NS/stale NP audit playbook |

### `plugins/systems-infrastructure`
| Consolidated Skill | Absorbed Legacy Skills / References |
|---|---|
| `administering-unix-systems` | `sysadmin`, `linux-rhel`, `solaris`, `dns-tools` |
| `configuring-cisco-networks` | `cisco-ios` |

---

## 2. Legacy Skills (41) → New Relative Paths

| Legacy Skill | New Plugin | Target Type | New Skill / Subagent | Relative Path(s) |
|---|---|---|---|---|
| `agent-evolution/` | `dev-workflow` | Skill + Subagent + Template | `evolving-agent-skills` + `agent-evolution` | `plugins/dev-workflow/.apm/skills/evolving-agent-skills/SKILL.md`, `plugins/dev-workflow/.apm/skills/evolving-agent-skills/references/evolution-log.md`, `plugins/dev-workflow/.apm/skills/evolving-agent-skills/references/knowledge-and-promotion.md`, `plugins/dev-workflow/.apm/skills/evolving-agent-skills/assets/templates/seven-section-skill-template.md`, `plugins/dev-workflow/.apm/agents/agent-evolution.md` |
| `ai-session-files/` | `dev-workflow` | Skill Reference | `managing-dev-sessions` | `plugins/dev-workflow/.apm/skills/managing-dev-sessions/references/ai-session-files.md` |
| `bc-gov-database-security/` | `security-and-networking` | Skill Reference | `securing-bc-gov-workloads` | `plugins/security-and-networking/.apm/skills/securing-bc-gov-workloads/references/database-security-standard.md` |
| `bc-gov-deployment-cicd-analyst/` | `openshift-devops` | Skill + Docs | `auditing-cicd-governance` | `plugins/openshift-devops/.apm/skills/auditing-cicd-governance/SKILL.md`, `plugins/openshift-devops/.apm/skills/auditing-cicd-governance/references/control-matrix-and-deliverables.md`, `docs/UPSTREAM-ALIGNMENT.md` |
| `bc-gov-design-system/` | `app-engineering` | Skill References | `building-bc-gov-web-apps` | `plugins/app-engineering/.apm/skills/building-bc-gov-web-apps/references/bc-gov-design-system.md`, `plugins/app-engineering/.apm/skills/building-bc-gov-web-apps/references/design-tokens.md` |
| `bc-gov-devops/` | `openshift-devops` | Skill + References | `deploying-bc-gov-workloads` | `plugins/openshift-devops/.apm/skills/deploying-bc-gov-workloads/SKILL.md`, `plugins/openshift-devops/.apm/skills/deploying-bc-gov-workloads/references/ag-helm-and-policy-gate.md`, `plugins/openshift-devops/.apm/skills/deploying-bc-gov-workloads/references/networkpolicy-patterns.md` |
| `bc-gov-emerald/` | `openshift-devops` | Skill Reference | `deploying-bc-gov-workloads` | `plugins/openshift-devops/.apm/skills/deploying-bc-gov-workloads/references/emerald-platform-mechanics.md` |
| `bc-gov-iam/` | `app-engineering` | Skill + References | `building-bc-gov-web-apps` | `plugins/app-engineering/.apm/skills/building-bc-gov-web-apps/SKILL.md`, `plugins/app-engineering/.apm/skills/building-bc-gov-web-apps/references/keycloak-realms-and-clients.md`, `plugins/app-engineering/.apm/skills/building-bc-gov-web-apps/references/react-oidc-client-ts.md`, `plugins/app-engineering/.apm/skills/building-bc-gov-web-apps/references/dotnet-jwt-and-backchannel-logout.md`, `plugins/app-engineering/.apm/skills/building-bc-gov-web-apps/references/iam-knowledge.md` |
| `bc-gov-multi-app-analyst/` | `openshift-devops` | Skill + Reference | `analyzing-ocp-platforms` | `plugins/openshift-devops/.apm/skills/analyzing-ocp-platforms/SKILL.md`, `plugins/openshift-devops/.apm/skills/analyzing-ocp-platforms/references/multi-app-orchestration.md` |
| `bc-gov-network-architect/` | `security-and-networking` | Skill (+ Audit Ref) | `designing-bc-gov-networks` | `plugins/security-and-networking/.apm/skills/designing-bc-gov-networks/SKILL.md`, `plugins/security-and-networking/.apm/skills/auditing-ocp-network-posture/references/gap-analysis-rubrics.md` |
| `bc-gov-networkpolicy/` | `security-and-networking` | Skill Ref + Templates | `designing-bc-gov-networks` | `plugins/security-and-networking/.apm/skills/designing-bc-gov-networks/references/networkpolicy-patterns.md`, `plugins/security-and-networking/.apm/skills/designing-bc-gov-networks/assets/templates/{allow-egress-dns,allow-frontend-to-api,allow-ingress-from-router,allow-egress-external-cidr,allow-cross-namespace}.yaml` |
| `bc-gov-rest-api/` | `app-engineering` | Skill Reference | `building-dotnet-apis` | `plugins/app-engineering/.apm/skills/building-dotnet-apis/references/bc-gov-rest-api-standard.md` |
| `bc-gov-sdn-zones/` | `security-and-networking` | Skill Reference | `designing-bc-gov-networks` | `plugins/security-and-networking/.apm/skills/designing-bc-gov-networks/references/sdn-zones-and-imit-standards.md` |
| `bc-migrate-service/` | — | Retired (Deprecated) | — | *Deprecated May 2026; superseded by `analyzing-ocp-platforms`* |
| `bc-resilience-service/` | — | Retired (Deprecated) | — | *Deprecated May 2026; superseded by `analyzing-ocp-platforms`* |
| `ci-cd-pipeline/` | `openshift-devops` | Skill Reference | `deploying-bc-gov-workloads` | `plugins/openshift-devops/.apm/skills/deploying-bc-gov-workloads/references/github-actions-option2.md` |
| `cisco-ios/` | `systems-infrastructure` | Skill + References | `configuring-cisco-networks` | `plugins/systems-infrastructure/.apm/skills/configuring-cisco-networks/SKILL.md`, `plugins/systems-infrastructure/.apm/skills/configuring-cisco-networks/references/ios-routing-switching.md`, `plugins/systems-infrastructure/.apm/skills/configuring-cisco-networks/references/nxos-and-recovery.md` |
| `container-network-analyst/` | `security-and-networking` | Skill + Subagent | `auditing-ocp-network-posture` + `container-network-analyst` | `plugins/security-and-networking/.apm/skills/auditing-ocp-network-posture/SKILL.md`, `plugins/security-and-networking/.apm/skills/auditing-ocp-network-posture/references/collection-commands.md`, `plugins/security-and-networking/.apm/skills/auditing-ocp-network-posture/references/gap-analysis-rubrics.md`, `plugins/security-and-networking/.apm/skills/auditing-ocp-network-posture/references/report-and-pdf-rendering.md`, `plugins/security-and-networking/.apm/agents/container-network-analyst.md` |
| `containerfile-standards/` | `openshift-devops` | Skill Ref + Templates | `deploying-bc-gov-workloads` | `plugins/openshift-devops/.apm/skills/deploying-bc-gov-workloads/references/containerfile-standards.md`, `plugins/openshift-devops/.apm/skills/deploying-bc-gov-workloads/assets/templates/Containerfile.dotnet`, `plugins/openshift-devops/.apm/skills/deploying-bc-gov-workloads/assets/templates/Containerfile.react` |
| `data-flow-lineage/` | `security-and-networking` | Skill + References | `mapping-data-lineage` | `plugins/security-and-networking/.apm/skills/mapping-data-lineage/SKILL.md`, `plugins/security-and-networking/.apm/skills/mapping-data-lineage/references/iscf-and-risk-matrix.md`, `plugins/security-and-networking/.apm/skills/mapping-data-lineage/references/foippa-residency-and-pia.md`, `plugins/security-and-networking/.apm/skills/mapping-data-lineage/references/oc-discovery-commands.md` |
| `diagram-generation/` | `dev-workflow` | Skill + Refs + Templates | `documenting-architecture` | `plugins/dev-workflow/.apm/skills/documenting-architecture/SKILL.md`, `plugins/dev-workflow/.apm/skills/documenting-architecture/references/ten-diagram-suite.md`, `plugins/dev-workflow/.apm/skills/documenting-architecture/references/plantuml-templates.md`, `plugins/dev-workflow/.apm/skills/documenting-architecture/assets/templates/{sequence,class,state,c4-context}.puml`, `plugins/dev-workflow/.apm/skills/documenting-architecture/assets/templates/architecture.{mmd,drawio}` |
| `dns-tools/` | `systems-infrastructure` | Skill Reference | `administering-unix-systems` | `plugins/systems-infrastructure/.apm/skills/administering-unix-systems/references/dns-diagnostics.md` |
| `doc-versioning/` | `dev-workflow` | Skill Reference | `documenting-architecture` | `plugins/dev-workflow/.apm/skills/documenting-architecture/references/doc-versioning.md` |
| `ef-core/` | `app-engineering` | Skill + References | `building-dotnet-apis` | `plugins/app-engineering/.apm/skills/building-dotnet-apis/SKILL.md`, `plugins/app-engineering/.apm/skills/building-dotnet-apis/references/ef-core-pomelo-patterns.md`, `plugins/app-engineering/.apm/skills/building-dotnet-apis/references/ef-core-migrations.md`, `plugins/app-engineering/.apm/skills/building-dotnet-apis/references/ef-knowledge.md` |
| `git-conventions/` | `dev-workflow` | Skill Reference | `managing-github-workflows` | `plugins/dev-workflow/.apm/skills/managing-github-workflows/references/git-conventions.md` |
| `github-workflow/` | `dev-workflow` | Skill + References | `managing-github-workflows` | `plugins/dev-workflow/.apm/skills/managing-github-workflows/SKILL.md`, `plugins/dev-workflow/.apm/skills/managing-github-workflows/references/rulesets-and-ci.md`, `plugins/dev-workflow/.apm/skills/managing-github-workflows/references/workflow-knowledge.md` |
| `linux-rhel/` | `systems-infrastructure` | Skill Reference | `administering-unix-systems` | `plugins/systems-infrastructure/.apm/skills/administering-unix-systems/references/linux-rhel.md` |
| `local-dev/` | `app-engineering` | Skill + References | `managing-local-dev` | `plugins/app-engineering/.apm/skills/managing-local-dev/SKILL.md`, `plugins/app-engineering/.apm/skills/managing-local-dev/references/dev-ctl-guide.md`, `plugins/app-engineering/.apm/skills/managing-local-dev/references/podman-and-mariadb-setup.md`, `plugins/app-engineering/.apm/skills/managing-local-dev/references/troubleshooting-and-knowledge.md` |
| `network-architect/` | `security-and-networking` | Skill Reference | `designing-enterprise-networks` | `plugins/security-and-networking/.apm/skills/designing-enterprise-networks/references/routing-switching-wan.md` |
| `network-security/` | `security-and-networking` | Skill References | `designing-enterprise-networks` | `plugins/security-and-networking/.apm/skills/designing-enterprise-networks/references/ios-security-controls.md`, `plugins/security-and-networking/.apm/skills/designing-enterprise-networks/references/bc-gov-imit-network-mapping.md` |
| `observability/` | `app-engineering` | Skill + References | `instrumenting-observability` | `plugins/app-engineering/.apm/skills/instrumenting-observability/SKILL.md`, `plugins/app-engineering/.apm/skills/instrumenting-observability/references/serilog-and-health-checks.md`, `plugins/app-engineering/.apm/skills/instrumenting-observability/references/prometheus-and-opentelemetry.md`, `plugins/app-engineering/.apm/skills/instrumenting-observability/references/pii-in-logs-audit.md`, `plugins/app-engineering/.apm/skills/instrumenting-observability/references/observability-knowledge.md` |
| `ocp-migration-analyst/` | `openshift-devops` | Skill + Subagent | `analyzing-ocp-platforms` + `ocp-migration-analyst` | `plugins/openshift-devops/.apm/skills/analyzing-ocp-platforms/SKILL.md`, `plugins/openshift-devops/.apm/skills/analyzing-ocp-platforms/references/oc-collection-and-toolkits.md`, `plugins/openshift-devops/.apm/skills/analyzing-ocp-platforms/references/migration-gaps-g1-g12.md`, `plugins/openshift-devops/.apm/skills/analyzing-ocp-platforms/references/report-format-and-pdf.md`, `plugins/openshift-devops/.apm/skills/analyzing-ocp-platforms/references/standards-catalog.md`, `plugins/openshift-devops/.apm/agents/ocp-migration-analyst.md` |
| `ocp-resilience-analyst/` | `openshift-devops` | Skill + Subagent | `analyzing-ocp-platforms` + `ocp-resilience-analyst` | `plugins/openshift-devops/.apm/skills/analyzing-ocp-platforms/SKILL.md`, `plugins/openshift-devops/.apm/skills/analyzing-ocp-platforms/references/resilience-checks-r01-r15.md`, `plugins/openshift-devops/.apm/agents/ocp-resilience-analyst.md` |
| `security-architect/` | `security-and-networking` | Skill + Subagent | `securing-bc-gov-workloads` + `security-architect` | `plugins/security-and-networking/.apm/skills/securing-bc-gov-workloads/SKILL.md`, `plugins/security-and-networking/.apm/skills/securing-bc-gov-workloads/references/owasp-dotnet-react-oidc.md`, `plugins/security-and-networking/.apm/skills/securing-bc-gov-workloads/references/ocp-rbac-and-image-audit.md`, `plugins/security-and-networking/.apm/agents/security-architect.md` |
| `session-workflow/` | `dev-workflow` | Skill + Reference | `managing-dev-sessions` | `plugins/dev-workflow/.apm/skills/managing-dev-sessions/SKILL.md`, `plugins/dev-workflow/.apm/skills/managing-dev-sessions/references/process-knowledge.md` |
| `solaris/` | `systems-infrastructure` | Skill Reference | `administering-unix-systems` | `plugins/systems-infrastructure/.apm/skills/administering-unix-systems/references/solaris-sparc.md` |
| `spec-kit/` | `dev-workflow` | Skill + Reference | `driving-spec-development` | `plugins/dev-workflow/.apm/skills/driving-spec-development/SKILL.md`, `plugins/dev-workflow/.apm/skills/driving-spec-development/references/spec-kit.md` |
| `spec-kitty/` | `dev-workflow` | Skill + Ref + Templates | `driving-spec-development` | `plugins/dev-workflow/.apm/skills/driving-spec-development/SKILL.md`, `plugins/dev-workflow/.apm/skills/driving-spec-development/references/spec-kitty.md`, `plugins/dev-workflow/.apm/skills/driving-spec-development/assets/templates/{spec,plan,work-package}.md.j2` |
| `sysadmin/` | `systems-infrastructure` | Skill | `administering-unix-systems` | `plugins/systems-infrastructure/.apm/skills/administering-unix-systems/SKILL.md` |
| `vault-secrets/` | `security-and-networking` | Skill Ref + Templates | `securing-bc-gov-workloads` | `plugins/security-and-networking/.apm/skills/securing-bc-gov-workloads/references/vault-secrets.md`, `plugins/security-and-networking/.apm/skills/securing-bc-gov-workloads/assets/templates/{secretstore,externalsecret}.yaml` |
| `zero-trust-architect/` | `security-and-networking` | Skill + Reference | `designing-enterprise-networks` | `plugins/security-and-networking/.apm/skills/designing-enterprise-networks/SKILL.md`, `plugins/security-and-networking/.apm/skills/designing-enterprise-networks/references/zero-trust-sase.md` |

---

## 3. Legacy Subagents (24) → New `.apm/agents/` or Retired to Skills

| Legacy Agent (`agents/*.md`) | Disposition | Justification / Notes | New Plugin | Relative Path / Target Skill |
|---|---|---|---|---|
| `agents/agent-evolution.md` | **Kept as Subagent** | Context isolation when scanning `AI/` logs & skills at session end | `dev-workflow` | `plugins/dev-workflow/.apm/agents/agent-evolution.md` |
| `agents/ocp-migration-analyst.md` | **Kept as Subagent** | Context isolation for raw `oc get -o yaml` cluster dumps | `openshift-devops` | `plugins/openshift-devops/.apm/agents/ocp-migration-analyst.md` |
| `agents/ocp-resilience-analyst.md` | **Kept as Subagent** | Context isolation for raw workload/PDB/pod YAML dumps | `openshift-devops` | `plugins/openshift-devops/.apm/agents/ocp-resilience-analyst.md` |
| `agents/security-architect.md` | **Kept as Subagent** | Independent/adversarial read-only security & STRA/PIA review (`Read, Grep, Glob`) | `security-and-networking` | `plugins/security-and-networking/.apm/agents/security-architect.md` |
| `agents/container-network-analyst.md` | **Kept as Subagent** | Context isolation for multi-namespace NetworkPolicy/Route YAML dumps | `security-and-networking` | `plugins/security-and-networking/.apm/agents/container-network-analyst.md` |
| `agents/bc-gov-devops.md` | Retired → Skill | Interactive deployment checklist; no isolation/adversarial need | `openshift-devops` | `plugins/openshift-devops/.apm/skills/deploying-bc-gov-workloads/SKILL.md` |
| `agents/bc-gov-iam.md` | Retired → Skill | Interactive auth integration; no isolation/adversarial need | `app-engineering` | `plugins/app-engineering/.apm/skills/building-bc-gov-web-apps/SKILL.md` |
| `agents/bc-gov-multi-app-analyst.md` | Retired → Skill | Main-thread orchestrator; belongs in skill | `openshift-devops` | `plugins/openshift-devops/.apm/skills/analyzing-ocp-platforms/SKILL.md` |
| `agents/bc-gov-network-architect.md` | Retired → Skill | Interactive connectivity design; no isolation need | `security-and-networking` | `plugins/security-and-networking/.apm/skills/designing-bc-gov-networks/SKILL.md` |
| `agents/ci-cd-pipeline.md` | Retired → Skill | Interactive CI/CD authoring; no isolation need | `openshift-devops` | `plugins/openshift-devops/.apm/skills/deploying-bc-gov-workloads/SKILL.md` |
| `agents/cisco-ios.md` | Retired → Skill | Interactive CLI config/triage; no isolation need | `systems-infrastructure` | `plugins/systems-infrastructure/.apm/skills/configuring-cisco-networks/SKILL.md` |
| `agents/data-flow-lineage.md` | Retired → Skill | Thin pointer wrapper; folded into skill | `security-and-networking` | `plugins/security-and-networking/.apm/skills/mapping-data-lineage/SKILL.md` |
| `agents/deployment-cicd-analyst.md` | Retired → Skill | Main-thread assessment orchestrator; belongs in skill | `openshift-devops` | `plugins/openshift-devops/.apm/skills/auditing-cicd-governance/SKILL.md` |
| `agents/diagram-generation.md` | Retired → Skill | Interactive diagramming; no isolation need | `dev-workflow` | `plugins/dev-workflow/.apm/skills/documenting-architecture/SKILL.md` |
| `agents/ef-core.md` | Retired → Skill | Inline data-layer coding; no isolation need | `app-engineering` | `plugins/app-engineering/.apm/skills/building-dotnet-apis/SKILL.md` |
| `agents/github-workflow.md` | Retired → Skill | Inline PR/git workflow; no isolation need | `dev-workflow` | `plugins/dev-workflow/.apm/skills/managing-github-workflows/SKILL.md` |
| `agents/local-dev.md` | Retired → Skill | Interactive local setup; no isolation need | `app-engineering` | `plugins/app-engineering/.apm/skills/managing-local-dev/SKILL.md` |
| `agents/network-architect.md` | Retired → Skill | Interactive topology Q&A; no isolation need | `security-and-networking` | `plugins/security-and-networking/.apm/skills/designing-enterprise-networks/SKILL.md` |
| `agents/observability.md` | Retired → Skill | Inline instrumentation coding; no isolation need | `app-engineering` | `plugins/app-engineering/.apm/skills/instrumenting-observability/SKILL.md` |
| `agents/session-workflow.md` | Retired → Skill | Main-thread session startup/shutdown; belongs in skill | `dev-workflow` | `plugins/dev-workflow/.apm/skills/managing-dev-sessions/SKILL.md` |
| `agents/spec-kit.md` | Retired → Skill | Interactive SDD workflow; no isolation need | `dev-workflow` | `plugins/dev-workflow/.apm/skills/driving-spec-development/SKILL.md` |
| `agents/spec-kitty.md` | Retired → Skill | Interactive SDD workflow; no isolation need | `dev-workflow` | `plugins/dev-workflow/.apm/skills/driving-spec-development/SKILL.md` |
| `agents/sysadmin.md` | Retired → Skill | Interactive host triage; no isolation need | `systems-infrastructure` | `plugins/systems-infrastructure/.apm/skills/administering-unix-systems/SKILL.md` |
| `agents/zero-trust-architect.md` | Retired → Skill | Interactive ZTA/SASE design; no isolation need | `security-and-networking` | `plugins/security-and-networking/.apm/skills/designing-enterprise-networks/SKILL.md` |

---

## 4. Legacy Root Templates & Planning Files

| Legacy Path | Disposition | New Path |
|---|---|---|
| `templates/SEVEN-SECTION-SKILL-TEMPLATE.md` | Moved to skill `assets/templates/` | `plugins/dev-workflow/.apm/skills/evolving-agent-skills/assets/templates/seven-section-skill-template.md` |
| `AI/nextSteps.md` | Moved to `docs/plans/` | `docs/plans/upstream-alignment-next-steps.md` |

---

## 5. Platform & Crow Enrichments

### Additions Enriched from `ag-devops` & [`bcgov/platform-developer-docs`](https://github.com/bcgov/platform-developer-docs) (Apache-2.0)
- **`plugins/openshift-devops` (`deploying-bc-gov-workloads`)**:
  - Added executable scripts (`scripts/{init,scaffold,validate,check_platform_rules}.py` + 56 pytest tests), 4-tool policy-as-code configs (Datree, Polaris, kube-linter, Conftest Rego), and `ag-helm-templates` / Option 2 CI/CD templates.
  - Added Apps-in-Any-Namespace Argo CD `Application`, `GitOpsTeam`, `ImageUpdater`, PostSync `route_with_cert`, `localsmtp` notifications, `allow-user-workload-monitoring`, and `go-crond` templates/guides.
  - Added Artifactory Archeobot CRs & Gold→GoldDR secret sync caveats, `bcgov-docker-local` prebuilt images, RHEL entitlement mounts, Kyverno rules, PID 1 init reapers (`Tini`/`dumb-init`/`s6-overlay`), cluster pruning, load testing policy, and app retirement runbook.
- **`plugins/openshift-devops` (`analyzing-ocp-platforms`)**:
  - Added `PS-05`–`PS-09` standards, CrunchyDB (`PostgresCluster`) vs. standalone Patroni (`nr-patroni-chart`) & `StorageMigration` checks, resource quota defaults & Registry auto-approval thresholds, CPU ratios & CFS throttling PromQL, PDB/QoS/termination caps, defunct PID checks, and `get_ns_resources.sh` export pattern.
- **`plugins/security-and-networking` (`securing-bc-gov-workloads`, `designing-bc-gov-networks`)**:
  - Updated Vault (`platform-services`, `auth/k8s-{silver,gold,golddr,emerald}`, dynamic DB & Transit secrets), ESO `external-secrets.io/v1`, Vault Agent Injector sidecar quota annotations, and Azure Key Vault SecretStore templates.
  - Aligned image audit baseline to `artifacts.developer.gov.bc.ca`, added Red Hat ACS / JFrog Xray / SIEM / `owasp-zap-openshift` controls, added `hosting-tiers-and-porter-tcp.md`, and fixed router-ingress `podSelector` & DNS `53`/`5353`.
- **`plugins/app-engineering` (`instrumenting-observability`, `building-bc-gov-web-apps`)**:
  - Added `sysdig-and-loki-monitoring.md` (`SysdigTeam`, `ServiceMonitor` vs. Sysdig Promscrape, AlertManager cadences, `AlertmanagerConfig` SMTP template, Loki routing, Sysdig quota/PVC PromQL) and `sysdigteam.tpl.yaml` / `servicemonitor.tpl.yaml`.
  - Added `bc-gov-reusable-services.md` (CDOGS, CHES, COMS, SonarCloud, `bcgov-docker-local` images), Pathfinder CSS vs. `onestopauth*` realm clarity, Gold/GoldDR DR, and `platform-services` Vault KV paths.

### Additions Enriched from [`bcgov/crow`](https://github.com/bcgov/crow) (MIT License, Copyright (c) 2026 Christian Baerike)
- **`plugins/dev-workflow` (`managing-github-workflows`, `managing-dev-sessions`)**:
  - Augmented `sast-and-release-ci.md` & `rulesets-and-ci.md` with Sonar `projectVersion`/`sonar.qualitygate.wait=true`/fork-PR isolation, fail-closed test/report gates, `actionlint`, PR fast vs. nightly deep test splits, rebuild-from-SHA approval-gated releases, runtime-vs-library dependency batching & 1-year abandonment checks, GitHub PR pagination + steelman code review, and `# crow-debt:` markers.
  - Added `project-context-manifest.md` (public-safe symbolic manifest) and `Verified/Inferred/Unknown` + single-writer ownership rules to `process-knowledge.md`.
- **`plugins/openshift-devops` (`auditing-cicd-governance`, `analyzing-ocp-platforms`, `deploying-bc-gov-workloads`)**:
  - Augmented `control-matrix-and-deliverables.md` (`CM-01`–`CM-04`) with blocking Sonar gate checks, Azure/Jenkins secret & polling traps, DB-migration artifact packaging vs. execution, and rebuild-from-SHA release checks; added `## Application & Release Continuity` (N-1 overlap, expand-contract DB evolution, worker drain, shared `terminationGracePeriodSeconds` budget) to `resilience-checks-r01-r15.md`.
- **`plugins/security-and-networking` (`securing-bc-gov-workloads`)**:
  - Augmented `owasp-dotnet-react-oidc.md` with ASP.NET Core middleware/antiforgery/JWT-alg/Data Protection/`ForwardedHeaders` blind spots, SPA `javascript:`/bundle-env/client-guard/state checks, real-wiring test assurance, and stateful invariants; added `llm-and-markdown-security.md`.
- **`plugins/app-engineering` (`building-dotnet-apis`, `building-bc-gov-web-apps`, `instrumenting-observability`)**:
  - Added Indigenous-language UTF-8/ICU readiness, RFC 9457 `ProblemDetails`, Polly v8 (`Microsoft.Extensions.Http.Resilience`), `Asp.Versioning`, narrow-question APIs, `ux-and-accessibility-patterns.md` (WCAG 2.2 AA deltas, sensitive-field masking, consequential decision UX), `dotnet-engineering-standards.md`, and `application-diagnostics-and-errors.md` (W3C `traceId`, UI error surface matrix, safe stand-ins).
