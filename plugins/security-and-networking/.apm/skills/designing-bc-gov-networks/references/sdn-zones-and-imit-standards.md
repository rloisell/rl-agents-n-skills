# BC Gov SDN Zones & IMIT Network Standards

## Contents

- [Information Security Classification Framework (ISCF)](#information-security-classification-framework-iscf)
- [SDN Security Classification Model (Low / Medium / High)](#sdn-security-classification-model-low--medium--high)
- [IMIT 6.13 Zone Model (v5)](#imit-613-zone-model-v5)
- [Zone Adjacency Rule — No Zone Hopping](#zone-adjacency-rule--no-zone-hopping)
- [Internet Egress & Ingress Constraints](#internet-egress--ingress-constraints)
- [Multi-Segment vs Single-Segment SDN](#multi-segment-vs-single-segment-sdn)
- [External Partner Connectivity — 3PG / ExtraNet (IMIT 5.08)](#external-partner-connectivity--3pg--extranet-imit-508)
- [Worked Example & Standards Quick Reference](#worked-example--standards-quick-reference)

## Information Security Classification Framework (ISCF)

> **Classify by data the workload is *responsible for storing*, not data it can access.**
> An application server that processes Protected B data in memory and forwards it to a database is *Low* (or *Medium* if it caches sensitive content); the database is *High*.

| ISCF Class | Examples | OpenShift `DataClass` | SDN classification | IMIT 6.13 zone |
| --- | --- | --- | --- | --- |
| Public / Unclassified | Public websites, open data, raw access logs | `Low` | Low | DMZ |
| Protected A | Low-sensitivity personal info, internal business | `Medium` | Medium | Zone B |
| Protected B (lower-risk) | Some medical / financial records | `Medium` | Medium | Zone B |
| Protected B (higher-risk) | Sensitive personal data, investigative records | `High` | High | Zone A |
| Protected C | Cabinet records, law enforcement data, classified | `High` | High | Zone A |

## SDN Security Classification Model (Low / Medium / High)

**Default-deny applies to all SDN traffic.** Guardrails are global *deny* rules that tenant security policies and NetworkPolicies cannot override.

- **Low** (maps to DMZ): Public info or no data at rest. Internet ingress denied by default (requires Public VIP + `Internet-Ingress:ALLOW`). Direct internet egress denied (use Forward Proxy). Internet-accessible Low without WAF cannot reach High; Low with WAF may reach High.
- **Medium** (maps to Zone B): Protected A / lower-risk Protected B. Internet ingress denied (no Public VIP). Direct internet egress denied (use Forward Proxy). Medium → Extranet (3PG) denied.
- **High** (maps to Zone A): Higher-risk Protected B / Protected C. Internet ingress denied (no Public VIP, even with WAF). Internet egress denied (Forward Proxy requires rare MISO exemption for licence/update/call-home only). High → Low / DMZ / Zone C / Extranet denied by guardrail.

## IMIT 6.13 Zone Model (v5)

| Zone | Name | ISCF data at rest | Notes |
| --- | --- | --- | --- |
| Internet | — | n/a | Common mgmt/DB ports (22, 3389, 23, 445, 139, 389, 636, 1521, 1433, 3306, 5432, ICMP) denied at perimeter |
| DMZ | Demilitarized Zone | Public | Proxies, web gateways; MUST be in DMZ AD domain (not IDIR); requires App Vuln Scan |
| SPAN/BC | Shared Provincial Access Network | Mixed | Hosts trusted and untrusted endpoints |
| Extranet | External partner landing zone | Varies | Ingress + egress MUST traverse 3PG-equivalent infrastructure (IMIT 5.08) |
| Zone C | Trusted Client Zone | Mostly Public / Protected A | IDIR-managed workstations (NOT server workloads). Sub-zones: Trusted, Semi-trusted, Untrusted, BUS. Never assign `DataClass: High` to Zone C. |
| Zone B | High Security Zone | Protected A / Protected B | Internal app tier; default Internet = No Access; outbound via Forward Proxy |
| Zone A | Restricted High Security Zone | Protected C | Server-to-server only; admin access via SAG only |
| Management Plane | Datacentre operations layer | n/a | Physically separate; reached via SAG only; non-Internet-routable IPs |

**Mandatory boundary controls (IMIT 6.13 v5 §5)**: all cross-zone traffic passes firewall + IPS + anomaly detection; no server/router/switch may straddle zones; avoid reverse proxies to a higher security zone; configure host firewalls outside OCIO datacentres.

## Zone Adjacency Rule — No Zone Hopping

```text
Internet  ↔  DMZ  ↔  Zone B  ↔  Zone A
              ↕         ↕         ↕
            (SDN)     (SDN)     (SDN)
            Low   ↔  Medium  ↔  High
```

| Source | Destination | Guardrail Action |
| --- | --- | --- |
| Public VIP | Medium / High / DMZ / Zone B / Zone A / Zone C | Deny |
| Internet | Low / Medium / High (direct) | Deny |
| Low (Internet-Accessible, no WAF) | High | Deny |
| Low / Medium / High | Internet (direct) | Deny |
| High | Low / DMZ / Zone C / Extranet | Deny |
| Medium | Extranet | Deny |

## Internet Egress & Ingress Constraints

- **Forward Proxy**: Whitelist-based; supports HTTP (80), HTTPS (443), SSH/SFTP (22), FTPS (21), LDAPS (636). To use: (1) add FQDN to Forward Proxy whitelist, (2) configure app proxy env vars, (3) write Egress NetworkPolicy to the proxy host (not public Internet CIDR).
- **Public VIPs**: Only path for internet ingress; attach only to Low workloads with `Internet-Ingress:ALLOW` in DMZ AD domain.
- **Geo-fencing**: Non-US/non-Canadian source IPs restricted to HTTP/HTTPS only when enabled.

## Multi-Segment vs Single-Segment SDN

- **Multi-Segment**: Separate per-classification segments tagged in IPAM; Data Centre Classic recognises Low ↔ DMZ, Medium ↔ Zone B, High ↔ Zone A.
- **Single-Segment**: Shared segment with DFW tags; tags are lost at the SDN perimeter so external networks treat all traffic as DMZ / Low (best suited to OpenShift intra-SDN flows).

## External Partner Connectivity — 3PG / ExtraNet (IMIT 5.08)

Connections to external government partners (other ministries, Crown corps, health authorities, municipalities, federal partners) on SPAN MUST use a **Third Party Gateway (3PG)**:

- **Mandatory controls**: logical/physical router separation, stateful firewall (default-deny + NAT), IPS/IDS, IMIT 6.10 encryption, no shared customer tunnels, separate physical router for PCI, ≥ 13 months raw log retention for Province SIEM.
- **Process**: (1) submit SSBC connection request, (2) obtain 3PG CIDR allocation, (3) write Egress NetworkPolicy targeting the **3PG CIDR** (not the partner's final IP). Never route partner traffic through the Forward Proxy.

## Worked Example & Standards Quick Reference

> **Q**: An API stores Protected-B (higher-risk) data and needs to call a public REST API.
> **A**: DataClass = `High` (Zone A); direct/proxy internet egress is blocked. Split the workload: keep the data store `High`, and add a `Medium` (or `Low` + WAF) proxy service that calls the public API via Forward Proxy and serves results internally.

| Question | Standard |
| --- | --- |
| What class is this data? | IMIT 6.18 ISCF |
| What zone? | IMIT 6.13 v5 + OCIO SDN Security Classification Model v1.0 |
| Can I reach the internet? | SDN guardrails + IMIT 6.13 §5 |
| Can I connect to another ministry? | IMIT 5.08 — 3PG / N2N Connectivity Standard |
| What network/comms controls apply? | IMIT 6.28 — Network and Communications Security |
