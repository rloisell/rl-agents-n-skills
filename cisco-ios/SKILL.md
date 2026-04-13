---
name: cisco-ios
description: Cisco IOS, IOS-XE, and NX-OS configuration and troubleshooting for home lab and enterprise environments. Covers initial device setup, interface configuration, VLANs and trunking (802.1Q), routing (static, OSPF, BGP, EIGRP), NAT/PAT, ACLs, HSRP, VTP, EtherChannel, SSH hardening, password recovery, IOS image management (TFTP/SCP), and NX-OS basics. Use when configuring Cisco routers and switches, troubleshooting connectivity, or building lab topologies.
metadata:
  author: Ryan Loiselle
  version: "1.0"
compatibility: Cisco IOS 12.x/15.x, IOS-XE 16.x/17.x, NX-OS 7.x/9.x. Home lab and enterprise. GNS3/EVE-NG compatible.
---

# Cisco IOS Skill

Cisco router and switch configuration reference — home lab to enterprise.

**Ryan's context**: CCNP R&S (BSCI/BCMSN/ISCW/ONT), active home lab. CCNA 2003–2006.

**Related skills:**
- Routing protocol depth → [`../network-architect/SKILL.md`](../network-architect/SKILL.md)
- ACLs, NAT, IPsec, ZBF → [`../network-security/SKILL.md`](../network-security/SKILL.md)

---

## Initial Device Setup

```cisco
! Connect via console (9600 8N1) then:
enable
configure terminal

! Hostname
hostname R1

! Disable DNS lookup (prevents typo delays in CLI)
no ip domain-lookup

! Time and timezone
clock timezone PST -8
clock summer-time PDT recurring
ntp server 216.239.35.0

! Enable password (use secret — MD5 hash)
enable secret StrongPassword1!

! Console and VTY lines
line console 0
 password ConsolePw1!
 login
 exec-timeout 10 0
 logging synchronous

line vty 0 4
 transport input ssh
 login local
 exec-timeout 10 0

! Local user (required for SSH)
username ryan privilege 15 secret Admin1Password!

! SSH setup
ip domain-name lab.example.com
crypto key generate rsa modulus 2048
ip ssh version 2
ip ssh time-out 60
ip ssh authentication-retries 3

! Disable Telnet on VTY (SSH only)
line vty 0 4
 transport input ssh

! Save
end
write memory
! or: copy running-config startup-config
```

---

## Interface Configuration

```cisco
! Physical interface — routed
interface GigabitEthernet0/0
 description WAN-to-ISP
 ip address 203.0.113.2 255.255.255.252
 duplex auto
 speed auto
 no shutdown

! Physical interface — layer 2 access port
interface FastEthernet0/1
 description PC-VLAN10
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 no shutdown

! Loopback (stable router-id / management address)
interface Loopback0
 description MGMT-LOOPBACK
 ip address 10.255.0.1 255.255.255.255
 no shutdown

! Sub-interface (router-on-a-stick inter-VLAN routing)
interface GigabitEthernet0/1.10
 encapsulation dot1Q 10
 ip address 10.0.10.1 255.255.255.0
 description VLAN10-GATEWAY

interface GigabitEthernet0/1.20
 encapsulation dot1Q 20
 ip address 10.0.20.1 255.255.255.0
 description VLAN20-GATEWAY

! Verify interfaces
show interfaces status
show ip interface brief
show interfaces GigabitEthernet0/0
```

---

## VLANs and Trunking (Catalyst Switches)

```cisco
! Create VLANs
vlan 10
 name DATA
vlan 20
 name VOICE
vlan 99
 name MGMT
vlan 999
 name NATIVE-UNUSED

! Access port
interface FastEthernet0/5
 switchport mode access
 switchport access vlan 10
 switchport voice vlan 20         ! Cisco IP phone: data on 10, voice on 20
 spanning-tree portfast
 spanning-tree bpduguard enable
 no shutdown

! Trunk port (to router or another switch)
interface GigabitEthernet0/1
 switchport trunk encapsulation dot1q   ! IOS — required before mode trunk
 switchport mode trunk
 switchport trunk native vlan 999       ! never use VLAN 1 as native
 switchport trunk allowed vlan 10,20,99,999
 no shutdown

! SVI — Layer 3 switch management/gateway interface
interface Vlan99
 description MGMT-SVI
 ip address 10.99.0.1 255.255.255.0
 no shutdown

ip default-gateway 10.99.0.254          ! for Layer 2 switch management

! Verify
show vlan brief
show interfaces trunk
show interfaces GigabitEthernet0/1 trunk
```

---

## VTP

```cisco
! Recommended: transparent mode (no VTP propagation risk)
vtp mode transparent
vtp domain LAB

! Server mode (propagates VLANs to clients)
vtp mode server
vtp domain CORP
vtp password SecretVTP1!
vtp version 3                          ! VTPv3 preferred — protects against reset attacks

show vtp status
show vtp counters
```

---

## Spanning Tree

```cisco
! Set root bridge (lower priority wins)
spanning-tree vlan 10 priority 4096     ! root
spanning-tree vlan 20 priority 8192     ! secondary root

! Or use macro
spanning-tree vlan 10 root primary
spanning-tree vlan 20 root secondary

! Global portfast default (all access ports)
spanning-tree portfast default

! Per-port hardening
interface range FastEthernet0/1-24
 spanning-tree portfast
 spanning-tree bpduguard enable

! Protect root bridge position on uplinks
interface GigabitEthernet0/2
 spanning-tree guard root

! Verify
show spanning-tree vlan 10
show spanning-tree summary
```

---

## EtherChannel

```cisco
! LACP (preferred)
interface range GigabitEthernet0/1-2
 switchport trunk encapsulation dot1q
 switchport mode trunk
 channel-group 1 mode active          ! LACP active
 no shutdown

interface Port-channel1
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,20,99

! PAgP (Cisco-only)
 channel-group 1 mode desirable

! Static
 channel-group 1 mode on

show etherchannel summary
show etherchannel 1 detail
```

---

## Static Routing

```cisco
! Static route
ip route 10.2.0.0 255.255.0.0 10.0.0.2

! Default route
ip route 0.0.0.0 0.0.0.0 203.0.113.1

! Floating static (higher AD — backup route)
ip route 0.0.0.0 0.0.0.0 203.0.113.5 254

! Null route  (blackhole / summary discard)
ip route 10.0.0.0 255.0.0.0 Null0

show ip route
show ip route static
```

---

## OSPF (IOS)

```cisco
router ospf 1
 router-id 10.255.0.1
 passive-interface default           ! suppress hellos on all interfaces
 no passive-interface GigabitEthernet0/0   ! re-enable on OSPF interfaces
 network 10.0.10.0 0.0.0.255 area 0
 network 10.0.20.0 0.0.0.255 area 0
 network 10.255.0.1 0.0.0.0 area 0  ! advertise loopback
 default-information originate       ! propagate default route (if you have one)

! Per-interface authentication
interface GigabitEthernet0/0
 ip ospf authentication message-digest
 ip ospf message-digest-key 1 md5 OSPFSecret1!

show ip ospf neighbor
show ip ospf database
show ip route ospf
```

---

## HSRP

```cisco
interface GigabitEthernet0/1
 ip address 10.0.10.2 255.255.255.0   ! real IP
 standby version 2
 standby 1 ip 10.0.10.1               ! virtual IP (default gateway for hosts)
 standby 1 priority 110               ! higher = active (default 100)
 standby 1 preempt                    ! take over when priority is highest
 standby 1 authentication md5 key-string HSRPsecret1!
 standby 1 track 1 decrement 20       ! track object; reduce priority if fails

ip sla 1
 icmp-echo 8.8.8.8 source-interface GigabitEthernet0/0
 frequency 10
ip sla schedule 1 life forever start-time now

track 1 ip sla 1 reachability

show standby brief
show standby GigabitEthernet0/1
```

---

## NAT / PAT

```cisco
ip nat inside source list NAT-INSIDE interface GigabitEthernet0/0 overload

ip access-list standard NAT-INSIDE
 permit 10.0.0.0 0.255.255.255

interface GigabitEthernet0/0
 ip nat outside

interface GigabitEthernet0/1
 ip nat inside

! Static NAT (DMZ server)
ip nat inside source static 10.0.0.10 203.0.113.10

show ip nat translations
show ip nat statistics
```

---

## DHCP Server

```cisco
ip dhcp excluded-address 10.0.10.1 10.0.10.20    ! reserve gateway + static range
ip dhcp excluded-address 10.0.10.254

ip dhcp pool VLAN10
 network 10.0.10.0 255.255.255.0
 default-router 10.0.10.1
 dns-server 8.8.8.8 8.8.4.4
 domain-name lab.example.com
 lease 1                                           ! 1 day

show ip dhcp pool
show ip dhcp binding
show ip dhcp conflict
```

---

## ACLs

```cisco
! Named extended ACL
ip access-list extended OUTBOUND-FILTER
 permit tcp 10.0.0.0 0.255.255.255 any eq 443
 permit tcp 10.0.0.0 0.255.255.255 any eq 80
 permit udp 10.0.0.0 0.255.255.255 any eq 53
 deny   ip any any log

interface GigabitEthernet0/1
 ip access-group OUTBOUND-FILTER out

show ip access-lists OUTBOUND-FILTER
show ip access-lists               ! check hit counters
```

---

## Password Recovery

```
Cisco Router (IOS):
1. Power cycle — press Break within 60s of power-on to enter ROMmon
2. rommon> confreg 0x2142    (skip startup-config on boot)
3. rommon> reset
4. Router boots with no config — type 'no' to skip setup dialog
5. Router> enable  (no password needed)
6. copy startup-config running-config
7. configure terminal → change enable secret
8. config-register 0x2102    (restore normal boot)
9. copy running-config startup-config → reload

Catalyst Switch (IOS):
1. Hold MODE button during power-on until System LED amber
2. switch: flash_init
3. switch: load_helper
4. switch: rename flash:config.text flash:config.text.bak
5. switch: boot
6. Proceed without config → enable → rename back → copy to running
7. Set new password → copy running-config startup-config → reload
```

---

## IOS Image Management

```cisco
! Check current image
show version | include IOS
show flash:

! Copy image via TFTP
copy tftp://10.0.0.5/c2900-universalk9-mz.SPA.157-3.M8.bin flash:

! Copy image via SCP (more secure)
copy scp://ryan@10.0.0.5/c2900-universalk9-mz.SPA.157-3.M8.bin flash:

! Verify MD5 integrity
verify /md5 flash:c2900-universalk9-mz.SPA.157-3.M8.bin

! Set new boot image
boot system flash:c2900-universalk9-mz.SPA.157-3.M8.bin
copy running-config startup-config
reload

! Back up config
copy running-config tftp://10.0.0.5/R1-backup.cfg
copy running-config scp://ryan@10.0.0.5/R1-backup.cfg
```

---

## Useful Show / Debug Commands

```cisco
! System
show version                         ! IOS version, uptime, hardware
show inventory                       ! chassis, modules, serial numbers
show environment all                 ! temperature, power, fans (Cat 6500+)
show processes cpu sorted            ! CPU utilisation per process
show processes memory sorted         ! memory per process

! Interfaces
show interfaces                      ! full detail all interfaces
show interfaces status               ! quick table (speed/duplex/VLAN)
show ip interface brief              ! IP addresses + line/protocol state
show interfaces counters errors      ! CRC, input errors, etc.

! Routing
show ip route                        ! full routing table
show ip route summary                ! summary counts per protocol
show ip protocols                    ! routing process status
show ip ospf neighbor                ! OSPF neighbour adjacencies
show ip bgp summary                  ! BGP peers + prefix counts

! Switching
show mac address-table               ! CAM table
show mac address-table count         ! how full is the CAM?
show cdp neighbors detail            ! adjacent Cisco devices
show lldp neighbors detail           ! LLDP neighbours

! Logging / debugging
show logging                         ! syslog buffer
debug ip packet                      ! packet-level (use carefully — CPU intensive)
debug ip ospf events
undebug all                          ! turn off all debugs
terminal monitor                     ! show debug output on SSH/VTY session
```

---

## NX-OS Differences (Nexus)

```cisco
! Feature enablement (NX-OS requires explicit feature activation)
feature ospf
feature bgp
feature lacp
feature vpc
feature interface-vlan
feature hsrp

! NX-OS VLAN syntax (no 'switchport trunk encapsulation dot1q' — not needed)
interface Ethernet1/1
 switchport mode trunk
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,20,99

! VPC (Virtual Port Channel) — active-active dual-homed to two Nexus switches
vpc domain 1
 peer-keepalive destination 10.0.0.2 source 10.0.0.1
 role priority 100                   ! lower = primary

interface port-channel10
 vpc 10

! NX-OS show commands
show feature
show vpc
show interface trunk
show vlan
show cdp neighbors

! VDC (Virtual Device Context — Nexus 7000/7700)
show vdc
switchto vdc <name>
```

---

## Home Lab Tips

```
GNS3 / EVE-NG image requirements:
  IOS 12.4 / 15.x for c3600/c7200 router images
  IOSv (IOS-on-QEMU) for IOS-XE 15.x/16.x
  IOSvL2 for Catalyst switching features
  NX-OSv for Nexus simulation

Console access:
  GNS3: right-click node → Console (aux port)
  Physical: USB-to-RJ45 console cable; 9600 8N1 in screen / SecureCRT

Quick reset physical switch:
  erase startup-config → reload → do NOT save when prompted

TFTP server (macOS):
  sudo launchctl load -F /System/Library/LaunchDaemons/tftp.plist
  sudo cp image.bin /private/tftpboot/
  # Files served from /private/tftpboot
```

---

## CISCO_IOS_KNOWLEDGE

> Append discoveries here. Format: `YYYY-MM-DD: <note>`
