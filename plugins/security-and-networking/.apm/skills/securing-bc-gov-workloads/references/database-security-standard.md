# BC Gov Database Security Standard (23 Mandatory Controls)

## Contents

- [Overview](#overview)
- [Mandatory Controls (1–23)](#mandatory-controls-123)
- [Application in BC Gov / Emerald Projects](#application-in-bc-gov--emerald-projects)
- [Companion Standards](#companion-standards)

## Overview

The **Database Security Standard for Information Protection** (v1.0, April 2018) establishes the baseline security controls for database systems used for BC Government services. Endorsed by ASRB and approved by the GCIO, all 23 controls apply to new database systems at procurement/implementation where reasonable; non-compliance requires an OCIO exemption.

> Privacy Impact Assessments (PIA) and Security Threat and Risk Assessments (STRA) may identify *additional* controls beyond this baseline.

## Mandatory Controls (1–23)

### Identification and Risk

| # | Control |
| --- | --- |
| 1 | Identify information security requirements for new databases. |
| 2 | Manage security risks related to production databases (STRA). |
| 3 | Classify data in production databases per ISCF (Public / Protected A / B / C). |
| 4 | Identify critical production databases and ensure a business continuity / DR plan. |

### Privacy and Encryption

| # | Control |
| --- | --- |
| 5 | Work with the Ministry Privacy Officer to ensure databases comply with FOIPPA and PIA outcomes. |
| 6 | Determine the use of encryption for **data in transit** and **data at rest** per IMIT 6.10. |

### Access and Separation of Duties

| # | Control |
| --- | --- |
| 7 | Separate responsibilities so no single person/team is entirely responsible for database operations *and* data content. |
| 8 | Formal user authorization process for granting and revoking access. |
| 9 | Employees accessing production databases meet onboarding/security clearance requirements. |
| 23 | Formal review of users and their access permissions to databases containing sensitive information. |

### Environment Segregation

| # | Control |
| --- | --- |
| 10 | Production databases' environments segregated from development/test (network, access, accounts). |
| 11 | Production data in non-production environments only with explicit approval; sensitive data MUST be sanitised/masked. |

### Vendors and Contractors

| # | Control |
| --- | --- |
| 12 | Service Providers/Contractors accessing data MUST comply with this Standard via contract clauses. |

### Authentication

| # | Control |
| --- | --- |
| 13 | Where reasonable, production databases authenticate via **government-approved authentication services** (not local DB accounts). |
| 14 | Production databases requiring password authentication use authentication mechanisms aligned with the Password Standard. |

### Vulnerability and Change Management

| # | Control |
| --- | --- |
| 15 | Conduct regular database vulnerability assessments. |
| 16 | Develop, document, maintain, and implement database security operating procedures. |
| 17 | Ensure changes to database systems follow the change management process. |
| 18 | Maintain a tested up-to-date backup. |
| 19 | Maintain documentation for database security configuration. |
| 20 | Apply database patches on a regular and timely basis. |

### Data Movement and Audit

| # | Control |
| --- | --- |
| 21 | Copy or transfer of bulk data outside production databases requires formal approval and logging. |
| 22 | Monitor and audit production databases (access, privilege use, schema changes). |

## Application in BC Gov / Emerald Projects

- **EF Core / Pomelo / MariaDB**: Provider-level encryption-at-rest is the responsibility of the database platform; encryption-in-transit (TLS) MUST be enforced on the connection string per Control #6.
- **Privileged access**: Route DBA access through the **Secure Access Gateway (SAG)** per IMIT 6.13; do not enable direct Internet ingress to database tiers (denied by SDN guardrail).
- **Test data**: Control #11 forbids unsanitised production data in non-production. The Application Security Standard reinforces this: if test data contains sensitive data classified MEDIUM or HIGH, it MUST be sanitised.
- **Bulk data export**: Control #21 — exports for analytics or replication need formal approval and logging. Tag export jobs in audit logs.
- **Backups (Controls #4 & #18)**: Control #18 requires *tested* backups, not just configured ones. STRA reviewers may ask for a recent restore test record:
  - **`BCDevOps/backup-container`** (`https://github.com/BCDevOps/backup-container`): Default for non-operator DBs (Patroni, MongoDB). Automates `pg_dump`/`mongodump`/`mysqldump` + automated restore verification into an empty DB (defaults: 6 daily, 4 weekly, 1 monthly on `nfs-file-backup` PVC; add custom step for S3).
  - **CrunchyDB Operator (`pgbackrest`)**: Built-in backup/restore and point-in-time recovery (PITR) for PostgreSQL; supports `local` (`nfs-file-backup` PVC) or `s3` (BC Gov S3 object storage with built-in multi-site DR, lower cost than `nfs-file-backup` PVC).
  - **CrunchyDB vs Patroni operational safety (Control #16 / #17)**: Use **`bcgov/crunchy-postgres`** (`PostgresCluster` CRD + built-in `pgbouncer` connection pooling) for operator-managed HA PostgreSQL vs **`bcgov/nr-patroni-chart`** (with `pgbouncer`) for Helm-managed Patroni clusters. **Never** run `patronictl` or make manual out-of-band edits on CrunchyDB (`PostgresCluster`) pods — manage CrunchyDB exclusively via `PostgresCluster` CRs and `pgbackrest` workflows.
  - **Storage threshold**: Patroni blocks/fails at 90% disk usage — set Sysdig storage alerts at ≤ 80%.
- **STRA artefacts**: When completing a STRA for a workload with a database, map each control 1–23 to either a control statement in the System Security Plan or a documented exemption.

## Companion Standards

| Topic | Standard |
| --- | --- |
| Data classification | IMIT 6.18 ISCF |
| Encryption requirements | IMIT 6.10 Cryptographic Standards |
| Network zone for the database tier | IMIT 6.13 (typically Zone B for Protected A/B-lower; Zone A for Protected B-higher/C) |
| Application security controls | Security Standard for Application and Web Development and Deployment |
| Password and authentication standard | Cross-government Password Standard |
