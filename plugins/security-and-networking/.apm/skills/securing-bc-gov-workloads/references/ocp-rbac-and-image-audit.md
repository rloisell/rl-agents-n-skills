# OpenShift RBAC Least-Privilege & Image Provenance Audit

## Contents

- [RBAC Least-Privilege Audit](#rbac-least-privilege-audit)
- [User Access, IDIR vs `@github` & Offboarding](#user-access-idir-vs-github--offboarding)
- [CronJob RBAC Anti-Pattern](#cronjob-rbac-anti-pattern)
- [Image Provenance Checklist](#image-provenance-checklist)
- [High-Risk Image + Exposure Pattern](#high-risk-image--exposure-pattern)

## RBAC Least-Privilege Audit

### Audit Command Sequence

```bash
# List all RoleBindings and their subjects in a namespace
oc get rolebindings -n <ns> -o json | jq '.items[] | {name: .metadata.name, role: .roleRef.name, subjects: [.subjects[]? | {kind, name}]}'

# Find ServiceAccounts with cluster-level roles
oc get clusterrolebindings -o json | jq '.items[] | select(.subjects[]?.namespace == "<ns>") | {name: .metadata.name, role: .roleRef.name}'

# Find pods not using a dedicated ServiceAccount (using default)
oc get pods -n <ns> -o json | jq '.items[] | select(.spec.serviceAccountName == "default" or .spec.serviceAccountName == null) | .metadata.name'
```

### Risk Tiers

| Binding | Risk | Action |
|---|---|---|
| `cluster-admin` to any namespace SA | CRITICAL | Remove immediately; escalate |
| `edit` on a SA running an internet-facing pod | HIGH | Downscope to minimum required verbs |
| Multiple workloads sharing one SA | MEDIUM | Blast radius on compromise — create dedicated SAs |
| `default` SA used by a pod | MEDIUM | No least-privilege — create a dedicated SA |
| Dedicated SA per workload, `view` or custom role | COMPLIANT | — |

Multi-service deployments typically accumulate 20–30 RoleBindings per namespace. High counts are expected, but always audit for `cluster-admin` bindings, shared ServiceAccounts, pods using `default`, and CronJob SAs with elevated permissions.

## User Access, IDIR vs `@github` & Offboarding

- **Identity formats (all lowercase)**:
  - **IDIR**: `<first>.<last>@gov.bc.ca` (requires IDIR MFA; **required** on Emerald and KLAB2, supported on all clusters).
  - **GitHub**: `<username>@github` (requires `bcgov` GitHub org membership + 2FA; available on KLAB, CLAB, Silver, Gold, GoldDR).
  - **Case sensitivity**: All usernames on OpenShift are **lowercase** — mixed-case bindings (e.g., `TheBestDev@github`) silently fail.
- **`admin` delete-namespace risk**: `admin` can view/modify any namespace resource (except quota) and **can delete the namespace**. Keep `admin` bindings minimal; assign `edit` to developers (create/delete apps, cannot view/modify roles or bindings) and `view` for read-only.
- **Offboarding (`bcgov/devops-requests`)**:
  1. Remove namespace RoleBindings: `oc -n <namespace> adm policy remove-role-from-user <role> <collaborator>`.
  2. Revoke OpenShift platform access and `bcgov`/`bcgov-c` GitHub org membership via **`bcgov/devops-requests`** (`https://github.com/bcgov/devops-requests/issues/new/choose`).

## CronJob RBAC Anti-Pattern

CronJobs that delete/restart pods require `delete` on `pods`. This is an anti-pattern:

- **Risk:** If the CronJob SA is compromised, an attacker can delete any pod in the namespace.
- **Root cause:** Unhealthy pods that do not self-heal via liveness probes.
- **Remediation:** Fix the liveness probe and restart policy so pods self-recover — eliminate the need for the CronJob entirely.
- **If CronJob must exist:** Scope the SA to a Role that allows `delete` only on pods with a specific label selector.

## Image Provenance Checklist

### Supply Chain Risk Tiers

| Image Source | Risk | Action |
|---|---|---|
| Public DockerHub `:latest` | CRITICAL | No provenance, mutable tag — mirror to Artifactory immediately |
| Public DockerHub SHA-pinned | HIGH | No BC Gov vulnerability scanning, not mirrored — mirror to Artifactory (`artifacts.developer.gov.bc.ca`) |
| Internal OpenShift ImageStream (`image-registry.openshift-image-registry.svc`) | LOW / LEGACY | Cluster-local only (not shareable across clusters, no JFrog Xray scanning) — flag for migration to Artifactory |
| Artifactory (`artifacts.developer.gov.bc.ca`) mutable tag (`:dev`, `:main`) | MEDIUM | Reproducibility risk — pin to SHA in non-dev environments |
| Artifactory (`artifacts.developer.gov.bc.ca`) SHA-pinned | COMPLIANT | Standard compliant registry |
| Artifactory SHA-pinned + Trivy/Xray-scanned + Cosign-signed | IDEAL | — |

### Audit Commands

```bash
# Find all container images NOT sourced from Artifactory (standard compliant registry)
oc get deployments,statefulsets -n <ns> -o json | \
  jq '.items[].spec.template.spec.containers[].image' | \
  grep -v 'artifacts.developer.gov.bc.ca'

# Also check initContainers
oc get deployments,statefulsets -n <ns> -o json | \
  jq '.items[].spec.template.spec.initContainers[]?.image' | \
  grep -v 'artifacts.developer.gov.bc.ca'

# Flag legacy cluster-local OpenShift ImageStreams for migration/review
oc get deployments,statefulsets -n <ns> -o json | \
  jq '.items[].spec.template.spec | (.containers[], .initContainers[]?) | .image' | \
  grep 'image-registry.openshift-image-registry.svc'
```

### Remediation Steps

1. Mirror the image to Artifactory (`docker pull` → `docker tag` → `docker push <artifactory>/...`).
2. Update the deployment to reference the Artifactory image ref.
3. Pin to a specific SHA digest: `image: artifacts.developer.gov.bc.ca/<repo>/<image>@sha256:<digest>`.
4. Add the image to the Trivy image-scan pipeline step and review **Red Hat ACS** (`https://acs.developer.gov.bc.ca`, active build/deploy/runtime policies) and **JFrog Xray** (`https://artifacts.developer.gov.bc.ca/ui/login/`, passive Artifactory artifact scan).
5. For production: add Cosign signing to the CI pipeline.

## High-Risk Image + Exposure Pattern

When a **DockerHub `:latest` admin UI image** (e.g., a Redis or database admin tool) is deployed with a **public Route and no authentication**, this is a critical combination:

| Risk Factor | Detail |
|---|---|
| Source | DockerHub (public) |
| Tag | `:latest` — mutable, no provenance |
| Exposure | Public Route with no authentication |
| Data access | Admin UI — full read/write access to data store |
| Classification | Data store may carry Protected B personal information |

Immediate remediation: remove the public Route, mirror the image to Artifactory, and pin to a SHA digest.
