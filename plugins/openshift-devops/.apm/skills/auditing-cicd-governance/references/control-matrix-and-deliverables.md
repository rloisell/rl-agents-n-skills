# Control Matrix, Examples & Deliverables

Control analysis domains, standard deliverable filenames, assessment examples, and authoritative references for CI/CD governance audits.

## Control Matrix Template

| Control ID | Control Domain | Current State | Evidence | Gap | Recommended Action | Owner | Target Date |
|---|---|---|---|---|---|---|---|
| CM-01 | Release Integrity | | | | | | |
| CM-02 | Quality Gates | | | | | | |
| CM-03 | Secrets Lifecycle | | | | | | |
| CM-04 | Governance Approval | | | | | | |
| CM-05 | Audit Retention | | | | | | |

Additional control areas to evaluate within the matrix:
- Determinism and artifact immutability
- Environment segregation and trust boundaries
- Software supply chain (dependency scanning, action pinning, provenance)
- Rollback readiness and change traceability

### CM-01–CM-04 Audit Checks (CI/CD & Release)

| Control ID | Specific Audit Checks |
|---|---|
| **CM-01** Release Integrity | - **Rebuild from immutable SHA**: Release pipelines must rebuild from an immutable commit SHA—never trust pre-built or mutable branch/tag artifacts as the release source.<br>- **Tag verification & release-notes sanitization**: Enforce signed tag verification (`--verify-tag`) and sanitize generated release notes to strip secrets, tokens, and internal URLs.<br>- **DB-migration packaging vs execution**: Package DB migrations into verified build artifacts (excluding secrets, dumps, and real data) while keeping migration execution out of CI. |
| **CM-02** Quality Gates | - **Blocking Sonar gate (not upload-only)**: Require `sonar.qualitygate.wait=true`. Flag upload-only configurations, Azure DevOps `PublishQualityGateResult` `pollingTimeoutSec` traps, and Jenkins `waitForQualityGate abortPipeline: true` lacking webhook + `timeout` wiring.<br>- **Zero-test fail-closed**: Fail closed when zero tests execute or expected test reports are missing—never silently downgrade to `UNSTABLE`.<br>- **Test harness classification**: Stamp test harnesses with an immutable build ID and `NonProduction` classification. |
| **CM-03** Secrets Lifecycle | - **Untrusted fork PR & cache isolation**: Isolate `pull_request_target` workflows from untrusted fork code execution and prevent cache poisoning across trust boundaries.<br>- **Jenkins `withCredentials` quoting**: Require single-quoted (`'...'`) Groovy shell scripts inside `withCredentials` blocks so Groovy interpolation never exposes secrets. |
| **CM-04** Governance Approval | - **Pre-tag protected environment**: Require protected environment approval gates *before* release tag creation or production artifact promotion. |

---

## Standard Output Set

Suggested versioned filenames:

- `report/<program>-deployment-cicd-analysis-v1.md`
- `report/<program>-deployment-cicd-analysis-v1.pdf`
- `docs/<program>-executive-summary-v1.md`
- `docs/<program>-adm-brief-v1.md`
- `docs/<program>-client-report-and-process-guide-v1.md`
- `docs/process-log/YYYY-MM-DD-<title>.md`

---

## Examples

### Example 1: SaaS pipeline assessment

- **Input**: Bitbucket pipeline PDF for a multi-tenant SaaS deployment
- **Action**: Extract content, map controls by intent, run security/network/CI-CD analyst passes, produce findings and phased roadmap (`0-30`, `31-90`, `90+` days)
- **Output**: Technical report, executive summary, one-page brief, control matrix

### Example 2: Hybrid CI/CD governance review

- **Input**: GitHub Actions workflows and deployment docs for container + SaaS services
- **Action**: Assess release integrity, approvals, secrets lifecycle, evidence retention, and supply-chain controls, splitting findings by platform context
- **Output**: Severity-ranked findings and phased remediation plan

---

## Edge Cases

1. **Image-only PDF**: Use OCR or request machine-readable export before finalizing conclusions.
2. **Missing governance data** (approvals/branch protections): Record as an assumption gap and mark affected findings as provisional.
3. **Mixed delivery models**: Split findings by platform context and provide a cross-cutting control summary.

---

## Authoritative References

1. **IMIT 6.28** — Communications and network security
2. **IMIT 5.08** — Network-to-network trust boundary
3. **IMIT 6.13 & ISCF intent** — Segregation and classification
4. **BC Gov application and deployment security standards**
5. **Companion skills/agents**: `deploying-bc-gov-workloads`, `security-architect`, `bc-gov-network-architect`, `zero-trust-architect`, `observability`
