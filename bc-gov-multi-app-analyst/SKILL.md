---
name: bc-gov-multi-app-analyst
description: Multi-app BC Gov OCP analysis orchestrator — phases 0-5, coupling matrix, per-app deep-dive template, cross-cutting reports, and PDF packaging.
tools: Bash, Read, Write, Grep, Glob, agent
user-invocable: true
metadata:
  author: Ryan Loiselle
  version: "1.0"
compatibility: >
  BC Gov OCP Silver/Gold/Emerald. Requires: oc CLI (logged in), gh CLI (authenticated),
  pandoc + Chrome headless for PDF render. Uses ocp-migration-toolkit and
  container-network-analysis-toolkit repos.
---

# BC Gov Multi-App Analyst

Repeatable orchestration pattern for structured analysis of 2+ interconnected BC Gov OCP applications.

---

## Pre-Flight Checklist

Before starting any phase, verify:

- [ ] `oc whoami` succeeds on source cluster (Silver, Gold, or other)
- [ ] `gh auth status` confirms GitHub CLI authenticated
- [ ] Target namespace prefixes confirmed (e.g. `<prefix1>`, `<prefix2>`, `<prefix3>`)
- [ ] GitHub repositories identified for each app
- [ ] Output repo scaffolded (see Phase 0)
- [ ] `ocp-migration-toolkit` cloned and `collect.sh` executable
- [ ] `container-network-analysis-toolkit` cloned and `collect.sh` executable (for cross-namespace flows)

---

## Phase 0 — Repository Scaffold

Set up the analysis repository using `rl-project-template` with the `rl-agents-n-skills` submodule.

```bash
# Clone template and initialise
gh repo create <org>/<analysis-repo> --template rloisell/rl-project-template --private
git clone git@github.com:<org>/<analysis-repo>.git
cd <analysis-repo>

# Add agents submodule
git submodule add git@github.com:rloisell/rl-agents-n-skills.git .agents

# Create output directory structure
mkdir -p AI/OCP-CLI-CAPTURES/{<ns1>,<ns2>,<ns3>}
mkdir -p AI/REPO-CAPTURES
mkdir -p docs/skill-proposals
mkdir -p report/apps/{<app1>,<app2>,<app3>}
mkdir -p report/cross-cutting
mkdir -p diagrams
mkdir -p scripts
```

Output structure:
```
<analysis-repo>/
├── AI/
│   ├── OCP-CLI-CAPTURES/
│   │   ├── <ns1>-dev/          # raw oc output per namespace
│   │   ├── <ns2>-dev/
│   │   └── <ns3>-dev/
│   ├── REPO-CAPTURES/          # GitHub repo snapshots + coupling matrix
│   └── nextSteps.md            # session continuity log
├── docs/
│   └── skill-proposals/        # Phase 4 skill extraction candidates
├── report/
│   ├── apps/
│   │   ├── <app1>/             # per-app deep-dive report
│   │   ├── <app2>/
│   │   └── <app3>/
│   └── cross-cutting/          # cross-app analysis reports
├── diagrams/                   # architecture + data flow diagrams
└── scripts/                    # collection scripts and helpers
```

---

## Phase 1 — Parallel OCP + GitHub Capture

Run for **each** application namespace. Use `ocp-migration-toolkit/collect/collect.sh` for automated collection.

```bash
# Per namespace — automated collection
cd ocp-migration-toolkit
./collect/collect.sh \
  --namespace <prefix> \
  --cluster silver \
  --repo <org>/<repo> \
  --target emerald \
  --output ../AI/OCP-CLI-CAPTURES/
```

If manual collection is needed, run these commands per namespace:
```bash
NS=<prefix>-dev
oc get dc,deployment,statefulset,daemonset -n $NS -o yaml > AI/OCP-CLI-CAPTURES/$NS/workloads.yaml
oc get svc,route -n $NS -o yaml > AI/OCP-CLI-CAPTURES/$NS/network-svc-routes.yaml
oc get networkpolicy -n $NS -o yaml > AI/OCP-CLI-CAPTURES/$NS/networkpolicies.yaml
oc get pvc -n $NS -o yaml > AI/OCP-CLI-CAPTURES/$NS/pvcs.yaml
oc get secret -n $NS --no-headers | awk '{print $1, $2}' > AI/OCP-CLI-CAPTURES/$NS/secret-names.txt
oc get configmap -n $NS -o json > AI/OCP-CLI-CAPTURES/$NS/configmaps.json
oc get rolebinding -n $NS -o yaml > AI/OCP-CLI-CAPTURES/$NS/rolebindings.yaml
oc get pods -n $NS -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{range .spec.containers[*]}{.image}{"\n"}{end}{end}' > AI/OCP-CLI-CAPTURES/$NS/image-refs.txt
oc get events -n $NS --sort-by='.lastTimestamp' | tail -30 > AI/OCP-CLI-CAPTURES/$NS/events.txt
```

For cross-namespace flow capture:
```bash
cd container-network-analysis-toolkit
./collect.sh --namespaces "<ns1>,<ns2>,<ns3>" --output ../AI/OCP-CLI-CAPTURES/
```

---

## Phase 1b — Multi-App Coupling Matrix

See `ocp-migration-analyst/SKILL.md` Phase 1b for the full coupling matrix collection workflow.

Output file: `AI/REPO-CAPTURES/coupling-matrix.md`

The coupling matrix must be produced **before** Phase 2 per-app deep-dives and before Phase 3 cross-cutting reports, because:
- It determines migration sequencing (most upstream app first)
- It identifies shared infrastructure that must be present in the target before any app cutover
- It surfaces cross-namespace NPs that affect network security posture

---

## Phase 2 — Parallel Per-App Deep-Dives

For each application, produce a deep-dive report at `report/apps/<app>/<program-area>-<app>-deep-dive-v1.md`.

Run per-app analyses **in parallel** where apps have no write-dependency on each other's output.

Each deep-dive report has **9 sections**:

```
## 1. Executive Summary
## 2. Architecture Overview
## 3. Application Resiliency
## 4. Container Resiliency (R01–R15 against OCP Resilience Toolkit criteria)
## 5. Security
## 6. Network
## 7. BC Gov Standards Compliance
## 8. Findings Backlog (prioritised by risk)
## 9. Sources and Evidence
```

### Per-App Sub-Agent Invocations

For each deep-dive, invoke these sub-agents with the collected data as context:

| Section | Sub-agent | Input |
|---|---|---|
| App Resiliency | `ocp-resilience-analyst` | workloads.yaml, pvcs.yaml, resource-quotas.yaml |
| Container Resiliency R01-R15 | `ocp-resilience-analyst` | image-refs.txt, workloads.yaml |
| Security | `security-architect` | image-refs.txt, rolebindings.yaml, Containerfiles from repo |
| Network | `bc-gov-network-architect` | networkpolicies.yaml, network-svc-routes.yaml, coupling-matrix.md |
| BC Gov Standards | `bc-gov-devops` + `bc-gov-emerald` | workloads.yaml, repo CI workflows |
| Observability | `observability` | workloads.yaml, repo source code (logging patterns) |
| IAM | `bc-gov-iam` | Keycloak clients from coupling-matrix.md, repo OIDC config |

---

## Phase 3 — Cross-Cutting Reports

Produce these reports at `report/cross-cutting/`:

| Report | File | Sub-agent(s) | Content |
|---|---|---|---|
| Network Connectivity | `<program-area>-network-connectivity-v1.md` | `bc-gov-network-architect` | All inter-app flows, cross-namespace NPs, cross-cluster paths, risk classification |
| Emerald Migration | `<program-area>-emerald-migration-v1.md` | `ocp-migration-analyst` | Gap analysis across all apps, migration sequencing from coupling matrix, phase plan |
| Standards Deviation Matrix | `<program-area>-standards-deviation-v1.md` | `bc-gov-devops` | Side-by-side comparison of all apps against Emerald/DevOps standards |
| Resiliency Rollup | `<program-area>-resiliency-rollup-v1.md` | `ocp-resilience-analyst` | R01-R15 grades across all apps in a single table |
| Security Rollup | `<program-area>-security-rollup-v1.md` | `security-architect` | Cross-app security findings, image provenance, RBAC, PII risk, data residency |

---

## Phase 4 — Skill/Toolkit Extraction

As patterns emerge during the analysis, document reusable knowledge for the skill library.

For each candidate pattern:
1. Create a file at `docs/skill-proposals/<topic>.md`
2. Document: the pattern observed, the concrete evidence, the generalised rule, and which skill to add it to
3. After engagement completion, raise PRs against `rloisell/rl-agents-n-skills` for each accepted skill update

Examples of reusable patterns extracted from past engagements:
- Cross-namespace NP risk classification → `bc-gov-network-architect`
- PII-in-logs checklist (Python/Go/Node.js) → `observability`
- RBAC CronJob anti-pattern → `security-architect`
- Image provenance risk tiers → `security-architect`
- External cloud data residency pattern → new `data-flow-lineage` skill

---

## Phase 5 — Executive Summary and Packaging

### Executive Summary

Produce `report/<program-area>-executive-summary-v1.md` with a RAG (Red/Amber/Green) traffic-light table:

```markdown
| Dimension | <App1> | <App2> | <App3> |
|---|---|---|---|
| Application Resiliency | 🟡 | 🔴 | 🟡 |
| Container Resiliency | 🔴 | 🔴 | 🟡 |
| Security | 🔴 | 🔴 | 🟡 |
| Network | 🟡 | 🟡 | 🟢 |
| BC Gov Standards | 🟡 | 🟡 | 🟡 |
| Observability | 🟡 | 🟡 | 🟡 |
| Emerald Migration Readiness | 🔴 | 🔴 | 🟡 |
```

### Additional Deliverables

- `PROD-ACCESS-ASK.md` — explicit list of production access required to complete findings that need prod data
- Diagrams: architecture overview, data flow, network topology (use `diagram-generation` agent)
- PDF render of all reports: `pandoc <report>.md -o <report>.pdf --pdf-engine=wkhtmltopdf`
- Git tag: `git tag v1.0 && git push --tags`

---

## BC_GOV_FOI_ORCHESTRATOR_KNOWLEDGE

<!-- agent-evolution appends discoveries here -->
<!-- Format: - YYYY-MM-DD: [engagement] <imperative statement> -->
- 2026-06-05: [multi-app-engagement] Parallel per-app deep-dives require coupling matrix first — sequencing without coupling matrix risks missing shared-infrastructure dependencies
- 2026-06-05: [multi-app-engagement] Phase 3 cross-cutting reports are higher value than per-app reports for executive stakeholders — prioritise these if time is constrained
- 2026-06-05: [multi-app-engagement] Skill extraction (Phase 4) is most effective when done continuously during the engagement, not as a post-engagement batch
