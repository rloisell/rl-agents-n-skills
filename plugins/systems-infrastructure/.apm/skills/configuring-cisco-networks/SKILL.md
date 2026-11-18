---
name: configuring-cisco-networks
description: Configures and troubleshoots Cisco IOS, IOS-XE, and NX-OS routers and switches across enterprise and lab topologies. Use when configuring VLANs, trunks, STP, EtherChannel, OSPF, HSRP, NAT/PAT, ACLs, DHCP, SSH hardening, password recovery, IOS image upgrades, or NX-OS VPCs.
compatibility: Cisco IOS 12.x/15.x, IOS-XE 16.x/17.x, NX-OS 7.x/9.x, GNS3/EVE-NG
---

# Configuring Cisco Networks

Cisco IOS, IOS-XE, and NX-OS configuration, troubleshooting, and recovery reference.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Produce complete, paste-ready Cisco IOS/NX-OS syntax with inline `!` comments.
- Group configuration blocks logically: `global -> interfaces -> routing -> security -> lines`.
- Append `end` and `write memory` at the close of configuration blocks.
- List `show` commands first when troubleshooting and explain what to inspect; use `debug` only briefly and always pair with `undebug all`.
- Use ASCII diagrams with interface labels and IP addresses for topology diagrams.

## Quick start

| Area | IOS / IOS-XE | NX-OS |
|------|--------------|-------|
| Switching | VLANs, trunking, STP/RSTP, EtherChannel | vPC, LACP, VLANs |
| Routing | OSPF, EIGRP, BGP, static, redistribution | OSPF, BGP |
| WAN | NAT/PAT, IPsec, GRE, DMVPN | — |
| Security | ACLs, SSH hardening, AAA, port-security | features, port-security |
| HA | HSRP, VRRP, GLBP | vPC, HSRP |
| Management | IOS image upgrades, password recovery, logging | NX-OS features, VDC |

## Workflow

| Scenario | Action |
|----------|--------|
| OSPF neighbour stuck in `EXSTART` | Check MTU mismatch: `show interfaces` both sides; align `ip mtu 1500` or `ip ospf mtu-ignore` |
| Interface `up/up` but no traffic | Check ACL hit counters (`show ip access-lists`), NAT translations, or brief `debug ip packet` |
| VLANs not crossing trunk | `show interfaces trunk` — confirm VLAN in allowed list and not pruned |
| EtherChannel not forming | Verify identical speed/duplex/VLAN/encapsulation on all members; `show etherchannel summary` |
| HSRP not becoming active | Check standby priority, `preempt`, and MD5 key-string via `show standby brief` |
| Switch won't accept login | Follow platform password recovery procedure |
| `% Login invalid` on console | `line con 0` with `login local` requires a valid local `username` |
| IOS image upgrade | `verify /md5` before setting `boot system`; retain old image until first clean reload |

## Verification

- **Switching & HA**: Verify trunking (`show interfaces trunk`), EtherChannel (`show etherchannel summary`), or HSRP/vPC (`show standby brief` / `show vpc`).
- **Routing & Traffic**: Confirm neighbour adjacency (`show ip ospf neighbor`), routing table (`show ip route`), and ACL/NAT counters (`show ip access-lists`, `show ip nat translations`).
- **Images & Persistence**: Confirm `verify /md5` on target IOS image, `show boot` variable, and saved startup config (`write memory`).

## References

- [IOS Routing & Switching](references/ios-routing-switching.md) — initial setup, interfaces, VLANs/trunking, VTP, STP, EtherChannel, static routing, OSPF, HSRP, NAT/PAT, DHCP, ACLs, and `show`/`debug` commands.
- [NX-OS, Image Management & Recovery](references/nxos-and-recovery.md) — ROMmon/Catalyst password recovery, IOS TFTP/SCP upgrades, NX-OS features/vPC/VDC, and GNS3/EVE-NG lab tips.
- [Acceptance Criteria](references/acceptance-criteria.md) — observable pass/fail criteria for Cisco IOS/IOS-XE/NX-OS configuration and troubleshooting outputs.
- For DNS resolution diagnostics (`dig`, `nslookup`, `host`) on network segments, invoke the sibling `administering-unix-systems` skill.
