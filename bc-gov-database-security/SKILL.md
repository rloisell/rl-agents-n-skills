---
name: bc-gov-database-security
description: BC Government Database Security Standard for Information Protection — 23 mandatory controls covering data classification, separation of duties, encryption, access provisioning, environment segregation, vulnerability assessment, change management, patching, bulk-data export controls, audit logging, and access reviews. Use when designing or reviewing database systems for BC Government services (Oracle, MariaDB, SQL Server, PostgreSQL, etc.) or when answering STRA/PIA questions about database controls.
tools: Read, Grep, Glob
metadata:
  author: Ryan Loiselle
  version: "1.0"
  sources:

    - title: "Database Security Standard for Information Protection v1.0 (April 2018)"
      note: "Authoritative — 23 numbered MUST controls; baseline for procurement and implementation of new database systems."
      url: "https://www2.gov.bc.ca/assets/gov/government/services-for-government-and-broader-public-sector/information-technology-services/standards-files/database_security_standards_for_information_protection_-_2018-04_version_1.pdf"

    - title: "IMIT 6.18 — Information Security Classification Standard (ISCF)"
      note: "Drives data classification decisions referenced in §3 of this standard."
      url: "https://www2.gov.bc.ca/gov/content/governments/services-for-government/information-management-technology/information-security/information-security-standards"

    - title: "IMIT 6.10 — Cryptographic Standards for Information Protection"
      note: "Encryption-at-rest and in-transit decisions cite IMIT 6.10."
      url: "https://www2.gov.bc.ca/gov/content/governments/services-for-government/information-management-technology/information-security/information-security-standards"

compatibility: All BC Gov database systems (Oracle, MariaDB, MySQL, PostgreSQL, SQL Server, etc.) hosting Government information.
---

# BC Gov Database Security Standard

The **Database Security Standard for Information Protection** (v1.0, April 2018) establishes
the baseline security controls for database systems used for BC Government services. It was
endorsed by ASRB and approved by the GCIO. **Where reasonable**, all 23 controls apply to new
database systems at procurement/implementation; non-compliance requires an OCIO exemption.

> Privacy Impact Assessments (PIA) and Security Threat and Risk Assessments (STRA) may
> identify *additional* controls beyond this baseline.

## Mandatory controls (verbatim summary)

### Identification and risk

| # | Control |
| --- | --- |
| 1 | Identify information security requirements for new databases. |
| 2 | Manage security risks related to production databases (STRA). |
| 3 | Classify data in production databases per ISCF (Public / Protected A / B / C). |
| 4 | Identify critical production databases and ensure a business continuity / DR plan. |

### Privacy and encryption

| # | Control |
| --- | --- |
| 5 | Work with the Ministry Privacy Officer to ensure databases comply with FOIPPA and PIA outcomes. |
| 6 | Determine the use of encryption for **data in transit** and **data at rest** per IMIT 6.10. |

### Access and separation of duties

| # | Control |
| --- | --- |
| 7 | Separate responsibilities so no single person/team is entirely responsible for database operations *and* data content. |
| 8 | Formal user authorization process for granting and revoking access. |
| 9 | Employees accessing production databases meet onboarding/security clearance requirements. |
| 23 | Formal review of users and their access permissions to databases containing sensitive information. |

### Environment segregation

| # | Control |
| --- | --- |
| 10 | Production databases' environments segregated from development/test (network, access, accounts). |
| 11 | Production data in non-production environments only with explicit approval; sensitive data MUST be sanitised/masked. |

### Vendors and contractors

| # | Control |
| --- | --- |
| 12 | Service Providers/Contractors accessing data MUST comply with this Standard via contract clauses. |

### Authentication

| # | Control |
| --- | --- |
| 13 | Where reasonable, production databases authenticate via **government-approved authentication services** (not local DB accounts). |
| 14 | Production databases requiring password authentication use authentication mechanisms aligned with the Password Standard. |

### Vulnerability and change management

| # | Control |
| --- | --- |
| 15 | Conduct regular database vulnerability assessments. |
| 16 | Develop, document, maintain, and implement database security operating procedures. |
| 17 | Ensure changes to database systems follow the change management process. |
| 18 | Maintain a tested up-to-date backup. |
| 19 | Maintain documentation for database security configuration. |
| 20 | Apply database patches on a regular and timely basis. |

### Data movement and audit

| # | Control |
| --- | --- |
| 21 | Copy or transfer of bulk data outside production databases requires formal approval and logging. |
| 22 | Monitor and audit production databases (access, privilege use, schema changes). |

## How to apply this in BC Gov / Emerald projects

- **EF Core / Pomelo / MariaDB**: see also the `ef-core` agent for migration patterns and
  service-layer separation. Provider-level encryption-at-rest is the responsibility of the
  database platform; encryption-in-transit (TLS) MUST be enforced on the connection string
  per Control #6.

- **Privileged access**: route DBA access through the **Secure Access Gateway (SAG)** per
  IMIT 6.13; do not enable direct Internet ingress to database tiers (denied by SDN guardrail).

- **Test data**: Control #11 forbids unsanitised production data in non-production. The
  Application Security Standard reinforces this: *if test data contains sensitive data
  classified MEDIUM or HIGH, it MUST be sanitised*.

- **Bulk data export**: Control #21 — exports for analytics or replication need formal
  approval and logging. Tag export jobs in audit logs.

- **Backups**: Control #18 requires *tested* backups, not just configured ones. STRA reviewers
  may ask for a recent restore test record.

- **STRA artefacts**: when completing a Security Threat and Risk Assessment for a workload
  with a database, map each control 1\u201323 to either a control statement in the System
  Security Plan or a documented exemption.

## Companion standards

| Topic | Standard |
| --- | --- |
| Data classification | IMIT 6.18 ISCF |
| Encryption requirements | IMIT 6.10 Cryptographic Standards |
| Network zone for the database tier | IMIT 6.13 (typically Zone B for Protected A/B-lower; Zone A for Protected B-higher/C) |
| Application security controls (segregation, code review, secure coding) | Security Standard for Application and Web Development and Deployment |
| Password and authentication standard | Cross-government Password Standard |
