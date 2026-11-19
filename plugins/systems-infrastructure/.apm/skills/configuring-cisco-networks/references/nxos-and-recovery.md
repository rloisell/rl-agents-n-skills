# Cisco NX-OS, Image Management & Recovery

Password recovery, IOS image upgrades, NX-OS differences (Nexus), and GNS3/EVE-NG lab reference.

## Contents

- [Password Recovery](#password-recovery)
- [IOS Image Management](#ios-image-management)
- [NX-OS Differences (Nexus)](#nx-os-differences-nexus)
- [Home Lab Tips](#home-lab-tips)

---

## Password Recovery

```text
Cisco Router (IOS):
1. Power cycle — press Break within 60s of power-on to enter ROMmon
2. rommon> confreg 0x2142    (skip startup-config on boot)
3. rommon> reset
4. Router boots with no config — type 'no' to skip setup dialog
5. Router> enable  (no password needed)
6. copy startup-config running-config
7. configure terminal -> change enable secret
8. config-register 0x2102    (restore normal boot)
9. copy running-config startup-config -> reload

Catalyst Switch (IOS):
1. Hold MODE button during power-on until System LED amber
2. switch: flash_init
3. switch: load_helper
4. switch: rename flash:config.text flash:config.text.bak
5. switch: boot
6. Proceed without config -> enable -> rename back -> copy to running
7. Set new password -> copy running-config startup-config -> reload
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
copy scp://<admin-user>@10.0.0.5/c2900-universalk9-mz.SPA.157-3.M8.bin flash:

! Verify MD5 integrity
verify /md5 flash:c2900-universalk9-mz.SPA.157-3.M8.bin

! Set new boot image
boot system flash:c2900-universalk9-mz.SPA.157-3.M8.bin
copy running-config startup-config
reload

! Back up config
copy running-config tftp://10.0.0.5/R1-backup.cfg
copy running-config scp://<admin-user>@10.0.0.5/R1-backup.cfg
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

! vPC (Virtual Port Channel) — active-active dual-homed to two Nexus switches
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

```text
GNS3 / EVE-NG image requirements:
  IOS 12.4 / 15.x for c3600/c7200 router images
  IOSv (IOS-on-QEMU) for IOS-XE 15.x/16.x
  IOSvL2 for Catalyst switching features
  NX-OSv for Nexus simulation

Console access:
  GNS3: right-click node -> Console (aux port)
  Physical: USB-to-RJ45 console cable; 9600 8N1 in screen / SecureCRT

Quick reset physical switch:
  erase startup-config -> reload -> do NOT save when prompted

TFTP server (macOS):
  sudo launchctl load -F /System/Library/LaunchDaemons/tftp.plist
  sudo cp image.bin /private/tftpboot/
  # Files served from /private/tftpboot
```
