# systems-infrastructure Plugin

Unix/Linux/Solaris systems administration, DNS diagnostics, and Cisco IOS/IOS-XE/NX-OS networking.

## Purpose
Provides self-contained skills for administering Solaris (9/10/11 SPARC and x86), RHEL/Linux (7/8/9, Rocky, AlmaLinux), DNS diagnostics (`dig`, `nslookup`, `host`), and Cisco IOS/IOS-XE/NX-OS routing, switching, and recovery.

## Plugin Components

### Skills
- `administering-unix-systems` — Platform-spanning Unix/Linux administration covering Solaris (SMF, ZFS, Zones, IPMP, DTrace, OBP, LDoms, VxVM), RHEL/Linux (systemd, LVM, SELinux, `nmcli`, `firewalld`, DNF/RPM, `kdump`, hardening), and DNS diagnostics (`dig`, `nslookup`, `host`, SPF/DKIM/DMARC, DNSSEC).
- `configuring-cisco-networks` — Cisco IOS, IOS-XE, and NX-OS configuration, troubleshooting, and recovery covering VLANs, trunking, STP, EtherChannel, OSPF, HSRP, NAT/PAT, ACLs, DHCP, SSH hardening, password recovery, IOS image management, and NX-OS vPC/VDC.

### Sub-Agents
None. Legacy `sysadmin` and `cisco-ios` agents have been retired into the self-contained skills above.

### Hooks
None.

## Directory Structure

```text
systems-infrastructure/
├── .apm/
│   └── skills/
│       ├── administering-unix-systems/
│       │   ├── SKILL.md
│       │   └── references/
│       │       ├── dns-diagnostics.md
│       │       ├── linux-rhel.md
│       │       └── solaris-sparc.md
│       └── configuring-cisco-networks/
│           ├── SKILL.md
│           └── references/
│               ├── ios-routing-switching.md
│               └── nxos-and-recovery.md
├── .claude-plugin/
│   └── plugin.json
├── apm.yml
└── README.md
```
