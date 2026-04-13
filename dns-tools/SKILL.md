---
name: dns-tools
description: DNS query and troubleshooting using dig, nslookup, and host. Covers all record types (A, AAAA, CNAME, MX, NS, SOA, TXT, PTR, SRV, CAA), delegation tracing, DNSSEC validation, reverse lookups, zone transfer testing, TTL analysis, and split-horizon diagnosis. Use when troubleshooting DNS resolution issues, validating zone configuration, checking email/SPF/DMARC records, or confirming propagation.
metadata:
  author: Ryan Loiselle
  version: "1.0"
compatibility: dig (BIND-utils/bind9-dnsutils), nslookup, host. macOS and Linux. Works against any recursive or authoritative resolver.
---

# DNS Tools Skill

DNS query, troubleshooting, and validation using `dig`, `nslookup`, and `host`.

---

## dig — Core Syntax

```bash
dig [@server] [name] [type] [+options]

# Examples
dig example.com                            # A record, default resolver
dig @8.8.8.8 example.com A                 # Query Google Public DNS
dig example.com AAAA                       # IPv6 address
dig example.com MX                         # Mail exchanger
dig example.com NS                         # Authoritative name servers
dig example.com SOA                        # Zone SOA record
dig example.com TXT                        # TXT records (SPF, DMARC, etc.)
dig example.com CAA                        # CA Authorisation (TLS issuance policy)
dig _dmarc.example.com TXT                 # DMARC policy
dig _smtp._tcp.example.com SRV             # SRV record lookup
dig -x 142.251.41.46                       # Reverse PTR lookup (IPv4)
dig -x 2607:f8b0:4004:c08::6a             # Reverse PTR lookup (IPv6)
```

---

## dig Output Anatomy

```
; <<>> DiG 9.18 <<>> example.com A
;; QUESTION SECTION:
;example.com.                   IN      A

;; ANSWER SECTION:
example.com.            300     IN      A       93.184.216.34

;; AUTHORITY SECTION:
example.com.            3600    IN      NS      a.iana-servers.net.

;; ADDITIONAL SECTION:
a.iana-servers.net.     3000    IN      A       199.43.135.53

;; Query time: 12 msec
;; SERVER: 192.168.1.1#53(192.168.1.1)
;; WHEN: ...
;; MSG SIZE rcvd: 56

Flags decoded:
  qr  — query response
  aa  — authoritative answer (from authoritative NS, not cache)
  rd  — recursion desired (client requested recursive resolution)
  ra  — recursion available (server supports recursion)
  ad  — authenticated data (DNSSEC validated)
  cd  — checking disabled (DNSSEC validation disabled by client)
```

---

## Useful dig Options

```bash
# Short output (answer only)
dig +short example.com

# Full trace from root (delegation chain)
dig +trace example.com

# No recursion (query authoritative directly)
dig +norec @ns1.example.com example.com

# Disable additional and authority sections
dig +noall +answer example.com MX

# Show DNSSEC signatures
dig +dnssec example.com

# Set specific UDP buffer size (DNSSEC requires larger buffers)
dig +bufsize=4096 example.com DNSKEY

# TCP query (zone transfers, large responses)
dig +tcp example.com ANY

# Multi-query in one command
dig example.com A example.com MX +noall +answer

# Batch from file
dig -f queries.txt +short

# Query time comparison across resolvers
for r in 8.8.8.8 1.1.1.1 9.9.9.9; do
  echo -n "$r: "; dig @$r +stats +noall example.com | grep "Query time"
done
```

---

## Record Types Reference

| Type | Description | Example value |
|------|-------------|---------------|
| A | IPv4 address | `93.184.216.34` |
| AAAA | IPv6 address | `2606:2800:220:1:248:1893:25c8:1946` |
| CNAME | Canonical name alias | `example.com.` |
| MX | Mail exchanger | `10 mail.example.com.` |
| NS | Authoritative name server | `ns1.example.com.` |
| SOA | Start of Authority | Serial, refresh, retry, expire, min TTL |
| TXT | Text (SPF, DMARC, DKIM, verification) | `"v=spf1 ip4:... ~all"` |
| PTR | Reverse DNS | `host.example.com.` |
| SRV | Service locator | `10 20 443 target.example.com.` |
| CAA | CA Authorization | `0 issue "letsencrypt.org"` |
| DNSKEY | DNSSEC public key | Zone signing key |
| DS | Delegation Signer | Hash of child zone KSK |
| TLSA | DANE certificate association | Hash of TLS cert |
| NAPTR | Name Authority Pointer (VoIP/ENUM) | Regex-based rewrite rules |

---

## Email DNS Records (SPF / DKIM / DMARC)

```bash
# SPF (TXT on domain apex)
dig +short example.com TXT | grep spf

# DKIM (TXT at selector._domainkey)
dig +short selector._domainkey.example.com TXT

# DMARC (TXT at _dmarc)
dig +short _dmarc.example.com TXT

# MTA-STS policy
dig +short _mta-sts.example.com TXT
curl https://mta-sts.example.com/.well-known/mta-sts.txt

# BIMI (Brand Indicators for Message Identification)
dig +short default._bimi.example.com TXT
```

---

## DNSSEC Validation

```bash
# Check if domain is DNSSEC-signed
dig +dnssec example.com | grep -E 'ad|RRSIG|DNSKEY'

# Verify chain of trust from root
dig +trace +dnssec example.com

# Check DS record at parent zone
dig +short example.com DS

# Validate using Unbound's local validator
unbound-host -D example.com

# Online DNSSEC debugger
# https://dnsviz.net/d/example.com/dnssec/
```

---

## Zone Transfers

```bash
# AXFR (full zone transfer — usually blocked externally)
dig @ns1.example.com example.com AXFR

# IXFR (incremental — from serial number)
dig @ns1.example.com example.com IXFR=2024010101

# Test if AXFR is improperly allowed
dig @ns1.example.com example.com AXFR | head -20
```

---

## Reverse DNS

```bash
# IPv4 reverse lookup (PTR)
dig -x 93.184.216.34

# IPv4 reverse in-addr.arpa form
dig 34.216.184.93.in-addr.arpa PTR

# IPv6 reverse lookup
dig -x 2606:2800:220:1:248:1893:25c8:1946

# IPv6 ip6.arpa expanded form
# Reverse each nibble of fully-expanded address
```

---

## DNS Propagation and Troubleshooting

```bash
# Compare authoritative vs cached answer
dig @ns1.example.com example.com    # authoritative
dig example.com                      # cached (via local resolver)

# Check all authoritative NS servers
for ns in $(dig +short example.com NS); do
  echo -n "$ns: "; dig @$ns +short example.com A
done

# Flush local DNS cache
# macOS
sudo dscacheutil -flushcache && sudo killall -HUP mDNSResponder
# RHEL/CentOS (systemd-resolved)
sudo systemd-resolve --flush-caches
# RHEL (nscd)
sudo service nscd restart

# Check SOA serial across NS (propagation check)
for ns in $(dig +short example.com NS); do
  echo -n "$ns serial: "; dig @$ns +short example.com SOA | awk '{print $3}'
done
```

---

## nslookup Reference

```bash
nslookup example.com                       # default resolver
nslookup example.com 8.8.8.8               # specific resolver
nslookup -type=MX example.com              # record type
nslookup -type=NS example.com
nslookup -debug example.com               # verbose output

# Interactive mode
nslookup
> server 8.8.8.8
> set type=TXT
> _dmarc.example.com
> exit
```

---

## host Reference

```bash
host example.com
host -t MX example.com
host -t NS example.com
host 93.184.216.34              # reverse lookup
host -a example.com             # all records
```

---

## Common DNS Troubleshooting Patterns

| Symptom | Check | Command |
|---------|-------|---------|
| Resolution works from some resolvers, not others | Cache poisoning / negative TTL | `dig +trace example.com` on failing resolver |
| NXDOMAIN unexpectedly | Typo, zone not delegated, glue missing | `dig +trace example.com` |
| SERVFAIL | DNSSEC failure, broken delegation | `dig +dnssec example.com` + dnsviz.net |
| Email delivery rejected | SPF/DKIM/DMARC misconfigured | `dig +short _dmarc.example.com TXT` |
| Slow resolution | High TTL on CNAME chain / resolver RTT | `dig +stats example.com` |
| Split-horizon mismatch | Internal vs external DNS returning different answers | Compare `dig @internal-resolver` vs `dig @8.8.8.8` |
| PTR missing | rDNS not delegated / not configured | `dig -x <ip>` + `dig <arpa-form> PTR` |
| CAA blocking cert issuance | CAA record restricts CA | `dig example.com CAA` |

---

## DNS Architecture Reference

```
Resolution hierarchy:
  Client → Local Resolver (OS cache) → Recursive Resolver (ISP/DoH/DoT)
       → Root NS (.) → TLD NS (.com) → Authoritative NS (example.com)

Zone types:
  Primary (master)   — writable; single source of truth for zone
  Secondary (slave)  — read-only copy via AXFR/IXFR
  Stub               — contains NS records only; used for conditional delegation
  Forward            — forwards queries for a zone to another server
  Hint               — root hints file (named.root / db.root)

Split-horizon DNS:
  Same zone name; different views per source IP
  Internal view: returns RFC 1918 / private addresses
  External view: returns public routable addresses
  Implemented in BIND9 (view clauses), Microsoft DNS (policies), Infoblox (DNS views)

DNSSEC chain of trust:
  Root (.) → TLD (.com) → Domain (example.com)
  Each zone signs its records with ZSK; parent zone holds DS record for child KSK
  Validation: recursive resolver checks RRSIG → DS → DNSKEY chain up to root trust anchor
```

---

## DNS_TOOLS_KNOWLEDGE

> Append discoveries here. Format: `YYYY-MM-DD: <note>`
