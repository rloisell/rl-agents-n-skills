---
name: network-architect
description: Network architecture and engineering — routing (BGP, OSPF, EIGRP), switching (STP, VLANs, 802.1Q, EtherChannel), WAN (MPLS, SD-WAN, DMVPN, IPsec), QoS, redundancy (HSRP/VRRP/GLBP), IPv4/IPv6 addressing and subnetting, and network troubleshooting. Use when designing topology, reviewing routing policy, troubleshooting L2/L3, or producing network architecture documentation.
metadata:
  author: Ryan Loiselle
  version: "1.0"
compatibility: Cisco IOS/IOS-XE/NX-OS focus (CCNP R&S baseline). Vendor-agnostic topology design. SD-WAN: Cisco Viptela, Fortinet, VMware VeloCloud.
---

# Network Architect Skill

Covers network design, routing/switching, WAN, and troubleshooting at CCNP depth.

**Ryan's context**: CCNA (2003–2006), CCNP R&S (BSCI/BCMSN/ISCW/ONT), Applied Computer Science. Currently designing enterprise SASE solutions.

**Shared skills referenced:**
- Zero Trust / SASE → [`../zero-trust-architect/SKILL.md`](../zero-trust-architect/SKILL.md)
- Network security controls → [`../network-security/SKILL.md`](../network-security/SKILL.md)
- DNS tools → [`../dns-tools/SKILL.md`](../dns-tools/SKILL.md)

---

## IP Addressing & Subnetting

### VLSM Quick Reference

| Prefix | Hosts | Typical use |
|--------|-------|-------------|
| /30 | 2 | Point-to-point links |
| /29 | 6 | Small DMZ / loopbacks |
| /28 | 14 | Small office |
| /27 | 30 | Medium VLAN |
| /26 | 62 | Large VLAN |
| /25 | 126 | Large campus segment |
| /24 | 254 | Standard site VLAN |
| /22 | 1022 | Supernet / summary |

### RFC 1918 Private Address Space
```
10.0.0.0/8        — Class A (large enterprise, data centres)
172.16.0.0/12     — Class B (medium enterprise)
192.168.0.0/16    — Class C (branch, home office)
```

### IPv6 Address Types
| Type | Prefix | Use |
|------|--------|-----|
| Global Unicast | 2000::/3 | Routable internet |
| Link-Local | fe80::/10 | On-link only; auto-assigned |
| Unique Local | fc00::/7 | Private (analogous to RFC 1918) |
| Multicast | ff00::/8 | Replaces broadcast |
| Loopback | ::1/128 | Local loopback |

---

## Routing Protocols

### OSPF

```
Key design rules:
- Area 0 (backbone) required; all other areas connect to it
- Use stub/totally stub for areas with single ABR
- Summarise at ABR boundaries (area range) and ASBR (summary-address)
- BFD for sub-second convergence on high-value links
- OSPF authentication: MD5 minimum; SHA-256 preferred (OSPFv3)

Troubleshooting checklist:
1. Are MTU values matching on both sides? (ip mtu mismatch → EXSTART/EXCHANGE stuck)
2. Are hello/dead timers matching?
3. Is the subnet mask identical?
4. Are area IDs matching?
5. Stub area flag mismatch?
```

### BGP

```
Key design rules:
- eBGP: always set next-hop-self on iBGP reflectors
- Use prefix-lists (not distribute-lists) for filtering — faster, cleaner
- Null-route aggregates before advertising summaries (ip route x.x.x.x 255... null0)
- AS-path prepending for inbound traffic engineering (not overused)
- Set MED for outbound preference signal to upstream
- BGP communities for policy tagging across eBGP peers

Path selection order (remember: N WLLA OMDI):
  Next hop reachable → Weight (Cisco-local) → Local-Pref → Locally originated
  → AS-path length → Origin (IGP < EGP < ?) → MED → eBGP > iBGP
  → IGP metric to next-hop → Router-ID (lowest)

Security hardening:
- TTL Security (GTSM): neighbor x ttl-security hops 1
- MD5 authentication on all eBGP sessions
- max-prefix with threshold + warning
```

### EIGRP

```
Feasibility condition: FD of successor > RD of feasible successor
Stuck-In-Active (SIA): query propagation too wide → use stub or summarisation
Named mode EIGRP preferred for configuration clarity
```

---

## Switching

### STP Variants

| Variant | Standard | Notes |
|---------|----------|-------|
| STP | 802.1D | Legacy; slow (30–50s convergence) |
| RSTP | 802.1w | Fast convergence (~1s); backward-compatible |
| PVST+ | Cisco | Per-VLAN STP; load balancing via root placement |
| Rapid PVST+ | Cisco | RSTP per VLAN; current default on Cisco |
| MST | 802.1s | Maps multiple VLANs to instances; scale |

```
STP hardening:
- PortFast on all access ports
- BPDU Guard on PortFast ports
- Root Guard on uplinks where root must not appear
- Loop Guard on non-designated ports (replaces UniDirectional Link Detection)
- BPDU Filter: use only on ports where STP BPDUs are explicitly unwanted
```

### VLANs and Trunking

```
802.1Q trunk: native VLAN must match on both sides (or use vlan dot1q tag native)
DTP: always disable on access ports (switchport nonegotiate)
VTP: use transparent mode or VTPv3 with password; avoid VTP v1/v2 in large environments

VLAN design conventions:
  VLAN 1   — never use for data; isolate or shut unused ports
  VLAN 99  — management VLAN (or any non-1 native)
  VLAN 10  — data
  VLAN 20  — voice (with QoS trust dscp on IP phones)
  VLAN 30  — management devices
  VLAN 100+ — service VLANs
```

### EtherChannel

```
LACP (802.3ad): preferred; interoperable
PAgP: Cisco-only
Static (on/on): use only when LACP unavailable

Load balancing hash options (balance on most variable field):
  src-mac / dst-mac / src-dst-mac
  src-ip  / dst-ip  / src-dst-ip   ← recommended for routed traffic
  src-port / dst-port / src-dst-port ← recommended for server farms
```

---

## WAN Technologies

### MPLS L3VPN

```
PE–CE routing: eBGP, OSPF, or static
Route distinguisher (RD): makes VPN routes unique in MP-BGP (not security)
Route target (RT): controls VPN import/export (the actual policy)
VRF: per-customer routing table on PE

Troubleshooting:
  show bgp vpnv4 unicast all summary
  show ip route vrf <name>
  show mpls ldp neighbor
  show mpls forwarding-table
```

### IPsec VPN

```
IKEv2 preferred (vs IKEv1 — less round-trips, better re-keying)
Encryption: AES-256-GCM
Integrity: SHA-256 or SHA-384
DH group: 14 minimum; 19/20 (ECDH) preferred
PFS: always enable (new DH exchange per SA)
Dead Peer Detection (DPD): always enable

Transform sets to avoid: DES, 3DES, MD5, DH group 1/2/5
```

### DMVPN

```
Phase 1: hub-to-spoke only (spoke cannot talk directly to spoke)
Phase 2: spoke-to-spoke (NHRP redirect; one NHRP resolution per pair required)
Phase 3: spoke-to-spoke with NHRP shortcut (summarise at hub; more scalable)
```

### SD-WAN (Cisco Viptela / Catalyst SD-WAN)

```
Control plane: vManage (GUI/API), vSmart (policy), vBond (orchestration)
Data plane: vEdge / cEdge with OMP (Overlay Management Protocol)
Policy types: centralized (control/data) vs local (access/device)
Application-aware routing: based on BFD SLA metrics (jitter, loss, latency)
```

---

## QoS

### DSCP Marking Reference

| Class | DSCP Decimal | Binary | Use |
|-------|-------------|--------|-----|
| EF | 46 | 101110 | VoIP RTP (voice bearer) |
| CS3 | 24 | 011000 | Call signalling |
| AF41 | 34 | 100010 | Video conferencing |
| AF31 | 26 | 011010 | Mission-critical data |
| AF11 | 10 | 001010 | Bulk data |
| CS1 | 8  | 001000 | Scavenger (low priority) |
| BE  | 0  | 000000 | Best effort (default) |

```
Trust boundary: always at the IP phone or first managed switch port
Mark at edge; never remark in the core
VoIP sizing rule: BW = (Codec_bps + 160b_overhead) × calls
CBWFQ + LLQ: queue voice in LLQ (priority); everything else in CBWFQ classes
```

---

## Gateway Redundancy

| Protocol | Standard | VIP ownership | Load balance |
|----------|----------|---------------|--------------|
| HSRP v2 | Cisco | Active router | No (one active) |
| VRRP | RFC 5798 | Master router | No |
| GLBP | Cisco | AVG + multiple AVF | Yes (per-host round-robin) |

```
Best practice: HSRP or VRRP for simplicity; GLBP when upstream bandwidth balance matters
Object tracking: track interface/IP SLA; decrement priority on failure to trigger failover
```

---

## Troubleshooting Methodology (OSI Bottom-Up)

```
L1  Physical   — cabling, SFP, interface status (show int, show cdp neigh)
L2  Data Link  — MAC table, ARP, STP state, trunk config (show mac address-table, show spanning-tree)
L3  Network    — routing table, ARP, ping, traceroute (show ip route, debug ip routing)
L4  Transport  — port reachability (telnet <ip> <port>), access-list hits
L7  App        — DNS resolution, TLS handshake, application logs
```

---

## NETWORK_KNOWLEDGE

> Append discoveries here. Format: `YYYY-MM-DD: <note>`
