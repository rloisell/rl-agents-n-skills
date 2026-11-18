# Spec-Kitty & BC Gov §1 Guide

Spec-first development using `spec-kitty` CLI and BC Government OCIO §1
Requirements Management alignment.

## Contents

- [Installation and initialization](#installation-and-initialization) • [Directory structure](#directory-structure) • [spec.md and plan.md schemas](#specmd-and-planmd-schemas) • [WP task file format](#wp-task-file-format) • [Pre-merge checklist](#pre-merge-checklist) • [BC Gov Requirements Management Standard](#bc-gov-requirements-management-standard) • [Knowledge](#knowledge)

## Installation and initialization

```bash
pip install spec-kitty
spec-kitty init --here --ai copilot --non-interactive --no-git --force

git add .kittify/ .github/prompts/
git commit -m "chore: initialise spec-kitty"
```

Add `__pycache__/`, `*.pyc`, and `*.pyo` to `.gitignore`.

### Creating and validating a feature

```bash
spec-kitty agent feature create-feature --id 001 --name "feature-slug"

# Run after writing spec.md, plan.md, and WP files (must return 0 mismatches)
spec-kitty validate-tasks --all
```

## Directory structure

```text
kitty-specs/
  {NNN}-{feature-slug}/
    spec.md                  # requirements, user stories, success criteria
    plan.md                  # phased implementation plan
    tasks/
      WP01-title.md          # atomic work package (< 2h each)
      WP02-title.md
    spec/
      fixtures/
        openapi/             # OpenAPI request/response .json examples
        db/                  # SQL migration preview .sql files
```

## spec.md and plan.md schemas

### spec.md required sections

```markdown
# Feature NNN — Feature Name

**Owner**: <Name / Role>
**Updated**: <Month Year>

## Overview
## User Stories
## Requirements
### Functional Requirements
### Non-Functional Requirements
### Constraints
## Assumptions
## Open Questions / Risks
## Success Criteria
## Out of Scope
## Dependencies
## Notes
```

### plan.md required sections

```markdown
# Plan — Feature NNN — Feature Name

## Technical Approach
## Entity Changes
## API Endpoints
| Method | Path | Request Body | Response | Status |
## Frontend Changes
## Testing Approach
## Phases
- Phase 1 — Backend: entities, migration, service, controller
- Phase 2 — Frontend: queries, hooks, page components
- Phase 3 — Testing and polish
```

## WP task file format

Work packages must be atomic (completable in under 2 hours). Lane lifecycle:
`planned -> in-progress -> review -> done`. Run `spec-kitty validate-tasks --all`
after changing lanes.

```yaml
---
work_package_id: "WP01"
title: "Short description (imperative, < 10 words)"
lane: "planned"
subtasks:
  - "WP01"
phase: "Phase 1 — Backend"
assignee: ""
agent: ""
shell_pid: ""
review_status: ""
reviewed_by: ""
history:
  - timestamp: "YYYY-MM-DDTHH:MM:SSZ"
    lane: "planned"
    agent: "system"
    action: "Created for feature spec"
---

## Work Package: WP01 — Title

### Goal
### Deliverables
- [ ] `src/<Project>.Api/Entities/<Entity>.cs`

### Acceptance Criteria
- [ ] AC-01:

### Notes
```

In implementation files, reference the driving WP:

```csharp
// Implements: WP01 (001-feature-slug)
```

## Pre-merge checklist

1. All WP files have `lane: "done"`.
2. `spec-kitty validate-tasks --all` reports 0 mismatches.
3. All success criteria checked off in `spec.md`.
4. OpenAPI fixtures committed under `spec/fixtures/openapi/` for each endpoint.
5. Unit tests passing.

## BC Gov Requirements Management Standard

For BC Government projects, every WP must be defensible against OCIO
[Development Standards for Information Systems and Services v3.0 (May 2015), §1 Requirements Management](https://www2.gov.bc.ca/assets/gov/government/services-for-government-and-broader-public-sector/information-technology-services/standards-files/development_standards_for_information_systems_and_services.pdf):

| BC Gov mandate | Spec-Kitty mapping |
|----------------|--------------------|
| (§1.2.1) Known requirements and constraints MUST be documented | `spec.md` Functional Requirements + Constraints sections |
| (§1.2.2) Known assumptions MUST be documented | `spec.md` Assumptions section |
| (§1.2.3) Known uncertainties MUST be documented | `spec.md` Open Questions / Risks section |
| (§1.2.5) Requirements MUST be subjected to an approval process | PR review on `spec.md` before WP creation |
| (§1.2.6) Approved requirements MUST have a sponsor and/or owner | `spec.md` Owner field |
| (§1.3.1) Each requirement MUST be testable against objective criteria | WP acceptance criteria checklist |
| (§1.3.4) Each requirement MUST be uniquely identified | `WP{NN}` numbering + `REQ-{NN}` IDs in `spec.md` |
| (§1.3.5) A requirement statement SHOULD express only one requirement | One acceptance criterion per checklist line |

## Knowledge

- 2026-02-27: [sample-app] [CONTEXT: config] `spec-kitty init` creates `.kittify/` and updates `.github/prompts/`. Commit both and add `__pycache__/` to `.gitignore`.
