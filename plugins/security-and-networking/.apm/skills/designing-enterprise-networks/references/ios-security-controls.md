# IOS / IOS-XE Security Controls

## Contents

- [Access Control Lists (IOS/IOS-XE)](#access-control-lists-iosios-xe)
- [NAT / PAT](#nat--pat)
- [IPsec VPN (IKEv2 Site-to-Site)](#ipsec-vpn-ikev2-site-to-site)
- [Zone-Based Firewall (ZBF — IOS-XE)](#zone-based-firewall-zbf--ios-xe)
- [Layer 2 Security Hardening](#layer-2-security-hardening)
- [Attack Vectors and Mitigations](#attack-vectors-and-mitigations)
- [Firewall Policy Design Principles](#firewall-policy-design-principles)

## Access Control Lists (IOS/IOS-XE)

### Standard ACL (source IP only — place closest to destination)

```cisco
ip access-list standard MGMT-PERMIT
 permit 10.10.0.0 0.0.255.255
 deny   any log

interface GigabitEthernet0/0
 ip access-group MGMT-PERMIT in
```

### Extended ACL (src, dst, protocol, port — place closest to source)

```cisco
ip access-list extended INTERNET-OUT
 permit tcp 10.0.0.0 0.255.255.255 any eq 443
 permit tcp 10.0.0.0 0.255.255.255 any eq 80
 permit udp 10.0.0.0 0.255.255.255 any eq 53
 deny   ip any any log

interface GigabitEthernet0/1
 ip access-group INTERNET-OUT out
```

### Object-Group ACL (IOS-XE)

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

**ACL Design Rules**: always end with explicit `deny any log`; avoid `log` on high-volume permit entries; prefer named ACLs; leave sequence gaps (10, 20, 30); verify with `show ip access-lists <name>`.

## NAT / PAT

```cisco
! PAT (overload) — many-to-one
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

! Verify: show ip nat translations | show ip nat statistics
```

## IPsec VPN (IKEv2 Site-to-Site)

```cisco
crypto ikev2 proposal IKEV2-PROPOSAL
 encryption aes-cbc-256
 integrity sha256
 group 19

crypto ikev2 policy IKEV2-POLICY
 proposal IKEV2-PROPOSAL

crypto ikev2 keyring KR-SITE-B
 peer SITE-B
  address 203.0.113.2
  pre-shared-key <preshared-key>

crypto ikev2 profile IKEV2-PROFILE
 match identity remote address 203.0.113.2
 authentication remote pre-share
 authentication local pre-share
 keyring local KR-SITE-B

crypto ipsec transform-set TS-AES256 esp-aes 256 esp-sha256-hmac
 mode tunnel

crypto map CM-SITE-B 10 ipsec-isakmp
 set peer 203.0.113.2
 set transform-set TS-AES256
 set ikev2-profile IKEV2-PROFILE
 match address ACL-VPN-TRAFFIC
 set pfs group19

interface GigabitEthernet0/1
 crypto map CM-SITE-B

ip access-list extended ACL-VPN-TRAFFIC
 permit ip 10.1.0.0 0.0.255.255 10.2.0.0 0.0.255.255
```

**Troubleshooting**: `show crypto ikev2 sa detail`, `show crypto ipsec sa`, `show crypto map`. Common failures: mismatched PSK (`AUTH_FAILED`), mismatched transform set (`NO_PROPOSAL_CHOSEN`), unmirrored traffic selector ACLs, or MTU issues (apply `ip tcp adjust-mss 1360`).

## Zone-Based Firewall (ZBF — IOS-XE)

```cisco
zone security INSIDE
zone security DMZ
zone security OUTSIDE

class-map type inspect match-any INTERNET-APPS
 match protocol http
 match protocol https
 match protocol dns

policy-map type inspect INSIDE-TO-OUTSIDE
 class type inspect INTERNET-APPS
  inspect
 class class-default
  drop log

zone-pair security ZP-INSIDE-OUTSIDE source INSIDE destination OUTSIDE
 service-policy type inspect INSIDE-TO-OUTSIDE

interface GigabitEthernet0/0
 zone-member security INSIDE
interface GigabitEthernet0/1
 zone-member security OUTSIDE
```

## Layer 2 Security Hardening

### DHCP Snooping & Dynamic ARP Inspection (DAI)

```cisco
ip dhcp snooping
ip dhcp snooping vlan 10,20,30

interface GigabitEthernet0/1
 ip dhcp snooping trust
 ip arp inspection trust

interface range GigabitEthernet0/2-24
 ip dhcp snooping limit rate 10

ip arp inspection vlan 10,20,30
arp access-list STATIC-SERVERS
 permit ip host 10.0.0.100 mac host aabb.cc11.2233
ip arp inspection filter STATIC-SERVERS vlan 10
```

### 802.1X & Port Hardening

```cisco
aaa new-model
aaa authentication dot1x default group radius
dot1x system-auth-control

radius server CORP-RADIUS
 address ipv4 10.0.0.5 auth-port 1812 acct-port 1813
 key <radius-secret>

interface GigabitEthernet0/5
 switchport mode access
 switchport nonegotiate
 dot1x port-control auto
 dot1x host-mode multi-auth
 dot1x timeout quiet-period 10
 spanning-tree portfast

! Shutdown unused ports, move native VLAN off 1, disable CDP on untrusted ports, enable storm control
```

## Attack Vectors and Mitigations

| Attack | Description | Mitigation |
| --- | --- | --- |
| ARP Spoofing / Poisoning | Attacker replies to ARP with own MAC → MITM | DAI, static ARP entries, 802.1X |
| VLAN Hopping (switch spoofing) | Attacker negotiates trunk via DTP | `switchport nonegotiate`, never use VLAN 1 on trunks |
| VLAN Hopping (double-tagging) | Exploit native VLAN to jump one hop | Change native VLAN to unused VLAN (e.g. 999) |
| Rogue DHCP | Attacker serves DHCP responses | DHCP Snooping (untrusted all access ports) |
| CAM Overflow | Flood MAC table → switch broadcasts all | Port security: `switchport port-security maximum 2` |
| STP Attack | Attacker sends BPDU to become root | BPDU Guard, Root Guard |
| IP Spoofing | Forge source IP | uRPF (`ip verify unicast source reachable-via rx`) |
| Smurf DDoS | Broadcast amplification | `no ip directed-broadcast` |
| DNS Amplification | Abuse open resolvers | Disable recursion on authoritative; rate limiting; DNS firewall |

## Firewall Policy Design Principles

1. Default deny — allowlist only what is explicitly needed.
2. Stateful inspection for return traffic — do not manually permit return flows.
3. Segment DMZ from inside — DMZ-to-inside requires explicit permit.
4. Log denies with sampling or rate limiting.
5. Explicit permit before implicit deny on all interfaces.
6. Never permit `any any` even temporarily.
7. Egress filtering on all interfaces (not just inbound from outside).
8. Null-route known bad prefixes at edge routers (RTBH).
9. Scrubbing: normalise fragments, enforce MSS, reject illegal flag combos.
10. Separate management plane — OOB management or dedicated VRF.
