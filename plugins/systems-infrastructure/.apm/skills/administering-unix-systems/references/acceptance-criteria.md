# Acceptance Criteria — Administering Unix Systems

Observable pass/fail criteria for validating outputs and workflows produced by `administering-unix-systems`.

## Contents

- [Output Formatting and Constraints](#output-formatting-and-constraints)
- [Workflow Scenario Criteria](#workflow-scenario-criteria)
- [Post-Change Verification Criteria](#post-change-verification-criteria)
- [Confidentiality and Safety Criteria](#confidentiality-and-safety-criteria)

## Output Formatting and Constraints

| Check | Pass Criteria | Fail Criteria |
|---|---|---|
| Platform label | Command sequence or config begins with an explicit platform label (`Solaris 9/10/11` or `RHEL 7/8/9`) | Platform is omitted or Solaris and RHEL commands are mixed without labelling |
| Diagnostic + resolution pair | Troubleshooting outputs include both a diagnostic command (e.g., `svcs -xv`, `journalctl -xe -u`) and a resolution command | Only a fix is given without diagnostics, or only diagnostics without remediation |
| DTrace script comments | Every DTrace probe includes inline `/* ... */` or `//` comments explaining what the probe captures | DTrace script has uncommented probes |
| Storage verification pairing | Destructive or resizing storage commands (`zpool`, `zfs`, `lvextend`, `xfs_growfs`, `resize2fs`) are paired with post-change verification (`zpool status`, `lvs`, `df -hT`) | Resizing/destructive storage commands appear without a verification step |
| Shell script safety | Any generated Bash script uses `set -euo pipefail` and `local` for function variables | Bash script omits `set -euo pipefail` or leaks global variables inside functions |

## Workflow Scenario Criteria

- **Service failure (Solaris SMF)**: Output checks `svcs -xv <svc>`, inspects dependency chain or `svcs -L <svc>`, and verifies properties via `svccfg -s <svc> listprop` before clearing/restarting with `svcadm`.
- **Service failure (RHEL systemd)**: Output checks `systemctl status <unit>` and `journalctl -xe -u <unit>` before restarting/enabling the unit.
- **ZFS / LVM storage**: ZFS pool issues inspect `zpool status -v` before `zpool replace` or `zpool scrub`; LVM extensions check `df -hT`, `pvs`, `vgs`, `lvs` before `lvextend` and filesystem resize (`xfs_growfs` / `resize2fs`).
- **SELinux denials (RHEL)**: Output inspects `ausearch -m avc -ts recent` and remediates with `semanage` / `restorecon` / `audit2allow` rather than recommending `setenforce 0` or disabling SELinux permanently.
- **Networking**: Solaris troubleshooting uses `dladm show-link`, `ipadm show-addr`, and `snoop`; RHEL troubleshooting uses `nmcli` and `firewall-cmd`.
- **DNS diagnostics**: Resolution/propagation checks compare `dig +trace <name>` and `dig @<auth-ns> <name>` against the local resolver; email/auth checks cover SPF/DKIM/DMARC/DNSSEC/PTR as applicable.

## Post-Change Verification Criteria

- **Services**: Confirmed `online` via `svcs <svc>` (Solaris) or `active (running)` via `systemctl is-active <unit>` (RHEL).
- **Storage**: Confirmed healthy pool/volume state and updated capacity via `zpool status -v` / `zfs list` (Solaris) or `lvs` / `df -hT` (RHEL).
- **Networking and DNS**: Confirmed link/address state (`ipadm show-addr` / `nmcli device status`) and expected authoritative answer (`dig +short @<auth-ns> <name>`).

## Confidentiality and Safety Criteria

- **No real client identifiers**: Hostnames, IPs, domains, and usernames use generic placeholders (`<host>`, `<svc>`, `<vg>`, `<lv>`, `example.com`, `198.51.100.x`) rather than real engagement assets.
- **No hardcoded secrets**: Passwords, keys, or subscription credentials are never hardcoded in command examples or scripts.
