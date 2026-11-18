# openshift-devops Plugin

BC Gov Emerald OpenShift deployment, CI/CD pipelines, platform migration, resilience, and governance audits.

## Purpose

Provides self-contained skills and isolated sub-agents for deploying workloads to BC Gov Emerald OpenShift, analyzing OpenShift platforms for migration readiness and workload resilience, and auditing CI/CD deployment governance.

## Plugin Components

APM and Claude Code auto-discover primitives under `.apm/`.

### Skills

| Skill | Description |
|---|---|
| `deploying-bc-gov-workloads` | Containerfile standards (port 8080, non-root), GitHub Actions ISB EA Option 2 CI/CD, Emerald platform mechanics (AVI InfraSettings, `DataClass`, `PriorityClass`, SCC), `ag-helm-templates` + policy-as-code gate, and NetworkPolicy patterns |
| `analyzing-ocp-platforms` | OpenShift migration gap analysis (G1–G12), workload resilience posture assessment (R01–R15), multi-app coupling matrix orchestration, and versioned PDF report generation |
| `auditing-cicd-governance` | Evidence-based CI/CD governance audits for SaaS, container, and hybrid delivery pipelines with control matrices (`CM-01`–`CM-05`) and phased remediation roadmaps |

### Sub-Agents

| Sub-Agent | Purpose |
|---|---|
| `ocp-migration-analyst` | Context-isolated parsing of raw `oc get -o yaml` namespace dumps for G1–G12 migration gap analysis and network flow mapping (preloads `analyzing-ocp-platforms`) |
| `ocp-resilience-analyst` | Context-isolated parsing of raw workload, PDB, HPA, PVC, and pod YAML dumps for R01–R15 resilience scoring and `RES-NN` task generation (preloads `analyzing-ocp-platforms`) |

### Hooks

None.

## Directory Structure

```text
openshift-devops/
├── .apm/
│   ├── agents/
│   │   ├── ocp-migration-analyst.md
│   │   └── ocp-resilience-analyst.md
│   └── skills/
│       ├── analyzing-ocp-platforms/
│       │   ├── SKILL.md
│       │   └── references/
│       ├── auditing-cicd-governance/
│       │   ├── SKILL.md
│       │   └── references/
│       └── deploying-bc-gov-workloads/
│           ├── SKILL.md
│           └── references/
├── .claude-plugin/
│   └── plugin.json
├── apm.yml
└── README.md
```
