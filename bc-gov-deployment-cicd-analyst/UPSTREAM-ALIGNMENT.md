# Upstream Alignment Plan
## bcgov/agent-skills Adoption Path for Deployment and CI/CD Analyst

## Objective

Contribute a reusable, BC Gov-aligned deployment and CI/CD analyst skill set upstream with minimal divergence from this repository.

## Recommended strategy

1. Develop and validate in this repository first.
2. Prepare a trimmed upstream version for bcgov/agent-skills.
3. Raise a focused PR containing only generic and org-safe content.
4. Keep local and upstream variants synchronized through periodic review.

## Branch and PR workflow

### Step 1 - Create local feature branch

Use branch naming that is explicit and PR-friendly:

- feature/deployment-cicd-analyst-skill

### Step 2 - Validate content for upstream readiness

Check for removal of:

1. Personal metadata and author-specific references where not required.
2. Project-specific assumptions tied to one ministry or platform.
3. External tool dependencies that are not generally available in bcgov contexts.

Retain:

1. Generic assessment phases.
2. Control matrix format.
3. Governance output templates.
4. BC Gov standards mapping intent.

### Step 3 - Create upstream adaptation branch

In a local clone of bcgov/agent-skills:

1. Create branch: feature/deployment-cicd-analyst-skill
2. Add skill under repository-conforming path (for example .github/skills/<name>/SKILL.md).
3. If supported, add matching agent prompt/persona file.
4. Add concise README entry and usage examples.

### Step 4 - Submit PR with acceptance framing

PR should include:

1. Problem statement: missing generic deployment/CI-CD analyst role.
2. What is added: skill, optional agent persona, output templates.
3. Scope statement: platform-agnostic; supports SaaS/OpenShift/hybrid.
4. Safety and policy statement: no sensitive data, no personal references.
5. Example engagement outputs and expected value.

## Alignment checklist (pre-PR)

- [ ] Naming follows bcgov conventions.
- [ ] Frontmatter fields match upstream schema.
- [ ] Terminology aligns with BC Gov standards language.
- [ ] References include only stable/public URLs where possible.
- [ ] No personal repo paths remain.
- [ ] Examples are generic and reusable.

## Post-merge maintenance model

1. Track upstream changes quarterly.
2. Keep local enhanced version where deeper operational detail is needed.
3. Backport accepted upstream improvements to this repository.

## Suggested first PR scope

Keep initial PR intentionally small:

1. New generic skill only.
2. Optional lightweight agent persona if upstream pattern supports it.
3. One short example output bundle template.

Follow with incremental PRs for:

1. Additional matrix templates.
2. Expanded SaaS-specific guidance.
3. Extended report packaging patterns.
