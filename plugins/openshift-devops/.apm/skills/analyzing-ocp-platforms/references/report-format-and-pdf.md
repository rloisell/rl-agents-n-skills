# Report Format & PDF Rendering

Canonical report structure, versioning rules, required metadata header, CSS visual standard, and Pandoc + headless Chrome PDF rendering.

## Contents

- [File Naming and Versioning](#file-naming-and-versioning)
- [Document Header (Required)](#document-header-required)
- [Table of Contents, Section Numbering & Footer](#table-of-contents-section-numbering--footer)
- [Standards Column (Required)](#standards-column-required)
- [Report Section Structures](#report-section-structures)
- [Copilot Utilization & Appendix Guidance](#copilot-utilization--appendix-guidance)
- [Visual Standard (`report-style.css`)](#visual-standard-report-stylecss)
- [PDF Rendering Commands](#pdf-rendering-commands)

---

## File Naming and Versioning

```text
<APP-NAME>-Migration-Analysis.md        # Migration report (or -v<N>.md)
<APP-NAME>-Migration-Analysis.pdf       # Rendered PDF
<APP-NAME>-Resilience-Report-v<N>.md    # ALWAYS version-numbered
<APP-NAME>-Resilience-Report-v<N>.pdf   # PDF parity required
```

- Never save resilience reports without `-v<N>` (`v1`, `v2`, ...).
- Never overwrite a previous version — create `v(N+1)` from a copy of `vN`.
- Every `.md` version must have a matching `.pdf`.

---

## Document Header (Required)

**Each metadata line must end with two trailing spaces (`  `)** to force a Markdown line break in the rendered PDF.

```markdown
# <APP_NAME> — Migration Analysis Report (or OpenShift Resilience Posture Report)
## OpenShift <SOURCE_PLATFORM> (<NAMESPACE>) → <TARGET_PLATFORM> Platform Migration

**Classification:** Protected B — Internal Use  
**Prepared by:** <Author Name>, Solution Architect Consultant (<Ministry / Program Area>) — Analysis, architecture review, and implementation planning  
**Prepared for:** <PRODUCT_OWNER_NAME>, Product Owner — for review and handoff to the implementation team  
**AI Analysis by:** GitHub Copilot — Technical analysis, gap identification, and documentation  
**Date:** <DATE> (v<N> — <brief description>)  
**Previous version:** v<N-1> (<DATE> — <what changed>) ← omit on v1  
**Namespace:** <ns-prefix> (<envs>) — <SOURCE_PLATFORM>, <dc-location>  
**Repository:** <REPO_URL>  
**Analysis scope:** Read-only — no changes made to repo, deployments, or environments.

<div style="page-break-after: always"></div>
```

---

## Table of Contents, Section Numbering & Footer

- Follow the header with a numbered, anchor-linked `## Table of Contents`.
- Top-level sections use `## N. Section Name`; subsections use `### N.M Subsection Name`.
- End every report with a footer:

```markdown
*Prepared by: <Author Name> (<Ministry / Program Area>) | AI Analysis: GitHub Copilot | Generated: <DATE> (v<N> — <description>)*
```

---

## Standards Column (Required)

Every finding in the Resilience Scorecard / Gap table and every remediation task table MUST include a `Standard` column citing IDs from [standards-catalog.md](standards-catalog.md):

```markdown
| ID | Category | Grade | Status | Affected Workloads | Standard |
|---|---|---|---|---|---|
| R04 | Liveness probe missing | D | ⛔ HIGH | All 3 `<app-a>` adapters | K8S-02; PS-03 |
```

```markdown
| Task | Category | Description | Effort | Standard |
|---|---|---|---|---|
| RES-01 | Probes | Add liveness probe ... | 2h | K8S-02; PS-03 |
```

---

## Report Section Structures

### Migration Report (12 Sections)

1. Executive Summary
2. Current State — Technical
3. Security and Programmatic Concerns
4. Distributed Tracing and Observability
5. Gap Analysis (G1–G12)
6. Network Flow Analysis
7. Resilience and Availability
8. Resource and Capacity Planning
9. Migration Plan — Task List (`HELM-XX`, `NP-XX`, `CI-XX`, `APP-XX`, `VAULT-XX`, `DATA-XX`, `ARCH-XX`)
10. Effort Estimation (task × AI-assist level × estimated hours)
11. Diagrams (PlantUML source state + target state)
12. Appendices (namespace inventory, raw manifests, FWCR templates, Vault paths)

### Resilience Report (13 Sections)

1. Executive Summary (with Resilience Scorecard table)
2. Workload Inventory
3. PodDisruptionBudget Analysis
4. Scaling & Autoscaling Configuration
5. Health Probe Analysis
6. Pod Scheduling & Anti-Affinity
7. Graceful Termination & Deployment Strategy
8. Resource Quality of Service (QoS)
9. Storage Resilience
10. Disruption Simulation (node drain / zone failure / upgrade)
11. Remediation Tasks (`RES-NN`, prioritized)
12. Appendix
13. Sources and References

---

## Copilot Utilization & Appendix Guidance

Include **Section 9.6 GitHub Copilot Utilization** (table of task categories, AI-assist icons `🤖`/`🤝`/`👤`/`💼`, estimated effort reduction, and submodule/`npx skills add` setup) and an **Appendix** mapping domain skills/agents to task IDs and example invocations.

---

## Visual Standard (`report-style.css`)

Every report PDF MUST be rendered with `report-style.css`:

| Property | Value |
|---|---|
| Body font | `Helvetica Neue, Helvetica, Arial, sans-serif` |
| Cover title colour | `#003366` (BC Gov navy) |
| Table header background | `#003366` (white text) |
| Table row stripe | `#f2f5f9` (even rows) |
| Table cell border | `1px solid #c8d0d8` |
| Section page breaks | All `h2` sections break to new page |

---

## PDF Rendering Commands

Always run from the report directory so relative image paths resolve correctly.

### macOS

```bash
cd <report-dir>
pandoc <REPORT>.md \
  --from=gfm --to=html5 --standalone \
  --css=report-style.css --embed-resources \
  --output=/tmp/report.html \
  --metadata title="<APP> — Analysis Report"

"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu \
  --print-to-pdf=<REPORT>.pdf \
  --print-to-pdf-no-header --no-pdf-header-footer \
  file:///tmp/report.html 2>/dev/null
```

### Linux (GitHub Actions / Container)

```bash
google-chrome-stable --headless --disable-gpu \
  --print-to-pdf=<REPORT>.pdf \
  --print-to-pdf-no-header --no-pdf-header-footer \
  file:///tmp/report.html
```
