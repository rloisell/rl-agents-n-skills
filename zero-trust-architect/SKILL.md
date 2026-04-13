---
name: zero-trust-architect
description: Zero Trust Architecture (ZTA) and SASE design — identity-first access, ZTNA, CASB, SWG, FWaaS, SSE/SASE frameworks, SD-WAN security integration, microsegmentation, policy engine design, and NIST SP 800-207 control mapping. Use when designing a ZTA, building a SASE deployment model, evaluating SD-WAN + security stack integration, or auditing implicit trust assumptions.
metadata:
  author: Ryan Loiselle
  version: "1.0"
compatibility: Vendor-agnostic. Covers Zscaler, Palo Alto Prisma SASE, Cisco SSE, Fortinet SASE, Cloudflare One, Netskope. Maps to NIST SP 800-207, Gartner SASE, and CISA Zero Trust Maturity Model.
---

# Zero Trust Architect Skill

Drives Zero Trust Architecture (ZTA) and SASE design, evaluation, and documentation.

**Ryan's context**: CCNA (2003–2006), CCNP R&S (full track), Applied Computer Science degree. Currently designing a SASE solution for employer. Transitioning into network solutions architecture.

**Shared skills referenced:**
- Network architecture fundamentals → [`../network-architect/SKILL.md`](../network-architect/SKILL.md)
- Network security controls → [`../network-security/SKILL.md`](../network-security/SKILL.md)

---

## Zero Trust Principles (NIST SP 800-207)

| Principle | What it means in practice |
|-----------|--------------------------|
| Verify explicitly | Authenticate and authorize every request — user, device, location, time |
| Use least privilege | JIT/JEA access; never standing permissions to sensitive resources |
| Assume breach | Segment everything; log all access; design for containment |
| Never trust the network | LAN ≠ trusted; same policy on-prem, cloud, remote |

---

## SASE Component Map

```
┌─────────────────────────────────────────────────────────────┐
│                    SASE Cloud Fabric                        │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  SWG          │  │  CASB        │  │  ZTNA        │      │
│  │ (web policy)  │  │ (SaaS DLP)   │  │ (app access) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  FWaaS        │  │  DNS Sec     │  │  DLP         │      │
│  │ (L4-L7 FW)   │  │ (DNS filter) │  │ (data egress)│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                             │
│              SD-WAN Underlay / IPsec Tunnels                │
└─────────────────────────────────────────────────────────────┘
         ↑                     ↑                    ↑
   Branch (CPE)         Remote User           Cloud App
   SD-WAN edge          Endpoint agent        (SaaS/IaaS)
```

### Component Definitions

| Component | Role | Key vendors |
|-----------|------|-------------|
| **ZTNA** | Replaces VPN; identity-aware app access broker | Zscaler ZPA, Palo Alto Prisma Access, Cloudflare Access, Cisco Duo NAS |
| **SWG** | Inline web proxy; URL/SSL inspection; malware | Zscaler ZIA, Netskope, Proxy SG |
| **CASB** | SaaS visibility, inline DLP, shadow IT | Netskope, McAfee MVISION, Zscaler CASB |
| **FWaaS** | Cloud-hosted stateful L4-L7 firewall | Palo Alto Prisma, Zscaler Cloud FW |
| **SD-WAN** | Underlay abstraction; policy-based routing | Fortinet, Cisco Viptela, VMware VeloCloud, Palo Alto Prisma SD-WAN |
| **DNS Security** | Block C2, malware domains, DNS tunneling | Cisco Umbrella, Cloudflare Gateway, Zscaler DNS |
| **DLP** | Data-in-motion inspection; prevent exfil | Netskope, Zscaler, Forcepoint |

---

## SASE Deployment Models

### Model 1: Single-Vendor SASE
All SSE + SD-WAN from one vendor (Palo Alto Prisma SASE, Fortinet SASE).
- **Pro**: single console, native integration, simplified licensing
- **Con**: vendor lock-in; best-of-breed gaps possible
- **Choose when**: org prioritises operational simplicity

### Model 2: Dual-Vendor (SSE + SD-WAN)
Best-of-breed SSE (Zscaler/Netskope) + separate SD-WAN (Fortinet/Viptela).
- **Pro**: flexibility; independent scaling
- **Con**: integration complexity; two support relationships
- **Choose when**: existing SD-WAN investment exists; security maturity is high

### Model 3: Hybrid Transition
Existing MPLS/VPN retained; SASE PoPs added in parallel for new workloads.
- **Best for**: phased migration with legacy branches that cannot immediately move

---

## ZTA Policy Engine Design

```
Request (user + device + app + context)
       ↓
[Identity Check]   ← IdP: Entra ID / Okta / Keycloak
       ↓
[Device Posture]   ← MDM / EDR signal (compliant / managed / health score)
       ↓
[Risk Score]       ← UEBA, time-of-day, geo, anomaly
       ↓
[Resource Policy]  ← least-privilege; app segment; data classification
       ↓
[PEP Enforcement]  ← ZTNA broker / inline proxy / microseg agent
       ↓
Allow / Deny / Step-up MFA / Quarantine
```

### Policy Decision Point (PDP) vs Policy Enforcement Point (PEP)
- **PDP**: decides (IdP + SIEM + posture signals) — often Okta/Entra conditional access or a PAM platform
- **PEP**: enforces at the network/app edge — ZTNA connector, SWG proxy, CASB inline

---

## Microsegmentation Approaches

| Approach | Granularity | Best for |
|----------|-------------|----------|
| Network-based (VLAN/VRF) | IP subnet | Simple east-west; legacy |
| Firewall-based (micro-perimeter) | App group | Data centre |
| Host-based agent | Process/app | Cloud workloads; hybrid |
| Cloud-native NSG/SG | VPC/subnet | AWS/Azure/GCP workloads |
| Identity-aware proxy | User + app | ZTNA zero-trust app access |

---

## CISA Zero Trust Maturity Model — Pillar Checklist

| Pillar | Traditional | Advanced | Optimal |
|--------|-------------|----------|---------|
| **Identity** | MFA on some apps | Phishing-resistant MFA everywhere | Continuous re-auth; UEBA |
| **Devices** | Corp-managed only | MDM + posture check at access | Automated remediation; EDR signal |
| **Networks** | VLAN segmentation | Encrypted in-enclave traffic | Full microseg; all traffic TLS |
| **Apps** | VPN to app subnet | Per-app ZTNA | Dynamic policy; app-layer ABAC |
| **Data** | Basic DLP | DLP + classification | DSPM; automated policy enforcement |

---

## Vendor Evaluation Scorecard

When evaluating SASE/SSE vendors, score on:

| Criterion | Weight | Notes |
|-----------|--------|-------|
| PoP coverage (latency to user base) | High | Must cover your key geographies |
| Single-pass architecture (no backhaul) | High | Traffic should not leave region unnecessarily |
| CASB inline + API mode | Medium | Inline for real-time; API for shadow IT |
| SSL/TLS inspection capacity | High | Without it, blind to 90% of threats |
| SD-WAN integration (native vs. API) | Medium | Native = lower latency & single policy |
| Licensing model (per-user vs. Mbps) | High | Per-user scales predictably |
| API & automation (Terraform provider) | Medium | GitOps-ready |
| Support for agentless access | Medium | Contractors, BYOD, OT devices |

---

## Common Pitfalls

| Pitfall | Mitigation |
|---------|------------|
| "VPN + ZT" as marketing, not architecture | Validate PEP is in-path, not sidecar |
| Split tunnel VPN called "ZTNA" | True ZTNA brokers per-app — no network access |
| Implicit trust within cloud VPC | Apply NSGs + lateral movement controls |
| CASB API-only (reactive) | Add inline CASB for real-time DLP |
| Policy complexity → no policy applied | Start with coarse-grained; iterate |
| Ignoring OT/IoT in ZTA scope | Certificate-based identity; agentless ZTNA |

---

## ZERO_TRUST_KNOWLEDGE

> Append discoveries here. Format: `YYYY-MM-DD: <note>`
