# Multi-App Orchestration (Phases 0–5)

Repeatable orchestration pattern for structured analysis of 2+ interconnected BC Gov OCP applications.

## Contents

- [Pre-Flight Checklist](#pre-flight-checklist)
- [Phase 0 — Repository Scaffold](#phase-0--repository-scaffold)
- [Phase 1 — Parallel OCP + GitHub Capture](#phase-1--parallel-ocp--github-capture)
- [Phase 1b — Multi-App Coupling Matrix](#phase-1b--multi-app-coupling-matrix)
- [Phase 2 — Parallel Per-App Deep-Dives](#phase-2--parallel-per-app-deep-dives)
- [Phase 3 — Cross-Cutting Reports](#phase-3--cross-cutting-reports)
- [Phase 4 — Skill/Toolkit Extraction](#phase-4--skilltoolkit-extraction)
- [Phase 5 — Executive Summary & Packaging](#phase-5--executive-summary--packaging)
- [Sanitized Multi-App Knowledge](#sanitized-multi-app-knowledge)

---

## Pre-Flight Checklist

- [ ] `oc whoami` succeeds on source cluster (Silver, Gold, or other)
- [ ] `gh auth status` confirms GitHub CLI authenticated
- [ ] Target namespace prefixes confirmed (`<prefix1>`, `<prefix2>`, `<prefix3>`)
- [ ] GitHub repositories identified for each app
- [ ] Private output repo scaffolded (Phase 0)
- [ ] `ocp-migration-toolkit` and `container-network-analysis-toolkit` cloned and executable

---

## Phase 0 — Repository Scaffold

```bash
gh repo create <org>/<analysis-repo> --template <org>/rl-project-template --private
git clone git@github.com:<org>/<analysis-repo>.git
cd <analysis-repo>

mkdir -p AI/OCP-CLI-CAPTURES/{<ns1>,<ns2>,<ns3>}
mkdir -p AI/REPO-CAPTURES docs/skill-proposals report/apps/{<app1>,<app2>,<app3>} report/cross-cutting diagrams scripts
```

Output structure:

```text
<analysis-repo>/
├── AI/
│   ├── OCP-CLI-CAPTURES/
│   │   ├── <ns1>-dev/
│   │   ├── <ns2>-dev/
│   │   └── <ns3>-dev/
│   ├── REPO-CAPTURES/          # GitHub repo snapshots + coupling matrix
│   └── nextSteps.md            # session continuity log
├── docs/skill-proposals/       # Phase 4 skill extraction candidates
├── report/
│   ├── apps/<app>/             # per-app deep-dive report
│   └── cross-cutting/          # cross-app analysis reports
├── diagrams/                   # architecture + data flow diagrams
└── scripts/                    # collection scripts and helpers
```

---

## Phase 1 — Parallel OCP + GitHub Capture

Run collection for **each** application namespace (see [oc-collection-and-toolkits.md](oc-collection-and-toolkits.md)). For cross-namespace flow capture:

```bash
cd container-network-analysis-toolkit
./collect.sh --namespaces "<ns1>,<ns2>,<ns3>" --output ../AI/OCP-CLI-CAPTURES/
```

---

## Phase 1b — Multi-App Coupling Matrix

Run Phase 1b **before** Phase 2 per-app deep-dives and Phase 3 cross-cutting reports whenever 2+ apps share cross-namespace NetworkPolicies, Keycloak realms, S3 buckets, SMTP relays, Redis streams, or CORS origins.

### Signals & Collection Commands

| Signal | Collection command |
|---|---|
| Cross-namespace NPs | `oc get networkpolicies -A -o json \| jq '.items[] \| select(.spec.ingress[]?.from[]?.namespaceSelector != null or .spec.egress[]?.to[]?.namespaceSelector != null) \| {ns: .metadata.namespace, name: .metadata.name}'` |
| CORS origins | `grep -r "CORS\|allowed.origin\|Access-Control" working/repo --include="*.yaml" --include="*.env*" --include="*.json" -l` |
| Shared ConfigMaps | Check for identical service URLs across multiple namespace ConfigMaps |
| Redis stream keys | `oc get configmaps -n <ns> -o json \| jq '.items[] \| .data \| to_entries[] \| select(.key \| test("STREAM\|TOPIC\|QUEUE")) \| {key, value}'` |
| Shared external services | Cross-reference Keycloak realm URLs, object storage bucket names, SMTP hosts across ConfigMaps |

### Output: `AI/REPO-CAPTURES/coupling-matrix.md`

Include tables for:
- **Cross-Namespace Network Links**: `Source NS | Target NS | NP Name | Direction | Scoped?`
- **HTTP Service Calls (Cross-App)**: `Caller App | Target App | URL Pattern | Protocol/Port | Via Public Route?`
- **Redis Stream Keys**: `Stream Key | Producer NS | Consumer NS`
- **Shared Object Storage**: `Bucket / Prefix | Apps Sharing`
- **Shared External Services**: `Service | Type | Apps Using`
- **Keycloak Clients**: `App | Realm | Client ID`
- **Database Isolation**: `App | DB Host | DB Name | Shared With`
- **Stale / Orphaned Resources**: `Resource | Namespace | Last Active | Notes`

### Migration Sequencing Rule

**Migrate the most-upstream (least-dependent) app first.**

- If `<app-a>` calls `<app-b>`, migrate `<app-b>`'s network-facing surface (Routes, Services) before `<app-a>`'s cutover.
- Apps with no direct K8s service calls to each other (only via public Routes) can be migrated in parallel.
- Shared infrastructure (Redis, S3, Keycloak) must be available in the target environment before any dependent app cutover.

```text
<app-c>   (consumed by <app-b> — migrate first)
   ↓
<app-b>   (consumed by <app-a> — migrate second)
   ↓
<app-a>   (end-user facing — migrate last)
```

---

## Phase 2 — Parallel Per-App Deep-Dives

Produce `report/apps/<app>/<program-area>-<app>-deep-dive-v1.md` in parallel where apps have no write-dependency on each other. Each deep-dive has **9 sections**:

1. Executive Summary
2. Architecture Overview
3. Application Resiliency
4. Container Resiliency (R01–R15)
5. Security
6. Network
7. BC Gov Standards Compliance
8. Findings Backlog (prioritised by risk)
9. Sources and Evidence

Delegate raw manifest parsing per domain: `ocp-resilience-analyst` (workloads, PDBs, PVCs, quotas), `security-architect` (images, RBAC, Containerfiles), `bc-gov-network-architect` (NPs, Routes, coupling matrix), `deploying-bc-gov-workloads` (Emerald/DevOps standards), `observability` (logging/tracing), `bc-gov-iam` (Keycloak clients).

---

## Phase 3 — Cross-Cutting Reports

Produce under `report/cross-cutting/`:

| Report | File | Content |
|---|---|---|
| Network Connectivity | `<program-area>-network-connectivity-v1.md` | Inter-app flows, cross-namespace NPs, cross-cluster paths, risk classification |
| Emerald Migration | `<program-area>-emerald-migration-v1.md` | Gap analysis across all apps, coupling-matrix sequencing, phase plan |
| Standards Deviation Matrix | `<program-area>-standards-deviation-v1.md` | Side-by-side comparison of all apps against Emerald/DevOps standards |
| Resiliency Rollup | `<program-area>-resiliency-rollup-v1.md` | R01–R15 grades across all apps in a single table |
| Security Rollup | `<program-area>-security-rollup-v1.md` | Cross-app security findings, image provenance, RBAC, PII risk, data residency |

---

## Phase 4 — Skill/Toolkit Extraction

Document reusable patterns at `docs/skill-proposals/<topic>.md` (observed pattern, concrete evidence, generalised rule, target skill) and raise PRs against `<org>/rl-agents-n-skills` after engagement completion.

---

## Phase 5 — Executive Summary & Packaging

Produce `report/<program-area>-executive-summary-v1.md` with a RAG traffic-light table (`🟢` / `🟡` / `🔴`) across Application Resiliency, Container Resiliency, Security, Network, BC Gov Standards, Observability, and Emerald Migration Readiness.

Additional deliverables:
- `PROD-ACCESS-ASK.md` — explicit list of production access required to complete prod-dependent findings
- Architecture, data flow, and network topology diagrams
- PDF render of all reports and `git tag v1.0 && git push --tags`

---

## Sanitized Multi-App Knowledge

- 2026-06-05: [multi-app-engagement] Parallel per-app deep-dives require coupling matrix first — sequencing without coupling matrix risks missing shared-infrastructure dependencies.
- 2026-06-05: [multi-app-engagement] Phase 3 cross-cutting reports are higher value than per-app reports for executive stakeholders — prioritise these if time is constrained.
- 2026-06-05: [multi-app-engagement] Skill extraction (Phase 4) is most effective when done continuously during the engagement, not as a post-engagement batch.
