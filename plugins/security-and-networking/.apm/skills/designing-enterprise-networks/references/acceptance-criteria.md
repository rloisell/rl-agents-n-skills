# Acceptance Criteria — Designing Enterprise Networks

Observable pass/fail criteria for Zero Trust / SASE architecture, L2/L3/WAN engineering, IOS/IOS-XE hardening, and BC Gov IMIT mapping.

## Zero Trust & SASE Architecture

| Criterion | Pass | Fail |
|---|---|---|
| Explicit verification | Architecture enforces user + device posture + risk verification at inline Policy Enforcement Points (PEP) driven by a Policy Decision Point (PDP). | Implicit trust based on IP subnet, VLAN, or internal network location. |
| Microsegmentation & SASE | SASE model (single-vendor, dual-vendor, or hybrid) and ZTNA/CASB/SWG/FWaaS boundaries are explicitly defined. | Flat internal network without east-west segmentation or undefined PEP placement. |

## Routing, Switching & WAN

| Criterion | Pass | Fail |
|---|---|---|
| Addressing & routing | IPv4/IPv6 addressing is conflict-free; OSPF/BGP/EIGRP neighbourships, route summarization, and HSRP/VRRP/GLBP redundancy are specified. | Overlapping subnets, asymmetric routing without state handling, or single points of failure. |
| WAN & MTU hygiene | MPLS/SD-WAN/DMVPN/IPsec topologies include QoS DSCP markings and TCP MSS clamping (`ip tcp adjust-mss 1360` over tunnels). | Tunnel designs omitting MTU/MSS clamping or QoS prioritization for real-time traffic. |

## Perimeter, Crypto & L2 Controls

| Criterion | Pass | Fail |
|---|---|---|
| Default-deny ACLs & ZBF | Named/object-group ACLs permit only required ports/protocols and terminate with `deny any log`; Zone-Based Firewall enforces inter-zone policy. | `permit any any` rules or ACLs without explicit deny/logging. |
| Strong IPsec crypto | IPsec uses IKEv2, AES-256-GCM (or AES-256-CBC), SHA-256+, DH Group 14+ (19/20 ECDH preferred), PFS, and DPD. | Any use of DES, 3DES, MD5, IKEv1, or DH Groups 1/2/5. |
| L2 switch hardening | Access ports disable DTP (`switchport nonegotiate`), move native VLAN off VLAN 1, enable PortFast + BPDU Guard, and deploy DHCP snooping + DAI + 802.1X. | Default VLAN 1 native trunking, enabled DTP, or unprotected access ports. |

## BC Gov IMIT Alignment & Verification

| Criterion | Pass | Fail |
|---|---|---|
| IMIT control mapping | Design maps controls to IMIT 6.28 (comms security), IMIT 6.13 (zones), and IMIT 5.08 (3PG N2N, >= 13-month log retention). | Missing IMIT control mapping or log retention below 13 months. |
| CLI verification plan | Includes verification commands (`show crypto ikev2 sa detail`, `show crypto ipsec sa`, `show ip access-lists`, `show ip dhcp snooping binding`, `show ip arp inspection statistics`). | Configuration delivered without operational verification steps. |
