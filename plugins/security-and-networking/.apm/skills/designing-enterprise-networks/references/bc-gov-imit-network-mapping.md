# BC Gov IMIT Network Standards Mapping

For BC Government networks, the following OCIO IMIT standards translate directly to technical controls. Cite them in network design documents and STRA submissions.

| IMIT Standard | Section | Controls implemented |
| --- | --- | --- |
| **IMIT 6.28** Network & Communications Security (v5.0, 2022 / Specs v1.0, 2024) | §3.1 Network controls | Configuration controls, MFA on devices, change management, baseline integrity |
| **IMIT 6.28** | §3.3 Logging, monitoring, detection | SIEM forwarding, IDS/IPS sensors, log boundary capture |
| **IMIT 6.28** | §3.5 Segregation | Zone segmentation, VLANs, security gateways, NetworkPolicy, Zone-Based Firewall |
| **IMIT 6.28** | §3.6 Routing controls | Anti-spoofing ACLs, uRPF, authenticated routing protocols, prefix filtering |
| **IMIT 6.28** | §3.7 Communication security | Encrypted transport (SSH/TLS/IPsec), anti-malware on transit |
| **IMIT 6.13** Network Security Zones (v5) | Zone model | DMZ / Zone B / Zone A boundaries; SDN Low/Medium/High |
| **IMIT 5.08** N2N Connectivity / 3PG (v2.0, 2022) | §5 Specifications | Stateful firewall + IPS/IDS at transit, default-deny, NAT to hide internals |
| **IMIT 5.08** | §5.1.3 Data in transit | IMIT 6.10 cryptography; encrypted tunnels / MPLS / isolated VLANs; PCI → separate physical router per circuit |
| **IMIT 5.08** | §5.1.4 Logging | Raw logs retained ≥ 13 months; available to Province SIEM |
