---
name: designing-enterprise-networks
description: Enterprise network architecture, Zero Trust/SASE design, and IOS/IOS-XE security controls — routing (BGP, OSPF, EIGRP), switching (STP, VLANs, 802.1Q, EtherChannel), WAN (MPLS, SD-WAN, DMVPN, IPsec), QoS, HSRP/VRRP/GLBP, ZTNA/CASB/SWG/FWaaS, ACLs, NAT/PAT, Zone-Based Firewall, L2 hardening, and BC Gov IMIT 6.28/6.13/5.08 mapping. Use when designing network topology, SASE/ZTA architecture, routing/firewall policy, or auditing switch/router security.
compatibility: Vendor-agnostic ZTA/SASE; Cisco IOS/IOS-XE/NX-OS (CCNP R&S baseline); BC Gov IMIT 6.28, 6.13, 5.08.
---

# Designing Enterprise Networks

Covers Zero Trust Architecture (ZTA) / SASE, core routing/switching/WAN engineering, IOS/IOS-XE security controls, and BC Gov IMIT network standard alignment.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

1. **Zero Trust default**: never trust the network; verify explicitly (user + device posture + risk) and enforce least privilege via inline Policy Enforcement Points (PEP).
2. **Default-deny firewalling**: permit only required ports/protocols; end named ACLs with explicit `deny any log`; never permit `any any`.
3. **Strong crypto only**: IPsec requires IKEv2, AES-256-GCM (or AES-256-CBC), SHA-256+, DH Group 14+ (19/20 ECDH preferred), PFS, and DPD; prohibit DES, 3DES, MD5, and DH 1/2/5.
4. **L2 hardening**: disable DTP (`switchport nonegotiate`), move native VLAN off VLAN 1, enable PortFast + BPDU Guard on access ports, and deploy DHCP snooping + DAI + 802.1X.
5. **BC Gov IMIT alignment**: map enterprise network designs to IMIT 6.28 (network/comms security), IMIT 6.13 (zones), and IMIT 5.08 (3PG N2N, ≥ 13-month log retention).

## Quick start

1. Identify the target scope: Zero Trust/SASE architecture, L2/L3/WAN routing, or IOS/IOS-XE perimeter hardening.
2. Apply the matching design patterns and CLI configurations from `references/`.
3. Validate control alignment against BC Gov IMIT 6.28, 6.13, and 5.08 where applicable.

## Workflow

1. **Define trust & SASE model**: Select single-vendor, dual-vendor, or hybrid SASE and design the PDP/PEP policy engine and microsegmentation per [zero-trust-sase.md](references/zero-trust-sase.md).
2. **Architect L2/L3 & WAN**: Plan IPv4/IPv6 addressing, OSPF/BGP/EIGRP routing, STP/VLAN/EtherChannel switching, MPLS/SD-WAN/IPsec WAN, QoS DSCP markings, and gateway redundancy per [routing-switching-wan.md](references/routing-switching-wan.md).
3. **Apply perimeter & L2 controls**: Author object-group/extended ACLs, NAT/PAT, IKEv2 IPsec, Zone-Based Firewall, and switch hardening per [ios-security-controls.md](references/ios-security-controls.md).
4. **Map to BC Gov standards**: Verify IMIT 6.28, 6.13, and 5.08 control coverage per [bc-gov-imit-network-mapping.md](references/bc-gov-imit-network-mapping.md).

## Verification

- Routing/WAN: verify OSPF/BGP neighbor state, `show crypto ikev2 sa detail`, `show crypto ipsec sa`, and MTU/MSS clamping (`ip tcp adjust-mss 1360`).
- Security/L2: verify ACL hit counters (`show ip access-lists`), `show ip dhcp snooping binding`, `show ip arp inspection statistics`, and ZBF zone-pair drops.

## References

- [zero-trust-sase.md](references/zero-trust-sase.md) — NIST SP 800-207 principles, SASE component map & deployment models, PDP/PEP policy engine, microsegmentation, CISA ZTMM, and vendor scorecard.
- [routing-switching-wan.md](references/routing-switching-wan.md) — VLSM/IPv6, OSPF/BGP/EIGRP, STP/VLANs/EtherChannel, MPLS/IPsec/DMVPN/SD-WAN, QoS DSCP, HSRP/VRRP/GLBP, and OSI troubleshooting.
- [ios-security-controls.md](references/ios-security-controls.md) — IOS/IOS-XE ACLs, NAT/PAT, IKEv2 site-to-site IPsec, Zone-Based Firewall, L2 hardening (DHCP snooping, DAI, 802.1X), attack mitigations, and firewall principles.
- [bc-gov-imit-network-mapping.md](references/bc-gov-imit-network-mapping.md) — IMIT 6.28, 6.13, and 5.08 control mapping table for BC Gov designs and STRA submissions.
- [Acceptance Criteria](references/acceptance-criteria.md) — Observable pass/fail criteria for Zero Trust/SASE, routing/WAN, perimeter/L2 controls, and IMIT alignment.
