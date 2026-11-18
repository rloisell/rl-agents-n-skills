# OpenShift RBAC Least-Privilege & Image Provenance Audit

## Contents

- [RBAC Least-Privilege Audit](#rbac-least-privilege-audit)
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
| Public DockerHub SHA-pinned | HIGH | No BC Gov vulnerability scanning, not mirrored — remediate |
| Internal registry mutable tag (`:dev`, `:main`) | MEDIUM | Reproducibility risk — pin to SHA in non-dev environments |
| Internal registry SHA-pinned | COMPLIANT | — |
| Internal registry SHA-pinned + Trivy-scanned + Cosign-signed | IDEAL | — |

### Audit Commands

```bash
# Find all container images NOT sourced from the internal OpenShift registry
oc get deployments,statefulsets -n <ns> -o json | \
  jq '.items[].spec.template.spec.containers[].image' | \
  grep -v 'image-registry.openshift-image-registry.svc'

# Also check initContainers
oc get deployments,statefulsets -n <ns> -o json | \
  jq '.items[].spec.template.spec.initContainers[]?.image' | \
  grep -v 'image-registry.openshift-image-registry.svc'
```

### Remediation Steps

1. Mirror the image to Artifactory (`docker pull` → `docker tag` → `docker push <artifactory>/...`).
2. Update the deployment to reference the Artifactory image ref.
3. Pin to a specific SHA digest: `image: artifacts.developer.gov.bc.ca/<repo>/<image>@sha256:<digest>`.
4. Add the image to the Trivy image-scan pipeline step.
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
