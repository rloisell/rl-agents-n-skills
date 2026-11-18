# security-and-networking Plugin

## Purpose

BC Gov application security, HashiCorp Vault secrets, data lineage/STRA/PIA, Zero Trust / SASE, and enterprise & OpenShift networking.

## Plugin Components

APM and Claude Code auto-discover primitives under `.apm/`.

### Skills

- `securing-bc-gov-workloads` — OWASP Top 10 (.NET 10 / React), OIDC PKCE, container security baseline, HashiCorp Vault & ESO, BC Gov Database Security Standard (23 controls), OpenShift RBAC & image provenance audits, and STRA/PIA gates.
- `mapping-data-lineage` — ISCF data classification, data flow ledger templates, cross-boundary risk matrix, FOIPPA s.30.1 cloud residency checks, OpenShift ConfigMap/env discovery commands, and PIA trigger checklists.
- `designing-enterprise-networks` — Zero Trust Architecture (NIST SP 800-207) & SASE design, routing/switching/WAN (OSPF, BGP, EIGRP, STP, MPLS, SD-WAN, IPsec, QoS), IOS/IOS-XE ACL/NAT/ZBF/L2 hardening, and BC Gov IMIT 6.28/6.13/5.08 control mapping.
- `designing-bc-gov-networks` — BC Gov SDN security classification (Low/Medium/High), IMIT 6.13 zones & 5.08 Third Party Gateway (3PG) / Forward Proxy egress, and OpenShift NetworkPolicy authoring (`two-policy rule`, `ag-helm` intent API).
- `auditing-ocp-network-posture` — Multi-namespace OpenShift network posture collection (`oc`/`jq`), cross-namespace & stale NetworkPolicy gap analysis, Route TLS & admin UI auditing, third-party egress classification, and 6-section Markdown/PDF report rendering.

### Sub-Agents

- `security-architect` — Independent, read-only (`Read`, `Grep`, `Glob`) adversarial security and STRA/PIA reviewer preloading `securing-bc-gov-workloads` and `mapping-data-lineage`.
- `container-network-analyst` — Isolated-context OpenShift network posture analyst (`Read`, `Grep`, `Glob`, `Bash`) for multi-namespace `oc`/NP/Route YAML dumps, preloading `auditing-ocp-network-posture` and `designing-bc-gov-networks`.

### Hooks

None.

## Directory Structure

```text
security-and-networking/
├── .apm/
│   ├── agents/
│   │   ├── container-network-analyst.md
│   │   └── security-architect.md
│   └── skills/
│       ├── auditing-ocp-network-posture/
│       ├── designing-bc-gov-networks/
│       ├── designing-enterprise-networks/
│       ├── mapping-data-lineage/
│       └── securing-bc-gov-workloads/
├── .claude-plugin/
│   └── plugin.json
├── apm.yml
└── README.md
```
