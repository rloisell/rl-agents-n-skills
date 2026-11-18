---
name: administering-unix-systems
description: Administers Solaris (9/10/11 SPARC and x86), RHEL/Linux (7/8/9, Rocky, AlmaLinux), and DNS diagnostics. Use when troubleshooting service failures, managing ZFS or LVM storage, configuring networking or firewalls, analyzing performance, hardening hosts, or validating DNS resolution.
compatibility: Solaris 9/10/11 SPARC & x86, RHEL 7/8/9, Rocky/AlmaLinux, BIND-utils (dig/nslookup/host)
---

# Administering Unix Systems

Platform-spanning Unix/Linux systems administration covering Solaris (9/10/11 SPARC/x86), RHEL (7/8/9), and DNS diagnostics.

## Contents

- [Constraints](#constraints)
- [Quick start](#quick-start)
- [Workflow](#workflow)
- [Verification](#verification)
- [References](#references)

## Constraints

- Label the target platform (`Solaris 9/10/11` or `RHEL 7/8/9`) at the top of any command sequence or configuration.
- Provide both the diagnostic command and the resolution command.
- Include inline comments explaining each probe in DTrace scripts.
- Always pair destructive or resizing storage operations with a post-change verification command (`zpool status`, `lvs`, `df -hT`).

## Quick start

| Task | Solaris | RHEL / Linux |
|---|---|---|
| Service management | `svcs` / `svcadm` / `svccfg` (SMF) | `systemctl` (systemd) |
| Service logs | `svcs -x <svc>` / `svcs -L <svc>` | `journalctl -u <unit>` |
| Storage | ZFS / UFS / VxVM / VxFS | LVM / ext4 / XFS / NFS |
| Volume snapshots | `zfs snapshot` | `lvcreate -s` (LVM snapshots) |
| Network bonding | IPMP (`ipadm`) / LACP (`dladm`) | `nmcli` / bonding / teaming |
| Package management | `pkg` (IPS) / `pkgadd` | `dnf` / `rpm` / `subscription-manager` |
| Performance tools | `dtrace` / `prstat` / `mpstat` / `iostat` | `perf` / `sar` / `vmstat` / `iostat` |
| Mandatory access | RBAC / Solaris Privileges | SELinux (`semanage`, `audit2allow`) |
| Virtualisation | LDoms / Zones | KVM / containers / namespaces |
| HW diagnostics | `prtdiag` / `prtconf` / `luxadm` / `cfgadm` | `dmidecode` / `lspci` / `lsblk` |
| Boot environment | OBP (`ok` prompt) -> `grub`/kernel | GRUB2 -> kernel -> systemd |
| Crash dump | `dumpadm` / `savecore` / `mdb` | `kdump` / `crash` |

## Workflow

| Scenario | Action |
|---|---|
| Service not starting (Solaris) | `svcs -xv <svc>` -> check dependency chain -> `svccfg -s <svc> listprop` |
| Service not starting (RHEL) | `systemctl status <unit>` -> `journalctl -xe -u <unit>` |
| ZFS pool degraded | `zpool status -v` -> identify failed device -> `zpool replace` or `zpool scrub` |
| LVM disk full | `df -hT` + `pvs && vgs && lvs` -> `lvextend -L +<size> /dev/<vg>/<lv>` -> `xfs_growfs` / `resize2fs` |
| High CPU (Solaris 10/11) | `prstat -a 1 5` / `prstat -Z` -> `dtrace` flame graph or `mdb` |
| High CPU (RHEL) | `top` / `sar -u 1 5` -> `perf top` -> `perf record -ag` / `perf report` |
| Solaris OBP prompt | `boot disk1 -s`, `probe-scsi-all`, `show-devs`, `setenv` |
| Cannot resolve packages (RHEL) | `subscription-manager repos --list-enabled` -> check `/etc/rhsm/rhsm.conf` proxy |
| Network interface down (Solaris) | `dladm show-link` -> `ipadm show-addr` -> `snoop` for live capture |
| SELinux blocking (RHEL) | `ausearch -m avc -ts recent` -> `audit2allow` -> `semanage` / `restorecon` |
| DNS resolution / propagation issue | `dig +trace <name>` -> compare `dig @<auth-ns>` vs local resolver |

## Verification

- **Services**: Confirm `online` state via `svcs <svc>` (Solaris) or `active (running)` via `systemctl is-active <unit>` (RHEL).
- **Storage**: Confirm pool/volume health and capacity with `zpool status -v` / `zfs list` or `lvs` / `df -hT`.
- **Networking & DNS**: Confirm link/address state (`ipadm show-addr` / `nmcli device status`) and authoritative DNS answers (`dig +short @<auth-ns> <name>`).

## References

- [Linux RHEL Administration](references/linux-rhel.md) — systemd, LVM, SELinux, `nmcli`, `firewalld`, DNF/RPM, performance, `kdump`, security hardening, and log locations.
- [Solaris & SPARC Administration](references/solaris-sparc.md) — SMF, ZFS, Zones, IPMP, `dladm`/`ipadm`, DTrace, SPARC hardware/OBP, LDoms, Jumpstart/AI, VxVM/VxFS, and log locations.
- [DNS Diagnostics](references/dns-diagnostics.md) — `dig`, `nslookup`, `host`, SPF/DKIM/DMARC, DNSSEC, AXFR/IXFR, reverse PTR, and split-horizon troubleshooting.
- [Acceptance Criteria](references/acceptance-criteria.md) — observable pass/fail criteria for Solaris, RHEL, and DNS administration outputs.
