---
name: solaris
description: Solaris 9/10/11 administration on SPARC (UltraSPARC III/IV/T-series) and x86. Covers SMF (svcs/svcadm/svccfg), ZFS (pools/datasets/snapshots/send-receive/scrub), Zones (sparse/whole-root/branded/LDoms), DTrace, IPMP, LACP/dladm/ipadm, VxVM/VxFS, UFS, OpenBoot (OBP), Jumpstart/AI install, hardware diagnostics (prtdiag/prtconf/luxadm/cfgadm), Solaris RBAC, and process management. Use when working on production Solaris systems or migrating Solaris workloads.
metadata:
  author: Ryan Loiselle
  version: "1.0"
compatibility: Solaris 9, 10, 11. SPARC UltraSPARC-III/IV, T1/T2/T4/T5/M-series. And x86 where noted.
---

# Solaris Skill

Expert Solaris administration reference — SPARC production focus.

**Ryan's context**: Expert-level Solaris 9/10/11 SPARC admin. UltraSPARC III/IV (`Sun Blade`, `Sun Fire`, `E6900`), T-series (`T1/T2/T4/T5`), M-series. Managed production systems including Jumpstart infrastructure, ZFS migrations, Solaris Zones, and VxVM storage stacks.

---

## SMF — Service Management Framework (Solaris 10/11)

```bash
# View service states
svcs -a                              # all services (online, offline, degraded, disabled)
svcs -x                              # only those with explanation (failed/degraded)
svcs -xv <svc-name>                  # verbose explanation with log path
svcs -l apache22                     # full property listing for a service

# Service control
svcadm enable  <svc>                 # enable (persistent across reboots)
svcadm disable <svc>
svcadm restart <svc>
svcadm refresh <svc>                 # re-read manifest properties (like reload)
svcadm clear   <svc>                 # clear maintenance state after fixing

# Configuration
svccfg import /var/svc/manifest/...  # import manifest
svccfg -s <svc> listprop             # list all properties
svccfg -s <svc> setprop <pg>/<prop>=<type>:<value>
svccfg -s <svc> delprop <pg>/<prop>

# Logs
svcs -L <svc>                        # print log path
tail -f $(svcs -L <svc>)             # follow service log

# Instance vs FMRI
svc:/network/http:apache22           # FMRI format: svc:/category/name:instance
svcs http                            # partial match also works
```

### Service States

| State | Meaning |
|-------|---------|
| online | Running normally |
| offline | Stopped; dependencies not yet met |
| disabled | Administratively disabled |
| maintenance | Failed; requires `svcadm clear` after fix |
| degraded | Running but not fully functional |
| uninitialized | Not yet evaluated |
| legacy_run | Pre-SMF init.d service that is running |

---

## ZFS

### Pool Management

```bash
# Create a mirror pool
zpool create -f rpool mirror c1t0d0 c1t1d0

# Check pool status
zpool status                         # health, errors, device list
zpool status -v                      # verbose — includes I/O errors per device
zpool list                           # capacity and allocation

# Scrub (data integrity check)
zpool scrub rpool
zpool status rpool                   # monitor progress

# Replace a failed disk
zpool replace rpool c1t0d0 c1t2d0    # online replacement

# Add log/cache devices (ARC/SLOG)
zpool add rpool log c2t0d0           # SLOG (ZIL) device
zpool add rpool cache c2t1d0         # L2ARC device

# Import/Export (for moving pools)
zpool export rpool
zpool import rpool
zpool import -d /dev/dsk             # scan a directory for pools
```

### Dataset Management

```bash
# Create datasets
zfs create rpool/data
zfs create -o mountpoint=/var/www rpool/www

# Properties
zfs get all rpool/data               # all properties
zfs set compression=lz4 rpool/data
zfs set quota=100G rpool/data
zfs set reservation=10G rpool/data
zfs set atime=off rpool/data         # disable atime for performance
zfs set recordsize=128k rpool/data   # tune for DB (128k–1M) or files (128k default)

# Snapshots
zfs snapshot rpool/data@snap1        # create
zfs list -t snapshot                  # list all snapshots
zfs diff rpool/data@snap1 rpool/data  # what changed since snapshot
zfs rollback rpool/data@snap1         # roll back (destroys newer snapshots)
zfs destroy rpool/data@snap1          # delete snapshot

# Clone
zfs clone rpool/data@snap1 rpool/data-clone

# Send / Receive (replication/migration)
zfs send rpool/data@snap1 | ssh backup-host zfs receive tank/data
zfs send -R rpool/data@snap1 | gzip > /backup/data.zfs.gz     # recursive + compress
zfs send -i rpool/data@snap1 rpool/data@snap2 | ...            # incremental send
```

---

## Solaris Zones

```bash
# List zones
zoneadm list -cv

# Zone states: configured → installed → ready → running

# Configure a sparse-root zone (Solaris 10)
zonecfg -z myzone
  create
  set zonepath=/zones/myzone
  set autoboot=true
  add net
    set address=10.0.0.50/24
    set physical=e1000g0
    set defrouter=10.0.0.1
  end
  verify; commit; exit

# Install
zoneadm -z myzone install
zoneadm -z myzone boot
zlogin myzone                        # interactive login to zone
zlogin -C myzone                     # console login

# Solaris 11 — ipkg zone (IPS-aware)
zonecfg -z myzone
  create -b                          # blank zone
  set brand=solaris
  ...

# Halt / uninstall
zoneadm -z myzone halt
zoneadm -z myzone uninstall
zonecfg -z myzone delete

# Branded zones (BrandZ) — run Solaris 8/9 apps on Solaris 10 host
zonecfg -z legacy8
  set brand=solaris8
  ...
```

---

## IPMP — IP Network Multipathing

```bash
# Solaris 10 style
# Create interfaces in an IPMP group
ifconfig e1000g0   plumb
ifconfig e1000g0   10.0.0.10/24 group ipmp0 up
ifconfig e1000g1   plumb
ifconfig e1000g1   10.0.0.11/24 group ipmp0 standby up

ifconfig ipmp0                       # show IPMP group status
ipmpstat -g                          # group summary
ipmpstat -i                          # interface detail

# Solaris 11 with dladm/ipadm
dladm create-ipmp ipmp0
dladm add-ipmp -i net0 ipmp0
dladm add-ipmp -i net1 ipmp0
ipadm create-addr -T static -a 10.0.0.10/24 ipmp0/v4
```

---

## Network Administration (Solaris 11)

```bash
# dladm — datalink management
dladm show-link                      # all links and state
dladm show-phys                      # physical interfaces
dladm show-bridge                    # bridges
dladm create-vlan -l net0 -v 100 net0.100    # VLAN interface
dladm create-aggr -l net0 -l net1 aggr0      # LACP aggregation
dladm show-aggr                      # aggregation status

# ipadm — IP address management
ipadm show-addr                      # all addresses
ipadm create-addr -T dhcp net0/dhcp  # DHCP
ipadm create-addr -T static -a 10.0.0.5/24 net0/v4  # static
ipadm delete-addr net0/v4

# snoop — Solaris packet capture (analogous to tcpdump)
snoop -d net0                        # capture on net0
snoop -o /tmp/cap.snoop              # save to file
snoop -i /tmp/cap.snoop              # read file
snoop host 10.0.0.1 and port 443     # filter
snoop -v                             # verbose decode
```

---

## DTrace

```bash
# One-liners
dtrace -n 'syscall:::entry { @[execname] = count(); }'     # syscall counts per process
dtrace -n 'io:::start { @[execname] = sum(args[0]->b_bcount); }'  # I/O bytes per proc
dtrace -n 'profile-997 /arg0/ { @[stack()] = count(); }'  # CPU flame graph

# Process-level tracing
dtrace -n 'syscall::read:entry /pid == $1/ { trace(arg2); }' <pid>

# ZFS I/O latency
dtrace -n 'zfs::: { @lat[probename] = quantize(arg0); }'

# Track slow disk I/Os (>10ms)
dtrace -n 'io:::done /args[0]->b_flags & B_READ &&
           (timestamp - self->start) > 10000000/
           { printf("%s %s %d\n", execname, args[2]->fi_pathname,
             (timestamp - self->start)/1000000); }
           io:::start { self->start = timestamp; }'
```

---

## Hardware Diagnostics (SPARC)

```bash
# System hardware inventory
prtconf                              # hardware tree and memory
prtconf -v                           # verbose (device properties)
prtdiag                              # system config + fault indicators
prtdiag -v                           # verbose — component status
psrinfo -v                           # CPU info
psrinfo -p                           # physical processor count

# Storage
luxadm display /dev/rdsk/c1t0d0s2   # Fibre Channel LUN detail
luxadm probe                         # scan for FC devices
cfgadm -al                           # all attachment points (slots, disks, SBus)
cfgadm -c configure c1               # configure a device
cfgadm -c unconfigure c1             # hot-remove preparation
iostat -xnz 2                        # per-disk I/O (extended, name, non-zero)

# FRU / fault isolation
fmadm faulty                         # active faults (Solaris 10/11 FMA)
fmadm repaired <uuid>                # mark FRU repaired
fmdump -e                            # error event log
fmsconfig                            # fault management config
```

---

## OpenBoot PROM (OBP) — SPARC

```
# Reach OBP:
  Halt system: init 0 → ok prompt
  Break from console: ~# (telnet), Break key, or Stop-A (keyboard)

# Key OBP commands
ok boot                              # boot default device
ok boot disk1                        # boot disk 1
ok boot disk1 -s                     # single-user mode
ok boot cdrom                        # boot from CD/DVD
ok boot net                          # net boot (RARP/TFTP/Jumpstart)
ok boot -r                           # reconfigure boot (rescans devices)
ok probe-scsi-all                    # scan all SCSI/FC buses
ok probe-ide                         # scan IDE
ok show-disks                        # list disk aliases
ok show-devs                         # device tree
ok devalias                          # list all device aliases
ok setenv auto-boot? false           # prevent auto-boot
ok setenv boot-device disk1 net      # set boot order
ok printenv                          # show all NVRAM variables
ok reset-all                         # hard reset (like power cycle)
```

---

## LDoms — Logical Domains (Oracle VM Server for SPARC)

LDoms virtualise T-series SPARC hardware (T1/T2/T4/T5/M-series) at the CPU/memory/IO level. Requires Solaris 10 Update 5+ or Solaris 11 on a CMT processor. The hypervisor runs in firmware; `ldm` is the management tool.

### Domain Roles

| Domain | Role | Notes |
|--------|------|-------|
| Primary (control) | Boots first; owns hardware; runs `ldmd` | Cannot be suspended or migrated |
| Service (I/O) | Hosts virtual disk/network switches | Usually `primary` also acts as service domain |
| Guest | Standard Solaris instance with virtual resources | Can be live-migrated (T4/T5) |
| Root | Has direct PCIe bus ownership | For physical I/O pass-through to a guest |

### Initial Setup (after enabling hypervisor)

```bash
# On first boot after enabling LDoms:
ldm set-core 4 primary        # allocate cores to primary domain
ldm set-memory 4G primary     # allocate memory to primary
ldm start-reconf primary      # stage reconfiguration (takes effect after reboot)
# Reboot system — hypervisor now active

# Verify hypervisor is running
virtinfo -a
ldm ls                        # list all domains (primary shows as active)
```

### Virtual Switch and VDS

```bash
# Create a virtual switch (backed by physical NIC)
ldm add-vswitch net-dev=net0 primary-vsw0 primary

# Create a virtual disk service (backed by ZFS volume or disk)
zfs create -V 80G rpool/vdisk-guest1
ldm add-vdsdev /dev/zvol/dsk/rpool/vdisk-guest1 vol1@primary-vds0

# If VDS not yet created:
ldm add-vds primary-vds0 primary
```

### Creating a Guest Domain

```bash
# Add core/memory/devices
ldm add-domain guest1
ldm set-core 2 guest1
ldm set-memory 4G guest1
ldm add-vnet vnet0 primary-vsw0 guest1               # virtual NIC
ldm add-vdisk vdisk0 vol1@primary-vds0 guest1         # virtual disk
ldm set-variable boot-device=vdisk0 guest1            # boot order

# Bind and start
ldm bind-domain guest1
ldm start-domain guest1
ldm attach-console guest1                             # attach to console (like serial)
# Detach console: ~.   (tilde-dot)
```

### Guest Domain Lifecycle

```bash
ldm ls                         # list all domains with status
ldm ls -l guest1               # detailed info (cores, memory, devices)
ldm stop-domain guest1         # graceful stop (calls init 5 inside guest)
ldm stop-domain -f guest1      # forced stop (power off)
ldm start-domain guest1
ldm destroy guest1             # remove domain (does not delete backing storage)

# Save/restore domain config
ldm add-spconfig saved-config  # save running config to SP
ldm list-spconfig              # list saved configs on SP
ldm remove-spconfig <name>
```

### Live Migration (T4/T5 — requires identical hardware generation)

```bash
ldm migrate-domain guest1 root@target-host
ldm migrate-domain -p guest1 root@target-host        # dry-run (check only)
```

### Resource Inspection

```bash
ldm ls-devices                 # all hardware resources (cores, memory, IO)
ldm ls-devices -a core         # all CPU cores
ldm ls-devices memory          # memory blocks
ldm ls-io                      # PCIe devices and assignment

# From inside a guest — confirm virtualised
virtinfo                       # shows LDom guest info
prtconf | grep -i "virtual"
```

### Console Access

```bash
# From primary (service) domain
ldm attach-console guest1      # direct attach
# Escape: ~.

# Via ILOM / XSCF Serial Console (T-series):
# ssh to ILOM → start /SP/console → select domain
```

### T-Series Hardware Notes

```
T1 (Niagara 1): 8 cores × 4 threads = 32 strands. Single CMT chip.
T2 (Niagara 2): 8 cores × 8 threads = 64 strands. Integrated 10GbE.
T4: 8 cores × 8 threads. Out-of-order exec; much stronger single-thread perf vs T1/T2.
T5: 16 cores × 8 threads = 128 strands per socket. Up to 8 sockets (T5-8 = 1024 strands).

Core allocation must be in whole cores (4 threads each on T1/T4; 8 on T2/T5).
Memory allocation must be aligned to Memory Address Range boundary (typically 256MB granularity).
LDom guests on T4/T5 support crypto acceleration (Camellia, AES, RSA) via virtual crypto service.
```

---

## Jumpstart / AI Install

```bash
# Solaris 10 Jumpstart
# Server requirements: RARP/BOOTP, TFTP, NFS
# Files: /etc/bootparams, /etc/ethers, /tftpboot/hostname
add_install_client -d -e <mac> -s <server>:<path> <arch> <type>

# Solaris 11 AI (Automated Install)
installadm create-service              # create install service
installadm create-client -e <mac>      # register client
installadm set-criteria -n <svc>       # system criteria (cpu, mem, disk)

# AI Manifest (XML specification of partitioning, packages, configuration)
ai_manifest.xml
```

---

## Solaris VxVM / VxFS

```bash
# Veritas Volume Manager
vxdisk list                          # disk inventory
vxdg list                            # disk groups
vxprint -htg rootdg                  # volume group structure
vxassist make vol1 10g mirror diskgroup=datadg   # create mirrored volume
vxstat                               # I/O stats

# VxFS
fsck -F vxfs /dev/vx/dsk/datadg/vol1   # check filesystem
vxtunefs /mountpoint                    # show tuning parameters
```

---

## Key Solaris Log Locations

| Log | Purpose |
|-----|---------|
| `/var/adm/messages` | Main system log (syslog output) |
| `/var/svc/log/<svc>.log` | SMF service log |
| `/var/log/syslog` | Alternative on some configs |
| `/var/crash/<host>` | Kernel crash dumps |
| `/var/adm/sulog` | su attempts |
| `/var/adm/wtmpx` | Login history (`last`) |
| `/var/adm/lastlog` | Last login per user |
| `fmdump -e` | FMA error events |

---

## SOLARIS_KNOWLEDGE

> Append discoveries here. Format: `YYYY-MM-DD: <note>`
