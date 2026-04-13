---
name: network-security
description: Network security controls including ACLs (standard/extended/named/object-group), NAT/PAT, IPsec VPN (IKEv1/IKEv2, site-to-site, remote access), zone-based firewall, VLAN security hardening (DHCP snooping, DAI, 802.1X, port security), and common attack vectors (ARP spoofing, VLAN hopping, rogue DHCP, DDoS mitigation). Use when designing or auditing firewall policy, ACL rules, VPN configurations, or switch security hardening.
metadata:
  author: Ryan Loiselle
  version: "1.0"
compatibility: Cisco IOS/IOS-XE ACLs, Cisco ASA/FTD, zone-based firewall (ZBF), Linux iptables/nftables, general IP security principles.
---

# Network Security Skill

Access control, encryption, firewall design, and Layer 2 security hardening.

**Related skills:**
- IPsec VPN depth and Zero Trust architecture → [`../zero-trust-architect/SKILL.md`](../zero-trust-architect/SKILL.md)
- Routing / switching context → [`../network-architect/SKILL.md`](../network-architect/SKILL.md)

---

## Access Control Lists (IOS/IOS-XE)

### Standard ACL (source IP only)

```cisco
ip access-list standard MGMT-PERMIT
 permit 10.10.0.0 0.0.255.255
 deny   any log

! Apply — standard ACLs as close to destination as possible
interface GigabitEthernet0/0
 ip access-group MGMT-PERMIT in
```

### Extended ACL (src, dst, protocol, port)

```cisco
ip access-list extended INTERNET-OUT
 permit tcp 10.0.0.0 0.255.255.255 any eq 443
 permit tcp 10.0.0.0 0.255.255.255 any eq 80
 permit udp 10.0.0.0 0.255.255.255 any eq 53
 deny   ip any any log

interface GigabitEthernet0/1
 ip access-group INTERNET-OUT out

! Extended ACLs as close to source as possible
```

### Object-Group ACL (IOS-XE — cleaner, reusable)

```cisco
object-group network INTERNAL-RFC1918
 10.0.0.0 255.0.0.0
 172.16.0.0 255.240.0.0
 192.168.0.0 255.255.0.0

object-group service PERMITTED-OUTBOUND
 tcp destination eq 443
 tcp destination eq 80
 udp destination eq 53

ip access-list extended OUTBOUND-POLICY
 permit object-group PERMITTED-OUTBOUND object-group INTERNAL-RFC1918 any
 deny ip any any log
```

### ACL Design Rules

```
- Extended ACL: place closest to source (reduces unnecessary traffic traversal)
- Standard ACL: place closest to destination
- Always end with explicit deny any log (implicit deny does not log)
- Use 'log' on deny entries for visibility; avoid 'log' on high-volume permit entries (CPU)
- Named ACLs always preferred (reorderable, descriptive)
- Sequence numbers: leave gaps (10, 20, 30) for later insertions
- Verify with: show ip access-lists <name> (check hit counters)
```

---

## NAT / PAT

```cisco
! PAT (overload) — most common; many-to-one
ip nat inside source list NAT-INSIDE interface GigabitEthernet0/1 overload

ip access-list standard NAT-INSIDE
 permit 10.0.0.0 0.255.255.255

interface GigabitEthernet0/0
 ip nat inside

interface GigabitEthernet0/1
 ip nat outside

! Static NAT — 1:1 mapping for DMZ servers
ip nat inside source static 10.0.0.10 203.0.113.10

! Static PAT — port forwarding
ip nat inside source static tcp 10.0.0.10 443 203.0.113.5 443

! Verify
show ip nat translations
show ip nat statistics
clear ip nat translation *    ! clears dynamic table
```

---

## IPsec VPN

### IKEv2 Site-to-Site (IOS-XE)

```cisco
! Crypto IKEv2 proposal (encryption settings)
crypto ikev2 proposal IKEV2-PROPOSAL
 encryption aes-cbc-256
 integrity sha256
 group 19

crypto ikev2 policy IKEV2-POLICY
 proposal IKEV2-PROPOSAL

! IKEv2 profile (authentication and matching)
crypto ikev2 profile IKEV2-PROFILE
 match identity remote address 203.0.113.2
 authentication remote pre-share
 authentication local pre-share
 keyring local KR-SITE-B

crypto ikev2 keyring KR-SITE-B
 peer SITE-B
  address 203.0.113.2
  pre-shared-key secret-key-here

! Transform set (IPsec ESP)
crypto ipsec transform-set TS-AES256 esp-aes 256 esp-sha256-hmac
 mode tunnel

! Crypto map
crypto map CM-SITE-B 10 ipsec-isakmp
 set peer 203.0.113.2
 set transform-set TS-AES256
 set ikev2-profile IKEV2-PROFILE
 match address ACL-VPN-TRAFFIC
 set pfs group19

interface GigabitEthernet0/1
 crypto map CM-SITE-B

! Traffic selector ACL (mirror on far end)
ip access-list extended ACL-VPN-TRAFFIC
 permit ip 10.1.0.0 0.0.255.255 10.2.0.0 0.0.255.255
```

### IPsec Troubleshooting

```bash
show crypto isakmp sa           # IKEv1 phase 1 SA (should be ACTIVE/QM_IDLE)
show crypto ikev2 sa detail     # IKEv2 SA status
show crypto ipsec sa            # phase 2 SA, encap/decap counters
show crypto map
debug crypto isakmp             # verbose IKE negotiation (use carefully in production)
debug crypto ipsec

# Common failure causes:
# - Mismatched pre-shared key → AUTH_FAILED in ISAKMP
# - Mismatched transform set → NO_PROPOSAL_CHOSEN
# - Mismatched ACL (traffic selectors not mirrored) → QM fails
# - MTU issues → tunnelled ICMP works but TCP sessions drop (MSS clamping needed)
ip tcp adjust-mss 1360          ! on tunnel or inside interface; clamp TCP MSS
```

---

## Zone-Based Firewall (ZBF — IOS-XE)

```cisco
! Define zones
zone security INSIDE
zone security DMZ
zone security OUTSIDE

! Class maps (traffic classification)
class-map type inspect match-any INTERNET-APPS
 match protocol http
 match protocol https
 match protocol dns

! Policy maps (action)
policy-map type inspect INSIDE-TO-OUTSIDE
 class type inspect INTERNET-APPS
  inspect
 class class-default
  drop log

! Zone-pairs (apply policy between zones)
zone-pair security ZP-INSIDE-OUTSIDE source INSIDE destination OUTSIDE
 service-policy type inspect INSIDE-TO-OUTSIDE

! Assign interfaces to zones
interface GigabitEthernet0/0
 zone-member security INSIDE

interface GigabitEthernet0/1
 zone-member security OUTSIDE
```

---

## Layer 2 Security Hardening

### DHCP Snooping

```cisco
! Enable globally and per VLAN
ip dhcp snooping
ip dhcp snooping vlan 10,20,30

! Trust only uplinks / DHCP server ports
interface GigabitEthernet0/1   ! uplink to distribution
 ip dhcp snooping trust

! All access ports are untrusted by default
! Rate limit DHCP on untrusted ports
interface range GigabitEthernet0/2-24
 ip dhcp snooping limit rate 10

! Verify
show ip dhcp snooping binding
show ip dhcp snooping statistics
```

### Dynamic ARP Inspection (DAI)

```cisco
! Requires DHCP snooping binding table
ip arp inspection vlan 10,20,30

! Trust uplinks
interface GigabitEthernet0/1
 ip arp inspection trust

! ARP ACL for static devices (printers, servers without DHCP)
arp access-list STATIC-SERVERS
 permit ip host 10.0.0.100 mac host aabb.cc11.2233
ip arp inspection filter STATIC-SERVERS vlan 10

show ip arp inspection statistics vlan 10
```

### 802.1X Port Authentication

```cisco
aaa new-model
aaa authentication dot1x default group radius
dot1x system-auth-control

radius server CORP-RADIUS
 address ipv4 10.0.0.5 auth-port 1812 acct-port 1813
 key radius-secret

interface GigabitEthernet0/5
 switchport mode access
 dot1x port-control auto
 dot1x host-mode multi-auth  ! allows phone + PC on same port
 dot1x timeout quiet-period 10
 spanning-tree portfast
```

### Additional L2 Hardening

```cisco
! Disable DTP on all access ports
interface range GigabitEthernet0/2-24
 switchport nonegotiate
 switchport mode access

! Shutdown unused ports
interface range GigabitEthernet0/10-20
 shutdown
 description ** UNUSED **

! Change native VLAN off VLAN 1
interface GigabitEthernet0/1
 switchport trunk native vlan 99
 switchport trunk allowed vlan 10,20,30,99

! Disable CDP on untrusted ports
interface range GigabitEthernet0/2-24
 no cdp enable

! Storm control (prevent broadcast storms)
interface range GigabitEthernet0/2-24
 storm-control broadcast level 10.00
 storm-control action shutdown
```

---

## Attack Vectors and Mitigations

| Attack | Description | Mitigation |
|--------|-------------|------------|
| ARP Spoofing / Poisoning | Attacker replies to ARP with own MAC → MITM | DAI, static ARP entries, 802.1X |
| VLAN Hopping (switch spoofing) | Attacker negotiates trunk via DTP | `switchport nonegotiate`, never use VLAN 1 on trunks |
| VLAN Hopping (double-tagging) | Exploit native VLAN to jump one hop | Change native VLAN to unused VLAN (e.g. 999) |
| Rogue DHCP | Attacker serves DHCP responses | DHCP Snooping (untrusted all access ports) |
| CAM Overflow | Flood MAC table → switch broadcasts all → sniff | Port security: `switchport port-security maximum 2` |
| STP Attack | Attacker sends BPDU to become root | BPDU Guard, Root Guard |
| IP Spoofing | Forge source IP | uRPF (`ip verify unicast source reachable-via rx`) |
| Smurf DDoS | Broadcast amplification | Disable directed broadcast: `no ip directed-broadcast` |
| DNS Amplification | Abuse open resolvers | Disable recursion on authoritative; rate limiting; DNS firewall |

---

## Firewall Policy Design Principles

```
1. Default deny — whitelist only what is explicitly needed
2. Stateful inspection for return traffic — don't manually permit return flows
3. Segment DMZ from inside — DMZ-to-inside requires explicit permit (never implicit)
4. Log denies — but not at line rate (use sampling or rate limiting)
5. Explicit permit before implicit deny on all interfaces
6. Never permit 'any any' even temporarily — use time-limited ACEs if must
7. Egress filtering — filter outbound from all interfaces (not just inbound from outside)
8. Null-route known bad prefixes at edge routers (RTBH)
9. Scrubbing: normalise fragments, enforce MSS, reject illegal flag combos
10. Separate management plane — OOB management or dedicated VRF
```

---

## NETWORK_SECURITY_KNOWLEDGE

> Append discoveries here. Format: `YYYY-MM-DD: <note>`
