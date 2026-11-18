# Routing, Switching, WAN, QoS & Troubleshooting

## Contents

- [IP Addressing & Subnetting](#ip-addressing--subnetting)
- [Routing Protocols (OSPF, BGP, EIGRP)](#routing-protocols-ospf-bgp-eigrp)
- [Switching (STP, VLANs, EtherChannel)](#switching-stp-vlans-etherchannel)
- [WAN Technologies (MPLS, IPsec, DMVPN, SD-WAN)](#wan-technologies-mpls-ipsec-dmvpn-sd-wan)
- [QoS (DSCP Marking Reference)](#qos-dscp-marking-reference)
- [Gateway Redundancy (HSRP / VRRP / GLBP)](#gateway-redundancy-hsrp--vrrp--glbp)
- [Troubleshooting Methodology (OSI Bottom-Up)](#troubleshooting-methodology-osi-bottom-up)

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

```text
10.0.0.0/8        — Class A (large enterprise, data centres)
172.16.0.0/12     — Class B (medium enterprise)
192.168.0.0/16    — Class C (branch, home office)
```

### IPv6 Address Types

| Type | Prefix | Use |
|------|--------|-----|
| Global Unicast | `2000::/3` | Routable internet |
| Link-Local | `fe80::/10` | On-link only; auto-assigned |
| Unique Local | `fc00::/7` | Private (analogous to RFC 1918) |
| Multicast | `ff00::/8` | Replaces broadcast |
| Loopback | `::1/128` | Local loopback |

## Routing Protocols (OSPF, BGP, EIGRP)

### OSPF

- Area 0 (backbone) required; all other areas connect to it.
- Use stub/totally stub for areas with a single ABR.
- Summarise at ABR boundaries (`area range`) and ASBR (`summary-address`).
- BFD for sub-second convergence on high-value links.
- OSPF authentication: MD5 minimum; SHA-256 preferred (OSPFv3).
- **Troubleshooting checklist**: (1) MTU mismatch (`EXSTART`/`EXCHANGE` stuck), (2) hello/dead timers, (3) subnet mask identical, (4) area IDs match, (5) stub area flag match.

### BGP

- eBGP: always set `next-hop-self` on iBGP reflectors.
- Use prefix-lists (not distribute-lists) for filtering — faster and cleaner.
- Null-route aggregates before advertising summaries (`ip route x.x.x.x 255... null0`).
- AS-path prepending for inbound traffic engineering; MED for outbound preference to upstream; BGP communities for policy tagging across eBGP peers.
- **Path selection order (N WLLA OMDI)**: Next hop reachable → Weight (local) → Local-Pref → Locally originated → AS-path length → Origin (`IGP < EGP < ?`) → MED → eBGP > iBGP → IGP metric to next-hop → Router-ID (lowest).
- **Security hardening**: TTL Security (`neighbor x ttl-security hops 1`), MD5 authentication on eBGP sessions, `max-prefix` with threshold + warning.

### EIGRP

- Feasibility condition: FD of successor > RD of feasible successor.
- Stuck-In-Active (SIA): query propagation too wide → use stub or summarisation.
- Named mode EIGRP preferred for configuration clarity.

## Switching (STP, VLANs, EtherChannel)

### STP Variants

| Variant | Standard | Notes |
|---------|----------|-------|
| STP | 802.1D | Legacy; slow (30–50s convergence) |
| RSTP | 802.1w | Fast convergence (~1s); backward-compatible |
| PVST+ | Cisco | Per-VLAN STP; load balancing via root placement |
| Rapid PVST+ | Cisco | RSTP per VLAN; current default on Cisco |
| MST | 802.1s | Maps multiple VLANs to instances; scale |

**STP hardening**: PortFast on all access ports, BPDU Guard on PortFast ports, Root Guard on uplinks where root must not appear, Loop Guard on non-designated ports, BPDU Filter only where STP BPDUs are explicitly unwanted.

### VLANs and Trunking

- 802.1Q trunk: native VLAN must match on both sides (or use `vlan dot1q tag native`).
- DTP: always disable on access ports (`switchport nonegotiate`).
- VTP: use transparent mode or VTPv3 with password; avoid VTP v1/v2 in large environments.
- Conventions: VLAN 1 never for data (isolate/shut unused); VLAN 99 management/unused native; VLAN 10 data; VLAN 20 voice (QoS trust DSCP); VLAN 30 management devices; VLAN 100+ service VLANs.

### EtherChannel

- LACP (802.3ad) preferred (interoperable); PAgP Cisco-only; static (`on/on`) only when LACP unavailable.
- Load balancing hash: `src-dst-ip` recommended for routed traffic; `src-dst-port` for server farms.

## WAN Technologies (MPLS, IPsec, DMVPN, SD-WAN)

### MPLS L3VPN

- PE–CE routing: eBGP, OSPF, or static.
- Route distinguisher (RD): makes VPN routes unique in MP-BGP (not security).
- Route target (RT): controls VPN import/export (the actual policy).
- VRF: per-customer routing table on PE.
- Troubleshooting: `show bgp vpnv4 unicast all summary`, `show ip route vrf <name>`, `show mpls ldp neighbor`, `show mpls forwarding-table`.

### IPsec VPN

- IKEv2 preferred (less round-trips, better re-keying vs IKEv1).
- Encryption: `AES-256-GCM`; Integrity: `SHA-256` or `SHA-384`; DH group: `14` minimum (`19`/`20` ECDH preferred).
- Always enable PFS and Dead Peer Detection (DPD).
- Avoid: DES, 3DES, MD5, DH group 1/2/5.

### DMVPN

- Phase 1: hub-to-spoke only.
- Phase 2: spoke-to-spoke (NHRP redirect; one NHRP resolution per pair).
- Phase 3: spoke-to-spoke with NHRP shortcut (summarise at hub; more scalable).

### SD-WAN (Cisco Viptela / Catalyst SD-WAN)

- Control plane: vManage (GUI/API), vSmart (policy), vBond (orchestration).
- Data plane: vEdge / cEdge with OMP (Overlay Management Protocol).
- Policy types: centralized (control/data) vs local (access/device).
- Application-aware routing: based on BFD SLA metrics (jitter, loss, latency).

## QoS (DSCP Marking Reference)

| Class | DSCP Decimal | Binary | Use |
|-------|-------------|--------|-----|
| EF | 46 | 101110 | VoIP RTP (voice bearer) |
| CS3 | 24 | 011000 | Call signalling |
| AF41 | 34 | 100010 | Video conferencing |
| AF31 | 26 | 011010 | Mission-critical data |
| AF11 | 10 | 001010 | Bulk data |
| CS1 | 8 | 001000 | Scavenger (low priority) |
| BE | 0 | 000000 | Best effort (default) |

- Trust boundary: at the IP phone or first managed switch port; mark at edge, never remark in core.
- VoIP sizing rule: `BW = (Codec_bps + 160b_overhead) × calls`.
- CBWFQ + LLQ: queue voice in LLQ (priority); everything else in CBWFQ classes.

## Gateway Redundancy (HSRP / VRRP / GLBP)

| Protocol | Standard | VIP ownership | Load balance |
|----------|----------|---------------|--------------|
| HSRP v2 | Cisco | Active router | No (one active) |
| VRRP | RFC 5798 | Master router | No |
| GLBP | Cisco | AVG + multiple AVF | Yes (per-host round-robin) |

Use HSRP or VRRP for simplicity; GLBP when upstream bandwidth balance matters. Track interfaces/IP SLA and decrement priority on failure.

## Troubleshooting Methodology (OSI Bottom-Up)

```text
L1 Physical   — cabling, SFP, interface status (show int, show cdp neigh)
L2 Data Link  — MAC table, ARP, STP state, trunk config (show mac address-table, show spanning-tree)
L3 Network    — routing table, ARP, ping, traceroute (show ip route, debug ip routing)
L4 Transport  — port reachability, access-list hits
L7 App        — DNS resolution, TLS handshake, application logs
```
