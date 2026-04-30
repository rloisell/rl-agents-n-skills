---
name: bc-gov-sdn-zones
description: BC Government network security classification and zone model. Use when determining what security zone a workload belongs to, mapping ISCF data classification to DataClass labels, designing connectivity between zones, evaluating internet egress constraints, or planning Third Party Gateway (3PG) connections to external partners.
tools: Read, Grep, Glob
metadata:
  author: Ryan Loiselle
  version: "1.1"
  sources:
    - title: "IMIT 6.13 — Network Security Zones Standard (v5)"
      url: "https://intranet.gov.bc.ca/assets/intranet/mtics/ocio/es/enterprise-services-division/information-security-branch/information-security-standards-and-guidelines/imit_613_network_security_zones_standard_v5.pdf"
      access: "BC Gov intranet"
    - title: "IMIT 6.13 — Network Security Zones Specifications (v1)"
      url: "https://intranet.gov.bc.ca/assets/intranet/mtics/ocio/es/enterprise-services-division/information-security-branch/information-security-standards-and-guidelines/imit_613_network_security_zones_specs_v1.pdf"
      access: "BC Gov intranet"
    - title: "IMIT 5.08 — Network-to-Network Connectivity Security Standard (v2.0, 2022)"
      url: "https://www2.gov.bc.ca/assets/gov/government/services-for-government-and-broader-public-sector/information-technology-services/standards-files/imit_508_network_to_network_connectivity_standard.pdf"
    - title: "IMIT 5.08 — Network-to-Network Connectivity Security Specifications (v1.0, 2022)"
      url: "https://www2.gov.bc.ca/assets/gov/government/services-for-government-and-broader-public-sector/information-technology-services/standards-files/imit_508_network-to-network_connectivity_specifications.pdf"
    - title: "IMIT 6.28 — Network and Communications Security Standard (v5.0, 2022; reviewed 2024)"
      url: "https://www2.gov.bc.ca/assets/gov/government/services-for-government-and-broader-public-sector/information-technology-services/standards-files/09_-_communications_security_standard_v10.pdf"
    - title: "IMIT 6.28 — Network and Communications Security Specifications (v1.0, 2024)"
      url: "https://www2.gov.bc.ca/assets/gov/government/services-for-government-and-broader-public-sector/information-technology-services/standards-files/imit_628_netowrk_and_communications_security_specifications.pdf"
    - title: "OCIO SDN Security Classification Model v1.0 (2022)"
    - title: "OCIO IMIT 6.18 — Information Security Classification Standard (ISCF)"
    - title: "ASRB SEP Network Zones submission v4.1"
compatibility: All BC Government workloads. SDN model applies to OpenShift Private Cloud (Silver, Gold, Emerald) and legacy gov.bc.ca network.
---

# BC Gov Network Security Classification & Zone Model

Core BC Government network architecture knowledge. Platform-independent — applies before
you write a single line of NetworkPolicy or Helm chart.

For Emerald-specific enforcement mechanics (AVI, pod labels), see `bc-gov-emerald`.
For NetworkPolicy YAML patterns, see `bc-gov-networkpolicy`.

---

## Information Security Classification Framework (ISCF)

The ISCF (IMIT 6.18) defines how sensitive government information is classified.
Every workload's `DataClass` label and network zone placement must be derived from ISCF.

> **Classify by data the workload is *responsible for storing*, not data it can access.**
> An application server that processes Protected B data in memory and forwards it to a
> database is *Low* (or *Medium* if it caches sensitive content); the database is *High*.
> — SDN Security Classification Model v1.0 §Guiding Principles

| ISCF Class | Examples | OpenShift `DataClass` | SDN classification | IMIT 6.13 zone |
|---|---|---|---|---|
| Public / Unclassified | Public websites, open data, IP addresses in raw access logs (subject to handling rules) | `Low` | Low | DMZ |
| Protected A | Low-sensitivity personal info, internal business | `Medium` | Medium | Zone B |
| Protected B (lower-risk) | Some medical / financial records | `Medium` | Medium | Zone B |
| Protected B (higher-risk) | Sensitive personal data, investigative records | `High` | High | Zone A |
| Protected C | Cabinet records, law enforcement data, classified | `High` | High | Zone A |

> Rule: **classify the data, then assign the zone.** Never infer classification from where a
> workload currently lives. Workload examples by classification:
>
> - **Low**: web frontends, application servers, UIs, APIs (no sensitive data at rest)
> - **Medium**: databases, file servers, analytics services storing Protected A / lower Protected B
> - **High**: databases, sensitive file stores, data warehouses storing Protected B (higher-risk) / Protected C

---

## SDN Security Classification Model (Low / Medium / High)

From the **OCIO SDN Security Classification Model v1.0 (June 2022)** — the workload-centric
model used by SDN tenants (including OpenShift Private Cloud namespaces). The SDN model
coexists with IMIT 6.13's zone model; they map to each other but have distinct enforcement.

**Default-deny applies to all SDN traffic.** Every flow (ingress *and* egress) is denied until
an explicit security policy permits it. Guardrails are global *deny* rules that security policies
cannot override; security policies are *allow* rules within what guardrails permit.

### Low

- Workloads responsible only for public information, or no information at rest
- Maps to: DMZ when traffic exits the SDN to a multi-zone network
- Internet ingress: **denied by default**; permitted only via Public VIP + `Internet-Ingress:ALLOW` tag
- Internet egress: **denied directly**; allowed via the SDN Forward Proxy (whitelist-based)
- A Low workload that is **Internet Accessible** without a WAF cannot reach any High workload
- A Low workload protected by a **Web Application Firewall** (configured + monitored) may reach High workloads
- Typical: web frontends, application servers, UIs, APIs

### Medium

- Workloads responsible for Protected A / lower-risk Protected B information
- Maps to: Zone B when traffic exits the SDN to a multi-zone network
- Internet ingress: **denied** (no Public VIP)
- Internet egress: **denied directly**; allowed via the SDN Forward Proxy
- Medium → Extranet (3PG): denied (Extranet flows route via Low + 3PG controls)
- Typical: databases, file servers, analytics services, data stores

### High

- Workloads responsible for higher-risk Protected B / Protected C information
- Maps to: Zone A when traffic exits the SDN to a multi-zone network
- Internet ingress: **denied** (no Public VIP, even with WAF)
- Internet egress: **denied**; SDN Forward Proxy requires **MISO exemption** (rare; intended for licence / update / call-home use cases only — not API integrations)
- High → Low / Zone DMZ / Zone C / Extranet: **denied by guardrail**
- High accepts ingress only from: Medium, High, Zone A, Zone B, and Low workloads that are *Non-Internet-Accessible* or *Internet-Accessible with WAF*
- Typical: sensitive databases, data warehouses, classified data stores

---

## IMIT 6.13 Zone Model (current, v5 — Aug 2022)

IMIT 6.13 v5 is the **current** Network Security Zones Standard — not historic. It applies to
all core government networks (Data Centre Classic, SPAN/BC) and coexists with the SDN
model above. Zone names persist in firewall rules, IPAM tagging, and partner connectivity.

| Zone | Name | ISCF data at rest | Notes |
|---|---|---|---|
| Internet | — | n/a | All traffic to perimeter is denied by default for common mgmt ports (SSH, RDP, Telnet, SMB, NetBIOS, LDAP/S, Oracle, SQL Server, MySQL, PostgreSQL, ICMP) |
| DMZ | Demilitarized Zone | Public | Hosts proxies, web gateways, citizen-facing interfaces; DMZ servers MUST NOT be in IDIR domain (DMZ AD domain only); apps require Application Vulnerability Scan before placement |
| SPAN/BC | Shared Provincial Access Network | Mixed | ISP-like service; hosts both trusted and untrusted endpoints |
| Extranet | External partner landing zone | Varies | All ingress + egress MUST traverse a 3PG-equivalent infrastructure (per IMIT 5.08) |
| Zone C | Trusted Client Zone | Mostly Public / Protected A | IDIR-managed endpoints (workstations, not server workloads). Sub-zones: **Trusted** (managed device + IDIR), **Semi-trusted** (unmanaged device + IDIR), **Untrusted** (non-IDIR + unmanaged), **BUS** (Building Utility Services). Inter-sub-zone controls require firewall + IPS + anomaly detection. |
| Zone B | High Security Zone | Protected A / Protected B | Internal app tier. Default Internet access = **No Access**. Outbound HTTP/HTTPS via OCIO Forward Proxy or DMZ-hosted proxy. If exception granted: server IP MUST be NAT'd; firewall rules MUST NOT have destination `Any`. |
| Zone A | Restricted High Security Zone | Protected C | Server-to-server only; no user devices. Admin access via SAG (Secure Access Gateway) only. |
| Management Plane | Datacentre operations layer | n/a | Physically separate; internally segmented; no direct access; reached via SAG only; IPs are not Internet-routable |
| Guest / BPS / Pharmanet / Collaboration | Specialty zones | Varies | Internet-bound traffic from Zone C / Guest MUST pass content filtering |

### Mandatory boundary controls (IMIT 6.13 v5 §5)

- **All traffic transiting a zone boundary MUST pass firewall rules + IPS + anomaly detection**
- Internet-bound traffic from Low Security Zones (Zone C, Guest) MUST pass content filtering
- Datacentre-to-datacentre zone extensions MUST be encrypted (per IMIT 6.10) unless using dedicated private circuits
- Servers in DMZ MUST be in DMZ AD domain (trust relationship to IDIR), NOT in IDIR domain
- A server, router, or switch MUST exist in only one non-management zone (no straddling)
- Reverse proxies to a *higher* security zone MUST be avoided
- Host firewalls MUST be configured on servers operating outside OCIO datacentres

---

## Zone Adjacency Rule — No Zone Hopping

**Only adjacent zones may initiate or service communication requests.** A workstation in
Zone C cannot initiate a session directly to data in Zone A; traffic must traverse
intermediate zone boundaries (where firewall + IPS + anomaly detection enforce policy).

```
Internet  ↔  DMZ  ↔  Zone B  ↔  Zone A
              ↕         ↕         ↕
            (SDN)     (SDN)     (SDN)
            Low   ↔  Medium  ↔  High
```

- The internet **cannot** initiate a session directly into Medium / High / Zone B / Zone A.
- Session initiation between adjacent zones may be **asymmetric**
  (e.g., Zone C → Internet permitted; Internet → Zone C denied).
- **NetworkPolicy and SDN Security Policies cannot override guardrails.** Adjacency is
  enforced at the SDN guardrail / firewall, not at the pod level. A NetworkPolicy allow
  rule from Internet to Medium is silently dropped at the guardrail.

### SDN guardrail key denies (selected)

| Source | Destination | Action |
|---|---|---|
| Public VIP | Medium / High / Zone DMZ / Zone B / Zone A / Zone C | Deny |
| Internet | Low / Medium / High (direct) | Deny |
| Low workload (Internet-Accessible, no WAF) | High | Deny |
| Low workload | Internet (direct) | Deny |
| Medium / High | Internet (direct) | Deny |
| High | Low / Zone DMZ / Zone C / Extranet | Deny |
| Medium | Extranet | Deny |

---

## Internet Egress Constraints by SDN Classification

| Classification | Direct Internet egress | Via SDN Forward Proxy | Notes |
|---|---|---|---|
| Low | Denied at guardrail | Allowed (whitelist-based) | Even Low workloads cannot egress directly to Internet |
| Medium | Denied at guardrail | Allowed (whitelist-based) | |
| High | Denied at guardrail | Exemption required (MISO) | Only for update / licence / call-home servers; not for API integrations |

### SDN Forward Proxy supported protocols

The Forward Proxy is whitelist-based (tenant-controlled list of accessible endpoints) and
supports these client protocols (per SDN Security Classification Model §Egress Traffic):

- HTTP (TCP 80) / HTTPS (TCP 443)
- SSH / SFTP (TCP 22)
- FTPS (TCP 21)
- LDAP-S (TCP 636)

Other protocols are not supported via the proxy. To reach the Internet from any SDN workload:

1. Add the destination FQDN to the tenant Forward Proxy whitelist
2. Configure the application to use the Forward Proxy endpoint
3. Write a NetworkPolicy Egress rule allowing traffic to the proxy host (not the final destination)
4. Do **not** write a CIDR NetworkPolicy pointing at the public Internet — it will be silently dropped at the guardrail

### Internet ingress constraints (perimeter denies)

The SDN perimeter denies inbound Internet traffic to common management/data ports
regardless of any tenant policy:

- SSH (22), RDP (3389), Telnet (23), SMB (445), NetBIOS (139)
- LDAP (389), LDAP-S (636)
- Oracle (1521), SQL Server (1433/1434), MySQL (3306), PostgreSQL (5432/5433)
- ICMP

With geo-fencing enabled, traffic from non-US/non-Canadian source IPs is restricted to
HTTP/HTTPS only.

### Public VIPs

- Public VIPs are the **only** path for Internet ingress to SDN workloads
- Public VIPs may attach **only** to Low workloads carrying the `Internet-Ingress:ALLOW` tag
- Public VIPs MUST NOT attach to Medium / High / DMZ / Zone B / Zone A / Zone C workloads
- Workloads receiving a Public VIP MUST be in the DMZ AD domain, not IDIR

---

## SDN Implementation Patterns — Multi-Segment vs Single-Segment

The SDN can be implemented two ways, with different implications when traffic crosses
the SDN perimeter to legacy multi-zone networks (Data Centre Classic):

### Multi-Segment (per-tenant Low / Medium / High network segments)

- Each tenant has separate network segments per classification, tagged in IPAM
- External multi-zone networks (Data Centre Classic) **can read** the SDN classification
- Mapping recognised at the boundary: Low ↔ DMZ, Medium ↔ Zone B, High ↔ Zone A
- Higher level of trust possible across the boundary

### Single-Segment (single network segment + tag-based classification)

- All workloads share one segment; classification enforced via tags / labels in the DFW
- Tags are **lost** at the SDN perimeter
- External networks treat all SDN traffic as the segment's *lowest* classification — in
  practice, **DMZ / Low**
- A Medium workload may be permitted by SDN guardrails to reach a Zone A workload, but
  the Zone A boundary firewall will deny it (source appears as DMZ)
- Best suited to containerised workloads (e.g., OpenShift); confines guardrail scope to
  intra-SDN flows

---

## External Partner Connectivity — Third Party Gateway (3PG) / ExtraNet

Any connection to an **external government partner** (other ministries, Crown corporations,
health authorities, municipalities, federal partners) must traverse the **ExtraNet zone** via a
**Third Party Gateway (3PG)**. This is the connectivity model mandated by
**IMIT 5.08 Network-to-Network Connectivity Security Standard** (a.k.a. the 3PG Standard).

### IMIT 5.08 — Mandatory N2N Controls

When one end of a connection is the SPAN network, the **3PG service MUST be used**
(IMIT 5.08 §5). The 3PG architecture provides:

| Control | Requirement |
|---|---|
| Connection routers | Logical (and where required, physical) separation guaranteed at all times |
| Stateful firewall | Mandatory; rules follow least-privilege; combined router+firewall acceptable if both requirements are met |
| IPS / IDS | Mandatory at the security transit point |
| Content filtering / malware protection | SHOULD be deployed |
| Data leakage protection | SHOULD be deployed |
| Default deny | All ports closed by default; internal addresses inaccessible by default; NAT used to hide IPs |
| Port-open requests | MUST be approved by the Information Owner and the contract-owning ministry |
| Encryption | Per IMIT 6.10 Cryptographic Standards; encrypted tunnels, MPLS, or end-to-end isolated VLANs |
| Traffic isolation | Province data MUST NOT share tunnels/circuits with other customers' data |
| PCI in-scope traffic | Separate **physical** router per circuit — virtualised routers and shared interfaces are NOT acceptable |
| Wireless on path | Minimum WPA2 encryption |
| Automated key exchange | Required on encrypted links |
| Logging | Raw logs retained ≥ 13 months; provided to Province on request for SIEM and incident response |

### Process

1. Submit a formal SSBC connection request referencing the target organisation and IP range
2. Await 3PG CIDR allocation from SSBC (the actual destination CIDRs are not directly routable)
3. Write an Egress NetworkPolicy targeting the **3PG CIDR** (not the partner's final destination IP)
4. The 3PG performs NAT/routing to the partner's network

> Do **not** attempt to route external-partner traffic through the SSBC Forward Proxy or
> the regular internet egress path — neither path reaches the ExtraNet segment.

### SPAN / BC Gov Network

Connections within the BC Gov SPAN network (e.g., to on-premises data centres, shared
services, or other ministries on the corporate LAN) are also subject to zone-to-zone
adjacency rules. Confirm the target system's zone before designing your NetworkPolicy.

---

## Worked Example — Classifying a New Workload

> **Q**: My API stores Protected-B (higher-risk) criminal justice data. What zone, what
> `DataClass` label, and can I call a public REST API for address validation?

1. Data class = Protected B (higher-risk) → **SDN High** → `DataClass: High` → IMIT 6.13 Zone A
2. Internet egress for High = denied at guardrail; SDN Forward Proxy requires MISO exemption
3. Options:
   - **Recommended**: split the workload — the data store stays *High*; create a *Medium*
     proxy service (or a *Low* + WAF service) that calls the public address-validation API
     via the Forward Proxy and serves the result to the *High* workload internally
   - Reclassify the *requesting* component if it is not itself responsible for High data
   - Apply for MISO exemption (lengthy; only justified for update / licence / call-home traffic)

---

## Quick Reference — Which Standard Governs?

| Question | Standard | Document |
|---|---|---|
| What class is this data? | IMIT 6.18 ISCF | gov.bc.ca information-security-classification |
| What zone? | IMIT 6.13 v5 (current) + OCIO SDN Security Classification Model v1.0 | IMIT 6.13 Standard + Specs (intranet) |
| Can I reach the internet? | SDN guardrail rules + IMIT 6.13 §5 Zone B Internet Access | OCIO SDN Security Classification Model v1.0 (2022); IMIT 6.13 Specs |
| Can I connect to another ministry? | IMIT 5.08 — 3PG / N2N Connectivity Standard | IMIT 5.08 Standard + Specifications (gov.bc.ca) |
| What network and communication controls apply? | IMIT 6.28 — Network and Communications Security | IMIT 6.28 Standard + Specifications (gov.bc.ca) |
| What pod label? | Emerald DataClass enforcement | `bc-gov-emerald` skill |
| How to write the NetworkPolicy? | NetworkPolicy patterns | `bc-gov-networkpolicy` skill |

Full URLs are in this skill's frontmatter `sources:` block.
