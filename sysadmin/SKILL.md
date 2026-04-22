---
name: sysadmin
description: Unix/Linux sysadmin skill covering Solaris 9/10/11 SPARC (LDoms, Zones, SMF, ZFS, DTrace) and RHEL/Linux (systemd, LVM, SELinux, firewalld, nmcli, dnf). Use when diagnosing service failures, managing storage, recovering from boot issues, configuring networking, or performing package management on Solaris or RHEL hosts. Delegates to solaris and linux-rhel skills.
tools: Read, Grep, Glob
metadata:
  author: Ryan Loiselle
  version: "1.0"
compatibility: Solaris 9/10/11 SPARC (Sun Fire, M-series LDoms), RHEL 7/8/9, Rocky Linux, AlmaLinux
---

# Sysadmin

Platform-spanning Unix/Linux systems administration. This skill is the entry point
for both Solaris and RHEL domains.

For detailed Solaris commands (SMF, ZFS, Zones, DTrace, IPMP, OBP), see `../solaris/SKILL.md`.
For detailed RHEL commands (systemd, LVM, SELinux, firewalld, nmcli), see `../linux-rhel/SKILL.md`.

---

## Platform Decision Table

| Task | Solaris | RHEL/Linux |
|---|---|---|
| Service management | `svcs` / `svcadm` / `svccfg` (SMF) | `systemctl` (systemd) |
| View service logs | `svcs -x <svc>` / `svcs -l <svc>` | `journalctl -u <unit>` |
| Storage management | ZFS / UFS / VxVM | LVM / ext4 / XFS |
| Volume snapshots | `zfs snapshot` | LVM snapshots |
| Network bonding | IPMP (`ipadm`) / LACP (`dladm`) | `nmcli` / bonding / teaming |
| Package management | IPS (`pkg`) / pkgadd | `dnf` / `rpm` |
| Performance tools | `dtrace` / `prstat` / `iostat` | `perf` / `sar` / `iostat` |
| Mandatory access | RBAC / Solaris Privileges | SELinux |
| Virtualisation | LDoms / Zones | KVM / containers |
| Boot environment | OBP (`ok` prompt) | GRUB2 |
| Crash dump | `dumpadm` / `savecore` | `kdump` / `crash` |

---

## Diagnostic First Steps

### Service failure
```bash
# Solaris
svcs -x                   # show services in maintenance/degraded
svcs -l <svc>             # detail including log path
tail -100 /var/svc/log/<svc>.log

# RHEL
systemctl status <unit>
journalctl -u <unit> -n 100 --no-pager
```

### Storage emergency
```bash
# Solaris ZFS
zpool status              # pool health
zfs list                  # dataset usage
zpool scrub <pool>        # start scrub

# RHEL LVM
pvs && vgs && lvs         # physical/volume/logical view
df -hT                    # filesystem usage + type
```

### Performance triage
```bash
# Solaris
prstat -a 1 5             # process CPU/memory
iostat -xn 1 5            # disk I/O

# RHEL
sar -u 1 5                # CPU utilisation
iostat -xz 1 5            # disk I/O
```

---

## SYSADMIN_KNOWLEDGE

<!-- agent-evolution appends discoveries here -->
<!-- Format: - YYYY-MM-DD: [Project] <imperative statement> -->
