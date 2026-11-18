---
name: driving-spec-development
description: >-
  Drives spec-first feature development using GitHub Spec-Kit (specify CLI) or
  Spec-Kitty (spec-kitty CLI), enforcing constitution, specification, planning,
  task breakdown, and validation gates before implementation, plus BC Gov OCIO
  §1 Requirements Management alignment. Use when starting a new feature, writing
  spec or plan files, generating work packages, or validating task boards.
---

# Driving Spec Development

Enforces Spec-Driven Development (SDD): no implementation code before the
specification, technical plan, and validated task breakdown exist.

## Contents

- [Constraints](#constraints) • [Quick start](#quick-start) • [Workflow](#workflow) • [Verification](#verification) • [References](#references)

## Constraints

1. **No skipping phases**: complete specification, plan, and task breakdown before writing implementation code.
2. **Spec before code**: every feature requires testable acceptance criteria and unique requirement IDs (`REQ-{NN}`).
3. **Commit scaffolding and ignore Python cache**: commit `.specify/` or `.kittify/` alongside `.github/prompts/` and add `__pycache__/`, `*.pyc`, `*.pyo` to `.gitignore`.
4. **BC Gov §1 compliance**: public-sector projects must map requirements, assumptions, uncertainties, approvals, and owners per [spec-kitty.md](references/spec-kitty.md#bc-gov-requirements-management-standard).

## Quick start

Choose one SDD toolchain per project:

| Aspect | GitHub Spec-Kit (`specify` CLI) | Spec-Kitty (`spec-kitty` CLI) |
|--------|--------------------------------|-------------------------------|
| Config dir | `.specify/` | `.kittify/` |
| Feature dir | Flexible / designated spec folder | `kitty-specs/{NNN}-{slug}/` |
| Task format | `tasks.md` checklist | `WP{NN}-title.md` with YAML frontmatter |
| Lane tracking | Phase-based | `planned -> in-progress -> review -> done` |
| Validation | `/speckit.analyze` + `spec-kit-verify` | `spec-kitty validate-tasks --all` |
| Extensions / presets | Supported (40+ extensions, presets) | Not supported |

## Workflow

### With Spec-Kit (`specify`)

```text
constitution -> specify -> (clarify) -> plan -> (analyze) -> tasks -> implement
```

See [spec-kit.md](references/spec-kit.md) for `uv` installation, slash commands,
extensions, and presets.

### With Spec-Kitty (`spec-kitty`)

```text
spec.md -> plan.md -> tasks/WP{NN}-*.md -> validate-tasks --all (0 mismatches) -> implement
```

See [spec-kitty.md](references/spec-kitty.md) for WP frontmatter schemas,
OpenAPI fixtures, lane progression, and BC Gov §1 alignment.

## Verification

- **Spec-Kit**: run `/speckit.analyze` (0 consistency issues), verify all acceptance criteria and tasks are checked, and run `/speckit.verify` if installed.
- **Spec-Kitty**: confirm all WP files reach `lane: "done"` and `spec-kitty validate-tasks --all` reports 0 mismatches.

```bash
spec-kitty validate-tasks --all
```

## References

- [GitHub Spec-Kit Guide](references/spec-kit.md) — `specify` CLI setup, SDD slash commands, extensions, presets, and pre-merge checklist
- [Spec-Kitty & BC Gov §1 Guide](references/spec-kitty.md) — `spec-kitty` directory layout, `spec.md`/`plan.md`/WP schemas, and OCIO §1 Requirements Management table
- Templates: [spec.md.j2](assets/templates/spec.md.j2) • [plan.md.j2](assets/templates/plan.md.j2) • [work-package.md.j2](assets/templates/work-package.md.j2)
- [Acceptance Criteria](references/acceptance-criteria.md) — observable pass/fail criteria for SDD phase gates and toolchain validation
