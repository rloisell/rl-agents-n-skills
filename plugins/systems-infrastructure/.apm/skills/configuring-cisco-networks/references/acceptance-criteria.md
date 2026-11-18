# Acceptance Criteria — Configuring Cisco Networks

Observable pass/fail criteria for validating configurations, troubleshooting steps, and recovery procedures produced by `configuring-cisco-networks`.

## Contents

- [Configuration Syntax and Structure](#configuration-syntax-and-structure)
- [Troubleshooting and Diagram Criteria](#troubleshooting-and-diagram-criteria)
- [Workflow Scenario Criteria](#workflow-scenario-criteria)
- [Verification and Persistence Criteria](#verification-and-persistence-criteria)
- [Confidentiality and Safety Criteria](#confidentiality-and-safety-criteria)

## Configuration Syntax and Structure

| Check | Pass Criteria | Fail Criteria |
|---|---|---|
| Paste-ready syntax | Complete Cisco IOS, IOS-XE, or NX-OS CLI blocks with inline `!` comments explaining non-obvious lines | Pseudocode, truncated snippets, or missing `!` comments on complex blocks |
| Logical block ordering | Configuration blocks follow `global -> interfaces -> routing -> security -> lines` | Sections are interleaved out of order |
| Config block termination | Configuration blocks close with `end` and `write memory` (or `copy running-config startup-config` on NX-OS) | Config mode is left open or startup config save is omitted |
| Secret handling | Passwords/keys use placeholders (`<secret>`, `<psk>`) and `service password-encryption` / `secret` hashing | Cleartext real credentials or unencrypted `password` when `secret` is supported |

## Troubleshooting and Diagram Criteria

- **`show` commands first**: Troubleshooting sequences list `show` commands first and explicitly state which fields/counters to inspect.
- **Safe `debug` usage**: `debug` commands are only used briefly when `show` output is insufficient, and are always paired with `undebug all` (`u all`).
- **ASCII topology diagrams**: Topology diagrams use ASCII art with explicit interface labels (e.g., `Gi0/0`, `Eth1/1`) and IP addresses/subnets.

## Workflow Scenario Criteria

- **OSPF adjacency (`EXSTART`)**: Checks MTU on both peers via `show interfaces` and resolves mismatch via `ip mtu 1500` or `ip ospf mtu-ignore`.
- **Interface `up/up` with no traffic**: Inspects ACL hit counters (`show ip access-lists`), NAT translations (`show ip nat translations`), or brief `debug ip packet` + `undebug all`.
- **VLANs and trunks**: Verifies allowed/pruned VLANs via `show interfaces trunk`.
- **EtherChannel / vPC**: Verifies matching speed, duplex, VLANs, and encapsulation across member links via `show etherchannel summary` (IOS) or `show vpc` (NX-OS).
- **HSRP**: Verifies priority, `preempt`, and MD5 authentication key-string via `show standby brief`.
- **Console/SSH login & recovery**: Ensures `line con 0` / `line vty` with `login local` is paired with a local `username <user> privilege 15 secret <secret>`; password recovery follows platform ROMmon/Catalyst steps.
- **IOS image upgrade**: Runs `verify /md5` on the target image before updating `boot system`, and retains the previous image until after the first clean reload.

## Verification and Persistence Criteria

- **Switching and HA**: Confirmed via `show interfaces trunk`, `show etherchannel summary`, `show standby brief`, or `show vpc`.
- **Routing and traffic**: Confirmed via `show ip ospf neighbor` (`FULL`), `show ip route`, `show ip access-lists`, and `show ip nat translations`.
- **Images and persistence**: Confirmed via `verify /md5`, `show boot`, and saved startup configuration (`write memory` / `copy running-config startup-config`).

## Confidentiality and Safety Criteria

- **Generic addressing**: Examples use RFC 1918 or RFC 5737 documentation subnets (`10.x.x.x`, `192.0.2.0/24`, `198.51.100.0/24`) and generic hostnames (`R1`, `SW1`, `<core-sw>`), never real client IPs or device names.
